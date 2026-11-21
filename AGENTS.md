# AGENTS.md — Agentic Coding & Documentation Guide for Verity

This file provides canonical context, architecture invariants, requirement/hazard identifiers, build instructions, course grading conventions, readability standards, milestone playbooks, and target codebase blueprints for AI coding agents (Antigravity, Codex, Claude Code, Cursor, Copilot, etc.) and contributors working in the **Verity** repository (`richy1337/Verity`).

---

## 1. Project Identity & Team Roster

- **Project Name:** **Verity** — Explainable, Uncertainty-Aware Digital Content Assessment
- **Course:** McMaster University SFWRENG 4G06 Software Engineering Capstone (2026–2027, Team 23 — "Dream Team")
- **Teaching Assistant (TA):** Rebecca Di Filippo (`@rebeccadifilippo`)
- **Repository:** `https://github.com/richy1337/Verity` (License: MIT)
- **Product Summary:** A user-triggered desktop Chromium browser extension (Manifest Version 3) and team-controlled Python FastAPI analysis service + offline CLI evaluation harness that helps users evaluate suspicious webpage text and static images (`PNG`, `JPEG`, `WebP`) for AI-generation, manipulation, and provenance (`EXIF` / `C2PA`) signals. Optional external provider APIs sit outside the trust boundary and stay disabled unless retention parity holds and explicit per-request `FR8` consent is granted. Verity surfaces source-grounded evidence, plain-language false-positive warnings (`FR3`(d)), explicit uncertainty/limitations, an `inconclusive` abstention state when signals are weak, conflicting, or out-of-domain (e.g., opinion, satire, or poetry under $g(r)$), and concrete next verification steps, while enforcing zero persistent retention of user-selected content.

### Team 23 Members, GitHub Handles & Consistent Roles
Keep each member's voice, role, and course background consistent across all deliverables (`VnVPlan`, `MLReport`, `MG`/`MIS`, `VnVReport`, `UsabilityReport`, `UserGuide`, `ReflectAndTrace`, and `Productivity Reports`). **Course policy (`capstone/AdminDetails/Wk04-a.tex`):** include Team 23 (`Team 23 — Dream Team`) on all documents, **never** include MacIDs, `@mcmaster.ca` MacID emails, student numbers, or physical team meeting locations inside deliverable `.tex`/`.pdf` documents, and always spell out full McMaster course names alongside course codes in reflections (the MacID/email column below is for internal course-repo/GitHub reference only):

| Member | MacID & Email | GitHub Handle | Primary Ownership | Secondary Ownership | Key Course Background (Code + Full Name) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Calvin Salsali** | `salsalic@mcmaster.ca` | `@CalvinSalsali04` | Chrome MV3 browser extension UI, DOM selection capture, extension-owned consent/result card (`M1`–`M3`), user personas, Winter Usability Report | ML evaluation review, documentation QA | `SFWRENG 3RA3` (*Software Requirements and Security Aspects*), `SFWRENG 4HC3` (*Human-Computer Interaction*), `SFWRENG 2AA4` (*Software Design I*) |
| **Raymond Tao** | `taor10@mcmaster.ca` | `@Raymondtaoo` | Text & image signal detection (`M7`–`M8`), assessment policy/calibration (`M9`), benchmark design (`HC3`/`RAID`, `Tiny-GenImage`/`GenImage`), Fall ML Model Report | Backend API review, experiment reproducibility | `SFWRENG 4AL3` (*Applied Machine Learning*), `STATS 3Y03` (*Probability and Statistics for Engineering*), `SFWRENG 2DM3` (*Discrete Mathematics with Applications I*), `SFWRENG 3RA3` |
| **Jaden Moore** | `moorej70@mcmaster.ca` | `@JadenAntM` | Python FastAPI analysis service, request coordinator & `UUIDv4` isolation (`M5`), timeout/cancellation state machine, CI/CD & milestone scheduling | Extension integration, concurrency & burst load testing | `SFWRENG 3BB4` (*Concurrent System Design*), `SFWRENG 2AA4` (*Software Design I*), `SFWRENG 3A04` (*Software Design II*) |
| **Richard Han** *(Liaison)* | `hanr23@mcmaster.ca` | `@richy1337` | Offline CLI evaluation harness (`M10`), input validation (`M4`), ephemeral cleanup (`M6`), reproducibility & privacy checks, adversarial/fuzzing test suite, FMEA traceability | Model integration, backend reliability | `SFWRENG 3S03` (*Software Testing*), `SFWRENG 3RA3` (*Software Requirements and Security Aspects*) |

---

## 2. Repository Structure, Tooling Inventory & LaTeX CI Build Pipeline

```text
Verity/
├── .github/
│   ├── ISSUE_TEMPLATE/        # bug_report.md, engineering_task.md, lect.md, peer_review.md, sup_meet.md, ta_meet.md, team_meet.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── scripts/
│   │   ├── build_index.py     # Generates GitHub Pages index from committed PDFs in pdfs/
│   │   ├── record_deps.py     # Parses pdflatex .fls recorder files to update .pdf-deps.json
│   │   └── select_docs.py     # Determines which .tex/.md files in docs/ need rebuilding from .pdf-deps.json
│   └── workflows/
│       ├── latex-pages.yml          # Compiles changed docs/ via Make + pdflatex, syncs pdfs/, deploys Pages
│       └── specification-checks.yml # Runs verify_specification.py --with-hazard and verify_design.py on PRs & main
├── .pdf-deps.json             # Dependency graph mapping each docs/**/*.tex to every file it \inputs or \includegraphics
├── ExceptionsGranted.md       # Records approved Fall CD: Machine Learning Model Report (pdfs/CDs/MLReport/main.pdf)
├── Makefile                   # Compiles %.tex -> %.pdf via pdflatex (+ bibtex when .aux exists) and %.md -> %.pdf via pandoc
├── docs/                      # Authoritative LaTeX source files (DO NOT commit compiled document PDFs inside docs/)
│   ├── Common.text            # Shared \progname and \authname macros
│   ├── Comments.text          # Instructor comment macros (\wss{})
│   ├── Reflection.text        # Shared reflection preamble
│   ├── SRS_Reflection.text    # SRS reflection questions
│   ├── Checklists/            # 13 official checklists (Writing, ProbState, DevPlan, SRS, SRS-SciComp, HA, VnV, POC, MG, MIS, Code, GettingStarted, FinalDoc)
│   ├── ProblemStatementAndGoals/ProblemStatement.tex
│   ├── DevelopmentPlan/DevelopmentPlan.tex
│   ├── SRS/                   # Meyer-adapted PEGS SRS (SRS.tex + SystemContextDiagram.pdf, WorkflowActivityDiagram.pdf/.tikz, RequirementTraceabilityDiagram.pdf)
│   ├── HazardAnalysis/        # FMEA Hazard Analysis (HazardAnalysis.tex + HazardComponentDiagram.pdf)
│   ├── projMngmnt/            # MeetingNotes.tex, POC_Productivity_Rep.tex, Rev0_Productivity_Rep.tex, Final_Productivity_Rep.tex
│   ├── VnVPlan/               # Verification & Validation Plan (VnVPlan.tex, README.md)
│   ├── CDs/
│   │   ├── MLReport/          # CD-Fall: main.tex, acl.sty, acl_natbib.bst, custom.bib, Expectations_ML.md
│   │   │   └── experiment/    # Reproducible CPU pilot scripts & artifacts (README.md, requirements.txt, run_text.py, run_image.py, text/*.json*, image/*.json*)
│   │   └── UsabilityTesting/  # CD-Winter: Expectations.md (target UsabilityReport.tex — Week 22, Mar 2027)
│   ├── Design/
│   │   ├── README.md
│   │   ├── SoftArchitecture/MG.tex   # Module Guide (M1–M10, AC1–AC13, Uses DAG, implementation schedule)
│   │   └── SoftDetailedDes/MIS.tex   # Module Interface Specification (M1–M10 typed contracts & TblLifecycle)
│   ├── Presentations/         # D0_ProofOfConceptDemo/, D1_Rev0Demo/, D2_FinalPresentation/, D3_EXPO/
│   ├── VnVReport/VnVReport.tex       # Verification & Validation Report (Week 22 — Mar 2027)
│   ├── UserGuide/UserGuide.tex       # End-User Installation & Usage Guide (Week 26 — Apr 2027)
│   └── ReflectAndTrace/ReflectAndTrace.tex # Final Reflection & Traceability Report (Week 26 — Apr 2027)
├── pdfs/                      # Committed PDF outputs mirroring docs/ directory structure for TA grading
├── refs/References.bib        # Shared BibTeX bibliography
├── src/                       # Production source code (currently scaffolded: README.md, TraceToDesign.md; Rev 0 targets: extension/, backend/, benchmark/)
└── test/                      # Automated verification scripts, synthetic fixture generator, and Rev 0 test suites
    ├── README.md
    ├── documentation/
    │   ├── verify_specification.py  # Parses SRS.tex & HazardAnalysis.tex (--with-hazard, --root, --srs)
    │   └── verify_design.py         # Audits MG.tex & MIS.tex (M1–M10, 52 trace rows, 13 ACs, DAG, 16 constants, 32 lifecycle rows, 10 schedule pairs)
    └── fixtures/
        ├── generate.py              # Deterministic fixture builder (--seed, --output, --text-and-png-only, FX-EVID, FX-ABST)
        ├── README.md                # Inventory & manual data-freeze recipes
        └── requirements.txt         # Optional Pillow dependency for JPEG/WebP/GIF fixture generation
```

