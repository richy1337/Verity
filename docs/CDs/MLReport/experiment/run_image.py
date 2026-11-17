"""An educational image-origin pilot on a small Tiny-GenImage sample."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep

import numpy as np
from PIL import Image, ImageOps
import PIL
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from run_text import SEED, choose_margin, outputs

DATASET = "TheKernel01/Tiny-GenImage"
SERVER = "https://datasets-server.huggingface.co/rows"
WINDOWS = {"train": ("train", (0, 32, 64, 96, 128, 160)),
           "validate": ("train", (192, 224)),
           "test": ("validation", (0, 32, 64, 96))}
WINDOW_SIZE = 16


def fetch(url, size):
    for attempt in range(4):
        try:
            with urlopen(url, timeout=25) as response:
                return response.read(size)
        except URLError:
            if attempt == 3:
                raise
            sleep(1 + attempt)


def dataset_rows():
    for split, (source, offsets) in WINDOWS.items():
        for offset in offsets:
            params = urlencode({"dataset": DATASET, "config": "default", "split": source,
                                "offset": offset, "length": WINDOW_SIZE})
            records = json.loads(fetch(f"{SERVER}?{params}", 15_000_000))["rows"]
            if len(records) != WINDOW_SIZE:
                raise ValueError(f"{source}[{offset}] returned {len(records)} rows")
            for item in records:
                row = item["row"]
                yield split, source, item["row_idx"], row


def load_sample(record, cache):
    split, source, index, row = record
    path = cache / f"{source}-{index}.image"
    if not path.exists():
        url = row["image"]["src"]
        host = urlparse(url)
        if host.scheme != "https" or host.hostname != "datasets-server.huggingface.co":
            raise ValueError("Unexpected dataset asset host")
        path.write_bytes(fetch(url, 10_000_001))
    content = path.read_bytes()
    if len(content) > 10_000_000:
        return None
    with Image.open(BytesIO(content)) as decoded:
        if not all(64 <= edge <= 4096 for edge in decoded.size):
            return None
        if decoded.format not in {"PNG", "JPEG", "WEBP"} or getattr(decoded, "n_frames", 1) != 1:
            return None
        image = ImageOps.exif_transpose(decoded).convert("RGB")
    thumb = np.asarray(image.convert("L").resize((9, 8)))
    dhash = int.from_bytes(np.packbits(thumb[:, 1:] > thumb[:, :-1]).tobytes(), "big")
    normalized = image.resize((64, 64), Image.Resampling.BILINEAR)
    recoded = BytesIO()
    image.save(recoded, format="JPEG", quality=60)
    recoded.seek(0)
    with Image.open(recoded) as altered:
        recompressed = altered.convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
    return {
        "split": split, "source": source, "row": index, "label": row["label"],
        "generator": row["generator"], "sha256": hashlib.sha256(content).hexdigest(),
        "dhash": dhash, "dimensions": image.size,
        "features": describe(normalized), "recompressed": describe(recompressed),
    }


def describe(image):
    arr = np.asarray(image, dtype=float) / 255.0
    means = arr.mean(axis=(0, 1))
    deviations = arr.std(axis=(0, 1))
    fields = [means, deviations]
    gray = arr.mean(axis=-1)
    for axis in (0, 1):
        gradients = np.abs(np.diff(gray, axis=axis))
        fields.append(np.array([gradients.mean(), gradients.std(),
                                np.quantile(gradients, 0.9), np.quantile(gradients, 0.99)]))
    spectrum = np.abs(np.fft.rfft2(gray - gray.mean())) ** 2
    y = np.fft.fftfreq(64)[:, None]
    x = np.fft.rfftfreq(64)[None, :]
    radius = np.sqrt(y * y + x * x)
    total = spectrum.sum() or 1
    fields.append(np.array([spectrum[(lower < radius) & (radius <= upper)].sum() / total
                            for lower, upper in [(0, .06), (.06, .15), (.15, .3), (.3, .72)]]))
    return np.concatenate(fields)


def screen_duplicates(rows):
    removed = set()
    exact = near = 0
    for i, row in enumerate(rows):
        for j in range(i):
            old = rows[j]
            if row["sha256"] == old["sha256"]:
                exact += 1
            elif (row["dhash"] ^ old["dhash"]).bit_count() <= 4:
                near += 1
            else:
                continue
            removed.update((i, j))
    return [row for i, row in enumerate(rows) if i not in removed], {
        "exact_pairs": exact, "near_pairs": near, "removed": len(removed)
    }


def fit(x, y):
    return make_pipeline(StandardScaler(), LogisticRegression(C=1, random_state=SEED)).fit(x, y)


def design(rows, key="features"):
    x = np.vstack([row[key] for row in rows])
    y = np.array([row["label"] for row in rows])
    return x, y


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    records = list(dataset_rows())
    with ThreadPoolExecutor(max_workers=10) as pool:
        collected = list(pool.map(lambda record: load_sample(record, args.cache), records))
    usable = [row for row in collected if row is not None]
    rows, duplicate_audit = screen_duplicates(usable)
    slices = {split: [row for row in rows if row["split"] == split] for split in WINDOWS}
    x, y = design(slices["train"])
    baseline = fit(x[:, :6], y)
    candidate = fit(x, y)

    x, y = design(slices["validate"])
    p = candidate.predict_proba(x)[:, 1]
    validation, feasible = choose_margin(y, p, baseline.predict(x[:, :6]))
    margin = validation["margin"]
    metrics, predictions = {}, []
    for name, features in [("test", "features"), ("jpeg60", "recompressed")]:
        x, y = design(slices["test"], features)
        p = candidate.predict_proba(x)[:, 1]
        base = baseline.predict(x[:, :6])
        metrics[name] = outputs(y, p, margin, base)
        for row, score, prior in zip(slices["test"], p, base):
            predictions.append({"variant": name, "sha256": row["sha256"],
                                "label": row["label"], "generator": row["generator"],
                                "probability": round(float(score), 12), "baseline": int(prior),
                                "outcome": int(score >= .5) if abs(score - .5) >= margin else "abstain"})
    summary = {"dataset": DATASET, "windows": WINDOWS, "window_size": WINDOW_SIZE,
               "selected": len(records), "invalid": len(collected) - len(usable),
               "duplicates": duplicate_audit, "pillow": PIL.__version__, "seed": SEED,
               "split_counts": {key: dict(Counter(row["label"] for row in values))
                                for key, values in slices.items()},
               "margin": margin, "validation_feasible": feasible,
               "validation": validation, "metrics": metrics}
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = [{k: v for k, v in row.items() if k not in ("features", "recompressed")}
                for row in rows]
    for name, data in [("metrics.json", summary), ("predictions.json", predictions),
                       ("split_manifest.json", manifest)]:
        (args.out / name).write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
