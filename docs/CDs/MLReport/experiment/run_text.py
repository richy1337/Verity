"""Verity Fall CD. Reproduce a scoped English text-origin pilot."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import platform
import re
import time
import unicodedata

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, f1_score
from sklearn.pipeline import make_pipeline

SOURCE = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all.jsonl"
SOURCE_SHA = "ee231f82283d754050a4dc58ecf9331afaf5daea7283c6da0b096ed0fb2774cf"
SEED = 23
DOMAIN_LIMIT = 1400
HELD_DOMAIN = "medicine"
DUPLICATE_THRESHOLD = 0.85
L2_C = 1.0
FLOOR, CEILING, TARGET, DELTA = 0.70, 0.10, 0.80, 0.10


@dataclass(frozen=True)
class Item:
    domain: str
    group: str
    label: int
    text: str
    identity: str
    split: str


def normalize(value):
    return " ".join(unicodedata.normalize("NFKC", value).split())


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bucket(group):
    return int(digest(f"{SEED}:{group}")[:15], 16) % 100


def partition(domain, group):
    if domain == HELD_DOMAIN:
        return "held_domain"
    draw = bucket(group)
    if draw < 70:
        return "train"
    if draw < 80:
        return "calibrate"
    if draw < 90:
        return "validate"
    return "test"


def load_items(path):
    rows = defaultdict(dict)
    domains_by_group = defaultdict(set)
    audit = Counter()
    for line in path.open(encoding="utf-8"):
        row = json.loads(line)
        audit["source_rows"] += 1
        group = digest(normalize(row["question"]).casefold())
        domain = row["source"]
        domains_by_group[group].add(domain)
        answers = rows[domain].setdefault(group, [set(), set()])
        for label, key in enumerate(("human_answers", "chatgpt_answers")):
            for text in row[key]:
                text = normalize(text)
                if 150 <= len(text) <= 10000:
                    answers[label].add(text)
                else:
                    audit["answer_outside_text_bounds"] += 1
    chosen = []
    for domain, groups in sorted(rows.items()):
        valid_groups = [
            group for group, pair in groups.items()
            if all(pair) and len(domains_by_group[group]) == 1
        ]
        audit[f"eligible_question_groups:{domain}"] = len(valid_groups)
        for group in sorted(valid_groups, key=lambda group: digest(f"{SEED}:{group}"))[:DOMAIN_LIMIT]:
            for label, choices in enumerate(groups[group]):
                text = min(choices, key=lambda value: digest(f"{SEED}:{value}"))
                chosen.append(Item(
                    domain, group, label, text, digest(text.casefold()), partition(domain, group)
                ))
    occurrences = Counter(item.identity for item in chosen)
    deduped = [item for item in chosen if occurrences[item.identity] == 1]
    audit["exact_duplicate_answers_removed"] = len(chosen) - len(deduped)
    cleaned, pairs = screen_near_duplicates(deduped)
    audit["cross_split_near_duplicate_pairs"] = pairs
    audit["near_duplicate_answers_removed"] = len(deduped) - len(cleaned)
    complete = Counter(item.group for item in cleaned)
    paired = [item for item in cleaned if complete[item.group] == 2]
    audit["unpaired_answers_removed"] = len(cleaned) - len(paired)
    return paired, dict(audit)


def screen_near_duplicates(items):
    # Exhaustive word-trigram set Jaccard across splits. Sparse products
    # enumerate pairs sharing at least one trigram, which is necessary at 0.85.
    vectorizer = CountVectorizer(
        ngram_range=(3, 3), binary=True, dtype=np.int32, token_pattern=r"(?u)\b\w+\b"
    )
    matrix = vectorizer.fit_transform([item.text for item in items])
    sizes = np.diff(matrix.indptr)
    transposed = matrix.T.tocsr()
    splits = np.array([item.split for item in items])
    excluded = set()
    matches = 0
    for start in range(0, len(items), 128):
        overlaps = (matrix[start:start + 128] @ transposed).tocoo()
        left = overlaps.row + start
        right = overlaps.col
        union = sizes[left] + sizes[right] - overlaps.data
        matched = (
            (left < right)
            & (splits[left] != splits[right])
            & (overlaps.data >= DUPLICATE_THRESHOLD * union)
        )
        matches += int(matched.sum())
        excluded.update(left[matched].tolist())
        excluded.update(right[matched].tolist())
    return [item for index, item in enumerate(items) if index not in excluded], matches


def label_array(items):
    return np.array([item.label for item in items], dtype=int)


def model(analyzer, ngrams):
    return make_pipeline(
        TfidfVectorizer(analyzer=analyzer, ngram_range=ngrams, min_df=3, max_features=60000,
                        sublinear_tf=True, dtype=np.float64),
        LogisticRegression(C=L2_C, solver="liblinear", max_iter=1000, random_state=SEED),
    )


def outputs(y, p, margin, baseline):
    selected = np.abs(p - 0.5) >= margin
    positive = p >= 0.5
    negatives = y == 0
    condition = selected & negatives
    tp = int(np.count_nonzero(positive & (y == 1) & selected))
    fp = int(np.count_nonzero(positive & negatives & selected))
    tn = int(np.count_nonzero(~positive & negatives & selected))
    fn = int(np.count_nonzero(~positive & (y == 1) & selected))
    def macro(expected, predicted):
        if len(expected) == 0:
            return None
        return float(f1_score(expected, predicted, labels=[0, 1], average="macro",
                              zero_division=0))
    macro_f1 = macro(y[selected], positive[selected])
    baseline_f1 = macro(y[selected], baseline[selected])
    return {
        "n": len(y), "coverage": float(np.mean(selected)), "assessed": int(selected.sum()),
        "abstain": int((~selected).sum()), "human_assessed": int(condition.sum()),
        "human_total": int(negatives.sum()), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "macro_f1": macro_f1, "baseline_same_items_f1": baseline_f1,
        "delta": macro_f1 - baseline_f1 if macro_f1 is not None else None,
        "all_item_fpr": fp / int(negatives.sum()) if negatives.any() else None,
        "assessed_fpr": fp / int(condition.sum()) if condition.any() else None,
        "forced_macro_f1": macro(y, positive),
        "full_population_macro_f1": macro(y, np.where(selected, positive, -1)),
        "baseline_forced_macro_f1": macro(y, baseline),
        "brier": float(brier_score_loss(y, p)),
        "class_coverage": {str(label): float(np.mean(selected[y == label])) for label in (0, 1)
                           if (y == label).any()},
    }


def evaluate_margin(y, p, baseline, margin):
    result = outputs(y, p, margin, baseline)
    result["margin"] = margin
    return result


def choose_margin(y, p, baseline):
    candidates = [evaluate_margin(y, p, baseline, i / 100) for i in range(0, 50)]
    feasible = [
        row for row in candidates
        if row["coverage"] >= FLOOR and row["assessed_fpr"] is not None
        and row["assessed_fpr"] <= CEILING
    ]
    if not feasible:
        fallback = [row for row in candidates if row["coverage"] >= FLOOR]
        return min(fallback, key=lambda row: (row["assessed_fpr"], -row["macro_f1"],
                                              -row["coverage"])), False
    return max(feasible, key=lambda row: (row["macro_f1"], row["coverage"])), True


def evaluate_split(items, learned, calibrator, baseline, margin):
    y = label_array(items)
    strings = [item.text for item in items]
    start = time.perf_counter()
    score = learned.decision_function(strings)
    p = calibrator.predict_proba(score.reshape(-1, 1))[:, 1]
    elapsed = time.perf_counter() - start
    base = baseline.predict(strings)
    metrics = outputs(y, p, margin, base)
    metrics["uncalibrated_brier"] = float(brier_score_loss(y, 1 / (1 + np.exp(-score))))
    metrics["prior_baseline_macro_f1"] = float(
        f1_score(y, np.zeros_like(y), labels=[0, 1], average="macro", zero_division=0)
    )
    metrics["gates"] = {
        "macro_f1": metrics["macro_f1"] is not None and metrics["macro_f1"] >= TARGET,
        "coverage": metrics["coverage"] >= FLOOR,
        "assessed_fpr": metrics["assessed_fpr"] is not None and metrics["assessed_fpr"] <= CEILING,
        "delta": metrics["delta"] is not None and metrics["delta"] >= DELTA,
    }
    metrics["slices"] = {}
    for name in sorted({item.domain for item in items}):
        mask = np.array([item.domain == name for item in items])
        metrics["slices"][name] = outputs(y[mask], p[mask], margin, base[mask])
    short = np.array([len(item.text) < 300 for item in items])
    if short.any():
        metrics["slices"]["150_to_299_chars"] = outputs(y[short], p[short], margin, base[short])
    rows = [
        {"id": item.identity, "group": item.group, "source": item.domain, "split": item.split,
         "length": len(item.text), "label": item.label, "probability": round(float(value), 12),
         "baseline": int(base[index]),
         "outcome": int(value >= 0.5) if abs(value - 0.5) >= margin else "abstain"}
        for index, (item, value) in enumerate(zip(items, p))
    ]
    return metrics, rows, elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    sha = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    if sha != SOURCE_SHA:
        raise SystemExit(f"Unexpected corpus checksum: {sha}")
    items, audit = load_items(args.corpus)
    splits = {name: [item for item in items if item.split == name]
              for name in ("train", "calibrate", "validate", "test", "held_domain")}
    assert len({item.identity for item in items}) == len(items)
    assert len({(item.group, item.split) for item in items}) == len(items) // 2
    assert not any(item.domain == HELD_DOMAIN for item in splits["train"])
    train_text = [item.text for item in splits["train"]]
    train_y = label_array(splits["train"])
    start = time.perf_counter()
    baseline = model("word", (1, 2)).fit(train_text, train_y)
    learned = model("char", (3, 5)).fit(train_text, train_y)
    train_seconds = time.perf_counter() - start
    fit_text = [item.text for item in splits["calibrate"]]
    cal_score = learned.decision_function(fit_text).reshape(-1, 1)
    calibrator = LogisticRegression(C=L2_C, solver="lbfgs", random_state=SEED)
    calibrator.fit(cal_score, label_array(splits["calibrate"]))
    val_text = [item.text for item in splits["validate"]]
    val_prob = calibrator.predict_proba(learned.decision_function(val_text).reshape(-1, 1))[:, 1]
    frozen, feasible = choose_margin(
        label_array(splits["validate"]), val_prob, baseline.predict(val_text)
    )
    margin = frozen["margin"]
    metrics = {}
    outcomes = []
    timings = {}
    for name in ("train", "test", "held_domain"):
        metric, predictions, elapsed = evaluate_split(
            splits[name], learned, calibrator, baseline, margin
        )
        metrics[name] = metric
        timings[name] = elapsed
        if name != "train":
            outcomes.extend(predictions)
    summary = {
        "dataset": SOURCE, "dataset_sha256": sha, "seed": SEED, "domain_limit": DOMAIN_LIMIT,
        "excluded": audit, "split_counts": {name: len(values) for name, values in splits.items()},
        "model": {"baseline": "word (1,2) TF-IDF + L2 LR",
                  "candidate": "character (3,5) TF-IDF + L2 LR",
                  "C": L2_C, "min_df": 3, "max_features": 60000,
                  "calibrator": "sigmoid (L2 logistic regression)",
                  "duplicate_jaccard_threshold": DUPLICATE_THRESHOLD},
        "held_domain": HELD_DOMAIN, "margin": margin, "validation_feasible": feasible,
        "validation": frozen, "metrics": metrics,
        "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                    "numpy": np.__version__, "scipy": scipy.__version__,
                    "scikit_learn": sklearn.__version__, "training_batches_seconds": train_seconds,
                    "score_batches_seconds": timings},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in [("metrics.json", summary), ("predictions.json", outcomes),
                       ("split_manifest.json", [
                           {"id": item.identity, "group": item.group, "source": item.domain,
                            "split": item.split, "label": item.label} for item in items])]:
        (args.output / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"split_counts": summary["split_counts"], "margin": margin, "metrics": metrics},
                     indent=2))


if __name__ == "__main__":
    main()
