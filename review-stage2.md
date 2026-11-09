# Stage 2 review — 2026-11-09

**Verdict: PASS. Proceed to Stage 3 only.**
Reviewed commit `db6603e` (HEAD matches origin/main), notebook cells 18–21 / Stage 2A–2D. No blocking defects found. Review covers code and saved Kubeflow results; GPU inference was not rerun locally.

## Verified

- All four cells executed (32–35), with saved outputs and no errors; code parses.
- BGE revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, dimension 384, encoder/tokenizer limit 512, CUDA, batch size 64 recorded.
- Passages are unprefixed; queries receive the BGE instruction. Both encodings are normalized, contiguous float32 arrays.
- Reusable DenseSearcher exposes build/search, returns original records plus ranks/scores, validates positive integer k and caps k at corpus size.
- FAISS IndexFlatIP uses exact inner product; normalized embeddings make it cosine similarity.
- Saved checks compare scores to brute-force dot products, verify sorted/repeated results, normalization and top-k bounds. Fixture retrieval: top-1 and top-3 both 6/6.
- Fixture build time 526.5 ms is clearly labelled as fixture-only; final-corpus A1 build time is still due in Stage 3.
- Stage 1 frozen content hash independently revalidated unchanged: `99eac52609fbde845b59fa30014d4cdd91457814b77443c0dd0c63b547882e0e`.

## Stage 3 requirements

- Use fixed-size 100/400 embedder-token windows, no overlap, within documents; retain stable unique IDs and raw offsets. Verify actual stored encoder inputs fit 512 including special tokens.
- Preserve frozen ten queries and sufficient spans; report any span split across boundaries without changing the span.
- Compare total chunks, hit@3 counts/percent and mean top-3 token totals using the embedding tokenizer. Use the same normalization as the frozen hit rule.
- Report actual full-corpus embedding + index-build times; keep model-load time and fixture time separate. State the final A1 facts for the chosen size.
- Choose the B–D size from measured results and generator-tokenized context budget; 512 is SFT training length, not the model architectural limit.
- Save chunks, indexes/embeddings, results and provenance/revision/config so later stages reuse the same inputs. Guard duplicate IDs and use a stable tie policy before cross-stage comparisons; the untied fixture does not establish tie behavior.
- No BM25, RRF, cross-encoder or generation implementation yet.
