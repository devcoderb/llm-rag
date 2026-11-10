# Stage 6 review — 2026-11-09

**Current verdict: Stage 6 deliverables approved after fallback review at `9f57596`; proceed to Stage 7.** The initial 1A-trial findings below are retained as history. Quality failures remain for D2; approval does not mean every generated answer follows the prompt.
Reviewed remote/executed commit `3c56a86` (fetched and fast-forwarded locally), cells 39–45. Implementation reviewed from code and saved outputs; GPU inference and PV JSON artifacts not independently rerun/retrieved. Existing local review/plan edits preserved.

## Verified setup and experiment

- Stage 5 conclusion corrected explicitly: hit@1 rises 40%→50%, hit@3 falls 70%→50%; latest executed reporting uses 10.6 ms CE time (a new run), with rankings unchanged.
- Stage 6 cells 41–45 executed 32–36, outputs present, no errors, syntax valid.
- Hash-checked reranked inputs for the same frozen ten queries; saved chunk IDs/text match FINAL_CHUNKS. U01 runs the same Dense top10 → cross-encoder top3 pipeline separately; longest U01 pair is 412 tokens, no CE truncation.
- CPT+adapter loaded first, 4-bit NF4/double quant/float16 compute. Tokenizer/embedding rows 49,152, pad16 distinct from EOS0, adapter r16/alpha32/q_proj,v_proj, nonzero LoRA-B. Saved weight hashes agree with earlier model verification.
- Saved chat template used; continuation-only decoding; greedy generation. All 11 formatted prompts plus 150-token output reserve fit: maximum 1,644+150=1,794 <=8,192. No context truncation.
- Exact prompts, numbered mappings, raw continuations, heuristic flags and model hashes are saved and reload-checked. Frozen query hash independently unchanged.

## Observed failures

- All ten main answers have no numbered citations; none passes the current heuristic checks.
- U01 does not abstain: it asserts “The United States won the FIFA World Cup in 2018” and adds further unsupported material, despite receiving unrelated finance passages.
- Ten of eleven continuations reach the 150-token limit; only Q04 stops on EOS. Repetitive invented subsequent questions appear in several outputs.
- Q03 changes the source’s 34% figure to 37.5%; Q04 answers with a payment-system-change restriction instead of the no-charge provision, although the needed span is present. These are concrete generation failures, beyond citation-format failures.
- Five main contexts contain the frozen span; five do not. A stronger generator cannot repair missing retrieval evidence: it should abstain when needed, without changing the required reranked contexts.

## Required continuation

1. **Model switch is justified and approved by this review.** Retain the complete 1A trial as evidence; do not request another operator approval solely to attempt the already-authorized fallback.
2. Try Meta Llama-3.1-8B-Instruct if weight access is available; otherwise Microsoft Phi-3.5-mini-instruct. Use the recorded US-first policy; Qwen only if feasible US choices fail, with reasons documented. Keep the later judge a different model.
3. Generate the same ten questions plus U01 from the same saved chunk mappings; use the fallback’s own saved chat template, explicit greedy decoding settings, checked prompt+output budget and model/tokenizer revisions. Do not shorten contexts or change questions/spans to improve results.
4. Save fallback prompts/raw outputs separately; show all ten answers, citation diagnostics and the U01 abstention response. Preserve the original baseline JSON/manifest rather than overwriting it. Document one concrete baseline failure and why the switch was made.
5. The current gate labels `answers=PASS` and prints “Gate 6: all checks passed” even though U01 failed and SWITCH_NEEDED is true. Label baseline execution separately from completed D1 compliance. Do not claim grounded-generation/abstention success or advance to Stage 7 until the fallback results have been reviewed. If fallback fails, retain evidence and report the unmet requirement honestly.

Lexical overlap is diagnostic only; it does not establish factual correctness or citation support. Do not add citations or replace text after generation to make a result pass.

## Next

Stage 6 fallback continuation only, concise assignment-stage reporting, then operator execution and Codex re-review. Judge implementation remains deferred.


## Fallback re-review — commit 9f57596

**PASS for required D1 run/evidence; proceed to D2 with errors preserved.** Fetched/fast-forwarded the latest notebook, preserving local review/plan changes. Cells 47–50 executed 37–40, saved outputs present, no errors; code parses. GPU inference/PV JSON files not rerun/retrieved independently.

