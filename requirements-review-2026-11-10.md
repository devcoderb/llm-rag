# Assignment 2B and notice-board requirements review

Reviewed 2026-11-10 against main commit `08a41b0`, its executed notebook, the local Assignment 2B PDF, Assignment 1A PDF B1, and the user-supplied notice-board text. The notice-board text's publication date and retrospective scope are not independently established. This report belongs on `codex/review-history`, outside the submitted notebook.

## Assessment

The 2B pipeline and required evidence are present. Parts A–C meet the checked implementation/reporting requirements. D1 was executed, including the required 1A baseline, documented switch and successful U01 test, but all-answer citation/abstention behaviour is not met. D2 evidence is complete; its judge is demonstrably fallible and the notebook discloses that. This is not a prediction of marks.

The additional dataset notice is not fully met or evidenced. Existing 1A artifacts must not be described as retrospectively corrected. No data, model, query, answer or verdict was changed by this review.

## Assignment PDF cross-check

| Requirement | Evidence | Assessment |
|---|---|---|
| One notebook, cleaned 1A texts, ten original evaluation questions/answers, original fine-tuned generator trial | Stages 0–1; 30 documents, ten unchanged held-out Q/A pairs; Stage 6 uses CPT + QLoRA first | Evidence present |
| Answer passages marked; embedding limit and tokenizer recorded | Stage 1 stores raw passages and character offsets; BGE tokenizer and 512-token encoder limit recorded | Met |
| A1 reusable dense search, model/vector/similarity/batch/build-time facts | Stage 2 build/search interface and fixture checks; Stage 3D final-corpus facts | Met; latest printed 400-token build time is 5.97 s |
| A2 fixed-size 100/400-token chunks, no overlap; chunk count, hit@3, top-three token totals, justified choice | Stages 3A–3E; 16,214 versus 4,065 chunks, hit@3 2/10 versus 7/10, mean top-three tokens 300 versus 1,200; generator budget checked | Met |
| A2 PDF wording inconsistency | Page 1 and submission checklist say 100/400; an intermediate table says 100/500 | 100/400 follows the explicit task and checklist; no new chunk-size change needed |
| B Dense/BM25/Hybrid, top five; RRF over top 20 each, constant 60, ranks from 1; hit rates/latency and reasoned choice | Stage 4 outputs and selected Dense method; warm-up excluded | Met |
| C best-method top ten, cross-encoder top three, per-query before/after, rank change/time/hit@1 and explanation | Stage 5; first-result change 70%, hit@1 40%→50%, hit@3 70%→50%, added 10.6 ms/query | Met; mixed result reported rather than hidden |
| D1 grounded prompt shown and ten answers generated from numbered reranked passages | Stages 6C–6D and 6H | Executed; behaviour not fully met |
| D1 out-of-domain question and abstention | U01 exact output `Not found in the documents` from Phi | Met for the selected generator; baseline failure preserved |
| D1 model switch permitted after a baseline failure, name and concrete example shown | Original model: 0/10 numbered citations and invented U01 answer; Llama access failed; Phi trial and comparison retained | Met; PDF model names are examples, so Phi is allowed |
| D1 every answer obeys grounding/citation/abstention instructions | Q03 cites nonexistent [5]; Q06 does not abstain; Q01/Q07/Q10 use extra wording instead of the exact fallback | Not fully met; five strict-check failures are disclosed. Grounding also needs content inspection, not citation-number checks alone |
| D2 distinct judge, explicit correctness/support rubric, deterministic decoding; prompt, ten verdict rows and summary | Tulu judge versus Phi generator; Stage 7A–7C, greedy decoding | Required evidence present |
| D2 three manual spot-checks and disagreement explanation | Q02/Q06/Q08; 1/3 agreement; Q06/Q08 explanations saved | Met; agreement is a measured result, not a pass target |
| D2 failed answer, all three chunks, cause and proposed fix | Q06 in 7E; source chunk Dense rank 102, BM25 rank 7; retrieval and generation causes; union-of-candidates and quote-first prompt proposed | Met; fixes are proposals, not executed improvements |
| Notebook with saved outputs and HTML of the same notebook | No saved error outputs; HTML regenerated after the latest main edits | Present; a clean, complete fresh-volume Run All has not been independently demonstrated by this review |

