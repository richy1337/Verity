# V&V input fixtures

These are input construction tools for the V&V plan, not production code or a completed test harness. Generated content is synthetic and may be redistributed under the repository license. It is not labelled evidence of human or AI authorship and must not enter the detector accuracy benchmark.

From the repository root:

```sh
python3 -m pip install -r test/fixtures/requirements.txt
python3 test/fixtures/generate.py --seed 42
python3 -m http.server 8001 --bind 127.0.0.1 --directory test/fixtures/generated
```

Start the same static server on port 8002 in a second terminal for FT-1's cross-origin image. Open `http://127.0.0.1:8001/pages/scope.html`. The product and Playwright harness are separate, planned deliverables.

The generator writes into ignored `test/fixtures/generated/`, including two 10 MB boundary files. `manifest.json` records the seed, Pillow/codec/zlib versions, SHA-256, byte count, Unicode code-point count for text, and expected boundary disposition. Compare hashes only within the recorded encoder environment; record a new manifest when codecs change. Use a fresh output directory for a clean generation. Never decode the bomb fixture before checking its dimensions.

| Available construction | Plan cases | Precise input |
|---|---|---|
| ASCII bounds | FT-2, UT-C3 | 0, 149, 150, 1,000, 10,000 and 10,001 code points; nonempty rejected strings contain a canary without changing the length |
| Unicode bounds | FT-2, UT-C3 | 149 and 150 code points containing `é`/`ü`; emoji variants at 149, 150, 10,000 and 10,001 code points distinguish code points from JavaScript UTF-16 length. Nonempty rejected variants retain the canary |
| Image bounds | FT-3, UT-C3 | 63x64 PNG, 64x63 JPEG, 64x64 PNG, 4096x4096 WebP, 4097x4096 PNG, 1024x1024 PNG padded to exactly 10,000,000 and 10,000,001 bytes |
| Bomb input | FT-3, UT-C3 | Exactly 200,000 bytes; valid IHDR with CRC declaring 30,000x30,000; truncated IDAT |
| Format/execution inputs | FT-4 | SVG script renamed PNG, animated GIF, MP4 signature, half-truncated JPEG, ELF renamed JPEG, and 500-character HTML/XSS text |
| Capture page and image | FT-1 | Exactly 500 target characters, sibling/cookie/storage canaries, same-origin and cross-origin 512x512 PNG |
| Lexicons | FT-5, FT-7 | Explicit accusation and guarantee terms; human semantic review remains necessary |
| Privacy canaries | FT-12, NFT-4 | Fifty unique 500-character texts and fifty 64x64 PNGs with matching tEXt canaries; the manifest assigns 9/9/8/8/8/8 paths for NFT-4. FT-12 uses six canaries and explicitly drives its six named paths. Use each canary in the user note too |
| Injection pairs | FT-8 | Fifteen clean/injected text pairs and fixed score/feature records for controlled instruction-handling checks |

The plan's remaining data must be frozen before execution. Their owners and dates are specified in the plan's data-collection appendix. They are not claimed to be committed here:

- **Provenance (Raymond):** obtain ten consenting team camera originals at 1024x1024; record hashes and permission. Sign copies with a test certificate using `c2patool`, recording its exact version, signing command, manifest and test trust-store policy. Generate Class B with `Image.save(..., format="JPEG", quality=70)` with EXIF omitted and without copying C2PA APP11 segments. Generate five Class C copies by changing one pixel after signing without resigning, and five by changing EXIF `Make` or `DateTimeOriginal` while retaining the signed assertions. Save parser validation reports and expected locators. Verify the intended contradiction using `c2patool` before using a file as a test oracle. A valid signature from a test certificate is not a public trust claim.
- **Evidence/abstention/grounding:** commit ten synthetic content items with declared stub features, ten borderline cases, twenty clearly identified opinion/satire/poetry texts, and ten contradicted explanation drafts with their feature registry. These are controlled functional inputs; real-detector behavior is evaluated separately on frozen, held-out data. Provenance-conflict cases reuse the approved signed photos.
- **Image prompt injection:** write the injected instruction to EXIF `ImageDescription`, `UserComment`, or `XPComment` in ten copies of approved photos; retain clean twins, exact tag values and hashes. Freeze noninstruction computed features for the controlled FT-8 run.
- **Hostile-page harness:** implement FT-16's five attacks and log both the attempted action and its observed effect. Verify the authoritative extension-owned controls, not an inaccessible page imitation.
- **Usability:** freeze the separate onboarding page, three unseen comprehension pages, expected primary evidence/tag, explanation/limitation text, fixed facilitator script and scorer answer sheet. Participant prompts use only neutral item numbers; expected statuses and answers stay in the facilitator/scorer materials. Item 2 is a satirical ESL-style passage; ESL authorship alone is not an abstention reason. Force timeout through a controlled provider/proxy delay; keep production test-mode flags off. Do not coach the scored tasks.
- **Performance:** commit the exact 100 text and 100 image IDs and native sizes described in the plan; record acquisition and rendered-result timestamps per request.
- **ML benchmark:** freeze licensed source revisions, label/source-group IDs, deduplication results, splits, subgroup annotations and checkpoint/config hashes under the plan's sampling protocol. Synthetic generated fixtures are excluded.

Do not substitute raw user selections for any fixture or store them in benchmark artifacts. A missing required asset is a blocked/not-run case, never a passing result.
