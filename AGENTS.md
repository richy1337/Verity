# AGENTS.md — Agentic Coding & Documentation Guide for Verity

This file provides canonical context, architecture invariants, requirement/hazard identifiers, build instructions, course grading conventions, future milestone playbooks, and target codebase blueprints for AI coding agents (Antigravity, Codex, Claude Code, Cursor, Copilot, etc.) and contributors working in the **Verity** repository (`richy1337/Verity`).

---

## 1. Project Identity & Team Roster

- **Project Name:** **Verity** — Explainable, Uncertainty-Aware Digital Content Assessment
- **Course:** McMaster University SFWRENG 4G06 Software Engineering Capstone (2026–2027, Team 23 — "Dream Team")
- **Teaching Assistant (TA):** Rebecca Di Filippo (`@rebeccadifilippo`)
- **Repository:** `https://github.com/richy1337/Verity` (License: MIT)
- **Product Summary:** A user-triggered desktop Chromium browser extension (Manifest Version 3) and Python FastAPI analysis pipeline + CLI benchmark harness that helps users evaluate suspicious webpage text and static images (`PNG`, `JPEG`, `WebP`) for AI-generation, digital manipulation, and provenance (`EXIF` / `C2PA`) signals. Verity surfaces source-grounded evidence, explicit uncertainty/limitations, an `inconclusive` abstention state when signals are weak or out-of-domain (e.g., opinion/satire), and concrete next verification steps, while enforcing zero default persistent retention of user-selected content.

### Team 23 Members, MacIDs, GitHub Handles & Consistent Roles
Keep each member's voice, role, MacID, and course background consistent across all deliverables (`VnVPlan`, `MLReport`, `MG`/`MIS`, `VnVReport`, `UsabilityReport`, `UserGuide`, `ReflectAndTrace`, and `Productivity Reports`):

| Member | MacID & Email | GitHub Handle | Primary Ownership | Secondary Ownership | Key Course Background |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Calvin Salsali** | `salsalic@mcmaster.ca` | `@CalvinSalsali04` | Chrome MV3 browser extension UI, DOM selection capture, Shadow-DOM result card, consent modal, user personas, Winter Usability Report | ML evaluation review, documentation QA | `SFWRENG 3RA3`, `SFWRENG 4HC3`, `SFWRENG 2AA4` |
| **Raymond Tao** | `taor10@mcmaster.ca` | `@Raymondtaoo` | Text & image detector pipeline, benchmark design (`RAID`/`HC3`, `CIFAKE`/`GenImage`), threshold calibration, Fall ML Model Report | Backend API review, experiment reproducibility | `SFWRENG 4AL3`, `STATS 3Y03`, `SFWRENG 2DM3`, `SFWRENG 3RA3` |
| **Jaden Moore** | `moorej70@mcmaster.ca` | `@JadenAntM` | Python FastAPI analysis service, `UUIDv4` request isolation, timeout/cancellation state machine, CI/CD & milestone scheduling | Extension integration, testing infrastructure | `SFWRENG 3BB4`, `SFWRENG 2AA4`, `SFWRENG 3A04` |
| **Richard Han** *(Liaison)* | `hanr23@mcmaster.ca` | `@richy1337` | CLI evaluation harness, reproducibility verification, zero-retention privacy checks, adversarial/fuzzing test suite, FMEA traceability | Model integration, backend reliability | `SFWRENG 3S03`, `SFWRENG 3RA3` |

---

## 2. Repository Structure & LaTeX CI Build Pipeline

```text
Verity/
├── .github/
│   ├── ISSUE_TEMPLATE/        # Course issue templates (ta_meet.md, team_meet.md, lect.md, peer_review.md, sup_meet.md)
│   ├── scripts/
│   │   ├── select_docs.py     # Determines which .tex/.md files in docs/ need rebuilding from .pdf-deps.json
│   │   ├── record_deps.py     # Parses pdflatex .fls recorder files to update .pdf-deps.json
│   │   └── build_index.py     # Generates GitHub Pages index from committed PDFs in pdfs/
│   └── workflows/
│       └── latex-pages.yml    # Compiles changed docs/ via Make + pdflatex, syncs to pdfs/, deploys Pages
├── .pdf-deps.json             # Dependency graph mapping each docs/**/*.tex to every file it \inputs or \includegraphics
├── ExceptionsGranted.md       # Records instructor/TA-approved exceptions (e.g., Fall CD: ML Model Report)
├── Makefile                   # Compiles %.tex -> %.pdf using pdflatex -interaction=nonstopmode -recorder
├── docs/                      # Authoritative LaTeX source files (DO NOT commit compiled document PDFs inside docs/)
│   ├── Common.text            # Shared \progname and \authname macros
│   ├── Comments.text          # Instructor comment macros (\wss{})
│   ├── Reflection.text        # Shared reflection preamble
│   ├── SRS_Reflection.text    # SRS reflection questions
│   ├── Checklists/            # Dr. Spencer Smith's official checklists (Writing, SRS, HA, VnV, POC, MG, MIS, Code, FinalDoc)
│   ├── ProblemStatementAndGoals/ProblemStatement.tex
│   ├── DevelopmentPlan/DevelopmentPlan.tex
│   ├── SRS/                   # Meyer-adapted PEGS SRS (SRS.tex + 3 vector diagram PDFs)
│   ├── HazardAnalysis/        # FMEA Hazard Analysis (HazardAnalysis.tex + HazardComponentDiagram.pdf)
│   ├── projMngmnt/            # MeetingNotes.tex and productivity reports (POC, Rev0, Final)
│   ├── VnVPlan/VnVPlan.tex    # Verification & Validation Plan (Target: Week 08 — Nov 2, 2026)
│   ├── CDs/
│   │   ├── MLReport/main.tex  # CD-Fall: Machine Learning Model Report (Target: Week 10 — Nov 16, 2026)
│   │   └── UsabilityTesting/  # CD-Winter: Usability Report (Target: Week 22 — Mar 8, 2027)
│   ├── Design/
│   │   ├── SoftArchitecture/MG.tex   # Module Guide (Target: Rev -1 Nov 16, 2026; Rev 0 Jan 18, 2027)
│   │   └── SoftDetailedDes/MIS.tex   # Module Interface Spec (Target: Rev -1 Nov 16, 2026; Rev 0 Jan 18, 2027)
│   ├── VnVReport/VnVReport.tex       # Verification & Validation Report (Target: Week 22 — Mar 8, 2027)
│   ├── UserGuide/UserGuide.tex       # End-User Installation & Usage Guide (Target: Week 26 — Apr 5, 2027)
│   └── ReflectAndTrace/ReflectAndTrace.tex # Final Reflection & Traceability Report (Target: Week 26 — Apr 5, 2027)
├── pdfs/                      # Committed PDF outputs mirroring docs/ directory structure for TA grading
├── refs/References.bib        # Shared BibTeX bibliography
├── src/                       # All production source code (extension/, backend/, benchmark/) MUST live here
└── test/                      # All automated unit, integration, privacy, and adversarial tests MUST live here
```

