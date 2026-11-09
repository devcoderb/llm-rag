# llm-rag: Assignment 2B (RAG pipeline), Group 157

Domain: Indian financial markets and digital payments (RBI / SEBI). Notebook: `Group157-Assignment-2b.ipynb`.
Plan and review gates: `implementation_plan.md`.

## Setup on Kubeflow (once per pod)

```bash
cd /home/group157
git clone https://github.com/devcoderb/llm-rag.git          # or: git -C llm-rag pull
bash llm-rag/kubeflow/setup_env.sh                           # creates venv-rag, registers kernel "Python (RAG venv)"
/home/group157/venv-rag/bin/python llm-rag/kubeflow/check_env.py
```

Then open `llm-rag/Group157-Assignment-2b.ipynb`, choose Kernel -> Change Kernel -> **Python (RAG venv)**, and run the cells in order.

The CPT model (1.45 GB) is not in git. The notebook looks for it at `$CPT_DIR`, then
`/home/group157/model-backups/cpt_model_1a`, then `/home/group157/cpt_model`, and verifies it against `models/MANIFEST.sha256`.

## Layout

| Path | Content |
|---|---|
| `data/` | frozen 1A corpus (30 texts) and Q/A files incl. the 957/239 split, with `MANIFEST.sha256` |
| `models/` | 1A QLoRA adapter and `MANIFEST.sha256` (also lists the CPT weight hashes) |
| `kubeflow/` | `setup_env.sh`, `check_env.py`, `requirements.txt` (the direct dependencies, single source of pins) |
| `assignment_2b_outputs/` | generated at run time on the volume (not in git) |