The PDF does not require high retrieval accuracy, perfect judge calibration or implementation of the proposed D2 fix. Low scores can be valid findings. It does require showing the work, explaining the result and not treating execution gates as proof of answer quality. D1's explicit U01 requirement passes for Phi; the broader generation instructions still have failures.

## Additional notice-board rules

| Rule supplied by the user | Current evidence | Status |
|---|---|---|
| Reuse cleaned documents, ten evaluation Q/A pairs and fine-tuned model; no new collection | Verified repository artifacts and executed baseline | Met |
| Minimum 40–50 quality JSONL pairs | 1,196 rows, 957 train / 239 eval | Count met; count alone does not establish quality |
| Spot-check 10–15 random pairs | No pre-training review recorded. Independent audit sample stored (12 train / 3 eval); auditor reading is not a recorded user review. Earlier seed-42 sample is coupled to split construction and all eval | Historical review not evidenced; user review remains to be recorded |
| Concise answers in own words, not lifted text | Sentence heuristic gives 1–3 sentences; 22 whole-response source matches and 107 high-overlap responses flagged | Sentence-length screen passes; own-words compliance not established. Inspect flagged answers; copying scores alone do not establish authorship |
| Genuine factual/procedural/comparative variety across source documents | All 30 sources have pairs; automatic type labels have false positives | Not verified; manual type review needed. The notice does not clearly require every type in every document |
| If LLM-generated, include exact 1–3-sentence/own-words instruction in the generation prompt | Human versus LLM provenance not established; no actual prompt retained in available artifacts | Conditional requirement not evidenced; record the real method, do not invent a historical prompt |
| Minimum response-length filter, at least 30 words | No filter recorded; 758/1,196 below 30 words, including 589/957 training answers and eight frozen evaluation answers | Not met |
| Flag any single template above 20% | No defined template grouping or detector in the original pipeline. Opening “Under …” is 49.5%; masked short-prefix heuristic max is 2.5% | Required check not implemented; actual template compliance unverified. Neither percentage alone proves semantic repetition or its absence |
| Avoid 2–3 phrasings cycling across hundreds of pairs | Surface wording measurements cannot establish semantic variety | Not verified |

The PDF and notice differ: the 1A PDF asks for a suitable dataset size, corpus-derived responses, an 80/20 split and an exact generation prompt if an LLM was used. It does not specify the notice's fixed pair minimum, 30-word minimum or 20% template flag. The 2B PDF requires reusing the historical artifacts. Whether the additional notice applies retrospectively needs faculty clarification; applicability uncertainty does not turn a measured gap into compliance.

## Independent checks in this review

- All 34 data files match `data/MANIFEST.sha256`; all eight repository adapter files match `models/MANIFEST.sha256`.
- The eight external CPT files are absent on this Mac; their current PV hashes were not rechecked. The notebook preserves prior executed verification.
- Recomputed 1,196 pairs, 758 responses below 30 words, and 22 normalised whole-response source matches from the current files. Remaining audit measurements are retained from the archived reproducible report; they are not presented as newly recomputed here.
- Reviewed actual saved outputs for chunk selection, reranking, Stage 6 gate and final Stage 7 gate. No training, inference, raw-label editing or fresh Kubeflow run.

## Completion and next actions

1. Add a concise conclusion to the notebook: completed pipeline, main retrieval trade-off, documented generator switch, remaining D1 failures and indicative D2 findings. Keep this notice review outside the notebook as requested.
2. Supply a shareable original CPT checkpoint URL; README still marks it missing. Public repository visibility alone does not make a full rerun possible without that checkpoint.
3. If needed, record a new user review of an independently drawn sample, real generation provenance, manual question types and a defined template rule. A review today does not prove pre-training checks happened.
4. Ask faculty about retrospective applicability before deciding to rebuild data. Do not silently expand frozen answers, change splits or retrain. A new validator or conclusion does not fix the missing historical length filter.
5. If corrections to training data are explicitly required, identify affected artifacts first: adapter retraining may be necessary; unchanged corpus does not require repeating CPT, and unchanged retrieval inputs do not require repeating retrieval experiments.
