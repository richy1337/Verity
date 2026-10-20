# Software Requirements Specification

`SRS.tex` is the authoritative Meyer-adapted PEGS specification. Compile from the repository root with:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=docs/SRS docs/SRS/WorkflowActivityDiagram.tikz
make -B docs/SRS/SRS.pdf
cp docs/SRS/SRS.pdf pdfs/SRS/SRS.pdf
python3 test/documentation/verify_specification.py
```

The tracked `.tikz` source regenerates the workflow diagram. Commit its PDF alongside source changes. Document PDFs live under `pdfs/`; figure PDFs remain beside `SRS.tex`.

The executable examples read the published Boolean guards and metric membership predicates. They check the waiting state, event precedence, guard partition and abstention/coverage counterexamples. They do not measure implemented detector quality or production privacy behavior. After PR #25 is included, add `--with-hazard` to check that the nine shared safety statements match.

The October 19 correction defines `MIN_COVERAGE = 0.70` for the existing overall coverage gate and changes `MAX_RETENTION_TIME` to a 1.0-second bound on releasing application-owned transient references. Raw-content persistence remains prohibited at all times. The initial meeting minutes record historical discussion; the current SRS governs the revised contract.
