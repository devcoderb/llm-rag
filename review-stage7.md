# Stage 7 review — 2026-11-10

**Verdict: execution verified; changes requested before Stage 8.**
Reviewed `df35c1b` (HEAD matches origin/main after fetch), Stage7 cells73–78 / 7A–7F, IDs cbfc1da0,3cbb672e,d18443ee,f34c42f1,1a521aab,53c7bf60. All6 cells executed47–52 with saved outputs and no errors; syntax checked. GPU inference and PV artifacts not independently rerun/retrieved. Notice-board dataset audit is separate and does not change this scope.

## Checks passed

- Judge IBM granite-3.0-8b-instruct differs from Phi generator; loaded revision5af56291a1c6ca9056df597aab0cff53edabddb0, bf16, greedy decoding. Prompt2268+reserve300=2568 <=4096, no truncation.
- Original Phi answers hash-checked, unchanged; frozen query hash independently unchanged. All11 verdicts parse; U01 excluded from out-of10 totals.
- Independently recounted raw judge outputs: correct0, partly correct7, wrong3, supported9, abstains1. Arithmetic matches printed totals. These are **unvalidated judge labels**, not established answer-quality counts.
- Three operator labels and a post-verdict explanation are saved; agreement2/3 accurately compares those original labels with this judge run.
- Q06 shows all3 full chunks and actual source-span chunk ranks (Dense102/BM257), supporting an analysis of missing retrieval evidence plus generation’s failure to abstain.

## Required corrections

### [P1] Format-only calibration passes a demonstrably incorrect judge

Stage7A marks both invented cases PASS because they parse. Its second case answers “Lyon” when the only supporting capital sentence says “Paris”, yet Granite returns SUPPORTED yes. That is a failed semantic calibration, regardless of successful format parsing.

The real-run errors are systematic: Q09 is marked partly correct because the judge says1% is omitted, although the answer says1% twice; Q02/Q05 are penalized for missing facts visibly present in their saved answers; Q03 is said to differ from the expected34%→83% despite giving those same numbers. Q06’s survey response is described as a key fact of the unrelated Small Payment System Providers expected answer. U01 exact abstention is marked partly correct/abstains no, against the explicit rubric. Eleven quote-consistency issues are flagged. These outputs cannot support a reliable correctness summary without qualification/correction of the judge method.

Sonnet: preserve this original run as version1. Add expected **content labels** to independent invented calibration cases: correct+supported, wrong+unsupported, wrong-but-supported, answerable-question abstention, unanswerable-question abstention. Require semantic calibration success before generating a revised ten-query summary. Improve judge instructions/data separation or use a feasible different US judge if needed; record prompt/model revisions and keep runs separate. Do not hard-code actual-question labels, repair verdicts silently, tune generator answers or alter frozen data. Parse success remains separate from semantic success. Honest calibration failure is preferable to a false PASS.

### [P2] Operator support labels contradict the stated abstention convention

Original manual labels for Q07/Q10 are SUPPORTED no. Their saved answers abstain; the rubric explicitly assigns abstentions SUPPORTED yes and wrong when a real expected answer exists. The Q10 explanation argues that missing evidence makes an abstention unsupported, which uses a different definition. Q07’s agreement with the judge is therefore agreement on the same rubric error.

Operator acknowledged the manual mistake in chat. Operator should explicitly revise the labels/explanation using the documented rubric. Preserve the original files and2/3 result; record revised manual review separately with timestamps/provenance. Any review made after seeing version1 verdicts must be described as a post-review correction, not original blind labels. Codex/Sonnet must not fabricate operator entries. Compare revised labels against the revised judge run when available.

### [P2] Q06 fix explanation misidentifies the candidate-pool exclusion

Stage7E says Stage4 top20 pools left the gold chunk out, but it is BM25 rank7 and was already in BM25 top20. It was excluded from the selected **Dense top10 reranking pool** (Dense rank102), not from both RRF input lists. Deeper RRF lists alone do not guarantee it survives fusion.