### Build & Git Rules for Agents
1. **Compiling Locally:** Compile any `.tex` file locally using `tectonic <file>.tex` (at `/opt/homebrew/bin/tectonic`) or `pdflatex`.
2. **Where PDFs Live:**
   - **Compiled document PDFs** (e.g., `SRS.pdf`, `HazardAnalysis.pdf`, `VnVPlan.pdf`) MUST be copied to `pdfs/<Subfolder>/<Doc>.pdf` and removed from `docs/<Subfolder>/<Doc>.pdf`.
   - **Embedded figure PDFs** inside `docs/<Subfolder>/` (such as `docs/SRS/SystemContextDiagram.pdf`) are ignored by the root `.gitignore` (`*.pdf`) unless staged with **`git add -f docs/<Subfolder>/<Figure>.pdf`**. Always `git add -f` any new figure PDF in `docs/` and add it to that document's array in `.pdf-deps.json` so GitHub Actions `pdflatex` can find it.
3. **Package Compatibility with CI:** GitHub Actions (`latex-pages.yml`) installs `texlive-latex-extra`, `texlive-science`, `texlive-fonts-extra`, `texlive-fonts-recommended`, `texlive-latex-recommended`, `lmodern`, and `pandoc`. Avoid obscure packages (such as `zed-csp`) that are not in standard TeX Live; use standard `amsmath`/`amssymb`, `tabularx`, `ltablex`, `booktabs`, `pdflscape`, `enumitem`, and `hyperref`.
4. **`ltablex` + `tabularx` Rule:** When `\usepackage{ltablex}` is loaded, every `tabularx` is already a page-breaking `longtable`. Put `\caption{...} \label{...}\\` **inside** `\begin{tabularx}` and **do not** wrap `tabularx` inside `\begin{table}[H] ... \end{table}` (which prevents page breaking and causes vertical page overflows).
5. **Special Compilation Cases:**
   - **`docs/CDs/MLReport/main.tex`:** Uses ACL 2-column style (`acl.sty`, `acl_natbib.bst`, `custom.bib`). Set `\usepackage[preprint]{acl}` or `\usepackage[final]{acl}` so author names/MacIDs render (never leave anonymous review mode). Because the root `Makefile` runs `pdflatex` without `bibtex`, either commit the generated `main.bbl` (produced via `tectonic` or `bibtex`) or add a `bibtex` step to `Makefile` when compiling `MLReport/main.tex`.
   - **`docs/Design/SoftDetailedDes/MIS.tex`:** Uses `\usepackage{xr}` with `\externaldocument{../../SRS/SRS}`. Ensure `docs/SRS/SRS.tex` is compiled first if using `\ref{...}` to SRS labels, or use explicit text/hyperref identifiers.

---

## 3. Canonical System Constants, Architecture & Identifier Registry

Future documents (`VnVPlan.tex`, `MLReport`, `MG.tex`, `MIS.tex`, `VnVReport.tex`, `ReflectAndTrace.tex`) and production code (`src/`) **must** use the exact same symbolic constants, subsystem boundaries, requirement IDs, and hazard IDs established in `docs/SRS/SRS.tex` and `docs/HazardAnalysis/HazardAnalysis.tex`.

### 3.1 Symbolic Constants (SRS Table 6)
| Symbolic Constant | Value | Unit | Meaning & Governing Requirements |
| :--- | :--- | :--- | :--- |
| `MIN_F1_SCORE` | `0.80` | Macro-$F_1$ | Minimum unweighted Macro-$F_1$ on held-out benchmark (`NFR1`, `H1`, `H2`) |
| `MIN_COVERAGE` | `70.0%` (`0.70`) | Proportion | Existing overall coverage floor for selective F1 acceptance; report per-class/subgroup coverage and full-population diagnostics (`NFR1`) |
| `MAX_FPR` | `10.0%` (`0.10`) | Probability | Maximum False Positive Rate on legitimate/authentic items (`NFR1`, `NFR10`, `H1`) |
| `MIN_BASELINE_DELTA` | `+0.10` | Macro-$F_1$ delta | Minimum Macro-$F_1$ improvement over naive baseline (`NFR1`, Peer Issue `#13`) |
| `MIN_UNDERSTANDING_RATE` | `80.0%` | Percentage | Minimum uncoached user comprehension rate in usability study (`NFR2`, `H5`) |
| `MIN_USABILITY_PARTICIPANTS` | `10` | Participants | Minimum sample size for Winter Usability Evaluation (`NFR2`) |
| `MAX_RESPONSE_TIME` | `10.0` | `s` | End-to-end latency bound; exceeding this transitions request to `failed` (`FR6`, `NFR3`, `SR4`, `H6`) |
| `LATENCY_PERCENTILE` | `90.0%` | Percentile | Share of valid single-item checks completing within `MAX_RESPONSE_TIME` (`NFR3`) |
| `MIN_TEXT_LENGTH` | `150` | `chars` | Minimum UTF-8 character count for text check (`FR1`, `FR2`, `SR6`, `H2`) |
| `MAX_TEXT_LENGTH` | `10,000` | `chars` | Maximum UTF-8 character count for text check (`FR1`, `FR2`, `SR6`, `H7`) |
| `MAX_IMAGE_SIZE` | `10.0` | `MB` | Maximum byte size for static image (`PNG`, `JPEG`, `WebP`) (`FR1`, `FR2`, `SR6`, `H7`) |
| `MIN_IMAGE_DIM` | `64 x 64` | `px` | Minimum image pixel dimensions (`FR2`, `SR6`, `H2`) |
| `MAX_IMAGE_DIM` | `4096 x 4096` | `px` | Maximum image pixel dimensions to prevent decompression bombs (`FR2`, `SR6`, `H7`) |
| `MAX_INSTALL_TIME` | `5.0` | `min` | Maximum end-user browser extension installation time (`NFR6`, `NFR.E.2`) |
| `MAX_RETENTION_TIME` | `1.0` | `s` | Proposed bound for stopping request-owned tasks and releasing application-owned transient raw-content references after a terminal decision; no persistent raw writes at any time (`FR9`, `NFR4`, `SR8`, `H4`) |
| `MIN_SERVICE_UPTIME` | `99.0%` | Percentage | Target availability during active testing/evaluation windows (`NFR8`) |
| `MAX_CONCURRENT_REQS` | `10` | Requests | Minimum concurrent requests maintaining strict `UUIDv4` isolation (`FR10`, `SR7`, `SR9`, `H8`, `H9`) |
| `MAX_REPRO_DELTA` | `0.005` | Macro-$F_1$ delta | Maximum cross-member benchmark reproduction discrepancy (`NFR7`, `H10`) |

