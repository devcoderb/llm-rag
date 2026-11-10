# llm-rag: Assignment 2B (RAG pipeline), Group 157

Domain: Indian financial markets and digital payments (RBI / SEBI). Deliverables: `Group157-Assignment-2b.ipynb` (all outputs saved) and `Group157-Assignment-2b.html` (the same notebook exported to HTML).

## Reviewing the submission (no GPU needed)

Open `Group157-Assignment-2b.html`, or the notebook, and read it top to bottom. Every stage shows its code, its saved output and an observation. Section order follows the assignment: Setup, Part A (spans, A1, A2), Part B, Part C, Part D (D1 grounded answers, D2 LLM judge), then the submission checklist. The "Models used" table near the top lists every model and why it was chosen.

Two extra items sit outside the graded flow and are kept separate on purpose:

| Path | Content |
|---|---|
| `audit/Group157-Assignment-2b-judge-audit.ipynb` | executed cells of the earlier judge attempts and the original judge run, with their saved outputs (summarised in the appendix of D2) |

## Re-running the notebook and getting the model artifacts

Everything below is only needed to re-run cells. You do not need the operator's Kubeflow volume.

**What is in this repository**

- `data/`: the frozen 1A corpus (30 texts) and Q/A files, including the 957/239 split, with `MANIFEST.sha256`. Stage 0C verifies them.
- `models/qlora_finance_adapter/`: the 1A QLoRA adapter and tokenizer (about 11 MB). `models/MANIFEST.sha256` holds its hashes and the hashes of the CPT checkpoint. Stage 0D verifies them.
- `eval/query_set_frozen.json`: the ten frozen questions, answer spans and the unanswerable query U01.

**Models downloaded automatically from Hugging Face** (public, no token needed; the notebook records each revision):

| Model | Used in |
|---|---|
| `BAAI/bge-small-en-v1.5` | Stages 2 to 5 |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Stage 5 |
| `microsoft/Phi-3.5-mini-instruct` (revision 2fe1924501) | Stage 6 fallback generator |
| `allenai/Llama-3.1-Tulu-3-8B` | Stage 7 judge |

`meta-llama/Llama-3.1-8B-Instruct` is gated. The notebook tries it first in Stage 6 and falls back to Phi when access is refused, so no access request is required.

**Not in git: the continued-pretraining (CPT) checkpoint.** The 1A baseline trial in Stage 6 (6A to 6E) loads the CPT model plus the adapter. The CPT folder has 8 files; `model.safetensors` is about 1.4 GB, too large for git. To obtain it:

1. Download the checkpoint published by Group 157 (location: see the line below) and unpack it so that its 8 files sit in one folder.
2. Put that folder at `~/model-backups/cpt_model_1a` or `~/cpt_model`, or point `CPT_DIR` at it before starting Jupyter.
3. Run Stage 0D. It compares the 8 files with `models/MANIFEST.sha256`. All must match; a re-trained CPT model will not be byte-identical and will be reported as changed.

CPT checkpoint location: `(to be filled in by Group 157 at submission: a Hugging Face model repository or release asset URL)`

Without the checkpoint, Stage 6A to 6E cannot be re-run. The saved baseline output in the notebook and HTML is the record of that trial, and Stage 6F onward reads the baseline output that 6E writes.

**Generated at run time.** The notebook writes its intermediate files to `/home/<user>/assignment_2b_outputs/` (not in git). Later runs reuse a saved file only when its hashes match and otherwise regenerate it. Stage 7B asks for three hand-checked answers and saves them in `stage7/final/manual_spotcheck.json`; a fresh run therefore asks for new labels, and the submitted labels are in the saved output.

## Setup on Kubeflow (once per pod)

```bash
cd /home/group157
git clone https://github.com/devcoderb/llm-rag.git          # or: git -C llm-rag pull
bash llm-rag/kubeflow/setup_env.sh                           # creates venv-rag, registers kernel "Python (RAG venv)"
/home/group157/venv-rag/bin/python llm-rag/kubeflow/check_env.py
```

Then open `llm-rag/Group157-Assignment-2b.ipynb`, choose Kernel -> Change Kernel -> **Python (RAG venv)**, and run the cells in order.

To add a package, add it to `kubeflow/requirements.txt` with a short comment, re-run `bash kubeflow/setup_env.sh`, and re-run `kubeflow/check_env.py` (it reads the same file).

## Final run and export (operator)

1. On the volume: `bash kubeflow/migrate_stage7_names.sh` (moves the Stage 7 files to the final names `stage7/final/` and `stage7/audit/`; nothing is deleted).
2. Pull the repository, close any open copy of the notebook without saving, reopen it, choose Restart Kernel and Run All.
3. Check that no cell shows an error, then export: `jupyter nbconvert --to html Group157-Assignment-2b.ipynb`.
4. Commit and push the notebook and the HTML.

## Layout

| Path | Content |
|---|---|
| `Group157-Assignment-2b.ipynb`, `.html` | the deliverables |
| `data/` | frozen 1A corpus (30 texts) and Q/A files incl. the 957/239 split, with `MANIFEST.sha256` |
| `models/` | 1A QLoRA adapter and `MANIFEST.sha256` (also lists the CPT weight hashes) |
| `eval/` | frozen ten-question set |
| `kubeflow/` | `setup_env.sh`, `check_env.py`, `requirements.txt` (the direct dependencies, single source of pins), `migrate_stage7_names.sh` (operator) |
| `audit/` | judge audit notebook (separate from the graded flow) |
| `assignment_2b_outputs/` | generated at run time on the volume (not in git); Stage 7 files are in `stage7/final/` and `stage7/audit/` |
