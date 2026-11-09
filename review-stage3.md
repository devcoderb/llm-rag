# Stage 3 review — 2026-11-09

**Verdict: PASS. Proceed to Stage 4 only.**
Reviewed executed commit `d86ccaa` plus local `5aa1192` (Stage 3B progress text only). Local branch is one commit ahead of origin/main after fetch; no computation changed after the saved run. Scope: cells 23–27, Stage 3A–3E. No blocking defect in the comparison or 400-token choice.

## Results

| Size | Chunks | Hit@3 | Mean top-3 embedder tokens | Split source spans | Build time |
|---|---:|---:|---:|---:|---:|
| 100 | 16,214 | 2/10 (20%) | 300.0 | 5/10 | 5.36 s |
| 400 | 4,065 | 7/10 (70%) | 1,200.0 | 0/10 | 5.75 s |

Chosen size: **400**. Five additional hits justify the fourfold retrieval-token cost on this fixed sample. Mean/max provisional generator prompt: 1,584.5/1,675 tokens, below the configured 8,192 positions. This establishes capacity headroom, not grounding competence beyond the 512-token SFT setting.

## Verified

- All five code cells executed (17–21) with saved outputs, no errors; all parse.
- Fixed token windows within documents, no overlapping raw ranges, stable unique IDs/raw offsets; all 30 documents represented. Per-document printed chunk counts sum independently to 16,214/4,065.
- Re-tokenized stored chunks fit the encoder: maxima including specials 104/404 <= 512. Tokenizer revision matches Stage 2.
- Hit computation uses whole frozen spans with the same normalized substring rule; reported split spans are not shortened. Top-3 totals use actual stored-chunk tokenizer lengths without specials.
- Stage 1 frozen hash independently remains `99eac52609fbde845b59fa30014d4cdd91457814b77443c0dd0c63b547882e0e`.
- Model/fixture load time excluded from actual full-corpus build times; final A1 facts and reasoned A2 choice are printed.
- Tie handling and duplicate-ID guard added. Saved reload test reproduces top-3 IDs/scores for all ten queries at chosen size, despite initial evaluation requesting top 20.
- Outputs report saved chunks/indexes/embeddings/results/config/summary and an SHA-256 manifest; FINAL_CHUNKS has 4,065 records.

Limits: GPU embedding/search were not rerun locally; dense result JSON/embeddings/indexes remain on the PV and were not independently retrieved. Retrieval values and reload assertions are reviewed from code and saved execution evidence.

## Follow-ups during Stage 4 setup

1. `load_dense_searcher` currently checks dimensions/counts/IDs, but does not verify `stage3_manifest.sha256`. Validate relevant file hashes and frozen query/model provenance before reuse; keep the final 400-token set unchanged. Do not require rebuilding if the saved files verify.
2. Chunk-gap diagnostics report 22/6 uncovered non-whitespace characters (100/400). Print their escaped values and a few source locations to establish whether they are tokenizer-ignored characters or meaningful text. The current outputs do not establish why. Do not describe corpus coverage as lossless. If meaningful text or any frozen span is affected, stop and correct/re-review chunking before B; otherwise record the diagnostic without changing frozen inputs.
3. Stage 6 must count the actual chat-formatted prompt plus requested output tokens. Current provisional check omits output reserve, but has over 6,500 tokens of position headroom, so the 400-token choice is unaffected.

## Next stage

Part B on unchanged FINAL_CHUNKS and ten queries: Dense/BM25/Hybrid top 5; RRF top 20 per input, rank starts at 1, constant 60, missing-list contribution zero. Report mean query latency with one discarded warm-up per method and hit@1/hit@3. Include query embedding/search/fusion as appropriate; exclude model/index build/load. Explain the best method with one actual query. No reranking/generation yet.
