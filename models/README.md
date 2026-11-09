# models/

- `qlora_finance_adapter/` : the 1A QLoRA adapter and tokenizer (LoRA r=16, alpha=32, q_proj/v_proj), committed here (about 11 MB).
- `MANIFEST.sha256` : SHA-256 of the adapter files **and of the CPT model files** (`cpt_model/model.safetensors` is 1.45 GB,
  too large for git, so it is not committed). Stage 0D compares the CPT weights on the Kubeflow volume with these hashes.

CPT model locations: Kubeflow volume `/home/group157/cpt_model`, and the operator's local `~/Downloads/asst1-archive/cpt_model`.
