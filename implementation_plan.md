# Assignment 2B — RAG Pipeline: Implementation Plan

**Group 157 · Domain: Indian Financial Markets & Digital Payments (final local sources: RBI / SEBI)**
**Deliverable:** one notebook `Group157-Assignment-2b.ipynb` (all outputs visible) + HTML export. 20 marks (A 5 · B 4 · C 4 · D 7).
**Implementer:** Sonnet. **Reviewer/tester:** Codex Sol. **Operator:** runs and explains each stage.
**Review status (2026-11-10):** Stages 0–6 remain approved. Stage 7 executed `df35c1b` reviewed; changes requested before Stage 8. Judge passes formatting but fails semantic calibration and misreads actual answers; original manual Q07/Q10 support labels conflict with the rubric (operator acknowledged mistake). Correct Q06 candidate-pool explanation. See `review-stage7.md`; preserve original runs and saved Phi answers.

**Working cadence:** Sonnet explains the concept, adds only the current stage’s small group of markdown/code cells, and gives the operator an expected-output checklist. Operator executes and discusses the outputs; Codex audits code, outputs and claims. Resolve defects before starting the next stage. Later stages below are a roadmap, not permission to generate the whole notebook at once.

**Requirements authority:** `concepts/Assignment 2B - RAG Pipeline.pdf`, pp. 1–5; 1A requirements: `../assignment-1a/concepts/Assignment1A_CPT-and-SFT-1.pdf`. Choices such as BGE, diverse documents and strict parsing are implementation decisions, not extra rubric requirements.

---

## 0. Where Assignment 1a leaves us (brief)

| Item | What 1a produced | Why it matters for 2B |
|---|---|---|
| Corpus | 30 cleaned RBI/SEBI `.txt` files, ~2.0M SmolLM2 tokens (`domain_corpus/`) | This is the RAG document collection. No new data. |
| Eval data | `instruction_dataset_curated.jsonl`: 1,196 pairs with fields `instruction, response, source_document, evidence`. 957 trained on, **239 held out** (Stage 8E, fixed seed) | The 10 queries come from the 239 held-out pairs. `evidence` is a candidate answer span requiring manual sufficiency and corpus-offset verification. Local audit: 1,181/1,196 match after lower-case/whitespace normalization; only 298 match literally. Held-out: 236/239 normalized, 54 literal. Uploaded corpus and Q/A ZIP is now verified identical to this local baseline (see `artifact-verification.json`). |
| Generator | SmolLM2-360M → CPT (ppl 7.67→5.76) → QLoRA (r16, α32, q/v, 4-bit, **max_length 512**, 5 epochs). Saved as `cpt_model/` + `qlora_finance_adapter/` | A 360M model instruction-tuned on short Q/A without retrieved context. Test grounding, citations and abstention; failure is a hypothesis, not a result. |
| Prompt format | Saved tokenizer’s `apply_chat_template`; 1A used a custom user/assistant template with EOS and a separate pad token | Reuse exactly when prompting this model. |

---

## 1. Spec snags to resolve before coding (note them in the notebook)