### Correction Coordination and Risk Status
The ephemeral cleanup contract in `codex/srs-lifecycle-privacy-fixes` establishes `MAX_RETENTION_TIME = 1.0 s` for bounded logical release of application-owned transient references, with zero persistent storage of raw user content at all times. This represents logical cleanup, not forensic memory zeroing.

The risk register distinguishes initial inherent risk estimates, conditional target estimates, and verified residual risk. All H1–H10 controls are planned engineering controls and residual risk remains unverified until test suites pass in CI. H1 and H5 retain a High conditional target and require rigorous held-out slice evaluation and uncoached comprehension testing before release claims can be made.

### 3.2 Five-State Request Lifecycle & Evidence Source Tags
- **Request Status Enum (`\mathcal{S}_{\text{status}}`):** `pending`, `completed`, `inconclusive`, `failed`, `cancelled` (`FR6`, `INV1`, `INV2`, `SR4`).
  - *Crucial Safety Invariant (`INV2`, `SR4`):* `failed`, `cancelled`, or partial signals must **never** map to a low-risk or authentic verdict; borderline/conflicting signals or subjective opinion/satire map to `inconclusive` (`FR4`, `SR1`).
- **Evidence Source Tags (`\mathcal{E}_{\text{src}}`):** Every displayed evidence item must be tagged in JSON as `observed_signal`, `external_reference`, or `inference`, rendered in UI as (1) `Observed Input Signal`, (2) `External Reference`, or (3) `Model Inference` (`FR7`, `SR5`, `INV3`, `H3`).

### 3.3 Subsystem & Component Mapping (SRS `S1`–`S4` $\leftrightarrow$ Hazard Analysis `C1`–`C7` $\leftrightarrow$ Design `M1`–`M10`)
- **SRS Black-Box Subsystems (`S1`–`S4`):**
  - `S1`: Browser Extension Selection, Consent & Display Boundary
  - `S2`: Input Validation, Request Isolation & Ephemeral Lifecycle Boundary
  - `S3`: Signal Analysis, Evidence Grounding & Uncertainty Boundary
  - `S4`: Reproducible Offline Benchmark & Fairness Evaluation Boundary
- **Hazard Analysis Internal Components (`C1`–`C7`):**
  - `C1`: Browser Extension Capture & Permission Controller (`H4`)
  - `C2`: Result Display & Uncertainty UI (`H1`, `H2`, `H5`, `H8`)
  - `C3`: Input Validation & Sanitization Gate (`H2`, `H7`)
  - `C4`: Request Isolation & State Coordinator (`H6`, `H8`, `H9`)
  - `C5`: Ephemeral Privacy & Buffer Lifecycle Handler (`H4`)
  - `C6`: Signal Detection & Grounded Evidence Engine (`H1`, `H2`, `H3`, `H6`)
  - `C7`: Offline Benchmark & Fairness Evaluation Workflow (`H10`)

### 3.4 Complete Requirement & Hazard ID Index
- **Goals (`G1`–`G6`):** `G1` Evidence-First Assessment; `G2` Honest Uncertainty & Safe Failure; `G3` Defensible Low-False-Accusation Quality; `G4` Non-Expert Understandability; `G5` Seamless In-Context Responsiveness; `G6` Privacy-First Ephemeral Handling.
- **Mandated Constraints (`C1`–`C6` in SRS):** `C1` Chrome MV3 Sandbox; `C2` Zero Specialized Client Hardware (`8 GB RAM`, no dedicated GPU); `C3` April 2027 Capstone Schedule; `C4` Zero-Cost / Open-Source Licensing; `C5` No Confidential User Training Data; `C6` TLS/HTTPS Transport.
- **Assumptions (`A1`–`A5`):** `A1` Potentially Sensitive/Malicious Selections; `A2` Fallible Detectors/APIs; `A3` Uncalibrated Raw Scores; `A4` Task-Bounded Benchmark Ground Truth; `A5` Standard Host Browser Integrity.
- **Functional Requirements (`FR1`–`FR14`):** `FR1` Scoped Selection; `FR2` Pre-Analysis Validation/Sanitization; `FR3` Evidence-Backed Output; `FR4` Uncertainty & `inconclusive` Abstention; `FR5` Verification Guidance; `FR6` 5-State Lifecycle Differentiation; `FR7` Source Attribution & Prompt-Injection Immunity; `FR8` Prior Informed Consent for External Transfer; `FR9` Ephemeral Processing & Zero Default Retention; `FR10` Unique `UUIDv4` Request Binding & Isolation; `FR11` In-Flight Cancellation; `FR12` Reproducible Benchmark Logging; `FR13` Image `EXIF`/`C2PA` Metadata Inspection; `FR14` Subgroup (`ESL`/Compressed-Image) Slice Reporting.
- **Non-Functional Requirements (`NFR1`–`NFR10` & `NFR.E.1`–`NFR.E.5`):** `NFR1` Accuracy & FPR Control; `NFR2` Usability Comprehension; `NFR3` Response Latency; `NFR4` Zero Persistent Retention; `NFR5` Cross-OS Chromium Portability; `NFR6` Installability ($\le 5.0\text{ min}$); `NFR7` Evaluation Reproducibility ($\pm 0.005$); `NFR8` Reliability & Fault Isolation; `NFR9` Detector Modularity; `NFR10` Cultural & Linguistic Fairness Auditing (`LO_Impact`).
- **Safety & Security Requirements (`SR1`–`SR9` — identical in SRS & HA):** `SR1` Visible Uncertainty; `SR2` No Personal Accusation; `SR3` No Authenticity Guarantee; `SR4` Safe Handling of Failed/Partial Analyses; `SR5` Grounded Explanations & Prompt-Injection Immunity; `SR6` Untrusted Webpage Content Sandboxing; `SR7` Strict Request-to-Result Association; `SR8` Controlled Access & Ephemeral Cleanup; `SR9` Cross-User & Cross-Session Isolation.
- **FMEA Hazards (`H1`–`H10`):** `H1` False Positive on Legitimate/ESL Content; `H2` False Negative Reassurance; `H3` Ungrounded Explanation / Prompt Injection; `H4` Unscoped Collection / Unconsented Transfer / Retention Leak; `H5` Over-Trust in Uncalibrated Score; `H6` Silent Timeout / Partial Failure Rendered Safe; `H7` Malicious Payload Execution / Decompression Bomb DoS; `H8` Stale Out-of-Order Async Overwrite; `H9` Cross-Session State Leakage; `H10` Leaky / Irreproducible / Biased Benchmark Evaluation.