Correct the diagnosis. One justified proposal is to merge/deduplicate Dense top10 and BM25 top10 **before cross-encoder reranking**: BM25 rank7 then enters the candidates. State that improved final top3 is a hypothesis requiring measurement, not guaranteed. Keep this as a proposed fix; do not rerun earlier assignment comparisons to replace results.

### Presentation follow-up

Stage7 headings/observations/checklist still say not executed/no results despite saved outputs. Update after revised review, explaining original judge failure, the corrected run and operator correction in simple question→expected→observed→meaning terms. Keep original raw judge outputs available. Do not claim the judge is accurate solely because all verdicts parse or the gate says COMPLETE.

## Next

Stage7 corrections and revised judge evaluation only, then Codex re-review. Stages0–6 and Phi answers remain approved/unchanged. No packaging approval yet.


## Corrections/interface re-review — 1546b34, 2026-11-10

**Manual interface and Q06 diagnosis accepted. Final ten-answer judge run remains pending; Stage 8 not yet approved.** Local HEAD matches origin/main. Notebook syntax and actual norm_qid function tested independently (numeric/formatted IDs accepted; out-of-range/invalid inputs rejected). Correction cells execute without errors; model tests/results are reviewed from saved outputs, not rerun locally.

- Actual accepted selection inputs are2,6,8 -> Q02,Q06,Q08. The loaded/replacement paths now print full question, expected answer, Phi answer, all3 numbered chunks and rubric. Saved labels: Q02 correct/yes; Q06 wrong/yes; Q08 wrong/yes. These fit the declared content-support convention. The selections changed after the initial judge review; preserve and describe their replacement/post-review provenance, not original blind labels.
- Reloaded paths show all evidence, but can still call print_manual_summary for a concise question/answer/label summary at the end, as the fresh-entry path does. No new labels required.
- Corrected Q06 evidence: goldchunk Dense102/BM257, inside BM25top20 but outside the selected Dense top10. RRF fused rank13 at depth20 and21 at depth50 demonstrate that deeper lists do not guarantee the cut. Proposed15-chunk union explicitly remains untested; accepted.
- Calibration now tests content rather than format only. Initial Granite full-label match4/12; revised Granite3.0 7/12; Granite3.3 8/12 with one malformed reply; Tulu3 8B 9/12, all12 correctness labels, all12 abstention labels and9/12 support labels match.

### Avoid an unnecessary perfect-score gate

The earlier review required semantic calibration to catch obvious judge failures; the resulting absolute12/12 gate is an extra review criterion, not a PDF requirement. Requiring perfect calibration from every small judge now prevents any final ten-query evaluation. Replace it transparently with a documented, limited judge selection based on measured calibration. Do not relabel failed cases as passed or relax labels silently.

**Next candidate selected for the final D2 evaluation: `allenai/Llama-3.1-Tulu-3-8B`.** It is already loaded/tested in the recorded US-first search and has the strongest recorded combined result. Use the revised rubric/prompt on the unchanged saved Phi answers. Disclose its three support-check calibration failures and validate resulting judgments manually; passing all correctness calibration cases is not proof that real-answer labels will be correct. Retain raw outputs and any disagreements. No further model-search loop or generator rerun is required now. This selection is approved for running the evaluation, not approval of unobserved final verdicts.

### Presentation for TAs

Version numbers were introduced to preserve earlier unsuccessful attempts and corrections. They are audit history, not separate assignment deliverables. The main D2 section should present **Final judge setup → Final ten-answer results → Three manual spot-checks → One failure/cause/fix → Observations**. Move unsuccessful judge tests and superseded labels/results to a clearly labelled appendix or separate audit notebook/files, retaining evidence and a short limitations note in main D2. Keep the complete1A→Phi generator-switch evidence required by D1.

No final revised verdicts exist in this run:7I/7J were skipped because SEL=None. Do not call the old unreliable0/7/3 summary the final evaluation. After the final judge run, replace stale pending/no-results prose with actual observations, report only one clearly designated final summary and spot-check result, and retain initial attempts only as historical evidence. Internal file paths/IDs may stay versioned; the TA-facing headings do not need “v1/v2” throughout.

### Next Sonnet action

