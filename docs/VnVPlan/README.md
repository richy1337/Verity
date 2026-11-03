# Verification and Validation Plan

`VnVPlan.tex` is the source; the reviewed output is `pdfs/VnVPlan/VnVPlan.pdf`.
The plan distinguishes available document/input checks from planned product tests.

From the repository root:

```sh
python3 test/documentation/verify_specification.py --with-hazard
python3 -m pip install -r test/fixtures/requirements.txt
python3 test/fixtures/generate.py --seed 42
make docs/VnVPlan/VnVPlan.pdf
```

After a local build, place the compiled document in `pdfs/VnVPlan/` and remove the generated document PDF from `docs/VnVPlan/`. Embedded figure PDFs elsewhere in `docs/` are separate assets and must be preserved.

The fixture generator, exact boundary recipes, expected dispositions and limitations are documented in [the fixture README](../../test/fixtures/README.md). The PDF's data-collection appendix defines fixed sample budgets, source grouping, analysis and evidence retention for assets that still need to be frozen before execution. Existing specification checks do not certify product behavior or inspect the plan's constants/traceability.

The follow-up review also requires team confirmation of personal disclosure/reflection attestations and separate evidence for peer-review issues and the V&V presentation. These activities are not inferred from passing document checks.
