# Fall ML report experiments

Both pilots run on CPU. These are measurements for the Fall report, with full product acceptance left to the V&V Plan. The text pilot compares word and character TF–IDF with logistic regression. The image pilot tests simple colour, gradient and frequency features.

## Replay

Use Python 3.12 and install the recorded versions.

```sh
python -m pip install -r requirements.txt
curl -fL https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/all.jsonl -o hc3.jsonl
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run_text.py hc3.jsonl text-replay
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run_image.py tiny-images image-replay
```

The text script verifies the HC3 checksum before reading any rows. The source was the [HC3 English release](https://huggingface.co/datasets/Hello-SimpleAI/HC3). Its general terms are CC BY-SA 4.0, with stricter original source terms taking precedence.

The image script fetches the documented sample windows from the [Tiny-GenImage dataset viewer](https://huggingface.co/datasets/TheKernel01/Tiny-GenImage) and caches the served bytes locally. The mirror lists CC BY-NC-SA 4.0. Compare the row identities and SHA-256 hashes in the replay's split manifest against the recorded manifest before comparing metrics. Delete the local input cache and rerun if it contains a partial download. The repository ships no benchmark inputs.

## Evidence

- `text/metrics.json` records splits, exclusions, fit settings, validation selection, held-out results and execution environment. A second run on the same host reproduced the prediction and split manifests byte for byte and matched every metric after excluding timing.
- `image/metrics.json` records the image sample, duplicate screen and held-out outcomes, including its paired JPEG re-encoding test. The image margin missed the validation FPR gate and is a comparison setting.
- Each `predictions.json.gz` holds the scored held-out outcomes and baseline decisions. Each `split_manifest.json.gz` holds the recorded identities and split assignments. Decompress with `gzip -dc`. The outputs do not include raw answers, prompts or image payloads.
- False-positive counts, confusion counts and assessed macro-F1 were independently recomputed from each held-out prediction file. The text overlap screen covers exact normalized answers and the specified word-trigram threshold. The image screen covers byte identity and nearby difference hashes. Neither screen measures all forms of semantic duplication.
