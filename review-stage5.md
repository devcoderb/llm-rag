# Stage 5 review — 2026-11-09

**Verdict: PASS, with one conclusion-wording correction. Proceed to Stage 6 only.**
Reviewed commit `9aa5de8`, cells 34–38 / Stage 5A–5E, code and saved Kubeflow outputs. No blocking implementation defect in this executed run. GPU scoring was not rerun locally; saved JSON/index files on PV were not independently retrieved.

## Part C results

| Measure | Result |
|---|---:|
| Hit@1 before / after | 4/10 (40%) → 5/10 (50%) |
| Hit@3 before / after | 7/10 (70%) → 5/10 (50%) |
| First-result change rate | 7/10 (70%) |
| Cross-encoder scoring time | 11.8 ms/query |
| Dense top10 retrieval, separate | 5.2 ms/query |
| Candidate span coverage | 8/10 |

Reranking improves first-position accuracy by one query but reduces the chance of evidence appearing anywhere in the three passages sent to generation. Q04/Q05/Q09 gain at rank1; Q01/Q08 lose. Continue using reranked top3 as required by D1; do not replace them with Dense results to improve Part D outcomes.

## Verified

- Five cells executed 26–30, saved outputs present, no errors; code parses.
- All ten candidate lists contain ten Dense chunks. Their top5 IDs/scores and baseline hit@1/@3 match Part B on the same final chunk set.
- Loaded cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2`, revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`, identity activation, CUDA, batch10.
- All 100 joint query/chunk pairs fit without truncation: 424–440 tokens <=512. Original chunk texts remain unchanged.
- Reranking sorts all ten scores descending with Dense-rank tie-break, returns candidates only and checks finite scores.
- All-ten before/after top3 IDs, score/snippet/hit flags are printed. Independently counted hit@1 4→5, hit@3 7→5, seven changed first results, three gains/two losses from those printed records.
- Warmed cross-encoder timing includes tokenization/scoring only; retrieval/model load excluded and CUDA synchronized. First ten-query pass reported separately from five-pass timing.
- Saved candidate scores, length checks, results, original top3 text and provenance. Reload asserts exact equality, three chunks per query and identity with original chunk text.
- Frozen Stage 1 content hash independently unchanged: `99eac52609fbde845b59fa30014d4cdd91457814b77443c0dd0c63b547882e0e`.

## Wording correction

Cell 37 (`ce66dd08`) constructs “Reranking raised hit@1 ... and hit@3 from 7/10 to 5/10”. Use separate verbs: **“Reranking raised hit@1 from 40% to 50%, but lowered hit@3 from 70% to 50%, adding 11.8 ms/query.”** Save this corrected conclusion in the result artifact as well; preserve scores/rankings/metrics. No model-scoring rerun is needed for an editorial correction; rerun the relevant reporting/save cells and regenerate their hashes consistently.

## Stage 6 handoff

D1 only. Load verified reranked top3; apply saved 1A tokenizer/chat template and compatible CPT+adapter loading (check vocab/pad/EOS and embeddings). Count actual formatted prompt plus generation reserve against context capacity. Generate ten answers greedily with numbered citations and exact abstention string “Not found in the documents”. Retrieve/rerank U01 separately through the same Dense-top10/CE-top3 pipeline and test abstention; keep it outside ten-query metrics. Preserve exact prompts, numbered chunk mappings, IDs/revisions/config and raw continuation-only outputs. Test 1A first; only a documented grounding/abstention failure permits the fallback, following US-first/Llama/Phi policy and Qwen last resort. Do not implement judge stage yet.