### Executable Documentation & Fixture Scripts
1. **`test/documentation/verify_specification.py`** (CI workflow `.github/workflows/specification-checks.yml`):
   - `python3 test/documentation/verify_specification.py --with-hazard` (also supports `--root <dir>` and `--srs <path>`).
   - Parses `SRS.tex` directly and executes 8 unit tests verifying: (a) the 5-row S.9.1 `pending` guard partition (`c, d, e, a, v`) is disjoint and complete across all $2^5 = 32$ Boolean assignments with cancellation $>$ deadline/error $>$ completion precedence; (b) S.9.2 full-population $\mathrm{TP}_c/\mathrm{FP}_c/\mathrm{FN}_c$ diagnostic formulas penalize sparse abstentions/errors; (c) `MIN_COVERAGE = 0.70` prevents selective-$F_1$ gaming; and (d) `--with-hazard` confirms `SR1`–`SR9` statements match verbatim between `SRS.tex` and `HazardAnalysis.tex`.
2. **`test/documentation/verify_design.py`** (CI workflow `.github/workflows/specification-checks.yml`):
   - `python3 test/documentation/verify_design.py`.
   - Audits `MG.tex` and `MIS.tex`: confirms all 52 required rows (`FR1`–`FR14`, `NFR1`–`NFR10`, `NFR.E.1`–`NFR.E.5`, `SR1`–`SR9`, `INV1`–`INV4`, `H1`–`H10`) map to non-empty subsets covering `M1`–`M10`; `AC1`–`AC13` cover `LC1`–`LC6` with 1-to-1 leaf ownership; all `MIS` `Uses` sets match the `MG` TikZ diagram edges (`12` edges) and form a DAG; every `MIS` operation has semantics (`M4` omits `initialize`, all others include it); all 32 Boolean assignments in `TblLifecycle` match SRS S.9.1; all `16` exported constants in `MIS` `TblConstants` match `MIS` usage; all `10` rows in `MG` `TblSchedule` have distinct owner and reviewer; and zero unresolved labels, `+` diff markers, `\wss{`, `TBD`, or adjacent headings exist.
3. **`test/fixtures/generate.py`**:
   - `python3 test/fixtures/generate.py --seed 42 --output /tmp/verity-fixtures` (default output if `--output` provided; pass `--text-and-png-only` for pure-Python execution without Pillow, generating 201 deterministic text, HTML, PNG, `FX-EVID`, `FX-ABST`, lexicon, PII canary, and injection fixtures plus `manifest.json`).
   - Materializes `FX-EVID` (`evidence/text-pos-1..3.txt`, `text-neg-1..3.txt`, `img-pos-1..2.png`, `img-neg-1..2.png`, `evidence/expected.json`, and `evidence/subtle_accusations.json` with 5 non-keyword subtle-accusation negative controls) and `FX-ABST` (`abstention/borderline-text-1..5.txt`, `abstention/borderline-img-1..5.png`, `abstention/expected.json`, and 20 concrete 200–1,500 char out-of-domain texts: `opinion-1..7.txt`, `satire-1..7.txt`, `poetry-1..6.txt`).
4. **`docs/CDs/MLReport/experiment/`**:
   - Reproducible CPU baseline pilots (`SEED = 23`, Python 3.12, pinned `requirements.txt`): `run_text.py` (English `HC3`, `3,212` held-out predictions across same-source `test` and held-domain `medicine`, character 3–5 vs. word 1–2 TF–IDF + L2 LR) and `run_image.py` (`Tiny-GenImage`, `64` held-out predictions clean + paired JPEG-60 re-encoding). Stores `metrics.json`, `predictions.json.gz`, and `split_manifest.json.gz` per modality without committing raw dataset text or image payloads.

### Build & Git Rules for Agents
1. **Compiling Locally:** Compile any `.tex` file locally using `tectonic <file>.tex` (`/opt/homebrew/bin/tectonic`) or `pdflatex`.
2. **Where PDFs Live:**
   - **Compiled document PDFs** (e.g., `SRS.pdf`, `HazardAnalysis.pdf`, `VnVPlan.pdf`, `MG.pdf`, `MIS.pdf`, `POC_Productivity_Rep.pdf`) MUST be copied to `pdfs/<Subfolder>/<Doc>.pdf` and removed from `docs/<Subfolder>/<Doc>.pdf`.
   - **Embedded figure PDFs** inside `docs/<Subfolder>/` (such as `docs/SRS/SystemContextDiagram.pdf` or `docs/HazardAnalysis/HazardComponentDiagram.pdf`) are ignored by the root `.gitignore` (`*.pdf`) unless staged with **`git add -f docs/<Subfolder>/<Figure>.pdf`**. Always `git add -f` any new figure PDF in `docs/` and add it to that document's array in `.pdf-deps.json` so GitHub Actions `pdflatex` can find it.
3. **Package Compatibility with CI:** GitHub Actions (`latex-pages.yml`) installs `texlive-latex-extra`, `texlive-science`, `texlive-fonts-extra`, `texlive-fonts-recommended`, `texlive-latex-recommended`, `lmodern`, and `pandoc`. Avoid obscure packages (such as `zed-csp`); use standard `amsmath`/`amssymb`, `tabularx`, `ltablex`, `booktabs`, `pdflscape`, `enumitem`, and `hyperref`.
4. **`ltablex` + `tabularx` Rule:** When `\usepackage{ltablex}` is loaded, every `tabularx` is already a page-breaking `longtable`. Put `\caption{...} \label{...}\\` **inside** `\begin{tabularx}` and **do not** wrap `tabularx` inside `\begin{table}[H] ... \end{table}` (which prevents page breaking and causes vertical page overflows).
5. **Special Compilation Cases:**
   - **`docs/CDs/MLReport/main.tex`:** Uses ACL 2-column style (`acl.sty`, `acl_natbib.bst`, `custom.bib`). Set `\usepackage[preprint]{acl}` or `\usepackage[final]{acl}` so all 4 author names render — **omit MacIDs and `@mcmaster.ca` emails** per `capstone/AdminDetails/Wk04-a.tex` (never anonymous review mode). `Makefile` runs `bibtex` via `COMPILE_BIBTEX` when an `.aux` file exists; confirm `main.bbl` / citations resolve cleanly with zero `[?]` markers.
   - **`docs/Design/SoftDetailedDes/MIS.tex`:** Uses `\newcommand{\pdfbase}{https://github.com/richy1337/Verity/blob/main/pdfs}` and `hyperref` links to `pdfs/` rather than `\usepackage{xr}` / `\externaldocument`, because compiled SRS PDFs live in `pdfs/SRS/`, not `docs/SRS/`.

---

## 3. Canonical System Constants, Architecture & Identifier Registry

All documents (`SRS.tex`, `HazardAnalysis.tex`, `VnVPlan.tex`, `MLReport`, `MG.tex`, `MIS.tex`, `VnVReport.tex`, `ReflectAndTrace.tex`) and production code (`src/`) **must** use the exact same symbolic constants, subsystem/module boundaries, requirement IDs, and hazard IDs.

### 3.1 Authoritative Symbolic Constants (SRS Table 6, MIS `TblConstants` & VnV Parameters)

