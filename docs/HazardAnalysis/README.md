# Hazard Analysis

This directory contains the Revision 0 Failure Mode and Effects Analysis (FMEA) and Safety and Security Requirements for Verity.

- [`HazardAnalysis.tex`](./HazardAnalysis.tex) --- Source document defining system boundaries, assumptions (`A1`--`A5`), component FMEA (`H1`--`H10`), control ownership and open verification gates, safety/security requirements (`SR1`--`SR9`), milestone roadmap, GenAI disclosure, and reflections.
- [`HazardComponentDiagram.pdf`](./HazardComponentDiagram.pdf) --- Component and trust-boundary diagram embedded into the compiled PDF.
- [`../../pdfs/HazardAnalysis/HazardAnalysis.pdf`](../../pdfs/HazardAnalysis/HazardAnalysis.pdf) --- Compiled PDF output built by CI and verified via `python3 test/documentation/verify_specification.py --with-hazard`.