### 3.5 Formal Invariants, Use Cases, Input Partition & Change Identifiers (`SRS.tex`)
All downstream documents (`VnVPlan.tex`, `MG.tex`, `MIS.tex`, `VnVReport.tex`, `ReflectAndTrace.tex`) must reference these exact SRS identifiers:
- **Formal System Invariants (`INV1`–`INV4`, SRS Section S.9.1):**
  - `INV1` (*Mutual Exclusion of Terminal Statuses*): At any time $t$, a request $r$ has exactly one status in $\mathcal{S}_{\text{status}} = \{\texttt{pending}, \texttt{completed}, \texttt{inconclusive}, \texttt{failed}, \texttt{cancelled}\}$.
  - `INV2` (*Safe Abstention & Non-Reassurance on Degraded Signals*): $\text{status}(r) \in \{\texttt{inconclusive}, \texttt{failed}, \texttt{cancelled}\} \implies \text{verdict\_safe}(r) = \texttt{false} \land \text{uncertainty\_banner}(r) = \texttt{true}$.
  - `INV3` (*Complete Source Tagging of Displayed Evidence*): $\forall e \in E_{\text{disp}}(r),\; \text{tag}(e) \in \mathcal{E}_{\text{src}} \land |\text{locator}(e)| > 0$.
  - `INV4` (*Bounded Application-Owned Transient Cleanup; No Persistent Raw Writes*): $\forall t > t_{\text{term}}(r) + \texttt{MAX\_RETENTION\_TIME},\; \text{Buffers}(r) = \emptyset$.
- **Product Use Cases (`UC1`–`UC4`, SRS Section E.6.2):**
  - `UC1`: Evaluate Suspicious Webpage Text Selection (`S1`, `S2`, `S3`)
  - `UC2`: Inspect Webpage Image for Manipulation and Provenance (`S1`, `S2`, `S3`)
  - `UC3`: Cancel an In-Flight Analysis Request (`S1`, `S2`)
  - `UC4`: Execute Offline Reproducible Benchmark and Fairness Audit (`S3`, `S4`)
- **Input Equivalence Classes & Boundary Partition (`Class 1`–`Class 9`, SRS Table 15 / `TblDomainCoverage`):**
  - `Class 1`: Empty selection ($L_T = 0$ or null image node) $\to$ Rejected pre-analysis (`FR2`)
  - `Class 2`: Short text ($1 \le L_T < \texttt{MIN\_TEXT\_LENGTH} = 150$) $\to$ Rejected (`FR2`, `H2`)
  - `Class 3`: Valid text ($150 \le L_T \le \texttt{MAX\_TEXT\_LENGTH} = 10,000$) $\to$ Accepted (`UC1`)
  - `Class 4`: Oversized text ($L_T > 10,000$) $\to$ Rejected (`FR2`, `H7`)
  - `Class 5`: Undersized image ($W_I < 64 \lor H_I < 64$) $\to$ Rejected (`FR2`, `H2`)
  - `Class 6`: Valid static image (`PNG`/`JPEG`/`WebP`, $64 \le W_I, H_I \le 4096$, $B_I \le 10.0\text{ MB}$) $\to$ Accepted (`UC2`)
  - `Class 7`: Oversized or decompression-bomb image ($W_I > 4096 \lor H_I > 4096 \lor B_I > 10.0\text{ MB}$) $\to$ Rejected (`FR2`, `H7`)
  - `Class 8`: Unsupported media format (`GIF`, `SVG`, `MP4`, or mismatched magic bytes) $\to$ Rejected (`FR2`, `H7`)
  - `Class 9`: Out-of-domain / subjective / satirical or prompt-injection text $\to$ `inconclusive` abstention (`FR4`, `SR1`) + payload treated strictly as inert data (`FR7`, `SR5`, `H3`)
- **Likely Changes (`LC1`–`LC6`) & Unlikely Changes (`ULC1`–`ULC4`, SRS Section P.1):**
  - `LC1`: Upgrading or swapping underlying text/image detector weights (`NFR9`)
  - `LC2`: Recalibrating confidence thresholds ($\tau_{\text{low}}, \tau_{\text{high}}, \tau_{\text{abs}}$) after empirical benchmark runs
  - `LC3`: Extending image provenance parsers (`EXIF` / `C2PA` / Content Credentials schema updates)
  - `LC4`: Refining result card UI layout, plain-language copy, and accessibility styling after Winter Usability Study
  - `LC5`: Expanding benchmark datasets or fairness subgroup slices (`ESL`, social-media recompression)
  - `LC6`: Adapting to minor Chromium Manifest V3 API updates
  - `ULC1`: User-triggered, scoped selection interaction model (`FR1`)
  - `ULC2`: Evidence-first, uncertainty-aware output contract with `inconclusive` abstention (`INV2`, `INV3`)
  - `ULC3`: Zero default persistent retention of raw user-selected content (`INV4`)
  - `ULC4`: Strict architectural boundary between interactive browser assessment (`S1`–`S3`) and offline evaluation (`S4`)

---

## 4. Course Grading & TA Conventions (Must Follow in Every Deliverable)

Based on TA Rebecca Di Filippo's rubric feedback (tracked in GitHub Issues `#17`–`#21`) and Peer Review Team 12's feedback (`#2`, `#3`, `#13`–`#16`), always enforce these rules:

1. **Revision History Tables:**
   - **Never** write `"Team 23"` or `"All"` in the Developer(s) column — always list specific individual names (`Calvin Salsali`, `Raymond Tao`, `Jaden Moore`, `Richard Han`).
   - **Never** write meta-descriptions like `"Revised against rubric and checklist"` — always describe concrete project, scope, or technical changes.
