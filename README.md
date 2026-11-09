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

## Adding a package later

1. Add it to `kubeflow/requirements.txt` (with a short comment on why it is needed).
2. Install it: re-run `bash kubeflow/setup_env.sh` in a terminal, **or** use the optional install cell in the notebook
   (Stage 0B-install: set `INSTALL_MISSING = True`, list the package in `EXTRA_PACKAGES`, run, restart the kernel).
3. `python kubeflow/check_env.py` now verifies it too, because it reads the same file.

Both routes install into the same `venv-rag` on the volume, so the package persists. The terminal route is preferred because it
keeps `requirements.txt`, the venv and `check_env.py` consistent.

## Layout

| Path | Content |
|---|---|
| `data/` | frozen 1A corpus (30 texts) and Q/A files incl. the 957/239 split, with `MANIFEST.sha256` |
| `models/` | 1A QLoRA adapter and `MANIFEST.sha256` (also lists the CPT weight hashes) |
| `kubeflow/` | `setup_env.sh`, `check_env.py`, `requirements.txt` (the direct dependencies, single source of pins) |
| `assignment_2b_outputs/` | generated at run time on the volume (not in git) |
