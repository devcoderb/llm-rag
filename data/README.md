# data/

Frozen copy of the Assignment 1A text data (verified byte-identical to the submitted 1A deliverables and the Kubeflow run).
`MANIFEST.sha256` lists a SHA-256 for every file; the notebook's Stage 0C re-checks it on every run.

- `corpus/` : 30 cleaned RBI / SEBI `.txt` files (the RAG document collection)
- `qa/instruction_dataset.jsonl` : 1,196 Q/A pairs as submitted in 1A (`instruction`, `response`)
- `qa/instruction_dataset_curated.jsonl` : same pairs in the same order, plus `source_document` and `evidence`
- `qa/instruction_dataset_train.jsonl` / `instruction_dataset_eval.jsonl` : the 1A split (957 / 239), exported by the 1A run.
  It is reproduced exactly by `random.Random(42).shuffle` on the full file, then `round(len*0.80)` for the split index.

Do not edit these files. If one must change, regenerate `MANIFEST.sha256` and say why in the commit message.
