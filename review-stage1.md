# Stage 1 review — 2026-11-09

**Verdict: PASS. Proceed to Stage 2 only.**
Reviewed executed notebook commit `1d74918`, cells 13–16 (Stage 1A–1D), and `eval/query_set_frozen.json`. Local HEAD matches origin/main. No blocking defects found.

## Verified

- All four Stage 1 cells have saved outputs (execution counts 16–19), without errors.
- Exact ordered reproduction of the 1A split: 957 training / 239 evaluation pairs.
- Q01–Q10 are unchanged evaluation-only Q/A pairs, from ten distinct documents (six RBI, four SEBI).
- Original row IDs, evaluation positions, Q/A hashes and document hashes match independently.
- Each raw span occurs once, matches its saved character offsets and normalizes to the saved span. Source passages and surrounding text support the full expected answers for all ten queries.
- Q08 correctly selects the general fifty-crore AMC provision; preserve its frozen span when comparing near-miss retrieval results.
- U01 is separate from the ten. Saved scans and lexical inspection support its use as an unanswerable sports question; inspect actual retrieved context again in D1.3. Keyword absence alone is not a general proof.
- Frozen content and source-file hashes verify independently. Freeze SHA-256: `99eac52609fbde845b59fa30014d4cdd91457814b77443c0dd0c63b547882e0e`.

## Notebook wording

Shorten Stage 1 markdown to assignment facts: unchanged ten evaluation questions, source spans/offsets, fixed hit rule, split limitation and separate U01. Remove first-person narration such as “I read” and avoid unsupported claims that selected passages are the shortest possible. Keep the printed query/answer/span evidence intact. This editorial change does not require changing the frozen query set or rerunning its selection.

## Stage 2 handoff

Build reusable dense search only: configured BGE embedder/tokenizer, query-only prefix, normalized float32 vectors, FAISS IndexFlatIP, deterministic ranked chunk IDs/scores/text and configurable top-k. Record actual model revision, vector dimension, encoder limit, device and batch size. Demonstrate on a small labelled fixture and check normalization, ranking and k bounds. Fixture timing is not the graded final-corpus build time; Stage 3 supplies 100/400 chunks and final A1 facts. Preserve Stage 0/1 and frozen inputs; do not implement chunk-size experiments, BM25, RRF or reranking yet.
