# Proof of Concept Demonstration

## User workflow and evidence output

Calvin leads this segment. The team’s [PoC Productivity Report](../../../pdfs/projMngmnt/POC_Productivity_Rep.pdf) schedules the FastAPI and browser extension integration for Revision 0. For the December 2 demo, run the result display on prepared response examples. Raymond presents the measured detector outcomes in the separate ML pilot segment.

From the repository root, run the walkthrough with Python 3:

```sh
python3 src/poc/walkthrough.py examples docs/Presentations/D0_ProofOfConceptDemo/samples/example-responses.json
```

1. **Completed text.** “This is an example result for the repair café passage. The assessment completed and flagged a writing pattern. Authentic writing can trigger the same signal. The user can check draft history or go to the original author.”
2. **Inconclusive image.** “This copy of *Blue Marble* is missing embedded provenance. That leaves its origin open from this copy alone. The user can compare it with NASA’s original archive record.”
3. **Failed analysis.** “The check didn’t complete, so the display shows a failure status with no assessment. Raymond will now show the measured results from our text and image pilots.”

Run the command on the demo laptop before the session. Each screen labels its outcome as an example response. The repair café passage is AI-drafted and fictional. The JPEG is NASA’s 640 × 640 derivative of Apollo 17 photograph AS17-148-22727, distributed without embedded EXIF or C2PA provenance. Both inputs are for the walkthrough and stay outside the benchmark. [NASA source and image credit](https://images.nasa.gov/details/as17-148-22727)

## Revision 0 service integration

The client can submit each sample to the local FastAPI endpoint when it is available:

```sh
python3 src/poc/walkthrough.py text docs/Presentations/D0_ProofOfConceptDemo/samples/repair-cafe.txt
python3 src/poc/walkthrough.py image docs/Presentations/D0_ProofOfConceptDemo/samples/blue-marble.jpg
```

Both commands call `POST /api/v1/analyze` on `127.0.0.1:8000`. Pass `--port` if FastAPI uses another port.