Use Tulu with disclosed calibration limitations for the real ten-answer judge run (U01 separate), compare against the operator’s current saved Q02/Q06/Q08 labels and capture any real disagreement explanation. Preserve the original audit artifacts; produce a single final D2 presentation and summary, then return for Codex review. Notice-board audit remains deferred until Stage7 approval.


## Single-flow final-run review — e9e8602 / d342bd2, 2026-11-10

**D2 execution, manual spot-check and failure analysis accepted. No more judge/model-search or Phi reruns required. Two reporting/save corrections remain before packaging.** Reviewed executed e9e8602 and local save-name fix d342bd2; local branch has this one save-fix commit ahead of origin/main. User-reported Mac hashes differ, so this note identifies commits actually inspected rather than assuming hash equality across copies. Audit notebook is separate, main D2 has one judge/results flow.

Verified from code and saved outputs:
- Six final-stage cells executed70–74,76; syntax valid, no error outputs. Execution-count gap is not itself a failure; final save cell was rerun.
- Tulu revision666943798adbde0b1aff34626007e26986a3c107, distinct from Phi, bf16/greedy. Max prompt2636 +400 reserve=3036 fits configured131072 positions.
- Calibration9/12, support-check failuresK03/K06/K12 explicitly WARN, not hidden. This does not prove final correctness.
- Independently counted raw judge labels:6correct,2partly,2wrong,7supported,3abstentions. One invalid citation[5] inQ03;2quote issues. U01 correct/yes/abstainsyes matches rubric.
- Operator Q02/Q06/Q08 labels and actual explanations saved;1/3 full agreement. Explanations correctly distinguish answer content from reference correctness and support.
- Q06 full3chunks/source diagnostics show missing expected evidence; gold Dense102/BM257, excluded by Dense top10 reranking. Candidate-union proposal is correctly stated as untested, not guaranteed improvement.
- Frozen input hash independently unchanged. Phi generation not rerun. Judge JSON writes/reloads evidenced in notebook; attached stage7/v2 files are not present in the accessible workspace, so their individual hashes have not been independently verified here.

### Reporting correction (no inference rerun)

The final Observations cell still says “Pending operator execution”. Replace it with the actual raw-judge summary, manual1/3 agreement and limitations. Explicitly identify **Q07 as a judge error**: it labels an answerable-question abstention CORRECT correct and ABSTAINS yes, contradicting the rubric. Also explain Q06/Q08 operator disagreements, Q01 support/abstention inconsistency and quote issues. Retain raw verdicts/counts unchanged and label them as judge-reported figures, not validated answer accuracy. Any human corrections must be separately attributed; do not silently change6/2/2 to an adjudicated total. Update observations/appendix/checklist to name the actual final files.

### [P2] Final-save manifest is not reliably created or resolvable

Final Stage7F (cell ID8c2ccbbd) writes stage7_final_manifest.sha256 only inside the `else` branch for a nonexistent final JSON. In the reported current PV state the final JSON already exists, so rerunning this save cell can print the new manifest name without creating/verifying it; the old filename remains stage7_v2_manifest.sha256.

The manifest writer also emits only f.name. MANUAL_PATH is stage7/manual_spotcheck.json, but the manifest lives in stage7/v2. Its `manual_spotcheck.json` entry therefore points at a nonexistent sibling unless a separate duplicate has been packaged there. Use paths relative to the manifest directory (e.g. ../manual_spotcheck.json) or collect all final submission artifacts under one folder. Validate from the manifest's own directory.

Sonnet: preserve all existing records. Choose one actual final manifest path; create/update it even when final JSON already exists; validate all referenced files and hashes. Check existing final JSON's model/revision, prompts, answers, labels/summary/spot-check against the current run, not just the raw verdict strings. Fail clearly if mismatched. This is a save/integrity fix only: run7F and reporting updates, not inference. Archive the legacy manifest or explain its role without claiming a nonexistent new file was verified.

Next: these two small corrections, then Stage7 reporting/save recheck. Notice-board audit follows Stage7 approval; packaging after that. Stages0–6 remain unchanged and approved.