| Symbolic Constant | Value | Unit | Scope & Governing Requirements |
| :--- | :--- | :--- | :--- |
| `MIN_F1_SCORE` | `0.80` | Macro-$F_1$ | SRS Table 6 & MIS `TblConstants`: Minimum assessed unweighted Macro-$F_1$ on held-out benchmark (`NFR1`, `H1`, `H2`) |
| `MIN_COVERAGE` | `70.0%` (`0.70`) | Proportion | SRS Table 6 & MIS `TblConstants`: Overall coverage floor for selective-$F_1$ acceptance; report per-class/subgroup coverage and full-population diagnostics (`NFR1`) |
| `MAX_FPR` | `10.0%` (`0.10`) | Probability / `%` | SRS Table 6 & MIS `TblConstants`: Maximum False Positive Rate (both $\mathrm{FPR}_{\text{assessed}}$ and $\mathrm{FPR}_{\text{all}}$) on authentic items (`NFR1`, `NFR10`, `H1`) |
| `MIN_BASELINE_DELTA` | `+0.10` | Macro-$F_1$ delta | SRS Table 6 & MIS `TblConstants`: Minimum Macro-$F_1$ improvement over frozen naive baseline on identical assessed set $A$ (`NFR1`, Issue `#13`) |
| `MIN_UNDERSTANDING_RATE` | `80.0%` (`0.80`) | Percentage | SRS Table 6: Minimum uncoached user comprehension rate in usability study (`NFR2`, `H5`) |
| `MIN_USABILITY_PARTICIPANTS` | `10` | People | SRS Table 6: Minimum participant sample size for Winter Usability Evaluation (`NFR2`) |
| `MAX_RESPONSE_TIME` | `10.0` | `s` | SRS Table 6 & MIS `TblConstants`: End-to-end admission-to-terminal latency bound; exceeding transitions to `failed` (`FR6`, `NFR3`, `SR4`, `H6`) |
| `LATENCY_PERCENTILE` | `90.0%` (`0.90`) | Percentile | SRS Table 6: Share of valid warm single-item requests completing within `MAX_RESPONSE_TIME` (`NFR3`, `NFT-3`) |
| `MIN_TEXT_LENGTH` | `150` | `chars` | SRS Table 6 & MIS `TblConstants`: Minimum Unicode code-point count for text check (`FR1`, `FR2`, `SR6`, `H2`) |
| `MAX_TEXT_LENGTH` | `10,000` | `chars` | SRS Table 6 & MIS `TblConstants`: Maximum Unicode code-point count for text check (`FR1`, `FR2`, `SR6`, `H7`) |
| `MAX_IMAGE_SIZE` | `10.0` | `MB` ($10^7\text{ B}$) | SRS Table 6 & MIS `TblConstants`: Maximum byte size for static image (`PNG`, `JPEG`, `WebP`) (`FR1`, `FR2`, `SR6`, `H7`) |
| `MIN_IMAGE_DIM` | `64 x 64` | `px` | SRS Table 6 & MIS `TblConstants`: Minimum pixel dimensions, inclusive per axis (`FR2`, `SR6`, `H2`) |
| `MAX_IMAGE_DIM` | `4096 x 4096` | `px` | SRS Table 6 & MIS `TblConstants`: Maximum pixel dimensions to prevent decompression bombs (`FR2`, `SR6`, `H7`) |
| `MAX_INSTALL_TIME` | `5.0` | `min` | SRS Table 6: Maximum end-user extension installation and first-check time (`NFR6`, `NFR.E.2`) |
| `MAX_DEV_SETUP_TIME` | `15.0` | `min` | SRS Table 6: Maximum clean-machine developer bootstrap time via single setup script (`NFR6`, `NFT-6`) |
| `MAX_RETENTION_TIME` | `1.0` | `s` | SRS Table 6 & MIS `TblConstants`: Bound for stopping request-owned tasks and releasing application-owned transient payload references after local terminal decision; zero persistent raw writes at all times (`FR9`, `NFR4`, `SR8`, `H4`) |
| `MIN_SERVICE_UPTIME` | `99.0%` (`0.99`) | Percentage | SRS Table 6: End-to-end operational availability target over `AVAILABILITY_WINDOW` (`NFR8`, `NFT-8`) |
| `MAX_CONCURRENT_REQS` | `10` | Requests | SRS Table 6 & MIS `TblConstants`: Minimum admitted concurrent capacity maintaining strict `UUIDv4` isolation and burst admission refusal above cap (`FR10`, `NFR8`, `SR7`, `SR9`, `H7`–`H9`) |
| `MAX_REPRO_DELTA` | `0.005` | Macro-$F_1$ / FPR delta | SRS Table 6 & MIS `TblConstants`: Maximum cross-member benchmark reproduction discrepancy (`NFR7`, `H10`) |
| `MAX_UI_RENDER_LATENCY` | `500` | `ms` | SRS Table 6 & MIS `TblConstants`: Maximum extension UI latency for synchronous pre-admission rejection or terminal status banner (`FR2`, `FR6`) |
| `MAX_CANCEL_UI_LATENCY` | `200` | `ms` | SRS Table 6 & MIS `TblConstants`: Perceptual UI transition bound to `cancelled` after user clicks Cancel (`FR11`) |
| `MAX_DELIVERY_RECORD_AGE` | `60` | `s` | **MIS `TblConstants` (Design):** Expiry age after terminal decision for safe status-delivery metadata in `M5` (contains no raw item or excerpt) |
| `HEALTH_PROBE_INTERVAL` | `60` | `s` | **VnV Parameter (`NFT-8` / `NFR8`):** Synthetic valid end-to-end + `GET /healthz` availability probe cadence |
| `AVAILABILITY_WINDOW` | `60` | `min` | **VnV Parameter (`NFT-8` / `NFR8`):** Nominal operational availability evaluation window (`60` scheduled e2e + `/healthz` probes) |

Additional VnV parameters in `VnVPlan.tex` (`TblVnVTestParams`): `TIMER_TOLERANCE = 100 ms`, `MAX_VALIDATION_RSS_DELTA = 25 MB`, `MAX_MODULE_REJECT_TIME = 50 ms`, `MAX_MODULE_HEAP = 10 MB`, `MAX_UNIT_RELEASE_TIME = 50 ms`, `MIN_SAFETY_BRANCH_COVERAGE = 0.85` (`C3`–`C6`), `MIN_OVERALL_LINE_COVERAGE = 0.80` (`C1`, `C2`, `C7`), `MAX_UNIT_SUITE_TIME = 60 s`, `MIN_INSTALL_PASS_RATE = 0.90`, `MIN_LIKERT_MEAN = 4.0`, `MIN_FAIRNESS_SLICE_SIZE = 50` source-distinct groups (`NFT-10`), `NEAR_TEXT_SIMILARITY = 0.80` Jaccard, `NEAR_IMAGE_DISTANCE = 5` bits pHash, `METRIC_EXPORT_TOLERANCE = 1e-12`, `CALIBRATION_BINS = 10`, `RACE_ITERATIONS = 100` (`FT-14`), `BENCHMARK_TRAIN_SIZE = 2,000`, `BENCHMARK_VALIDATION_SIZE = 1,000`, `BENCHMARK_TEST_SIZE = 1,000`.

### Ephemeral Cleanup & Risk Verification Status
- The ephemeral cleanup contract establishes zero persistent storage of raw user content at all times plus `MAX_RETENTION_TIME = 1.0 s` for stopping request-owned tasks and logically releasing application-owned transient payload references after every terminal outcome (and `60 s` expiry on safe non-payload status-delivery records in `M5`). This represents bounded logical cleanup, not forensic kernel/heap zeroing, and cannot recall bytes already transmitted to a consented external provider.
- In Hazard Analysis (`PR #83`, `Issue #63`), speculative qualitative likelihood estimates were removed from the risk register in favor of concrete **Hazard Control Ownership and Open Verification Gates**. All `H1`–`H10` engineering controls remain open verification gates until automated and empirical V&V suites pass in CI/milestone runs.

### 3.2 Five-State Request Lifecycle & Evidence Source Tags
- **Request Status Enum (`\mathcal{S}_{\text{status}}`):** `pending`, `completed`, `inconclusive`, `failed`, `cancelled` (`FR6`, `INV1`, `INV2`, `SR4`).
  - *Crucial Safety Invariant (`INV2`, `SR4`):* `pending`, `inconclusive`, `failed`, or `cancelled` must **never** map to a low-risk summary or authenticity guarantee; borderline/conflicting signals or inputs failing domain gate $g(r)$ (`opinion`, `satire`, `poetry`) map to `inconclusive` (`FR4`, `SR1`).
- **Evidence Source Tags (`\mathcal{E}_{\text{src}}`):** Every displayed evidence item must be tagged in JSON as `observed_signal`, `external_reference`, or `inference`, rendered in UI as (1) `Observed Input Signal`, (2) `External Reference`, or (3) `Model Inference` (`FR7`, `SR5`, `H3`).

### 3.3 Subsystem, Component & Module Mapping (`S1`–`S4` $\leftrightarrow$ `C1`–`C7` $\leftrightarrow$ `M1`–`M10`)
- **SRS Black-Box Subsystems (`S1`–`S4`):**
  - `S1`: Extension Selection, Consent & Display Boundary
  - `S2`: Validation, Isolation & Lifecycle Boundary
  - `S3`: Signal Analysis & Uncertainty Boundary
  - `S4`: Offline Benchmark Evaluation Boundary
- **Hazard Analysis Internal Components (`C1`–`C7`):**
  - `C1`: Browser Extension Capture & Permission Controller (`H4`)
  - `C2`: Result Display & Uncertainty UI (`H1`, `H2`, `H5`, `H8`)
  - `C3`: Input Validation & Sanitization Gate (`H2`, `H7`)
  - `C4`: Request Isolation & State Coordinator (`H6`, `H8`, `H9`)
  - `C5`: Ephemeral Privacy & Buffer Lifecycle Handler (`H4`)
  - `C6`: Signal Detection & Grounded Evidence Engine (`H1`, `H2`, `H3`, `H6`)
  - `C7`: Offline Benchmark & Fairness Evaluation Workflow (`H10`)
- **Design Module Decomposition (`MG.tex` & `MIS.tex` `M1`–`M10`):**
  - **Hardware-Hiding (`M1`):** `M1` *Browser and host bridge* (`S1`; wraps browser/OS services)
  - **Behaviour-Hiding (`M2`–`M6`):**
    - `M2`: *Selection and consent* (`S1`, `C1`)
    - `M3`: *Result card* (`S1`, `C2`)
    - `M4`: *Input validation* (`S2`, `C3` — pure library, omits `initialize`)
    - `M5`: *Request coordinator* (`S2`, `C4`)
    - `M6`: *Temporary content* (`S2`, `C5` — `WorkerLease` `hold`/`borrow`/`release`)
  - **Software-Decision-Hiding (`M7`–`M10`):**
    - `M7`: *Text signals* (`S3`, `C6`)
    - `M8`: *Image signals and provenance* (`S3`, `C6`)
    - `M9`: *Assessment policy* (`S3`, `C6` — calibration margin, conflict, and domain gate $g(r)$)
    - `M10`: *Offline evaluation* (`S4`, `C7` — deterministic metrics recomputation and slice auditing)

