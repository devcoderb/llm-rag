# Stage 4 review — 2026-11-09

**Verdict: PASS. Proceed to Stage 5 only.**
Reviewed commit `4268274`, cells 29–32 / Stage 4A–4D. Code and saved Kubeflow outputs reviewed; GPU retrieval/latency were not rerun locally. No blocking defects found.

## Part B results

| Method | Hit@1 | Hit@3 | Mean latency, ten-query pass |
|---|---:|---:|---:|
| Dense | 4/10 (40%) | 7/10 (70%) | 5.47 ms |
| BM25 | 3/10 (30%) | 7/10 (70%) | 12.07 ms |
| Hybrid RRF | 4/10 (40%) | 6/10 (60%) | 19.53 ms |

**Chosen method: Dense.** It ties BM25 at hit@3, has higher hit@1 and lower measured latency. Hybrid provides no gain on this set. Q04 evidence supports the explanation: gold dense rank 2, outside BM25 top20; RRF contribution 1/62 = 0.01613 and hybrid rank below 5.

## Verified

- All four Stage 4 cells have saved successful outputs (execution 23–26); code parses.
- Saved outputs confirm all 11 Stage 3 artifact hashes, final 4,065 chunks, embedder revision and frozen query provenance match. Verified loader rechecks hashes before loading.
- Gap follow-up completed: all six excluded characters in the final 400-token set are control codes; none lies inside a frozen span. The 100-token diagnostic also identifies format/private-use characters. Preserve this qualified observation rather than treating all Unicode control/format/private-use categories as universally meaningless.
- BM25 tokenization/stop-word handling is consistent between chunks and queries, with numeric tokens kept and a documented positive-score-only policy.
- Hybrid fetches top20 per input and fuses ranks starting at 1, constant 60, zero missing-list contribution and deterministic positional tie-breaking; top5 cut follows fusion.
- Independently executed the actual pure-Python RRF function: hand scores, ties, missing input and empty-list checks pass.
- Independently recomputed all three hit@1/hit@3 counts from the printed per-query gold-rank table; they match the summary. Dense hit@3 matches Stage 3 (7/10).
- Timing code discards a warm-up for each method and includes actual query encoding/search/fusion with CUDA synchronization. The required ten-query-pass mean is printed separately from five-pass descriptive timing; model/index/BM25 building is excluded.
- Q04 worked example and best-method choice follow actual rankings and scores. Stage 4 JSON records metrics, results, chosen method, tokenizer/RRF settings and provenance; saved-file write is evidenced, artifact itself remains on PV.
- Frozen Stage 1 content hash independently revalidated unchanged: `99eac52609fbde845b59fa30014d4cdd91457814b77443c0dd0c63b547882e0e`.

## Stage 5 handoff

Part C only: use Dense top10 candidates from the same saved chunks and ten queries. Confirm its pre-rerank top1/top3 agrees with Part B; baseline hit@1 is 4/10 (40%). Load the configured cross-encoder, record exact model/revision and joint query+chunk token lengths, rerank top10 to top3. Show all ten before/after top3; compute first-result change rate and hit@1 after. Time cross-encoder scoring only after a warm-up, excluding retrieval/model load; save candidates, scores, top3 and provenance. Report an honest gain/no-gain conclusion. No generation or judge implementation yet.