2. **High-Level Goals vs. Testable Requirements:**
   - High-level product goals (`G1`–`G6`) must read as non-expert product selling points (*Problem $\to$ What it causes $\to$ What Verity addresses*), while numerical percentages and tolerances belong in symbolic constants and `FR`/`NFR`/`VnV` tables.
3. **Reflections:**
   - Always include both a **Team Synthesis** and **four individual first-person subsections** (`Calvin Salsali`, `Raymond Tao`, `Jaden Moore`, `Richard Han`) that discuss real technical trade-offs/debates, specific McMaster courses, and concrete resolutions.
4. **Generative AI Use Disclosures:**
   - Explicitly list tool names and versions (e.g., **Google Gemini 3.1 Pro**), map which team member used the tool for which sections, and document **completed human verification steps** already performed by each named member (never leave future-tense placeholders like *"The team will verify before submission"*).
5. **No Unresolved Placeholders:**
   - Never leave `"TBD"`, `"Not set"`, or instructor `\wss{...}` comments visible in rendered PDFs.
6. **Dr. Spencer Smith's `Writing-Checklist.tex` Rules:**
   - **Always include introductory bridge text between headings:** Never place a `\subsection` immediately after a `\section` (or a `\subsubsection` immediately after a `\subsection`) without at least 1–2 sentences of introductory text explaining the section's contents.
   - **Never have a single subsection inside a section:** Any section that is subdivided must have at least two subsections.
   - **Define acronyms at first use AND in an Acronym Table** with hyperlinks to their contextual definitions.
   - **Provide legends or explicit graphical notation definitions** for every arrow and box border in every diagram.

---

## 5. Official SFWRENG 4G06 Schedule, Peer Review & CEAB Learning Outcomes

Derived from the official course repository (`Capstone_Outline.tex`, `Attributes_Indicators_LOs.tex`, `Schedule.xlsx`, and `Teams/`):

### 5.1 Course Deliverable Schedule & Weights (`Capstone_Outline.tex`)
Always name GitHub Milestones and schedule rows using these official course week numbers and deliverable titles:

| Course Week | Target Date | Official Deliverable Name | Course Weight | Authoritative Source Path(s) in `Verity` |
| :--- | :--- | :--- | :--- | :--- |
| **Week 03** | Sept 21, 2026 | Team Formed, Project Selected | `0%` | Course registration (`Teams/TeamInfo/TeamSummary_hanr23.json`) |
| **Week 04** | Sept 28, 2026 | Problem Statement, POC Plan, Development Plan, Team Charter Rev 0 | `2%` | `docs/ProblemStatementAndGoals/ProblemStatement.tex`, `docs/DevelopmentPlan/DevelopmentPlan.tex` |
| **Week 06** | Oct 19, 2026 | **Req. Doc. and Hazard Analysis Revision 0** | `7%` | `docs/SRS/SRS.tex`, `docs/HazardAnalysis/HazardAnalysis.tex`, `docs/projMngmnt/MeetingNotes.tex` |
| **Week 08** | Nov 2, 2026 | **V&V Plan Revision 0** *(+ Informal VnV & PoC Plan Pres. Oct 23; POC Team Prod. Rep. Nov 3)* | `5%` | `docs/VnVPlan/VnVPlan.tex`, `docs/projMngmnt/POC_Productivity_Rep.tex` |
| **Week 10** | Nov 16, 2026 | **Design Document Rev -1 and CD-Fall Rev 0** | `3%` | `docs/Design/SoftArchitecture/MG.tex`, `docs/Design/SoftDetailedDes/MIS.tex`, `docs/CDs/MLReport/main.tex` |
| **Week 11+12** | Nov 16–27, 2026 | **Proof of Concept Demonstration + Interviews** | `5%` | `src/benchmark/`, `src/backend/`, `src/extension/` |
| **Week 16** | Jan 18, 2027 | **Design Document Revision 0** | `4%` | `docs/Design/SoftArchitecture/MG.tex`, `docs/Design/SoftDetailedDes/MIS.tex` |
| **Week 18+19** | Feb 1–12, 2027 | **Revision 0 Demonstration + Interviews** *(+ Rev 0 Prod. Rep.)* | `10%` | Full MV3 extension + FastAPI backend + `docs/projMngmnt/Rev0_Productivity_Rep.tex` |
| **Week 22** | Mar 8, 2027 | **V&V Report Rev 0 and CD-Winter Rev 0** | `4%` | `docs/VnVReport/VnVReport.tex`, `docs/CDs/UsabilityTesting/UsabilityReport.tex` |
| **Week 24** | Mar 22, 2027 | **Final Demonstration (Revision 1)** | `20%` | Frozen Revision 1 product release (`src/` & `test/`) |
| **Week 26** | Apr 5–7, 2027 | **EXPO Demonstration (`10%`) & Final Documentation Rev 1 (`30%`)** | `40%` | All `docs/` updated to Rev 1 + `docs/UserGuide/UserGuide.tex` + `docs/ReflectAndTrace/ReflectAndTrace.tex` + `docs/projMngmnt/Final_Productivity_Rep.tex` |

### 5.2 Peer Review Assignments (`TeamComposition.csv` & `TeamRevAssig-00-Primary.md`)
- **Incoming Peer Reviewer — Team 12 ("SnowSight AI" — `https://github.com/CodeMaster177/snowsight-ai`):**
  - **Members:** Krish Dogra (`@CodeMaster177`), Edward Jung (`@junged856`), Saad Pahore (`@SaadPahore`), Jeffery Liu (`@liujeffery`). Always triage and link Team 12's issues in our docs and PRs.
