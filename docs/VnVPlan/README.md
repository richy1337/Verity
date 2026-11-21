# Verification and Validation Plan

`VnVPlan.tex` is the authoritative LaTeX source; the reviewed PDF output lives at `pdfs/VnVPlan/VnVPlan.pdf`.
The plan separates currently runnable documentation and fixture checks from planned dynamic product and human usability tests.

From the repository root:

```sh
python3 test/documentation/verify_specification.py --with-hazard
python3 test/documentation/verify_design.py
python3 test/fixtures/generate.py --text-and-png-only --seed 42
tectonic docs/VnVPlan/VnVPlan.tex
```

For full image-fixture generation (including Pillow-built boundary and decompression-bomb PNG/JPEG/WebP files):

```sh
python3 -m pip install -r test/fixtures/requirements.txt
python3 test/fixtures/generate.py --seed 42
```

After compiling locally, copy `VnVPlan.pdf` to `pdfs/VnVPlan/VnVPlan.pdf` and delete the compiled PDF from `docs/VnVPlan/` so only source files remain inside `docs/`.

See [`test/fixtures/README.md`](../../test/fixtures/README.md) for fixture inventories (including `FX-EVID` subtle-accusation controls and `FX-ABST` genre texts) and Section 6.3 of the plan for dataset licensing, freeze gates, and evidence archiving rules.