### 3.4 Complete Requirement & Hazard ID Index (With Key Specification/Test Refinements)
- **Goals (`G1`–`G6`):** `G1` Evidence-First Assessment; `G2` Honest Uncertainty & Safe Abstention; `G3` Defensible Low-False-Accusation Detection Quality; `G4` Non-Expert Understandability; `G5` Seamless In-Page Responsiveness; `G6` Privacy-First Ephemeral Handling.
- **Mandated Constraints (`C1`–`C6` in SRS):** `C1` Browser MV3 Sandbox; `C2` Zero End-User GPU / CLI (`8 GB RAM` consumer laptop); `C3` Capstone Calendar (Apr 2027); `C4` Zero-Cost Open Source; `C5` No Private Training Data; `C6` TLS/HTTPS Transport.
- **Assumptions (`A1`–`A5`):** `A1` Sensitive / Hostile Selections; `A2` Fallible Detectors & APIs; `A3` Uncalibrated Raw Scores; `A4` Task-Bounded Ground Truth; `A5` Standard Host Browser Integrity.
- **Functional Requirements (`FR1`–`FR14`):** `FR1` Scoped Selection; `FR2` Pre-Analysis Validation/Sanitization; `FR3` Evidence & Flag Warning (**`FR3`(d) / Issue `#65`:** whenever signals flag synthetic/manipulated content, display a **plain-language warning stating that authentic human material can still be falsely flagged**); `FR4` Uncertainty & Safe Abstention (**Issue `#58`:** fail-closed **domain-applicability gate $g(r)$** returning `true` only for calibrated supported domains and **`false` for `opinion`, `satire`, `poetry`**, forcing `inconclusive` while keeping task exclusions distinct); `FR5` Verification Guidance; `FR6` 5-State Lifecycle; `FR7` Source Attribution & Prompt-Injection Immunity; `FR8` Prior Informed Consent for External Transfer; `FR9` Ephemeral Processing & Zero Retention; `FR10` Unique Request Binding & Session Isolation; `FR11` In-Flight Cancellation; `FR12` Reproducible Benchmark Logging; `FR13` Image `EXIF`/`C2PA` Inspection; `FR14` Subgroup (`ESL`/Compressed-Image) Slice Reporting.
- **Non-Functional Requirements (`NFR1`–`NFR10` & `NFR.E.1`–`NFR.E.5`):** `NFR1` Accuracy & FPR Control; `NFR2` Result Understandability; `NFR3` Response Latency (warm SLA separate from cold-start diagnostics); `NFR4` Zero Persistent Retention; `NFR5` Cross-OS Desktop Chromium Portability (Chrome/Edge/Playwright Chromium; Brave deferred); `NFR6` Installability & Dev Setup; `NFR7` Evaluation Reproducibility ($\pm 0.005$); `NFR8` Availability, Fault Recovery & Burst Load (**Issues `#59`, `#64`:** $\ge \texttt{MIN\_SERVICE\_UPTIME}$ over `AVAILABILITY_WINDOW` = `60 min` polling `/healthz` + valid e2e probes every `HEALTH_PROBE_INTERVAL` = `60 s`, 50-fault recovery, and **clean concurrent burst load capping above `MAX_CONCURRENT_REQS` (`10`)** via retryable `failed` refusal without breaking admitted `UUIDv4` isolation); `NFR9` Detector Replaceability; `NFR10` Cultural & Compression Fairness Auditing.
- **Safety & Security Requirements (`SR1`–`SR9` — identical verbatim in SRS & HA, enforced by `verify_specification.py --with-hazard`):** `SR1` Uncertainty Must Stay Visible; `SR2` No Accusation from a Detector Score; `SR3` No Safety or Authenticity Guarantee; `SR4` Safe Handling of Failed and Partial Analyses; `SR5` Grounded Explanations and Prompt-Injection Immunity; `SR6` Untrusted Webpage Content Sandboxing; `SR7` Strict Request-to-Result Association; `SR8` Controlled Content Access and Ephemeral Cleanup; `SR9` Cross-User and Cross-Session Isolation.
- **FMEA Hazards (`H1`–`H10`):** `H1` False-Positive Flag on Legitimate/ESL Content; `H2` False-Negative Reassurance; `H3` Ungrounded Claim / Prompt Injection; `H4` Unscoped Capture / Retention Leak; `H5` Over-Trust in Raw Score; `H6` Silent Timeout / Failure Shown Safe; `H7` Malicious Payload & Valid-Traffic Burst Saturation; `H8` Stale Async Overwrite; `H9` Cross-Session Leakage; `H10` Leaky / Irreproducible / Biased Evaluation.

### 3.5 Formal Invariants, Use Cases, Input Partition & Change Identifiers (`SRS.tex`)
Downstream documents and tests must reference these exact SRS identifiers:
- **Formal System Invariants (`INV1`–`INV4`, SRS Section E.5 & S.9.1):**
  - `INV1` (*Status Exclusivity*): Every admitted request $r \in \mathcal{R}$ holds exactly one state $\text{status}(r) \in \mathcal{S}_{\text{status}} = \{\texttt{pending}, \texttt{completed}, \texttt{inconclusive}, \texttt{failed}, \texttt{cancelled}\}$; invalid selections rejected at pre-admission (`FR2`) never enter $\mathcal{R}$.
  - `INV2` (*No Silent Reassurance*): $\text{status}(r) \in \{\texttt{pending}, \texttt{inconclusive}, \texttt{failed}, \texttt{cancelled}\} \implies$ never display a low-risk signal summary (`FR4`, `SR4`).
  - `INV3` (*Strict Request-to-Result Binding*): $\forall r \neq q,\; \text{result}(r)$ is never bound to or rendered as the assessment for $q$ (`FR10`, `SR7`, `SR9`). *(Aligned across `SRS.tex` PR `#84` and `MG.tex`/`MIS.tex` PR `#81`; evidence source tagging $\mathcal{E}_{\text{src}}$ is specified by `FR7`, `SR5`, `H3`, and SRS S.9.1 Well-Formed Result Invariant.)*
  - `INV4` (*Zero Persistence & Bounded Cleanup*): Raw content never enters persistent storage/logs; request work halts and application-owned transient references release within `MAX_RETENTION_TIME` after terminal decision (`FR9`, `NFR4`, `SR8`).
- **Product Use Cases (`UC1`–`UC4`, SRS Section S.7):**
  - `UC1`: Analyse a Supported Webpage Item (`S1`, `S2`, `S3`)
  - `UC2`: Handle Weak, Conflicting, or Out-of-Domain Signals (`S1`, `S2`, `S3`)
  - `UC3`: Reject Invalid Input or Handle Service/Timeout Fault (`S1`, `S2`)
  - `UC4`: Cancel Request or Decline External Consent (`S1`, `S2`)
  - *(Offline benchmark evaluation in `S4` is governed via `FR12`, `FR14`, `NFR1`, `NFR7`, `NFR10`, and `FT-15`.)*
- **Input Equivalence Classes & Boundary Partition (`Class 1`–`Class 9`, SRS `TblDomainCoverage` / VnV `TblClassCoverage`):**
  - `Class 1`: Valid text, strong signals ($150 \le L \le 10{,}000$, outside abstention margin) $\to$ `completed` (`UC1`)
  - `Class 2`: Valid image, strong signals (`PNG`/`JPEG`/`WebP`, $\le 10.0\text{ MB}$, $64 \times 64$..$4096 \times 4096$) $\to$ `completed` (`UC1`)
  - `Class 3`: Weak, borderline, or conflicting signals $\to$ `inconclusive` (`FR4`, `UC2`)
  - `Class 4`: Opinion, satire, or poetry ($g(r) = \texttt{false}$) $\to$ `inconclusive` fail-closed (`FR4`, `SR1`, `UC2`)
  - `Class 5`: Empty or out-of-bounds input ($L = 0$, $L < 150$, $L > 10{,}000$, $D < 64$, $D > 4096$, size $> 10.0\text{ MB}$) $\to$ Synchronous pre-admission rejection $\le \texttt{MAX\_UI\_RENDER\_LATENCY}$ (`FR2`, `UC3`)
  - `Class 6`: Unsupported format or active script (`GIF`, `MP4`, `SVG`/HTML/JS, corrupted header) $\to$ Pre-admission rejection, zero script execution (`FR2`, `SR6`, `H7`)
  - `Class 7`: Prompt-injected input $\to$ Treated strictly as inert data; locator-backed grounding enforced (`FR7`, `SR5`, `H3`)
  - `Class 8`: Consent declined or user cancelled during `pending` $\to$ `cancelled`, $0\text{ B}$ outbound on decline, cleanup $\le \texttt{MAX\_RETENTION\_TIME}$ (`FR8`, `FR11`, `UC4`)
  - `Class 9`: Timeout ($\ge \texttt{MAX\_RESPONSE\_TIME}$) or dependency fault (crash / HTTP 5xx) $\to$ `failed`, never low-risk (`FR6`, `SR4`, `H6`, `UC3`)