1. **Chunk sizes disagree in the PDF:** text says *100 and 400*, the table rows say *100 and 500*, and the header has a garbled "(1M)". **Decision:** run **100 and 400** (the text), label the table rows accordingly, and add one line in the notebook noting the PDF discrepancy. Optionally add a 500 row as an extra (it fits a 512-token embedder).
2. **Embedder limit:** `all-MiniLM-L6-v2` truncates at 256 tokens, so 400 would be silently cut. The spec says switch model *or* shrink the size, and state which. **Decision:** switch to `BAAI/bge-small-en-v1.5` (512 tokens, 384-d), keeping 100 and 400 as specified.
3. **Generator context:** your 1A instruction SFT used a 512-token sequence setting. Three 400-token **embedding-tokenizer** chunks exceed that training setting, but generator token counts differ. **512 is the SFT sequence setting, not an architectural limit.** CPT used 1,024-token blocks; upstream SmolLM2 config has `max_position_embeddings=8192`. Read the uploaded checkpoint/tokenizer config and measure the full generator prompt plus output budget. Do not force 512-token inference truncation or predict failure from length alone.
4. **Upload verified (2026-11-07):** `/Users/devb/Downloads/1a-corpus.zip` is byte-for-byte identical to `../assignment-1a/deliverables/deliverables.zip`, including the ZIP itself (SHA-256 `19380e78811a32088cf56ff1b6412942120e4a749781ddb58dcd81d6bbe8d34e`). All 31 entries match relative names, sizes and SHA-256: 30 cleaned texts and a 1,196-row Q/A-only JSONL. No missing, extra or changed files. The texts also match `../_scratch_text/cleaned30/`. Ordered uploaded Q/A pairs match the curated metadata file. Per-file evidence is saved in `artifact-verification.json`; originals were preserved. This verifies corpus/full QA, not absent split or model artifacts.
5. The archive’s `instruction_dataset.jsonl` strips `source_document` and `evidence`. Its ordered Q/A pairs match the local curated file. Join metadata only after verifying this relationship for the uploaded data; prefer actual exported train/eval JSONLs over reconstruction. Model checkpoint and adapter are not in the small deliverables ZIP; inventory them separately on Kubeflow.
6. **Cross-encoder ID (verified 2026-11-09, Stage 0F on the pod):** both `cross-encoder/ms-marco-MiniLM-L-6-v2` (the PDF's spelling) and `cross-encoder/ms-marco-MiniLM-L6-v2` resolve on Hugging Face (about 0.30 GB each). Use the PDF's `L-6-v2` and record the exact revision loaded; an earlier note here calling `L-6-v2` incorrect was wrong.

---

## 2. Design decisions (fixed once, used everywhere)

| Decision | Choice | Rationale |
|---|---|---|
| Embedder | `BAAI/bge-small-en-v1.5`, L2-normalised, query prefix `"Represent this sentence for searching relevant passages: "` | 512-token limit fits both sizes; normalised + `IndexFlatIP` = cosine |
| Index | FAISS `IndexFlatIP` | Exact search; ~20k vectors is trivial |
| Chunking | Fixed-size by **embedder tokens**, no overlap, per document (never across docs). Keep `doc_id, char_start, char_end` per chunk | Matches spec; offsets make span matching and debugging easy |
| Hit definition | Normalised (lower-case, collapsed whitespace) answer span is a substring of the normalised chunk | Explicit matching convention; preserve the original source substring and offsets as well |
| Query set | 10 held-out pairs, frozen in one cell, reused by every part | Comparability across A/B/C/D |
| Randomness | One global seed; generation greedy/`do_sample=False`; judge `temperature=0` | Reproducible for Codex and graders |
| Generator | Try A1 model first; switch only with evidence (D1) | Spec allows a switch only after showing the problem |
| Judge | A model **different from the generator** | Spec requirement; avoids self-grading |

**Operator model preference (2026-11-09; replacement generator and LLM judge):** prefer US-developed models. Primary: `meta-llama/Llama-3.1-8B-Instruct` (Meta); secondary: `microsoft/Phi-3.5-mini-instruct` (Microsoft). Consider a suitable Google Gemma or IBM Granite instruct checkpoint if access, load compatibility or output quality prevents a usable Llama/Phi pairing. Use `Qwen/Qwen2.5-7B-Instruct` only as a last resort after documenting why the feasible US options did not work. DeepSeek is no longer the planned tertiary choice under this updated preference.

The assignment still requires testing the existing 1A generator first. If it succeeds, use Llama as judge, or Phi if Llama is unavailable. If switching is justified, a candidate all-US pairing is Phi generator + Llama judge; the reverse is also possible after output checks. Distinct model IDs are mandatory; neither role is proven suitable until tested for grounding or judge-label quality. Do not download all candidates up front.

Current execution target is **L40S, 47.8 GB total / 39.4 GB free GPU memory, 19.3 GB container RAM** (Stage 0 saved output), rather than assuming the historical A100. Load generation/judge models sequentially, use memory-efficient loading, reserve prompt/output memory, and check actual loading. Freeze exact model/tokenizer revisions when selected.


---

## Stage 0 — Artifact verification, environment and scaffolding (current stage)

**Current boundary:** corpus/full-QA upload comparison has passed (`artifact-verification.json`). Prepare scaffold and use the submitted notebook’s confirmed split procedure and historical checkpoint inventory; check current pod paths and runtime/resources before gate 0 is passed. No additional weight upload is required.

**Learn:** RAG = retrieve → (rerank) → generate with citations → evaluate. Missing evidence limits what a grounded answer can claim.

**Do**
1. Sonnet creates only the introduction, requirements map, and Stage 0 cells in `Group157-Assignment-2b.ipynb`. Explain CPT → instruction SFT → RAG: CPT changes domain-language predictions; SFT trains question/answer behavior; LoRA trains low-rank adapters with frozen base weights; QLoRA adds a quantized frozen base. RAG retrieves evidence at inference time and does not retrain either model. A 1A perplexity improvement does not establish grounded QA quality.
2. Inventory uploaded Kubeflow artifacts against the local baseline: corpus SHA-256 manifest; full and split JSONL counts/schema/Q/A identities; CPT checkpoint, tokenizer and adapter presence/config on the execution pod. If only the small ZIP is uploaded, mark split/model verification pending rather than claim it contains them. Reconcile differences before proceeding.
3. Inspect actual GPU, free VRAM, host RAM, free persistent disk, kernel and installed versions. The 1A setup specifies **16 GiB host RAM and a 15 GiB persistent volume**; these are distinct from GPU VRAM. Reuse compatible packages; add `rank_bm25` and missing dependencies without blindly upgrading the pinned 1A environment. Print and save versions.
4. Check model access and disk budget first. Download only retrieval models when needed; defer generator/judge weights to D. A 4-bit runtime load does not imply a 4-bit download or cache. Record each selected model ID/revision, checkpoint download size, cache location and intended precision. Load large models sequentially; if local storage/access is insufficient, document a feasible different judge model or available remote inference route before D. No requirement to download two 7–8B checkpoints now.
5. Config cell: seed, paths (`domain_corpus/`, `cpt_model/`, `qlora_finance_adapter/`, `instruction_dataset.jsonl`), model names, `TOP_K` constants.
6. Load verified corpus into `docs = {doc_id: text}`; assert 30 docs; save the input manifest and artifact provenance.

**Done when:** uploaded corpus/data verified, model artifacts located (or missing items explicitly resolved), 30 docs load, config/resource/version report printed. Corpus/full-QA comparison passed. Submitted notebook confirms split procedure/counts and historical checkpoint inventory. Stage 0 only needs its notebook setup and current pod path/runtime checks; separate model-weight uploads are unnecessary. 
**Codex gate 0:** uploaded-vs-local comparison reviewed; reproducible configurable paths; seeds set; no missing input silently replaced; model download plan fits actual resources. Operator explains where corpus, QA metadata, CPT weights and adapter live.

---

## Stage 1 — Query set and answer spans (prerequisite for A, B, C)

**Learn:** retrieval is evaluated against ground truth; a span-based "hit" is strict but cheap.

**Do**
1. Prefer verified `instruction_dataset_eval.jsonl` and train export. Reconstruction fallback must replicate Stage 8B/8C validated row order, `random.Random(42).shuffle(records)` and `split_index = round(len(records)*0.80)` exactly (not a generic `train_test_split`). Local ordered Q/A identity matches the curated file; confirm against uploads. Assert 957 train, 239 eval and no exact Q/A overlap. Select 10 unchanged evaluation questions and expected answers; retain original row IDs and QA hashes. Diverse RBI/SEBI documents and question types are desirable, not rubric quotas. Do not require NPCI: no standalone NPCI source is present in the local final corpus.
2. Manually check each expected answer against its source. Use evidence as a starting point, then mark a sufficient sentence/short passage in the original text and record its exact raw substring and character offsets. Normalize whitespace/case for matching with a mapping back to raw offsets; do not assert that all curated strings are literal substrings. A short fragment that fails to support the answer is not a valid answer span. Freeze spans before retrieval; do not shorten or move them to improve hit rates.
3. Show a table: `qid | query | expected answer (response) | answer span | source_document`.
4. Add the **11th "not in corpus" query** now (used in D1.3). Use a clearly out-of-domain factual question, inspect lexical searches and retrieved results across the corpus, and document why it is unanswerable. Absent keywords alone do not establish absence of an answer. Keep this query separate from all out-of-10 metrics; run it through retrieval → reranking → generation in D1.
5. Note lexical bias in the selected evaluation questions when interpreting BM25 results. Keep their original wording for the graded ten; optional paraphrases belong in a separately labelled robustness analysis and never replace the required evaluation queries.

**Record:** the 10-query table (Part A checklist item "answer span marked").
**Done when:** `assert all(span_norm in doc_norm)` passes for all 10.
**Codex gate 1:** exact questions/answers trace to the verified SFT evaluation split; spans are sufficient raw source passages with offsets; all ten are frozen. This prevents exact training-pair reuse; it does not establish unseen facts/documents because CPT and other SFT pairs use the same corpus.

---

## Stage 2 — A1: Dense search function (2 marks)

**Learn:** bi-encoder embeds query and chunk independently → fast semantic relevance scoring. `IndexFlatIP` searches these vectors exactly; this is not an approximate-nearest-neighbor index. Inner product on normalised vectors = cosine.

**Do**
0. Start with a tiny clearly labelled text fixture to demonstrate the search interface; this is a mechanics check, not graded retrieval evidence. Stage 3 supplies the real chunk sets and final A1 facts table.
1. Write `build_dense_index(chunks, model, batch_size)` → returns `(index, embeddings, build_seconds)` and `dense_search(query, k)` → ranked chunk ids + scores. Expose one reusable search interface (class or callable) that builds from any chunk set and returns top-k chunk records for a query; helpers may separate embedding/build/search (1 mark).
2. Report (1 mark): model name, vector size (384), similarity (cosine via normalised IP), batch size (e.g. 64), **index build time for the final chunk set** (embedding + `index.add`, wall clock). Time the final chunk size, not just one trial.

**Record:** a small "A1 facts" table.
**Pitfalls:** prefixing passages as well as queries (apply BGE instruction to queries only); forgetting the query prefix; not normalising; reporting build time for the wrong chunk set.
**Codex gate 2:** function is reusable for any chunk list; normalisation present; timing method stated.

---

## Stage 3 — A2: Chunk size 100 vs 400 (3 marks)

**Learn:** small chunks → precise but fragmented, answers get split; large chunks → more context, more noise and more tokens sent to the generator.

**Do**
1. Chunker on embedder tokens (use `tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)`), windows of N tokens, no overlap, per document; preserve character offsets and stable chunk IDs. Retokenize each stored raw chunk to verify its actual encoder length including special tokens; splitting in the middle of a word can change re-tokenized counts. Log final short chunks and any boundary adjustments. Assert actual length ≤ the loaded encoder limit; do not trust nominal N alone.
2. For each N in {100, 400}: build index, run 10 queries top-3, compute: **total chunks, hit rate@3 (%), tokens sent per query (sum of the top-3 stored chunk token counts without special tokens, averaged)**. State the tokenizer used for counting. Also log how many spans straddle a chunk boundary at each size (explains misses).
3. Fill the table (2 marks). Then 2–3 sentences naming the size for Parts B–D (1 mark), weighing hit rate, tokens/query and generator context. Rule of thumb to decide *from your data*: compare actual hits and embedding-token costs, then inspect full prompts in the generator tokenizer and available context budget. Do not pick a size from a presumed 512-token architectural cap or an anticipated switch.

**Pitfalls:** hit rate has 10% granularity, so don't over-interpret one query; overlapping chunks (spec says none); counting words not tokens.
**Codex gate 3:** token counts use the stated tokenizer; no chunk exceeds the model limit; the decision follows from the table; chunk set saved/frozen as `FINAL_CHUNKS`.

---

## Stage 4 — Part B: Dense vs BM25 vs Hybrid RRF (4 marks)

**Learn:** dense captures meaning, BM25 captures exact terms (regulation names, section numbers, figures). RRF fuses *ranks*, not scores: `RRF(d)=1/(60+r_dense)+1/(60+r_bm25)`.

**Do** (all on `FINAL_CHUNKS`, same 10 queries, return top 5)
1. **Dense row** (1): reuse A1.
2. **BM25 row** (1): `rank_bm25.BM25Okapi` on lower-cased, regex-tokenised chunks (keep numbers; stop-word removal optional but be consistent). 
3. **Hybrid row** (1): take **top 20** from each, rank starting at 1, missing-from-list contributes 0, sum RRF, keep top 5. Dedupe by chunk id.
4. Metrics: avg query latency (ms) = top-5 time per query averaged over 10, after **one discarded warm-up run**; hit@1, hit@3. State what latency includes (query embedding, search, and for hybrid both searches + fusion); exclude model/index loading and cached-query shortcuts. Synchronize CUDA at timing boundaries where needed and record device/batch size. Warm up each method separately. 
5. 2–3 sentences (1 mark): best method, citing **one specific query** (show its top results across methods).

**Minimal RRF skeleton** (use the same deterministic tie policy for all retrieval depths)
```python
def rrf(dense_ids, bm25_ids, k=60, top=5):
    s = {}
    for lst in (dense_ids, bm25_ids):            # each list: top-20, best first
        for r, cid in enumerate(lst, start=1):   # ranks start at 1
            s[cid] = s.get(cid, 0) + 1/(k + r)
    return [c for c,_ in sorted(s.items(), key=lambda x: (-x[1], x[0]))][:top]
```
**Pitfalls:** fusing only top-5 (spec says 20); rank starting at 0; time.time() vs `time.perf_counter()`; including warm-up; ties in RRF (break deterministically).
**Codex gate 4:** RRF formula/ranks/k exactly per spec; top-20 fusion; warm-up skipped; metric code matches the definitions table; unit-test RRF on a hand-computed example.

---

## Stage 5 — Part C: Cross-encoder reranking (4 marks)

**Learn:** a cross-encoder reads (query, chunk) *together* → more accurate but slow, so it is applied only to a short candidate list (bi-encoder/BM25 for recall, cross-encoder for precision).

**Do**
1. Take the **best Part B method** (justify by the numbers), retrieve **top 10**, score with `cross-encoder/ms-marco-MiniLM-L-6-v2` (the PDF's ID; `max_length=512`), keep **top 3** (1 mark). Count the combined query/chunk pair with the cross-encoder tokenizer (different from BGE); log truncation and ensure it does not silently drop evidence. Keep original chunk text for metrics and generation.
2. Show for each of 10 queries the top 3 **before and after** (chunk id + first ~80 chars + hit flag), and compute **rank change rate** = share of queries whose **first** result changes (1 mark).
3. Table (1 mark): reranking time per query (ms, cross-encoder scoring of the 10 candidates only, after warm-up), rank change rate, hit@1 before (from Part B), hit@1 after. Sanity check: "before" must equal the Part B value for the same method.
4. 2–3 sentences (1 mark): did it help? Use before/after hit@1 and added ms. An honest "no gain, +X ms" is a valid answer.

**Pitfalls:** "before" from a different method/top-k than Part B; changing the chunk set; confusing rank change with hit change.
**Codex gate 5:** before/after use the same candidate list; deterministic ranking ensures top-10 retrieval has the same top-1/top-3 prefix as Part B; time excludes retrieval; metric definitions match; conclusion is supported by the numbers. Save the **reranked top-3 per query** (`RERANKED_TOP3`), which feeds Part D.

---

## Stage 6 — D1: Grounded generation (3 marks)

**Learn:** grounding = answer only from supplied context + cite; "abstention" = say "Not found in the documents". Small models often ignore context.

**Do**
1. **Prompt (1 mark)** — show it in the notebook. Wrap in the model's template (`User: … Assistant:` for the A1 model). Skeleton:
```
Answer the question using ONLY the numbered chunks below.
Cite the chunk numbers you used like [1] or [2].
If the chunks do not contain the answer, reply exactly: Not found in the documents

[1] <chunk 1>
[2] <chunk 2>
[3] <chunk 3>

Question: <query>
```
2. **Run the A1 model first** (CPT + adapter loaded as in 1a, same 4-bit setup and saved tokenizer; verify pad/EOS IDs, vocab size and resized embeddings before attaching the adapter), greedy, `max_new_tokens≈150`, 10 queries with reranked top-3 labelled [1]–[3]; show all 10 answers (1 mark). Keep these raw outputs and the exact prompts/token counts; decode only generated continuation tokens. Save all [1]–[3] to chunk-ID mappings. Check citation numbers are valid and inspect whether cited passages support the claims.
3. **Not-found query (1 mark):** run the 11th query through the same pipeline; show the reply. Use the PDF’s exact fallback string `Not found in the documents` consistently in prompt and checks (without adding a required final period).
4. **Switch decision (conditional):** if the A1 model ignores chunks, fails the grounding/abstention requirement, save **one concrete example** of the failure, then switch to a US instruct model using the preference/pairing in §2; Qwen is last resort only. Name the selected model, explain the choice, and rerun 1–3. Load in bf16 (or 4-bit) with `low_cpu_mem_usage=True` on the current L40S; free GPU memory between models and respect the measured 19.3 GB container RAM limit.
5. **Judge/generator separation:** use a different named LLM from the chosen generator. Follow the operator’s US-first model preference in §2; select a feasible judge after checking access, resources and complete judge-prompt context length. Qwen is allowed only if feasible US options fail, with the reason documented. Run sequentially and preserve raw outputs.
6. Check context budget: print prompt token length for each query (3 chunks + instructions) against the uploaded generator configuration’s context capacity, reserving `max_new_tokens`. Record 512 as the SFT setting and 1,024 as CPT block length separately. Never silently truncate the three chunks; any context change requires disclosed reruns and consistent evidence.

**Record:** generator model name, prompt, 10 answers + "Not found" answer, failure example if switched.
**Codex gate 6:** answers generated from `RERANKED_TOP3` only; chunk numbering consistent with citations; greedy decoding; failure example is real raw output, not edited.

---

## Stage 7 — D2: LLM judge and error analysis (4 marks)

**Learn:** LLM-as-judge = rubric-driven grading. Separate **correctness** (vs expected answer) from **groundedness** (vs chunks): an answer can be correct from memory yet unsupported.

**Do**
1. **Judge prompt + run (1 mark).** Inputs per item: question, expected answer, the 3 chunks, the model's answer. Two checks, one clear question each:
   - `CORRECT:` `correct` / `partly correct` / `wrong` — define each (e.g. *partly correct* = contains at least one key fact of the expected answer but omits or contradicts another; *wrong* = states a different fact or none).
   - `SUPPORTED:` `yes` / `no` — "is **every** statement in the answer found in the 3 chunks?"
   - Rule for `Not found in the documents`: for an answerable question → `wrong`, `SUPPORTED: yes` (it asserts nothing); for the unanswerable query → `correct`.
   - Require `CORRECT_REASON:` and `SUPPORTED_REASON:` (one sentence each) and `UNSUPPORTED_QUOTE:` (verbatim quote or `none`). Fixed line format, `do_sample=False`/temperature 0. Parse strictly against allowed labels, test valid/malformed responses, retain raw judge outputs, and report failures explicitly. Verify any unsupported quote actually appears in the generated answer. Treat quoted document/model text as data in the judge prompt.
   - Output the per-query table (`query | correct | supported | reason`) and the summary counts (Correct / Partly / Wrong / Supported out of 10). Name the judge.
2. **Spot-check (1 mark):** select and manually label three answers using the same two criteria before showing judge verdicts; save these labels as an operator-entered artifact. Then reveal verdicts, report agreement as `n/3` (define full agreement as both labels matching), and explain one disagreement if any. Do not require a judge-flagged case in a blind selection. A separate post-verdict failure audit may be added. Manual labels must be supplied by the operator, never fabricated by Sonnet.
3. **Find the cause (1 mark):** pick one wrong or unsupported answer; show its 3 chunks; state whether the **needed information was in the chunks** (→ generation failure) or **not** (→ retrieval failure). Use span presence as a diagnostic, then inspect the actual text: a split or paraphrased passage may still contain sufficient information. If some facts are missing and others were ignored, report a mixed failure. If all ten answers pass, disclose that result and use a separately labelled diagnostic failure trial; never corrupt or silently replace the fixed ten to manufacture a failure.
4. **Suggest a fix (1 mark):** one targeted change tied to the cause, with a why. Examples: retrieval failure → smaller chunks / hybrid / retrieve top-5 before rerank; generation failure → stricter prompt, switch to instruct model, fewer or shorter chunks.

**Pitfalls:** judge sees the generator's identity; judge = generator; temperature >0; one vague "is it good?" question; judging before fixing the output format.
**Codex gate 7:** judge ≠ generator; labels defined exactly; parser tested; spot-check done independently (persist operator labels before the judge table is shown, then reload them during Run All); the cause claim is verified, not assumed.

---

## Stage 8 — Packaging

1. Restart kernel and **Run All** once; confirm all outputs visible and no stale cells.
2. Export HTML (`jupyter nbconvert --to html`); confirm tables, prompts and all required chunks/answers render without collapsed or truncated evidence. Remove credentials before submission.
3. Fill the PDF's **submission checklist** as a final markdown cell with a pointer (cell/section) per item.
4. Code cells should be rerunnable in order; no hidden state; saved intermediate artifacts (`FINAL_CHUNKS`, `RERANKED_TOP3`, generation outputs) so the judge stage can rerun without regenerating. Save these to disk rather than Python variables alone; cache keys must include corpus/query/config/model/prompt hashes. Make Run All regenerate missing outputs or explicitly load matching artifacts; reject stale caches and print provenance. Preserve operator-entered spot-check labels.

**Codex gate 8:** checklist complete; notebook runs top-to-bottom; HTML matches notebook.

---

## 9. Likely outcomes (sanity checks, not targets)

- BM25 may match or beat dense on queries with exact regulation/figure terms; hybrid can improve or worsen measured hits. Don't force the "expected" result; explain what you see.
- Reranking can add little when hit@1 is already high; measure the cost for 10 pairs on the actual device.
- The 360M A1 model may ignore context, omit citations or fail abstention. Test these behaviors and retain evidence; budget a fallback without assuming it will be needed.
- 10 queries = 10-point granularity on every rate; report counts (e.g. "7/10") next to percentages.

---

## 10. Mark-to-stage map

| Marks | Where | Evidence in notebook |
|---|---|---|
| A1 (2) | Stage 2 | function + facts table incl. build time |
| A2 (3) | Stage 3 | chunk table + 2–3 sentence decision |
| B (4) | Stage 4 | 3-row table, best-method paragraph with example |
| C (4) | Stage 5 | before/after top-3, 4-row table, verdict |
| D1 (3) | Stage 6 | prompt, 10 answers, not-found answer, switch evidence |
| D2 (4) | Stage 7 | judge prompt/results/summary, spot-check, cause, fix |

---

## 11. Codex review protocol

**Workflow:** explain → implement current stage only → operator runs → Codex reviews the saved cells, complete outputs, artifacts and claims against the PDF → Sonnet fixes → operator explains result → move on. A commit is optional when a repository is available; this folder currently has no 2B Git repository. Codex needs the actual results to review claims. Model versions, paths and metrics remain unverified until execution evidence is available.

**Gate record per stage:** `not started / implemented, awaiting run / executed, awaiting review / changes requested / passed`; include notebook cell IDs, artifact paths, checks run, defects and next action. No stage is passed from plan text alone. Every stage ends with one operator question testing the concept, not just whether the cell ran.

**Prompt template (per stage)**
> You are reviewing Stage N of Assignment 2B (RAG pipeline) against `IMPLEMENTATION_PLAN.md` and `Assignment 2B - RAG Pipeline.pdf`. Check: (1) every numbered step's requirement is met; (2) metric definitions match the PDF exactly; (3) the same 10 queries, chunk set and top-k are used where required; (4) no leakage or off-by-one in ranks; (5) every written conclusion is supported by the printed numbers. List defects by severity with the cell reference; don't rewrite the code.

**Cross-stage invariants Codex should verify**
1. 10 unchanged questions and expected answers are from the verified 1a SFT evaluation split; sufficient spans exist in corpus; identical across A, B, C, D.
2. Chunks never exceed the embedder limit; token counts use the stated tokenizer; no overlap.
3. Hybrid uses top-20 per method, `k=60`, ranks from 1; hit@1/hit@3 computed per the definitions.
4. Reranking "before" equals Part B's value for the same method; rank change = top-1 changed.
5. Generator input is `RERANKED_TOP3` only; judge ≠ generator; greedy/temperature 0; Not-found handled.
6. Failure example and root-cause analysis come from real saved outputs.
7. Submission checklist fully covered; HTML export present.


## 12. Planning review record and next handoff (2026-11-07)

- **Confirmed against PDF:** 20 marks (A5/B4/C4/D7), 10 evaluation queries and spans, 100/400 no-overlap chunking, top-20 RRF with rank 1 and constant 60, top-10 → reranked top-3, ten generated answers plus one unanswerable query, different judge, manual spot-check, cause/fix, visible notebook outputs and HTML. Page 2 shows 500; pages 1 and 5 say 400. Use 100/400 and disclose discrepancy. Do not interpret the table header “1M” as a one-million-token corpus requirement.
- **Confirmed from saved 1A code/outputs:** SmolLM2-360M; CPT PPL 7.6670 → 5.7551; 1,024-token CPT blocks; 957/239 shuffled split; Adapter B r16/alpha32/q_proj,v_proj; 4-bit NF4; SFT setting 512 and five epochs. This was a static review, not a rerun or a complete correctness audit of 1A.
- **Confirmed locally:** final ZIP and scratch cleaned texts match byte-for-byte; exported Q/A order matches curated metadata; evidence statistics recorded above. **Upload now confirmed:** `1a-corpus.zip` matches the local ZIP and all 31 payload files exactly; see `artifact-verification.json`. **Submitted notebook now reviewed:** code and saved outputs match the local notebook; historical split/counts and checkpoint inventory confirmed. **Remaining:** current pod availability/runtime checks, not additional weight uploads. Uploaded markdown contains stale run summaries (see below).
- **Corrected:** corpus provider assumption, literal-vs-normalized spans, exact split reconstruction, query paraphrasing, 512 context-limit confusion, up-front download/storage assumptions, blind spot-check ordering, and overconfident failure predictions.
- **Next Sonnet action:** Stage 0 only. Prepare concept explanation, configurable inventory/resource cells and comparison manifest; reuse the completed corpus/QA comparison report; finish split provenance and checkpoint/runtime inventory. Stop with printed evidence for Codex gate 0. Do not start retrieval or training yet.

Reference checks (official primary sources; runtime configs remain authoritative): [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5) documents 384 dimensions, 512-token sequence length, query instruction and normalized embeddings; [SmolLM2 config](https://huggingface.co/HuggingFaceTB/SmolLM2-360M/blob/main/config.json) gives the upstream 8,192-position limit; [cross-encoder model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) (the PDF's ID; the `L6-v2` spelling also resolves). Recheck loaded revisions in the notebook.


### Submitted Kubeflow notebook clarification (2026-11-07)

`/Users/devb/Downloads/Group157-Assignment-1a.ipynb` has 149 cells. It is not byte-identical to the local notebook, but all code-cell sources, saved outputs and execution counts match. Differences are confined to 43 markdown cells. Treat the operator-supplied file as the submitted-run reference and preserve it unchanged.

Saved outputs establish the historical run: Stage 8E has 1,196 total / 957 training / 239 evaluation examples; Stage 11A reports both splits, CPT and adapter present; Stage 11B lists `/home/group157/cpt_model` (8 files, about 1.4 GB) and `/home/group157/qlora_finance_adapter` (8 files, about 10.8 MB). GPU output records A100-SXM4-80GB and PyTorch 2.5.1+cu124. Use the saved split procedure with the verified ordered dataset if exported splits are unavailable; read exports directly when present. These outputs are sufficient historical evidence for planning; do not require model uploads or retraining.

**Documentation discrepancy:** uploaded markdown cell 99 says 711 / 569 / 142 while execution cell 98 says 1,196 / 957 / 239; markdown cell 143 says 18 docs and 41 / 33 / 8 pairs while execution cell 142 says 30 docs and 1,196 / 957 / 239. Final markdown cell 148 also describes an older run with outdated PPL values. Cell numbers here are zero-based. For 2B, carry forward the saved execution evidence, not these stale prose figures. Full code/output comparison and examples are recorded in `artifact-verification.json`.

**Sonnet next:** finish Stage 0 using this evidence. On the current pod, print existence of corpus, split, CPT and adapter paths and inspect resources. This is a routine reuse check, not a request for further artifact uploads. Keep submitted 1A notebook unchanged; do not rerun training for verification.


### PV location confirmed by operator (2026-11-07)

Operator confirms the prior artifacts exist on the mounted persistent volume, with repository name `llm-assignment-1a-finance-corpus`. The provided notation `llm-assignment-1a-finance-corpus//home/group157/` appears to combine the repository/UI location and mount path; do not encode it as a literal filesystem path. The executed notebook records `/home/group157` as its working directory and artifact root. Start with configurable `ARTIFACT_ROOT = Path("/home/group157")`; locate the repository independently and print `resolve()` results for both. If the current layout differs, adjust configuration from the printed directory inventory without relocating or overwriting artifacts.

Corpus/split/model persistence is now operator-confirmed. No additional uploads are required for planning. Sonnet can implement Stage 0 immediately; existence checks and runtime/resource output are routine setup evidence, not a further prerequisite imposed on the operator before implementation.