- **Outgoing Peer Review Target — Team 06 ("Blockchainerz" / DAIIM — `https://github.com/robertLam04/daiim`):**
  - **Project:** *DAIIM — A Decentralized Marketplace for Reliable and Verifiable AI Inference*
  - **Members:** Robert Lam (`@robertLam04`), Nathan Hum (`@Nathan-Hum`), Aidan Lao (`@aidanlao`), Keira Laskoski (`@keiralaskoski`); Assigned TA: Rashad Bhuiyan (`@RashadBhuiyan`).
  - **Standard Peer Reviews (ProbState/DevPlan, SRS, Hazard Analysis, VnV Plan, VnV Report):** Open **more than 5 high-quality, rubric-grounded GitHub Issues** on `https://github.com/robertLam04/daiim` using the `peer_review` issue template and tagging `@rebeccadifilippo` (our grading TA) and `@RashadBhuiyan` (Team 06's TA).
  - **Special Design Document Rev 0 Peer Review Rule (`LO_ComprehendInstruct`):** Instead of $>5$ issues, Team 23 implements one module from Team 06's MIS via a PR, opens 1 summary issue on Team 06's repo, and reflects on the experience in MIS Reflection Question 7.
- **Custom Document Note (`ExceptionsGranted.md`):** Ensure our Fall Custom Document (`docs/CDs/MLReport/main.tex` — Machine Learning Model Report) and Winter Custom Document (`docs/CDs/UsabilityTesting/` — Usability Report) remain recorded in `ExceptionsGranted.md` and synchronized with `Teams/TeamInfo/TeamProjectDescription_hanr23.json`.

### 5.3 CEAB Graduate Attribute Learning Outcomes (`Attributes_Indicators_LOs.tex`)
Explicitly tag and satisfy these Learning Outcomes in the corresponding deliverables:
- **`LO_SpecMath`** (*First-order logic, set theory, and Parnas tabular expressions*): Assessed in **SRS** (Section S.9.1 includes a Parnas Horizontal Condition Table + set/first-order logic invariants) and **Design Document (MIS)**.
- **`LO_EngFund`** (*Hazard, safety, and risk analysis*): Assessed in **Hazard Analysis** (IEC 60812 FMEA + Elimination vs. Mitigation hierarchy).
- **`LO_Assumptions`** (*Reasonable assumptions and system/subsystem boundaries enabling modular subset tracing*): Assessed in **SRS** (Sections E.4, S.1, S.2) and **Hazard Analysis** (Sections 3 & 4).
- **`LO_ContextAndConstraints`** (*Context, constraints, and prior approaches*): Assessed in **SRS** (Sections G.1, E.3, E.7).
- **`LO_Standards`** (*Applicable technical standards, codes, legal & regulatory factors*): Assessed in **SRS** (Section S.8.4) and **Hazard Analysis** (Section 2).
- **`LO_Impact`** (*Societal impact: health, safety, legal, cultural/ESL fairness, and communicating uncertainty in engineering decisions*): Assessed in **SRS** (Sections G.5, S.7 `NFR10`) and **Hazard Analysis** (Section 2).
- **`LO_Reflect` & `LO_ExtKnowledge`** (*Identifying educational needs and independently acquiring/evaluating external knowledge*): Assessed in **SRS Reflection Q5 & Q6**, **VnV Plan Reflection Q3 & Q4**, and **VnV Report Reflection**.
- **`LO_Plan` & `LO_Tests`** (*Investigation data collection/analysis & test planning*): Assessed in **VnV Plan**.
- **`LO_ProbSolutions`, `LO_Explores` & `LO_ComprehendInstruct`** (*Limitations of proposed solution, alternative design trade-offs, and implementing a peer MIS module*): Assessed in **Design Document (`MG.tex` & `MIS.tex` Reflection Q5–Q7)**.
- **`LO_Synthesize`** (*Synthesizing test and evaluation results into valid conclusions*): Assessed in **VnV Report**.
- **`LO_PrototypeIterate`, `LO_Justifies`, `LO_Economic`, `LO_Equity`, `LO_Manages`**: Assessed in **Final Reflection & Traceability Report (`docs/ReflectAndTrace/ReflectAndTrace.tex`)**.

---

## 6. Git History, PR Stack (`#22`–`#25`) & Issue Registry (`#1`–`#21`)

### 6.1 Completed PR Stack (Weeks 04–06)
- **PR `#1` (Merged):** Initial Week 04 Problem Statement, Development Plan, and Meeting Notes.
- **PR `#22` (`docs/week04-feedback-fixes` $\to$ `main`):** Resolves TA Rebecca Di Filippo's Week 04 rubric feedback (`#18`–`#21`) and Team 12 peer review issues (`#2`, `#3`, `#13`–`#16`) in `ProblemStatement.tex` and `DevelopmentPlan.tex`.
- **PR `#23` (`docs/oct7-ta-meeting-notes` $\to$ `docs/week04-feedback-fixes`):** Documents Oct 7 TA consultation (`#17`) in `docs/projMngmnt/MeetingNotes.tex`.
- **PR `#24` (`docs/srs-rev0` $\to$ `docs/oct7-ta-meeting-notes`):** Complete Meyer-adapted PEGS `docs/SRS/SRS.tex` Rev 0 + 3 vector diagram PDFs (`SystemContextDiagram.pdf`, `WorkflowActivityDiagram.pdf`, `RequirementTraceabilityDiagram.pdf`).
- **PR `#25` (`docs/hazard-analysis-rev0` $\to$ `docs/srs-rev0`):** Complete IEC 60812 FMEA `docs/HazardAnalysis/HazardAnalysis.tex` Rev 0 + `HazardComponentDiagram.pdf` + `.pdf-deps.json` + `AGENTS.md`.

### 6.2 Canonical GitHub Issue Registry (`#1`–`#21`)
| Issue(s) | Category | Summary & Resolution / Target Deliverable |
| :--- | :--- | :--- |
| `#2`, `#3`, `#13`–`#16` | Incoming Peer Review (Team 12) | `#2` Proactive pre-POC false-positive mitigations; `#3` 3-Step Team Charter check-in protocol; `#13` `+0.10` Macro-$F_1$ baseline delta (`MIN_BASELINE_DELTA`); `#14` Quantified SRS NFR targets; `#15` Exclude opinion/satire from truth scoring; `#16` Expanded stakeholder & persona tables. Closed/addressed in `#22` & `#24`. |
| `#17` | TA Consultation | Oct 7 TA meeting notes with Rebecca Di Filippo (`MeetingNotes.tex`, PR `#23`). |
| `#18`–`#21` | TA Rubric Feedback (Week 04) | `#18` Problem Statement & Goals; `#19` Concrete POC candidates & datasets; `#20` Development Plan schedule dates; `#21` Individual reflections & verified GenAI disclosures. Addressed in PR `#22`. |
| `#4`–`#12` | October POC Engineering Backlog | `#4` Parent POC Epic (`@richy1337`); `#5` Issue labels (`@CalvinSalsali04`); `#6` Benchmark shortlist (`@Raymondtaoo`); `#7` Metric formulas & baseline rules (`@Raymondtaoo`); `#8` POC scope & demo checklist (`@CalvinSalsali04`); `#9` Freeze JSON schema & 5-state lifecycle (`@JadenAntM`); `#10` POC Milestone (`@JadenAntM`); `#11` Ephemeral zero-retention rule (`@richy1337`); `#12` CI & verification roadmap (`@richy1337`). |

---

## 7. Deliverable-Specific Playbooks & Checklist Rules (Weeks 08–26)

Every upcoming deliverable has an authoritative template in `docs/`, a `.pdf-deps.json` entry, and a grading checklist in `docs/Checklists/`.

### 7.1 Week 08 (Nov 2, 2026): Verification & Validation Plan (`docs/VnVPlan/VnVPlan.tex`)
- **Compiled Output:** `pdfs/VnVPlan/VnVPlan.pdf` (Checklist: `docs/Checklists/VnV-Checklist.tex`).
- **Mandatory Template Fixes & Checklist Rules:**
  1. **Revision History Table:** Use **`(Date | Developer(s) | Change)`** with named individuals (`Calvin Salsali`, `Raymond Tao`, `Jaden Moore`, `Richard Han`).
  2. **No Magic Numbers:** Every test threshold must reference a symbolic constant from SRS Table 6 (e.g., `\texttt{MIN\_F1\_SCORE} = 0.80`, `\texttt{MAX\_FPR} = 10.0\%`, `\texttt{MAX\_RESPONSE\_TIME} = 10.0\text{ s}`, `\texttt{MIN\_TEXT\_LENGTH} = 150`).
  3. **Static Verification Checklists:** Section 3 must define concrete walkthrough/inspection checklists for verifying the SRS, Hazard Analysis, Design Document, and source code.
  4. **System Tests (Section 4.1 & 4.2):**
     - Every Functional Requirement (`FR1`–`FR14`), Safety Requirement (`SR1`–`SR9`), Non-Functional Requirement (`NFR1`–`NFR10`, `NFR.E.1`–`NFR.E.5`), Hazard mitigation (`H1`–`H10`), and Input Equivalence Class (`Class 1`–`Class 9`) must have at least one test case ID (`T-FR1`, `T-SR4`, `T-NFR1`, etc.).
     - Specify **Type** (Dynamic/Static, Manual/Automated), **Initial State**, **Specific Inputs** (with exact boundary values like `149 chars`, `150 chars`, `10,000 chars`, `10,001 chars` and derivation rationale), **Explicit Expected Outputs** (exact `status` enum and UI banner state), and **How Result Will Be Checked**.
     - Include **specific WCAG 2.1 AA accessibility tests** and the **Usability Survey / Comprehension Questions** in Appendix (`Section 6.2`) used to measure `MIN_UNDERSTANDING_RATE = 80.0%` across `MIN_USABILITY_PARTICIPANTS = 10` (`NFR2`, `H5`).
  5. **Unit Test Description (Section 5):** Define the `pytest` / Vitest unit testing strategy, coverage targets ($\ge 80\%$ on core validation/lifecycle modules), and mock/stub conventions, noting which low-level unit test cases await Week 16 MIS completion.
  6. **Lifelong Learning Reflection (`LO_Reflect`):** In Reflection Q3 & Q4, **each of the 4 team members** must identify 1 specific new skill/knowledge item needed for V&V, list $\ge 2$ learning approaches, and justify their chosen approach.

### 7.2 Week 08 / Week 19 / Week 26: Team Productivity Reports (`docs/projMngmnt/*_Productivity_Rep.tex`)
- **Files:** `POC_Productivity_Rep.tex` (Nov 3, 2026), `Rev0_Productivity_Rep.tex` (Feb 2027), `Final_Productivity_Rep.tex` (Apr 2027).
- **Strict Format Rules:** Never delete sections or alter column structures; delete the 5th dummy row (`Name 5`) in every table since Team 23 has 4 members; keep reporting windows strictly disjoint (`Sept -> POC`, `POC -> Rev 0`, `Rev 0 -> Final`); link every meeting, attended lecture, and TA consultation to a GitHub Issue.

### 7.3 Week 10 (Nov 16, 2026): Fall Custom Document — ML Model Report (`docs/CDs/MLReport/main.tex`)
- **Compiled Output:** `pdfs/CDs/MLReport/main.pdf` (Rubric: `docs/CDs/MLReport/Expectations_ML.md`).
- **Build & Content Rules:**
  1. Set **`\usepackage[preprint]{acl}`** (or `\usepackage[final]{acl}`) so all 4 author names and MacIDs (`{salsalic,taor10,moorej70,hanr23}@mcmaster.ca`) render on the PDF.
  2. Include **$\ge 5$ academic citations** (`custom.bib`) and ensure `bibtex` / `tectonic` generates `main.bbl`.
  3. Cover all 7 required sections (`Introduction & Task Definition`, `Related Work`, `Datasets & Preprocessing` [`RAID`/`HC3` + ESL slice; `CIFAKE`/`GenImage` + recompressed slice], `Baseline & Candidate Architectures` [`TF-IDF` + Logistic Regression & `ResNet-18` vs. `RoBERTa`/`DeBERTa` & `ViT`/`CLIP` + `EXIF`/`C2PA`], `Experimental Setup & Calibration` [temperature scaling + $[\tau_{\text{low}}, \tau_{\text{high}}]$ abstention], `Results, Error Analysis & Fairness Audit`, `Ethical Considerations & Limitations`) plus an unnumbered **`\section*{Team Contributions}`**.

### 7.4 Week 10 (Nov 16, 2026 — Rev -1) & Week 16 (Jan 18, 2027 — Rev 0): Design Document (`MG.tex` & `MIS.tex`)
- **Authoritative Paths:** `docs/Design/SoftArchitecture/MG.tex` (`docs/Checklists/MG-Checklist.tex`) and `docs/Design/SoftDetailedDes/MIS.tex` (`docs/Checklists/MIS-Checklist.tex`).
- **Canonical Module Decomposition (`M1`–`M10` mapping `S1`–`S4` & `C1`–`C7`):**
  - **Hardware-Hiding (`M1`):** `M1` Chromium Host & OS Runtime Bridge.
  - **Behaviour-Hiding (`M2`–`M6`):** `M2` Selection Capture & Consent Controller (`S1`, `C1`); `M3` Result Card & Uncertainty Display Module (`S1`, `C2`); `M4` Input Validation & Media Sanitization Gate (`S2`, `C3`); `M5` Request Lifecycle & Isolation Coordinator (`S2`, `C4`); `M6` Ephemeral Buffer & Zero-Retention Manager (`S2`, `C5`).
  - **Software-Decision-Hiding (`M7`–`M10`):** `M7` Text Signal Detection & Grounding Module (`S3`, `C6`); `M8` Image Manipulation & Provenance (`EXIF`/`C2PA`) Module (`S3`, `C6`); `M9` Uncertainty Calibration & Abstention Decision Module (`S3`, `C6`); `M10` Reproducible Benchmark & Fairness Audit Harness (`S4`, `C7`).
- **Checklist Rules:** Every module secret in `MG.tex` must be a **single noun phrase** (*Service* = what; *Secret* = how); Anticipated Changes (`AC`) must be a superset of SRS `LC1`–`LC6` and trace 1-to-1 to leaf modules; the Uses hierarchy must be a DAG; every module in `MIS.tex` starts with `\newpage` and uses formal state/transition notation (`LO_SpecMath`) rather than raw code.

### 7.5 Week 11–12 (Nov 16–27, 2026): Proof of Concept (POC) Demonstration
- **Checklist:** `docs/Checklists/POC-Checklist.tex` (`LO_Risks`). **No slide deck is allowed** — demonstrate directly from live running software (`src/benchmark/`, `src/backend/`, `src/extension/`) and repository artifacts.

### 7.6 Week 22 (Mar 8, 2027) & Week 26 (Apr 5–7, 2027): V&V Report, Winter Usability Report & Final Docs
- **Winter Usability Report:** Create `docs/CDs/UsabilityTesting/UsabilityReport.tex` following `docs/CDs/UsabilityTesting/Expectations.md`, add it to `.pdf-deps.json`, and report comprehension ($\ge 80.0\%$) across $\ge 10$ participants (`NFR2`, `H5`).
- **Final Reflection (`docs/ReflectAndTrace/ReflectAndTrace.tex`):** Explicitly satisfy `LO_PrototypeIterate`, `LO_Justifies` (separate subsections for Limitations, Assumptions, Constraints), `LO_Economic`, `LO_Equity`, and `LO_Manages`.

---

## 8. Target Codebase Architecture, Directory Layout & API Contract (`src/` & `test/`)

Per `docs/Checklists/Code-Checklist.tex`, **all production source code must live inside `src/`** and all automated tests inside `test/`. Import all thresholds from a single canonical constants module mirroring SRS Table 6 (no magic numbers).

### 8.1 Canonical Codebase Layout (`src/` and `test/`)
```text
Verity/
├── src/
│   ├── extension/                 # S1 (Modules M1, M2, M3) — Chrome Manifest V3 Extension (TypeScript)
│   │   ├── manifest.json          # MV3 manifest: activeTab, contextMenus, storage (no <all_urls> scraping)
│   │   ├── background.ts          # Service worker: UUIDv4 lifecycle, AbortController cancellation (M2, M5)
│   │   ├── content.ts             # Scoped DOM selection & image capture + consent modal trigger (M2)
│   │   ├── ui/                    # Shadow-DOM result card, 5-state badges, source tags, verification steps (M3)
│   │   └── constants.ts           # Mirrors SRS Table 6 symbolic constants
│   ├── backend/                   # S2 & S3 (Modules M4–M9) — Python FastAPI Service
│   │   ├── main.py                # FastAPI app, CORS, lifespan model loader, /api/v1/analyze & /health
│   │   ├── constants.py           # Canonical SRS Table 6 symbolic constants (MIN_TEXT_LENGTH=150, etc.)
│   │   ├── schemas.py             # Pydantic v2 models enforcing SRS Section S.5 JSON contract & INV1–INV3
│   │   ├── validation.py          # M4 (C3): UTF-8 length, magic-byte MIME, pixel dims (64..4096), bomb guard
│   │   ├── lifecycle.py           # M5 (C4): UUIDv4 state machine, 10.0s timeout, cancellation, session isolation
│   │   ├── ephemeral.py           # M6 (C5): Request-owned task/buffer cleanup within MAX_RETENTION_TIME; never persist raw content (INV4)
│   │   └── detectors/             # S3 (C6)
│   │       ├── base.py            # Abstract Detector interface (NFR9 modularity)
│   │       ├── text_detector.py   # M7: DeBERTa/RoBERTa classifier + linguistic burstiness/perplexity signals
│   │       ├── image_detector.py  # M8: ViT/CLIP visual detector + EXIF/C2PA provenance parser (FR13)
│   │       └── calibration.py     # M9: Temperature scaling, [tau_low, tau_high] -> inconclusive abstention
│   └── benchmark/                 # S4 (Module M10 / C7) — Reproducible CLI Evaluation Harness
│       ├── cli.py                 # Deterministic benchmark runner (--seed 42, --dataset, --output)
│       ├── metrics.py             # Unweighted Macro-F1, FPR, ECE, Brier, p50/p90 latency, subgroup slices (FR14)
│       └── baselines.py           # Naive majority & TF-IDF/ResNet-18 baselines for MIN_BASELINE_DELTA (+0.10)
└── test/                          # Automated V&V Test Suite (pytest + Vitest/Playwright)
    ├── unit/                      # Module-level unit tests (M2–M10, Class 1–Class 9 boundary tests)
    ├── integration/               # FastAPI + detector pipeline lifecycle, timeout (MAX_RESPONSE_TIME), concurrency
    ├── privacy/                   # Ephemeral buffer purge & zero disk/DB/log retention verification (INV4, H4)
    └── adversarial/               # Prompt-injection payloads (H3), decompression bombs (H7), ESL fairness slices (H1)
```

### 8.2 Canonical JSON API Contract (`POST /api/v1/analyze`, SRS Section S.5)
- **Request (`AnalyzeRequest`):** `req_id` (`UUIDv4`), `session_token` (`UUIDv4`), `modality` (`"text" | "image"`), `payload` (UTF-8 string `150..10000` chars or base64 `PNG`/`JPEG`/`WebP` $\le 10.0\text{ MB}$, `64x64..4096x4096` px), `source_origin`, `consent_granted` (`bool`), `client_timestamp_ms`.
- **Response (`AnalyzeResponse`):** `req_id` (`UUIDv4`), `status` (`"pending" | "completed" | "inconclusive" | "failed" | "cancelled"`), `summary_label` (non-accusatory string), `calibrated_confidence` (`float | null`), `uncertainty` (plain-language interval/notice), `signals[]` (`signal_id`, `source` $\in \{\texttt{"observed\_signal"}, \texttt{"external\_reference"}, \texttt{"inference"}\}$, `locator`, `summary`), `limitations[]`, `verification_steps[]`, `latency_ms`.