- **Likely Changes (`LC1`–`LC6`) & Unlikely Changes (`ULC1`–`ULC4`, SRS Section P.3 & MG `AC1`–`AC13`):**
  - `LC1`: Upgrading text/image model weights (`AC1` $\to$ `M7`, `AC2` $\to$ `M8`)
  - `LC2`: Adjusting retained modalities/thresholds (`AC3` $\to$ `M9`)
  - `LC3`: Extending provenance/signal fields (`AC4` $\to$ `M7`, `AC5` $\to$ `M8`)
  - `LC4`: Tuning latency/bounds constants in SRS Table 6 (`AC6` $\to$ `M4`, `AC7` $\to$ `M5`)
  - `LC5`: Shifting local vs. team-managed remote service deployment (`AC8` $\to$ `M1`)
  - `LC6`: Refining result card wording and accessibility layout after `NFR2` (`AC9` $\to$ `M3`)
  - Additional MG Anticipated Changes: `AC10` (`M1` browser API), `AC11` (`M10` benchmark source/slice), `AC12` (`M2` consent disclosures), `AC13` (`M6` transient cleanup machinery).
  - `ULC1`: Scoped, user-triggered decision-support boundary; `ULC2`: Five-state lifecycle separating `inconclusive` and `failed`; `ULC3`: Zero default persistence & bounded cleanup (`INV4`); `ULC4`: Source-attributed, non-accusatory output framing (`SR2`, `SR5`).

---

## 4. Course Grading, TA Conventions & Document Readability / Anti-Bloat Standards

Based on TA Rebecca Di Filippo's rubric reviews (`#17`–`#21`, `#53`–`#67`, `#72`–`#76`), Peer Reviews (`#2`, `#3`, `#13`–`#16`, `#29`–`#34`, `#42`–`#52`), and `/Users/raymondtao/GitHub/RLCatan` exemplary capstone benchmarks, enforce every rule below:

### 4.1 Readability, Page/Word Scales & Anti-Bloat Standards
Target concise, scannable, human-reviewable PDFs calibrated against `/Users/raymondtao/GitHub/RLCatan` benchmarks:

| Document | `RLCatan` Benchmark | Verity Target / Refactored Baseline |
| :--- | :--- | :--- |
| `ProblemStatement.pdf` | 7 pp / 2,307 words | 8 pp / 2,307 words (`main`) |
| `DevelopmentPlan.pdf` | 13 pp / 3,204 words | 13 pp / 5,338 words (`main`) |
| `SRS.pdf` | 58 pp / 13,941 words | ~40–55 pp / ~13,000 words (`PR #84`: 40 pp / 13,192 words, down from 76 pp / 22,967 words) |
| `HazardAnalysis.pdf` | 19 pp / 4,020 words | ~19–22 pp / ~4,000–6,700 words (`PR #83`: 20 pp / 6,650 words, down from 35 pp / 10,932 words) |
| `VnVPlan.pdf` | 37 pp / 8,090 words | **32–40 pp / ~8,000–10,000 words** (down from 68 pp / 21,902 words on `main`) |
| `MG.pdf` | 19 pp / 3,967 words | ~17–19 pp / ~4,000 words (`PR #81`: 17 pp / 4,065 words) |
| `MIS.pdf` | 40 pp / 10,095 words | ~35–40 pp / ~9,000–10,100 words (`PR #81`: 35 pp / 9,034 words) |
| `VnVReport.pdf` | 34 pp / 6,691 words | ~30–36 pp / ~6,500–8,000 words (Week 22 target) |
| `ReflectAndTrace.pdf` | 17 pp / 5,725 words | ~15–18 pp / ~5,000–6,000 words (Week 26 target) |
| `*_Productivity_Rep.pdf` | 4 pp / ~466–795 words | 4 pp / ~500–1,300 words (`PR #80`: 4 pp / 1,295 words) |
| `CD-Fall` / `CD-Winter` | 17 pp / 4,675 words (`Usability`) | `MLReport`: 5 pp / 2,711 words (`PR #82`); `UsabilityReport`: ~15–18 pp |

### 4.2 Separation, Reflection, Linking & Table-Numbering Rules
1. **Abstraction Separation (`SRS` & `VnVPlan`):**
   - Put requirement statements first and keep black-box observable behavior in `SRS` separate from internal architecture (`UUIDv4`, JSON keys, FastAPI/Celery details belong in `MG`/`MIS`, not `FR10`/`NFR9` — `Issue #54`).
   - In `VnVPlan`, keep **`Control`** (manual/automatic) and **`Type`** (functional vs. non-functional, dynamic vs. static) crisp and separate from low-level implementation/toolchain details (`How Test Will Be Performed` holds `pytest`, `Playwright`, `tcpdump`, etc. — `Issue #72`).
2. **Concise Authentic Reflections (No `Team Synthesis` or `LO_*` Bloat):**
   - Always write **4 concise first-person individual subsections** (`Calvin Salsali`, `Raymond Tao`, `Jaden Moore`, `Richard Han`) grounded in real design/testing trade-offs, mistakes, and resolutions (`Issues #67`, `#76`).
   - **Spell out full McMaster course names alongside course codes** (see Section 1 roster table).
   - **Drop bloated `Team Synthesis` prose** and **never place `LO_*` CEAB rubric tags** (such as `LO_Impact`, `LO_Reflect`, `LO_SpecMath`) inside rendered prose, headings, or table captions.
3. **Companion Links Must Target `pdfs/.../*.pdf`:**
   - All cross-document hyperlinks must point to `pdfs/<Subfolder>/<Doc>.pdf` (or GitHub blob URLs under `pdfs/`), **never** `docs/<Subfolder>/<Doc>.tex` (`Issue #47`).
4. **Renumbering-Resilient Cross-Document Table References:**
   - Never hardcode brittle bare table numbers (e.g., `"HA Table 4"`) across documents when an upstream document adds or reorders tables. Reference named sections, LaTeX `\label`s, or descriptive table titles (e.g., *"HA FMEA Worksheet"*, *"HA Risk Register"*, *"SRS Domain Coverage table"*).
   - **Recorded Table Number Shifts (`PR #83` HA & `PR #84` SRS):**
     - In `HazardAnalysis.pdf` (`PR #83`), inserting **Table 3: Standards Directly Informing Hazard Controls** shifted `Assumptions` (`3 -> 4`), **FMEA Worksheet (`4 -> 5`)**, **Risk Register / Control Ownership (`5 -> 6`)**, **Traceability Matrix (`6 -> 7`)**, and **Roadmap (`7 -> 8`)**.
     - In `SRS.pdf` (`PR #84`), `TblSymbolicConstants` remains **Table 6**, `TblStakeholders` **Table 7**, `TblSubsystemMapping` **Table 13**, `TblFuncReqs` **Table 14**, `TblNFRs` **Table 15**, `TblSafetyReqs` **Table 16**, **`TblDomainCoverage` Table 17**, **`TblPOCPlan` Table 18**, **`TblPhaseInPlan` Table 19**, **`TblTraceabilityMatrix` Table 20**, **`TblFeedbackTrace` Table 21**.
5. **Generative AI Use Disclosures (Confirmed Tools & Completed Audits):**
   - Every new or refactored deliverable must cite the four confirmed team tools with exact names/versions:
     - **`OpenAI Codex (GPT-6.1)`**
     - **`Anthropic Claude Sonnet 5.5`**
     - **`Google Gemini Flash 3.8`**
     - **`Google Gemini 4 Hydrogen`**
   - Map each named team member to the sections/scripts assisted and record **completed human verification checks** actually run (e.g., `verify_specification.py --with-hazard`, `verify_design.py`, `generate.py`, independent metric recomputation, PDF visual inspection). Never leave unverified future-tense promises, truncated/missing minor versions, or unconfirmed model names.
6. **Course Privacy, Revision History, Goals, Placeholders & `Writing-Checklist.tex`:**
   - **Team Identification vs. PII (`capstone/AdminDetails/Wk04-a.tex`):** Include Team number and team name (`Team 23 — Dream Team`) on every document, but **never** print MacIDs (e.g., in author blocks or team-role tables), student numbers, or private physical meeting locations in deliverable `.tex`/`.pdf` files.
   - Revision History tables must name specific individual developers (never `"Team 23"` or `"All"`) and concrete technical/scope changes.
   - High-level Goals (`G1`–`G6`) read as non-expert product value propositions (*Problem $\to$ What it causes $\to$ What Verity addresses*), keeping tolerances in `TblSymbolicConstants` and requirements.
   - Zero `"TBD"`, `"Not set"`, `??`, backticks in LaTeX prose, or visible `\wss{...}` comments in PDFs.
   - Always include 1–2 sentences of introductory bridge text between headings, never have a single subsection inside a section, define acronyms at first use + Acronym Table, and provide legends in every diagram.

---

## 5. Official SFWRENG 4G06 Schedule, Milestones & Peer Assignments

Derived from `/Users/raymondtao/GitHub/capstone` (`Capstone_Outline.tex`, `AdminDetails/Wk06-a.tex`, `Wk08-a.tex`, `Schedule.xlsx`, `Teams/POCDemoSchedule.csv`, `Teams/InformalPresSchedules/*_Rebecca.md`, `Teams/TeamRevAssig-*.md`, `Teams/TeamComposition.csv`):

### 5.1 Course Deliverable Schedule, Room Slots & Weights
Always name GitHub Milestones and schedule rows using these official course weeks and confirmed 2026–2027 dates:

| Course Week | Date / Window | Official Deliverable / Event & Location | Weight | Authoritative Source Path(s) in `Verity` |
| :--- | :--- | :--- | :--- | :--- |
| **Week 03** | Sept 21, 2026 | Team Formed, Project Selected *(Informal PS: Sept 23, 4:10–4:30 pm, ITB/112)* | `0%` | Course registration (`Teams/TeamInfo/TeamSummary_hanr23.json`) |
| **Week 04** | Sept 28, 2026 | Problem Statement, POC Plan, Development Plan, Team Charter Rev 0 | `2%` | `docs/ProblemStatementAndGoals/ProblemStatement.tex`, `docs/DevelopmentPlan/DevelopmentPlan.tex` |
| **Week 06** | Oct 19, 2026 | **Req. Doc. & Hazard Analysis Rev 0** *(Informal SRS: Oct 7, 3:10–3:30 pm, ITB/112)* | `7%` | `docs/SRS/SRS.tex`, `docs/HazardAnalysis/HazardAnalysis.tex`, `docs/projMngmnt/MeetingNotes.tex` |
| **Week 08** | Nov 2, 2026 | **V&V Plan Rev 0** *(Informal VnV/PoC: Oct 28, 3:30–3:50 pm, ITB/112)* | `5%` | `docs/VnVPlan/VnVPlan.tex` |
| **Week 10** | Nov 16 / Nov 19, 2026 | **Design Doc Rev -1 & CD-Fall Rev 0** (Nov 16; *Informal: Nov 11, 3:50–4:10 pm, ITB/112*); **POC Team Productivity Report & Avenue Survey** (Nov 19) | `3%` | `docs/Design/SoftArchitecture/MG.tex`, `docs/Design/SoftDetailedDes/MIS.tex`, `docs/CDs/MLReport/main.tex`, `docs/projMngmnt/POC_Productivity_Rep.tex` |
| **Weeks 11–12** | **Dec 2, 2026 (5:45–6:00 pm, ITB/201)** | **Proof of Concept Demonstration + Interviews** with TA Rebecca Di Filippo (15-min slot, max 5-min live software demo, **no slides**) | `5%` | Live scripts (`docs/CDs/MLReport/experiment/`, `test/fixtures/generate.py`, `test/documentation/`) |
| **Week 13** | **Dec 9, 2026 (4:10–4:30 pm, ITB/112)** | **Term 1 Code Review Interviews** with TA Rebecca Di Filippo (`4CodeReview-1_Rebecca.md`, `Wk08-a.tex`) | — | Code walkthroughs & POC artifacts |
| **Weeks 15–16** | **Jan 12** (Informal, 3:10–3:30 pm, ITB/112) & **Jan 18, 2027** | **Design Document Revision 0** (`Jan 18`, `Wk08-a.tex`; implement Team 06's peer MIS module due **Jan 21, 2027**) | `4%` | `docs/Design/SoftArchitecture/MG.tex`, `docs/Design/SoftDetailedDes/MIS.tex`, `src/` |
| **Weeks 18–19** | Feb 1–12, 2027 | **Revision 0 Demonstration + Interviews** *(+ Rev 0 Team Productivity Report)* | `10%` | Integrated MV3 extension + FastAPI backend (`src/` & `test/`) + `docs/projMngmnt/Rev0_Productivity_Rep.tex` |
| **Weeks 20–22** | Feb 23 / Mar 2 / ~Mar 8–9, 2027 | **Term 2 Code Review** (Feb 23, 3:30–3:50 pm, ITB/112); **Informal VnV Report** (Mar 2, 3:50–4:10 pm, ITB/112); **V&V Report Rev 0 & CD-Winter Rev 0** (Wk 22) | `4%` | `docs/VnVReport/VnVReport.tex`, `docs/CDs/UsabilityTesting/UsabilityReport.tex` |
| **Week 24** | Mar 22–28, 2027 | **Final Demonstration (Revision 1)** | `20%` | Frozen Revision 1 product release (`src/` & `test/`) |
| **Week 26** | Apr 5–7, 2027 | **EXPO Demonstration (`10%`) & Final Documentation Rev 1 (`30%`)** | `40%` | All `docs/` at Rev 1 + `UserGuide.tex` + `ReflectAndTrace.tex` + `Final_Productivity_Rep.tex` |

*Informal Presentation Schedule Note:* Team 23 is supervised by **Rebecca Di Filippo** and appears exclusively in `Teams/InformalPresSchedules/*_Rebecca.md` (`0PS` through `7VnvReport`, all in **ITB 112**). Schedule files named `*_Melvin.md` (such as `5DesDoc_Melvin.md`) belong to TA Melvin Mokhtari for Teams 14 and 21.

### 5.2 Peer Review Assignments (`TeamRevAssig-*`, `Wk06-a.tex` & `TeamComposition.csv`)
- **Primary Incoming Reviewer of Team 23 — Team 16 ("DevSquared" / *Game 'N Grow* — `https://github.com/meena-alomran/game-n-grow/`):**
  - **Members:** Omar Ghoneim (`@Omar-Ghon`), Meena Al Omran (`@meena-alomran`), Maya Azar (`@Azarm1`), Amirah Abdel-Rahman (`@amirah-ar`), Marko Popovic (`@MarkoPopo`); Assigned TA: Rashad Bhuiyan (`@RashadBhuiyan`).
  - **Scope:** Primary reviewer of Team 23 across **SRS + Hazard Analysis** (following the Week 06 `Wk06-a.tex` swap: *"Teams 16 and 23 have changed who they are reviewing"*), **Design Document Rev -1**, **Design Document Rev 0**, and **V&V Report** (plus additional VnV Plan issues `#45`, `#47`, `#49`–`#52`).
- **Rotating Incoming Reviewer (Problem Statement/DevPlan & V&V Plan) — Team 12 ("SnowSight AI" — `https://github.com/CodeMaster177/snowsight-ai`):**
  - **Members:** Krish Dogra (`@CodeMaster177`), Edward Jung (`@junged856`), Saad Pahore (`@SaadPahore`), Jeffery Liu (`@liujeffery`); Assigned TA: Rashad Bhuiyan (`@RashadBhuiyan`).
  - **Scope:** Reviewed Team 23 on **Problem Statement & DevPlan** (`#2`, `#3`, `#13`–`#16`) and **V&V Plan** per `TeamRevAssig-03-VnV.md` (`#42`–`#44`, `#46`, `#48`).
- **Outgoing Peer Review Target of Team 23 — Team 06 ("Blockchainerz" / *DAIIM* — `https://github.com/robertLam04/daiim`):**
  - **Project:** *DAIIM — A Decentralized Marketplace for Reliable and Verifiable AI Inference*
  - **Members:** Robert Lam (`@robertLam04`), Nathan Hum (`@Nathan-Hum`), Aidan Lao (`@aidanlao`), Keira Laskoski (`@keiralaskoski`); Assigned TA: Rashad Bhuiyan (`@RashadBhuiyan`).
  - **Standard Peer Reviews (ProbState/DevPlan, SRS, Hazard Analysis, VnV Plan, Design Rev -1, VnV Report):** Open **more than 5 high-quality, rubric-grounded GitHub Issues** on `https://github.com/robertLam04/daiim` using `peer_review` and tagging `@rebeccadifilippo` and `@RashadBhuiyan`. *(Team 06 is Verity's outgoing review target and does not review Team 23; Team 06's assigned outgoing review target in `TeamRevAssig-00-Primary.md` is Team 07.)*
  - **Design Document Rev 0 Peer Implementation Rule:** Instead of $>5$ issues, Team 23 implements one module from Team 06's MIS via a PR on Team 06's repo, opens 1 summary issue, and reflects in MIS Reflection Q7 (linking the PR).
- **Custom Documents & Pending Course-Repo MR (`capstone/Teams/TeamComposition.csv` L110):**
  - `ExceptionsGranted.md` records Team 23's approved Fall Custom Document as the **Machine Learning Model Report** (`pdfs/CDs/MLReport/main.pdf`), confirmed November 16, 2026. Winter Custom Document remains the **Usability Report**.
  - **Pending External MR:** `/Users/raymondtao/GitHub/capstone/Teams/TeamComposition.csv` line 110 still lists `User/Stakeholder/Client interview report` for Team 23's Fall CD instead of `Machine Learning (ML) model report`; a manual external Merge Request on the McMaster GitLab course repo is pending to update line 110.

### 5.3 CEAB Graduate Attribute Learning Outcomes (Authoring Guidance Only)
Use `Attributes_Indicators_LOs.tex` internally when authoring deliverables to ensure full CEAB coverage, **without** inserting `LO_*` tags into rendered document prose or captions:
- `LO_SpecMath` (SRS S.9.1 Parnas table & MIS formal spec); `LO_EngFund` (Hazard Analysis FMEA); `LO_Assumptions` (SRS & HA boundaries); `LO_ContextAndConstraints` (SRS G.1, E.3, E.7); `LO_Standards` (SRS & HA standards); `LO_Impact` (societal/ESL fairness & uncertainty communication); `LO_Reflect` & `LO_ExtKnowledge` (SRS/VnV reflections); `LO_Plan` & `LO_Tests` (VnV Plan); `LO_ProbSolutions`, `LO_Explores`, `LO_ComprehendInstruct` (MG/MIS & peer module PR); `LO_Synthesize` (VnV Report); `LO_PrototypeIterate`, `LO_Justifies`, `LO_Economic`, `LO_Equity`, `LO_Manages` (ReflectAndTrace).

---

## 6. Git History, PR Stack & Issue Registry (`#1`–`#85`)

### 6.1 Key Merged & Active PRs
- **Weeks 04–06 (`#1`, `#22`–`#25`, merged):** Problem Statement & Dev Plan rubric fixes (`#22`), Oct 7 TA Meeting Notes (`#23`), Meyer PEGS SRS Rev 0 (`#24`), Hazard Analysis Rev 0 (`#25`), initial VnV Plan, Design Rev -1, and Fall ML Report Rev 0.
- **November POC & TA-Feedback Refactor Stack (Open PRs `#80`–`#84` + PR 6):**
  - **PR `#80` (`docs/poc-productivity-report`):** Complete `POC_Productivity_Rep.tex` (4 pp / 1,295 words) + `TeamComposition.csv` L110 note (Issue `#79`).
  - **PR `#81` (`fix/design-rev-1-cleanup`):** Remove stray `Review-69.md`/`.pdf`, update `MG.tex` (17 pp / 4,065 words) & `MIS.tex` (35 pp / 9,034 words) with Acronyms, `INV3` alignment, schedule, AI disclosures & individual reflections (Issue `#77`).
  - **PR `#82` (`fix/ml-report-rev0`):** `MLReport/main.tex` (5 pp / 2,711 words) verification audit, POC bridging, TikZ source chart, and Tiny-GenImage table (Issue `#78`).
  - **PR `#83` (`docs/ha-refactor-ta-feedback`):** Refactor `HazardAnalysis.tex` to 20 pp / 6,650 words, remove qualitative likelihood matrix, add `H1` false-positive notice & `H7` burst saturation, update AI disclosure & reflections (Issues `#62`–`#65`).
  - **PR `#84` (`docs/srs-refactor-ta-feedback`):** Refactor `SRS.tex` to 40 pp / 13,192 words, clean black-box separation, `FR3`(d) warning, `FR4` $g(r)$ gate, `NFR8` e2e availability + burst cap, `INV3` alignment, AI disclosure & reflections (Issues `#53`–`#61`, `#65`–`#67`).
  - **PR 6 (`docs/vnv-refactor-ta-feedback`):** Refactor `VnVPlan.tex` to target 32–40 pp, add `TblSRSVerifChecklist`, 4-role 45-min walkthrough, `FT-5` subtle rubric + `evidence/subtle_accusations.json`, `FT-6` $g(r)$ + 20 `FX-ABST` genre texts, `NFT-1`/`3`/`5`/`7`/`8`/`10` updates, and `test/fixtures/generate.py` `--text-and-png-only` (Issues `#72`–`#76`, `#42`–`#52`).

### 6.2 Canonical GitHub Issue Registry (`#1`–`#79`)
| Issue(s) | Category | Summary & Resolution / Target Deliverable |
| :--- | :--- | :--- |
| `#2`, `#3`, `#13`–`#16` | Incoming Peer Review (Team 12, Wk 04) | `#2` Pre-POC FP mitigations; `#3` 3-Step Charter check-in; `#13` `+0.10` Macro-$F_1$ delta; `#14` Quantified NFRs; `#15` Exclude opinion/satire; `#16` Expanded personas. Closed in `#22` & `#24`. |
| `#4`–`#12`, `#37`–`#38` | POC Backlog & Team Meetings | Initial POC setup/backlog (`#4`–`#12`) and Sept 28 / Oct 18 team meeting records (`#37`–`#38`). Closed. |
| `#17`–`#21` | TA Meeting & Wk 04 Rubric Feedback | Oct 7 TA meeting (`#17`), Goals/POC/DevPlan/Reflections (`#18`–`#21`). Closed in `#22` & `#23`. |
| `#29`–`#34` | Incoming Peer Review (Team 16, Wk 06) | HA table refs (`#29`), `INV1` states (`#30`), low-risk definition (`#31`), constants convention (`#32`), stakeholders (`#33`), undefined acronyms (`#34`). Closed. |
| `#42`–`#52` | Incoming Peer Review (Teams 12 & 16, Wk 08 VnV) | Team 12 (`#42` availability, `#43` fairness pass/fail, `#44` cold vs. warm latency, `#46` cross-member repro contingency, `#48` symbol links); Team 16 (`#45` reflections, `#47` doc links, `#49` refs, `#50` NFR tests, `#51` system test types, `#52` usability survey). Addressed in PR 6. |
| `#53`–`#67` | TA Rubric Feedback (SRS & HA Refactor) | SRS scan/abstraction/status/constants/boundary/opinion-satire/availability/targets/stakeholders/verification/reflections (`#53`–`#61`, `#66`–`#67`); HA readability/likelihoods/bursts/false-flag (`#62`–`#65`). Addressed in PRs `#83`–`#84`. |
| `#72`–`#79` | TA Feedback & November POC Fixes | VnV readability/`Control`+`Type` (`#72`), SRS checklist & walkthrough (`#73`), `FT-5`/`FT-6` tone & $g(r)$ (`#74`), NFR inputs/`NFT-5`/CD-Fall (`#75`), reflections/GenAI (`#76`), Design Rev -1 (`#77`), ML Report (`#78`), POC Productivity Report (`#79`). Addressed in PRs `#80`–`#82` & PR 6. |

---

## 7. Deliverable-Specific Playbooks & Test Contracts (Weeks 08–26)

### 7.1 Verification & Validation Plan (`docs/VnVPlan/VnVPlan.tex` $\to$ `pdfs/VnVPlan/VnVPlan.pdf`)
- **Static Verification & Walkthroughs (Section 3):**
  - Includes the 8-item **SRS Verification Checklist** (`TblSRSVerifChecklist`), links/explains `verify_specification.py --with-hazard` and `verify_design.py`, and defines the **45-minute 4-role structured code walkthrough protocol** (**Moderator**: Richard Han, **Author**: component owner, **Reader**: independent verifier, **Scribe**: Jaden Moore; diffs circulated 24 h ahead) tracing `C1` $\to$ `C3` $\to$ `C4` $\to$ `C6` $\to$ `C5` $\to$ `C2`.
- **Mandatory System Test Contracts (Section 4):**
  - Keep `Control` and `Type` clean and distinct from toolchain procedures in `How Test Will Be Performed`.
  - **`FT-5` (Evidence, FP Warning & Tone):** Automated schema/`signals[]`/false-positive banner/`FX-LEX/accusatory.txt` checks + **independent 2-reviewer subtle-tone rubric** (`0–2` blame/intent scale scored blindly by Calvin Salsali & Richard Han) paired with 5 non-keyword controls in `FX-EVID` (`evidence/subtle_accusations.json`).
  - **`FT-6` (Abstention & Genre Gate):** 35 `FX-ABST` / `FX-PROV` items (10 borderline, 5 C2PA-valid conflict photos with $\hat{p}=0.88$, and 20 out-of-domain 200–1,500 char texts across `opinion-1..7`, `satire-1..7`, `poetry-1..6`) verifying fail-closed domain gate $g(r) = \texttt{false} \implies \texttt{inconclusive}$ (`INV2`).
  - **`NFT-1` (Detection Quality):** Evaluated on locked Rev 0 splits (`BENCHMARK_TEST_SIZE = 1,000` balanced items/modality) anchored to `docs/CDs/MLReport/experiment/`.
  - **`NFT-3` (Response Latency):** Strictly separates **5 fresh Cold-Start launches** (diagnostic log) from **100 Warm Steady-State requests/modality** on `FX-PERF` (`LATENCY_PERCENTILE` $\ge 90.0\%$ within `MAX_RESPONSE_TIME = 10.0 s`, counting `failed` in denominator).
  - **`NFT-5` (Desktop Chromium Portability):** Automated Playwright Chromium CI matrix + manual Chrome & Edge smoke checklist across macOS 13+, Windows 10/11, Ubuntu 22.04+ (Chromium $\ge 120$); **Brave explicitly deferred out-of-scope**.
  - **`NFT-7` (Reproducibility):** Role-based **Benchmark Author** (tags commit with manifests, SHA-256 hashes, config, seed, OS/CPU/package metadata) + **Independent Reproducer** (replays on separate host verifying $|\Delta F_1|, |\Delta \text{FPR}| \le \texttt{MAX\_REPRO\_DELTA} = 0.005$).
  - **`NFT-8` (Availability, Recovery & Burst Load):** `AVAILABILITY_WINDOW = 60 min` polling `GET /healthz` + alternating synthetic valid e2e probes every `HEALTH_PROBE_INTERVAL = 60 s` (`60` e2e probes, $\ge 99.0\%$), separate 50-fault recovery sequence, and **concurrent bursts of 15–20 valid requests ($> \texttt{MAX\_CONCURRENT\_REQS} = 10$)** refusing excess cleanly with retry-safe `failed` banners (`SR4`).
  - **`NFT-10` (Fairness Audit):** Minimum `MIN_FAIRNESS_SLICE_SIZE = 50` source-distinct items/slice (native-English, Liang ESL, academic prose; camera vs. JPEG-70/50) with Wilson CIs and explicit rules: (1) **Block/Fail** if $< 50$ items or $A_0 = 0$; (2) **Pass-with-Disclosure** if overall `NFR1` passes and every slice with $\text{FPR} > \texttt{MAX\_FPR}$ renders a UI `limitations[]` banner; (3) **Fail Overall** if aggregate `NFR1` fails or an elevated-FPR slice lacks UI disclosure or an approved scope decision.
  - **Usability Survey (Section 6.2):** Includes Comprehension Item `C1(d)` specifically testing plain-language interpretation of the `H1` false-positive warning and `Q2` testing in-page workflow ease (`G5`).

### 7.2 Productivity Reports (`docs/projMngmnt/*_Productivity_Rep.tex`)
- **Files:** `POC_Productivity_Rep.tex` (Nov 2026, PR `#80`), `Rev0_Productivity_Rep.tex` (Feb 2027), `Final_Productivity_Rep.tex` (Apr 2027).
- **Rules:** Keep standard section/table structures, remove the 5th dummy row (`Name 5`), keep reporting windows strictly disjoint, link meetings/lectures/TA consultations to GitHub Issues, and record `TeamComposition.csv` Custom Document alignment status.

### 7.3 Fall Custom Document — ML Model Report (`docs/CDs/MLReport/main.tex` & `experiment/`)
- **Compiled Output:** `pdfs/CDs/MLReport/main.pdf` (5 pp / 2,711 words; Rubric: `docs/CDs/MLReport/Expectations_ML.md`).
- **Scope & Artifacts:** Documents deterministic CPU baseline pilots (`docs/CDs/MLReport/experiment/run_text.py`, `run_image.py`, `requirements.txt`) on English `HC3` (`3,212` held-out predictions across same-source and held-domain `medicine`; character TF–IDF reached $0.991$ assessed Macro-$F_1$ at $81\%$ coverage, $+0.007$ over word baseline, and falsely flagged $5/27 = 18.5\%$ of assessed `wiki_csai` human answers) and `Tiny-GenImage` ($64$ held-out clean + JPEG-60 pairs, failing all acceptance gates). Commits only hashes/manifests/metrics/predictions—never raw corpus text or images—and motivates Rev 0 neural candidates (`RoBERTa`/`DeBERTa`, `ViT`/`CLIP` + `EXIF`/`C2PA`).

### 7.4 Design Document (`docs/Design/SoftArchitecture/MG.tex` & `docs/Design/SoftDetailedDes/MIS.tex`)
- **Module Decomposition (`M1`–`M10`):** Follow Section 3.3 (`M1` Browser and host bridge; `M2` Selection and consent; `M3` Result card; `M4` Input validation; `M5` Request coordinator; `M6` Temporary content; `M7` Text signals; `M8` Image signals and provenance; `M9` Assessment policy; `M10` Offline evaluation).
- **Checklist & Verification Rules:** Keep `verify_design.py` passing (`10` modules, `52` requirement/hazard rows, `13` `AC`s covering `LC1`–`LC6`, acyclic `12`-edge `Uses` DAG, `16` exported literals in `MIS` `TblConstants`, `32`-assignment `TblLifecycle` matching SRS S.9.1, `10` distinct owner/reviewer rows in `MG` `TblSchedule`). In `MIS.tex`, each module begins with `\newpage` and specifies formal state/transition semantics (`out :=`, `exc :=`) rather than raw implementation code.

### 7.5 POC Demo, Rev 0, Winter Usability & Final Documentation (Weeks 11–26)
- **POC Demo (Dec 2, 2026, 5:45–6:00 pm, ITB/201):** Follow `docs/Checklists/POC-Checklist.tex` and `Wk06-a.tex` (*"PoC demo plans should match Dev Plan document"* — update `DevelopmentPlan.tex` or state demo scope differences explicitly). **No slide deck allowed** — demonstrate directly from live code (`docs/CDs/MLReport/experiment/`, `test/fixtures/generate.py`, `test/documentation/`) and discuss POC scope/decision rules.
- **Winter Usability Report (`docs/CDs/UsabilityTesting/UsabilityReport.tex`, Week 22):** Follow `docs/CDs/UsabilityTesting/Expectations.md`, register in `.pdf-deps.json`, run uncoached `NFT-2` + `NFT-6` Part A with $\ge 10$ participants verifying $\ge 80.0\%$ comprehension (including `C1(d)` false-positive warning).
- **Final Reflection (`docs/ReflectAndTrace/ReflectAndTrace.tex`, Week 26):** Address limitations, assumptions, constraints, economics, equity, prototype iterations, and full traceability without `LO_*` rubric tags cluttering prose.

---

## 8. Target Codebase Architecture, Directory Layout & API Contract (`src/` & `test/`)

Per `docs/Checklists/Code-Checklist.tex`, **all production source code must live inside `src/`** and all automated tests inside `test/`. Import all thresholds from a single canonical constants module mirroring SRS Table 6 & MIS `TblConstants` (no magic numbers). *(Currently `src/` holds scaffold files `README.md` & `TraceToDesign.md`; the layout below defines the Rev 0 implementation target aligned with `M1`–`M10`.)*

### 8.1 Canonical Codebase Layout (`src/` and `test/`)
```text
Verity/
├── src/
│   ├── extension/                 # S1 (Modules M1, M2, M3) — Chrome Manifest V3 Extension (TypeScript)
│   │   ├── manifest.json          # MV3 manifest: activeTab, contextMenus, storage (no <all_urls>, history, cookies)
│   │   ├── background.ts          # Service worker / host message bridge (M1, M2)
│   │   ├── content.ts             # Scoped read-only DOM selection & image capture (M1, M2)
│   │   ├── ui/                    # Extension-owned consent prompt & isolated result card (M2, M3)
│   │   └── constants.ts           # Mirrors SRS Table 6 / MIS TblConstants
│   ├── backend/                   # S2 & S3 (Modules M4–M9) — Python FastAPI Service
│   │   ├── main.py                # FastAPI app, CORS, lifespan loader, /api/v1/analyze & /healthz (NFT-8)
│   │   ├── constants.py           # Canonical SRS Table 6 + MAX_DELIVERY_RECORD_AGE=60 constants
│   │   ├── schemas.py             # Pydantic v2 models enforcing SRS Section S.5 JSON contract & INV1–INV3
│   │   ├── validation.py          # M4 (C3): Unicode code-point bounds, magic-byte MIME, dims (64..4096), bomb guard
│   │   ├── lifecycle.py           # M5 (C4): CheckKey/UUIDv4 state machine, 10.0s deadline, cancellation, burst cap
│   │   ├── ephemeral.py           # M6 (C5): WorkerLease (hold/borrow/release) <= MAX_RETENTION_TIME; zero persistent writes (INV4)
│   │   └── detectors/             # S3 (C6)
│   │       ├── base.py            # Abstract Signal extractor interface (NFR9 modularity)
│   │       ├── text_detector.py   # M7: RoBERTa/DeBERTa classifier + linguistic signals
│   │       ├── image_detector.py  # M8: ViT/CLIP visual detector + EXIF/C2PA provenance parser (FR13)
│   │       └── calibration.py     # M9: Assessment policy, domain gate g(r), conflict k(r), abstention margin
│   └── benchmark/                 # S4 (Module M10 / C7) — Reproducible CLI Evaluation Harness
│       ├── cli.py                 # Deterministic benchmark runner (--seed, --config)
│       ├── metrics.py             # Assessed & full-population Macro-F1, FPR_assessed/FPR_all, coverage, ECE, Brier, slices (FR14)
│       └── baselines.py           # Naive TF-IDF+LR / ResNet-18 baselines for MIN_BASELINE_DELTA (+0.10)
└── test/                          # Automated V&V Test Suite (pytest + Vitest + Playwright)
    ├── documentation/             # Existing: verify_specification.py, verify_design.py
    ├── fixtures/                  # Existing: generate.py (--seed, --text-and-png-only), README.md, requirements.txt
    ├── unit/                      # Rev 0 target: UT-C1..UT-C7 (M1–M10, Class 1–9 boundary tests)
    ├── integration/               # Rev 0 target: FastAPI + detector lifecycle, MAX_RESPONSE_TIME, burst cap, /healthz probes
    ├── privacy/                   # Rev 0 target: Weak-ref cleanup <= MAX_RETENTION_TIME & zero-sink retention (FT-12, NFT-4)
    └── adversarial/               # Rev 0 target: Prompt-injection (FT-8), bombs/XSS (FT-3/4), hostile DOM (FT-16), ESL slices (NFT-10)
```

### 8.2 Canonical JSON API Contract (`POST /api/v1/analyze`, SRS Section S.5)
- **Health Endpoint (`GET /healthz`):** Liveness probe paired with synthetic e2e probes in `NFR8` / `NFT-8`.
- **Request (`AnalyzeRequest`):** `req_id` (`UUIDv4`), `session_token` (`UUIDv4`), `modality` (`"text" | "image"`), `payload` (UTF-8 string `150..10000` Unicode code points or base64 `PNG`/`JPEG`/`WebP` $\le 10.0\text{ MB}$, `64x64..4096x4096` px), `source_origin`, `consent_granted` (`bool`), `client_timestamp_ms`.
- **Response (`AnalyzeResponse`):** `req_id` (`UUIDv4`), `status` (`"pending" | "completed" | "inconclusive" | "failed" | "cancelled"`), `summary_label` (non-accusatory string), `false_positive_warning` (plain-language `H1` notice required whenever flagged, `FR3`(d)), `calibrated_confidence` (`float | null`), `uncertainty` (plain-language interval/notice), `signals[]` (`signal_id`, `source` $\in \{\texttt{"observed\_signal"}, \texttt{"external\_reference"}, \texttt{"inference"}\}$, `locator`, `summary`), `limitations[]`, `verification_steps[]`, `latency_ms`.