- Llama failed with a recorded gated-repository 401; Microsoft Phi-3.5-mini-instruct loaded successfully. Selected revision `2fe192450127e6a83f7441aef6e3ca586c338b77`, bf16, reported GPU allocation 7.88 GB.
- Baseline hash reverified unchanged; fallback has separate records/manifest and actual failure examples. Same eleven questions, user-message text, numbered chunk IDs/order; fallback's own chat template, explicit greedy settings and EOS tokens.
- Prompt+output maximum 1,923 <=131,072 configured positions; no prompt truncation.
- U01 returns exactly **Not found in the documents**. Ten main answers are displayed and saved. Six contain at least one in-range citation, but only five have nonempty citations all within [1]–[3]; Q03 additionally cites nonexistent [5]. Three main answers reach the 150-token limit (Q04/Q05/Q06).
- Q01/Q07/Q10 are semantic abstentions with extra wording/punctuation; exact-match checks flag them but they should be judged using an explicit semantic-abstention rule in D2. Do not postprocess them into the exact fallback.
- Q08 answers one hundred crore instead of the expected fifty crore; keep this distractor failure for source-grounded error analysis. Citation-number validity does not establish support or correctness (also inspect Q02's cited chunk).
- Independently counted citation/abstention/token-limit results from displayed output and revalidated frozen content hash unchanged.

The current D1_MET gate checks a stronger condition than assignment completion (all ten must cite or use the exact fallback). The assignment explicitly asks for wrong/unsupported answers to be evaluated in D2. Rename that result **strict instruction-compliance checks** and separately show **D1 required evidence complete**. Preserve the FAIL results as quality findings. Do not tune or regenerate answers merely to make the ten pass before judging them. U01’s mandatory abstention demonstration is now present.

### Stage 7 handoff

Judge the saved Phi answers with a different model. Llama access is currently unavailable and Phi cannot judge itself. Candidate US alternative: `ibm-granite/granite-3.0-8b-instruct` (IBM; Apache-2.0; native Granite config saved with Transformers 4.46.0.dev0; 4,096 positions). Check actual pod access/load and complete prompt+output length with the pinned 4.46.3 environment before use. Release the generation model first; do not truncate evidence. This is a candidate, not a tested judge-quality claim. Official model/config references: https://huggingface.co/ibm-granite/granite-3.0-8b-instruct and https://huggingface.co/ibm-granite/granite-3.0-8b-instruct/blob/main/config.json.

D2 requires per-query correct/partly correct/wrong and supported yes/no, reasons/unsupported quotes, out-of-ten summary, three operator-entered manual checks, one source-inspected failure cause and a targeted fix. Capture manual labels before exposing judge verdicts; never fabricate operator labels. Evaluate semantic abstentions consistently against expected answers and context, keeping U01 outside the ten-query totals. Record invalid citation IDs separately from answer correctness/content support. Save raw prompts/verdicts, parse errors and provenance; do not repair labels silently.


## Presentation re-review — commits b2aac74 / 9411623

**Stage 6 approval reaffirmed; proceed to Stage 7.** Remote origin/main already contains both named commits (HEAD/origin divergence 0/0); no push or inference rerun needed. Compared with executed `9f57596`: all 40 code-cell sources and saved outputs are identical. Added HTML flow diagram and plain-text fallback accurately show baseline failure → Llama401 → Phi → U01 success, without claiming a tested judge.

Before final presentation, make these small markdown corrections alongside Stage 7 implementation (no generation rerun):
- Label D1 “required runs/evidence complete; strict instruction compliance failed”, rather than leaving the entire stage described as not met. Retain every failure flag.
- “A missing whole frozen span” does not universally prove the context lacks sufficient information. Avoid the absolute claims “no generator can answer” and “a better retriever is the only fix”. State that recovering missing evidence requires a retrieval/reranking/context change, while a generator can improve abstention and citation behavior. Inspect actual passages for D2 root-cause claims.
- The Stage 6 setup summary reports six answers with any valid citation, not six with all citations valid: five are wholly within [1]–[3], and Q03 also cites [5]. Label the distinction.
- Q08 is compared against the frozen fifty-crore expected answer; the judge does not choose a new legal interpretation or silently change the reference answer. Investigate any reference ambiguity manually against the supplied corpus.

**Judge decision for next implementation:** test `ibm-granite/granite-3.0-8b-instruct` as the US judge candidate, different from Phi. Validate access/load, full untruncated prompt plus output budget (4,096 positions), and label-format behavior before the ten-query run. Do not wait for Meta approval; Llama access can be handled separately if desired. If Granite fails, record the actual issue and try a feasible US alternative before Qwen.
