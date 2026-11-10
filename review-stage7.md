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
