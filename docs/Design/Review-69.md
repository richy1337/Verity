# Review of Design Revision -1, PR #69

Reviewed November 18, 2026 at commit `4fbb82c1a9e6eba73aee030862d16588af2094f6`, using the supplied **41-point MG/MIS rubric**, the repository's MG, MIS and Writing checklists, current SRS, Hazard Analysis and V&V Plan, and the [course MIS reflection prompts](https://github.com/smiths/capTemplate/blob/main/docs/Design/SoftDetailedDes/MIS.tex). This review does not predict a TA mark. The SRS is authoritative where the older AGENTS.md registry differs (notably 1.0-second cleanup and strict request-binding INV3).

The ten-module decomposition is a sound starting point: live processing and offline evaluation are separated, request state has one owner, uncertainty is distinct from failure, and the Uses relation is acyclic. The changes below repair implementation ambiguities and incomplete document sections while keeping those boundaries.

## Findings and corrections

1. **High: stateful modules have no callable initialization contract.** The original MIS describes empty registries and loaded model configuration but provides neither initialization signatures nor guards. Independent implementations could accept work before the detector or ownership registry exists. The follow-up defines abstract-object scope, common initialization, readiness checks, immutable configuration matching and typed state. M4 remains a stateless library.

2. **High: some operation signatures cannot supply what their semantics require.** [M2 preview, lines 247–275](https://github.com/richy1337/Verity/blob/4fbb82c1a9e6eba73aee030862d16588af2094f6/docs/Design/SoftDetailedDes/MIS.tex#L247) promises a disclosure but returns only modality and route, with no explicit policy version/eligibility record. M6 requires a worker lease for borrow but no operation issues one. The follow-up introduces ConsentPreview, makes hold return the lease, and states how M5 delegates it. Image provenance is carried separately within Signals so M9 can consume it without an undeclared input.

3. **Medium: constants are named but not given literal values.** The [M5 exported constants](https://github.com/richy1337/Verity/blob/4fbb82c1a9e6eba73aee030862d16588af2094f6/docs/Design/SoftDetailedDes/MIS.tex#L415) and other modules leave implementers to consult another document. The MIS checklist requires explicit values. The follow-up adds values/units, inclusive bounds, code-point text length and decimal image MB. It preserves the current SRS cleanup bound of **1.0 second**, with no persistent raw writes at any time. A separately identified design constant bounds safe delivery metadata to 60 seconds; it does not extend raw-content retention.

4. **Design work for the next revision.** This revision defers detailed UI, communication protocols and database design. The MIS specifies observable behavior and state ownership, including extension-controlled consent and results, bounded access to selected content and abstention when text applicability is unsupported or uncertain. The V&V Plan tracks the integration choices and release evidence.

5. **Medium: lifecycle and evaluation contracts need explicit pass/fail conditions.** The original pending-state decision combines completion/abstention in prose, and M10 refers generally to FPR denominators. The follow-up mirrors the SRS's five disjoint guard rows, defines score validity before use, and gives the coverage and assessed/full-negative FPR formulas. Empty required populations and undefined metrics cannot pass. Model and baseline F1 use identical assessed IDs. The availability statement now follows NFT-8's health probes, with recovery and capacity verified separately.

6. **Timeline and traceability.** The timeline is an explicit rubric item. The follow-up gives all ten modules an owner, reviewer, target window, dependency and confidence check. It separates combined requirement rows and explains M10’s offline entry point. The MIS locates staged content, service buffers, loaded models, display data and offline artifacts so each has a clear owner.

7. **Still requires contributor input: individual reflections.** The follow-up supplies a team synthesis for prompts 1–6, including limitations (LO_ProbSolutions) and alternatives (LO_Explores). The reflection is due November 21 for the November 16 milestone. Contributors can add details from their own work. Question 7 follows the peer-module implementation and must link its PR and discuss both implementation directions if applicable.

## Rubric assessment and remaining work

| Rubric row | Finding and follow-up |
| --- | --- |
| SoftArchitec: Timeline (3) | Originally empty. Added a module-level Rev 0 implementation plan with named owners/reviewers, date windows, dependencies, confidence tests and integration gates. Dates and assignments are proposed plans. |
| SoftArchitec: Quality Information (3) | Core modules and change sets existed. Clarified state and transport boundaries and linked the SRS, HA, V&V and companion design documents. |
| SoftArchitec: Reasonable Design (3) | Uses DAG was already acyclic. Kept it, clarified noun-phrase secrets, module classifications and the offline M10 exception. Broader detector-plus-provenance strategy remains one image-analysis secret with a common public interface. |
| SoftArchitec: Traceability (3) | Split combined requirement rows and checked every FR, NFR, NFR.E, SR and INV plus H1–H10 has an allocation; every module has requirements. Each AC has one owner. LC1/LC3/LC4 split across independent secrets with the exception explained. |
| SoftArchitec: Presentation (3) | Improved document navigation, captioned tables, corrected revision metadata and rebuilt the vector PDFs. |
| DetDesDoc: Syntax (3) | Added initialization/readiness rules for all nine abstract objects, explicit constant values, typed state/environment and complete consent/lease/provenance types. M4 remains stateless. |
| DetDesDoc: Semantics (3) | Added common output/failure notation, constructor invariants, command acknowledgment exceptions, disjoint lifecycle guards and mathematical decision/metric conditions. |
| DetDesDoc: State Information (3) | Explicit ownership table in prose distinguishes M2 staging, M5 lifecycle/delivery, M6 raw buffers, M3 screen data and M7–M9 loaded artifacts. Transfers do not create a second mutable owner. |
| DetDesDoc: Environment variables (3) | Typed browser document, screen, input, network, clocks, model files, benchmark files and output directory; operations describe reads and writes. |
| DetDesDoc: EnoughToBuild (3) | Removed several implementation-blocking omissions. Capture, genre recognition and model quality are specified release gates; a successful document build is not proof of implemented product behavior. Independent implementation review remains valuable. |
| Reflection (3) | Original appendix empty. Added evidence-based synthesis for all six design prompts; Contributors can add personal experiences, and question 7 follows peer implementation. No personal experience or completed peer work is invented. |
| Gen AI Use Disclosure (3) | The MG and MIS retain the team's disclosure and verification wording, list Richard Han's use of Claude Fable 5.2 and Claude Opus 5.5, and summarize the tools and checks used for the follow-up. |
| Informal TA presentation (2) | Attendance and engagement cannot be established by repository edits. All four members should attend prepared with questions and record actual feedback. |
| CI/CD (3) | PR #69's LaTeX workflow succeeded. Enabled its build on the stacked target branch as well. The first follow-up run exposed failed APT downloads silently accepted by the package-cache action; the build now uses Ubuntu 24.04 and a normal fail-fast APT installation. A subsequent regional-mirror download stall repeated on a fresh runner; the workflow now prefers Ubuntu's main HTTPS archive, limits acquire retries/timeouts and caps the installation step at 15 minutes. Added a read-only workflow running eight existing SRS/HA checks and the MG/MIS audit on every PR. **Production unit tests, lint/coverage and required branch checks are not yet established.** The PR #69 source tree is still a scaffold, so this does not justify full CI/CD credit. The administrator must require checks in branch protection; workflow existence alone cannot block a merge. |

There are enough unresolved personal-reflection and product-CI obligations that a Level 4 or full-score claim would be premature. The follow-up is a draft to make the design corrections reviewable while those obligations are resolved.

Suggested TA questions: Is the fail-closed text scope acceptable until the genre gate is validated? How should the team handle the baseline-gain target when a stronger baseline leaves little headroom? Which cross-domain and subgroup evidence is expected before enabling a directional result?

## Source control

This is a follow-up to PR #69 and targets `docs/design-doc-rev-1`, so its diff contains review corrections only. It does not rewrite the teammate's commit or merge the branch. [PR #68](https://github.com/richy1337/Verity/pull/68) also changes MG/MIS while supplying the separate Fall ML report. Preserve the reviewed design version when reconciling that overlap and bring in its ML report/experiment artifacts deliberately; do not assume both PRs can be merged unchanged. The repository rulesets endpoint returned an empty list; classic branch protection was not established by that read and requires an administrator audit.

## Verification

- `python3 test/documentation/verify_specification.py --with-hazard` passed all eight existing checks.
- Both documents built with the repository Makefile using pdflatex, BibTeX and two final pdflatex passes.
- `python3 test/documentation/verify_design.py` checks all ten modules, each FR/NFR/NFR.E/SR/INV and H1–H10, LC1–LC6, the Uses DAG, explicit constant definitions, and complete operation signature/semantics pairs.
- All 32 lifecycle Boolean assignments were checked for exactly one matching guard, with cancellation, deadline/error and completion precedence matching the SRS. This checks the specification; it is not an implementation test.
- The compiled PDFs are synchronized into `pdfs/Design/`; compiled document PDFs are removed from `docs/`. Dependency records are refreshed from the builds.
- PDF layout review includes all rendered pages and larger views of the type/constant tables, module interfaces, lifecycle table and Uses figure. Local build logs contain no overfull boxes or unresolved citations/references.
- No production behaviour, detector benchmark rerun, independent human review, attendance or completed peer implementation is claimed by these checks.

## Joint publication audit of PRs #69 and #70

The combined branch has no merge conflicts and both CI jobs passed before this final contract audit. PR #70 targets PR #69's branch: merge #70 into #69 first, then re-run #69's main-target checks before publishing from main. PR #70 carries the updated disclosure and rubric timeline. No merge or release was performed by this audit.

The final audit adds M1's dependency on M4's exported capture bounds to both Uses descriptions and the diagram; gives M5 explicit safe-response/terminal/expiry state and timer-only retirement; removes an undeclared acknowledgment protocol; aligns unsupported/uncertain applicability labels; and fixes both classes and the zero-denominator convention for assessed macro-F1. The original PR description's zero-second cleanup and INV3 attribution are corrected to match the current SRS.

Technical publication and rubric completion are separate checks. The rubric sets November 21 as the reflection deadline for the November 16 milestone. The schedule records proposed implementation dates and ownership. Product-test merge gates and actual TA-presentation participation cannot be certified by this documentation audit.
