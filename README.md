# Assignment 2B: Finance RAG Pipeline · Group 157

This project builds and evaluates a retrieval-augmented generation (RAG) pipeline for Indian financial markets and digital payments. It reuses the cleaned RBI and SEBI documents, evaluation questions and fine-tuned model from Assignment 1A. No new documents are collected and no model is retrained in 2B.

The pipeline compares chunk sizes and search methods, reranks retrieved passages, generates answers with source citations, and checks those answers with a separate LLM judge and a manual spot-check.

## Team members

| Name | BITS ID | Email |
|---|---|---|
| Pradeep Anand C | 2025ae05886 | 2025ae05886@wilp.bits-pilani.ac.in |
| Dron Adhikari | 2025ae05184 | 2025ae05184@wilp.bits-pilani.ac.in |
| Pravallika Donthala | 2025ae05181 | 2025ae05181@wilp.bits-pilani.ac.in |
| B Devchandraaj | 2025ae05469 | 2025ae05469@wilp.bits-pilani.ac.in |

## Project outline and submission

| Section | Task | Notebook stage |
|---|---|---|
| Setup | Verify reused data, model files and environment | 0 |
| Preparation | Select ten evaluation questions and mark their answer passages | 1 |
| A1 | Build reusable dense search and report the embedding/index details | 2; final-corpus build time in 3 |
| A2 | Compare 100- and 400-token chunks and justify the chosen size | 3 |
| B | Compare Dense, BM25 and Hybrid search using hit rates and latency | 4 |
| C | Rerank search results and measure changes in accuracy, ranking and time | 5 |
| D1 | Generate cited answers, test an unanswerable question and document the model switch | 6 |
| D2 | Judge correctness and support, manually check three verdicts, and explain one failure with a proposed fix | 7 |

Open [Group157-Assignment-2b.html](Group157-Assignment-2b.html) to review the saved execution without a GPU. [Group157-Assignment-2b.ipynb](Group157-Assignment-2b.ipynb) contains the code, saved outputs and observations. The separate [judge audit notebook](audit/Group157-Assignment-2b-judge-audit.ipynb) records earlier judge attempts; the main notebook presents the selected judge and final results.

## Repository structure and reused files

All paths below are relative to the cloned repository.

```text
llm-rag/
├── Group157-Assignment-2b.ipynb       # Executed assignment notebook
├── Group157-Assignment-2b.html        # HTML export of the same notebook
├── data/
│   ├── corpus/                      # 30 cleaned RBI / SEBI text documents
│   ├── qa/                          # Original Q/A pairs, evidence and split exports
│   ├── MANIFEST.sha256               # Expected fingerprints of the 34 data files
│   └── README.md
├── models/
│   ├── qlora_finance_adapter/        # Trained 1A adapter and its tokenizer
│   ├── MANIFEST.sha256               # Adapter and external CPT file fingerprints
│   └── README.md
├── eval/query_set_frozen.json        # Ten questions, expected answers, spans and U01
├── kubeflow/
│   ├── setup_env.sh                  # Create the RAG environment and Jupyter kernel
│   ├── check_env.py                  # Verify packages, imports and basic operations
│   ├── requirements.txt              # Dependency versions used by both scripts
│   └── migrate_stage7_names.sh       # Optional migration of an older run's files
├── audit/
│   └── Group157-Assignment-2b-judge-audit.ipynb
├── README.md
└── LICENSE
```

**Git** means supplied by cloning this repository, even though the clone itself is stored on the PV. **Group 157 PV** means the existing 1A files outside the clone. Paths beginning with `data/`, `models/` or `eval/` are relative to the repository folder found in 0A.

| Input | Supplied by | Read from | Contents and use |
|---|---|---|---|
| Cleaned finance documents | Git | `data/corpus/*.txt` | 30 RBI/SEBI texts used as the searchable document collection |
| Complete instruction dataset | Git | `data/qa/instruction_dataset.jsonl` | 1,196 original finance question-answer pairs from 1A |
| Questions with source evidence | Git | `data/qa/instruction_dataset_curated.jsonl` | The same pairs with source filenames and evidence text for tracing answers to the corpus |
| Training split | Git | `data/qa/instruction_dataset_train.jsonl` | 957 pairs used for 1A QLoRA training; checked against evaluation pairs for overlap |
| Evaluation split | Git | `data/qa/instruction_dataset_eval.jsonl` | 239 held-out pairs from which the ten evaluation questions were selected |
| Frozen evaluation questions | Git | `eval/query_set_frozen.json` | Q01–Q10, expected answers, source passages and offsets, plus the separate U01 question |
| Data fingerprints | Git | `data/MANIFEST.sha256` | Expected hashes for the 34 data files, checked in 0C |
| Model fingerprints | Git | `models/MANIFEST.sha256` | Expected hashes for the adapter and external CPT files, checked in 0D |
| 1A QLoRA adapter tensor | Git | `models/qlora_finance_adapter/adapter_model.safetensors` | The trained adapter weight updates attached to the CPT model in the baseline trial |
| Adapter configuration and tokenizer | Git | `models/qlora_finance_adapter/` | `adapter_config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `merges.txt`, `vocab.json` and `README.md` accompany the adapter |
| 1A CPT model tensor | Group 157 PV | `/home/group157/model-backups/cpt_model_1a/model.safetensors` | The existing finance CPT weights, reused directly; not downloaded by Git clone |
| CPT configuration and tokenizer | Group 157 PV | `/home/group157/model-backups/cpt_model_1a/` | `config.json`, `generation_config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `merges.txt` and `vocab.json` accompany the CPT weights |

For the existing Group 157 run, the CPT files are already on the mounted PV at `/home/group157/model-backups/cpt_model_1a/`; the notebook reuses them directly. The original PV corpus, Q/A and adapter copies are cross-checks only; their Git copies supply the pipeline inputs. Other model downloads and generated outputs are described below.

## Clone, set up and verify on Kubeflow

The executed notebook used Python 3.11.11, PyTorch 2.5.1+cu124 and an NVIDIA L40S with 47.8 GB GPU memory; the container RAM limit was 19.3 GB. These are the recorded run specifications, not measured minimum requirements. The setup script inherits PyTorch and CUDA from the notebook image, so use a PyTorch/CUDA notebook environment for this workflow.

Run these commands in a Kubeflow terminal. The example uses the Group 157 persistent volume at `/home/group157`.

```bash
cd /home/group157
git clone https://github.com/devcoderb/llm-rag.git
cd llm-rag
bash kubeflow/setup_env.sh
/home/group157/venv-rag/bin/python kubeflow/check_env.py
```

`setup_env.sh` creates `/home/group157/venv-rag`, installs the dependencies in `kubeflow/requirements.txt`, registers **Python (RAG venv)** and saves installed versions to `/home/group157/rag_requirements.txt`. It leaves the 1A environment separate. Re-running the script reuses the environment and restores the kernel registration after a pod restart.

The verification script is **`check_env.py`**, not `verify.py`. It checks package versions and imports, FAISS indexing/search and BM25 scoring, without downloading models. It also reports GPU availability and a small 4-bit operation. GPU diagnostics and the interpreter summary are informational, so inspect those messages as well as the final package and functional check results. Passing this script does not verify model access, the CPT files or a full notebook run; Stage 0 checks those inputs separately.

The Stage 0 section of the notebook repeats these terminal commands under **Before 0A: Get the repository and prepare the Python environment** for users opening the notebook directly.

**Change the notebook interpreter/kernel before execution:** open `Group157-Assignment-2b.ipynb`, choose **Kernel → Change Kernel → Python (RAG venv)**. If the existing selection is the 1A/LLM environment, switch it to the RAG kernel. In an editor that asks for a Python interpreter, select `/home/group157/venv-rag/bin/python`.

For a different namespace or volume, set `VOLUME_ROOT` when running both setup and verification. Set the notebook's `ARTIFACT_ROOT` separately in cell 0A, before its paths are constructed, or in the Jupyter process environment before starting Jupyter. A terminal export does not change the environment of an already-running notebook kernel.

| Setting | Default | Used by |
|---|---|---|
| `VOLUME_ROOT` | `/home/group157` | Setup and environment verification |
| `VENV_DIR` | `<VOLUME_ROOT>/venv-rag` | Optional custom Python environment location for both scripts |
| `ARTIFACT_ROOT` | `/home/group157` | Notebook: external 1A artifacts and generated output folder |
| `CPT_DIR` | First valid candidate described below | Notebook: external CPT checkpoint |

## Obtain the 1A CPT checkpoint before running

The repository includes the corpus, Q/A files, frozen query set and QLoRA adapter. It does **not** include the continued-pretraining checkpoint: its `model.safetensors` file is about 1.45 GB. A fresh clone alone is therefore insufficient for a complete rerun.

**Reuse the existing 1A tensor files on the Group 157 PV; do not retrain them for 2B.** Stage 6 loads the original CPT `model.safetensors` from `CPT_DIR` and attaches `models/qlora_finance_adapter/adapter_model.safetensors` from this clone. Keep each artifact with its matching configuration and tokenizer files. The repository adapter is already the 1A artifact; the optional adapter on the original volume is only a cross-check. Stage 0D verifies the recorded hashes. Downloading the original SmolLM2 base checkpoint is not a substitute for the finance CPT checkpoint.

**CPT download location: not yet supplied by Group 157.** A shareable checkpoint URL must be provided so another user can reproduce the full run without access to the original volume.

Obtain the original eight-file CPT folder and place it at one of these locations:

1. The directory specified by `CPT_DIR`.
2. `<ARTIFACT_ROOT>/model-backups/cpt_model_1a/`.
3. `<ARTIFACT_ROOT>/cpt_model/`.

Cell 0A selects the first candidate containing `model.safetensors`. Stage 0D verifies all eight files against `models/MANIFEST.sha256`. A newly trained model is not a substitute for the recorded checkpoint because its hashes will differ. Missing CPT files are reported during setup and prevent a complete run, including the 1A baseline generation in Stage 6.

Original corpus, Q/A and adapter copies on the volume are optional cross-checks; the committed repository copies are used as inputs. The separate CPT checkpoint is required. Saved notebook and HTML outputs remain readable without it.

## Models used and why

| Role | Model or method | Stage | Reason used in this run |
|---|---|---|---|
| Embedder | `BAAI/bge-small-en-v1.5` | 2–5 | Small 384-dimension model with a 512-token input limit; its tokenizer also sizes the chunks |
| Keyword search | BM25 (`rank_bm25`, BM25Okapi) | 4 | Provides a keyword baseline; Hybrid combines its ranks with Dense using reciprocal rank fusion |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | 5 | Named in the assignment; scores each query and passage together to reorder the candidates |
| Generator tested first | SmolLM2-360M CPT checkpoint + 1A QLoRA adapter | 6 baseline | Reuses the required 1A model; its saved answers had no numbered citations and did not abstain on U01 |
| Generator selected | `microsoft/Phi-3.5-mini-instruct` (revision `2fe1924501`) | 6 fallback | The preferred Llama model returned HTTP 401; Phi returned the exact required abstention for U01 |
| Judge | `allenai/Llama-3.1-Tulu-3-8B` | 7 | Different from the generator; matched 9/12 known-label calibration cases, the best of the four recorded judge attempts |

The notebook downloads the embedding, reranking, fallback and judge checkpoints from Hugging Face when they are not cached, and records their revisions. `meta-llama/Llama-3.1-8B-Instruct` is the preferred fallback candidate in the code; access was gated in the submitted run, so Phi was selected. Qwen is a last-resort candidate in the switch logic and was not used for the submitted answers. Stage 0's metadata checks include preliminary candidates, not just the models ultimately selected.

## Execution and generated outputs

After selecting the RAG kernel and supplying the CPT checkpoint, execute the notebook in order from Stage 0 to Stage 7. Later stages depend on earlier variables and saved files. Read each stage's checks and observations before continuing. Stage 7 includes interactive manual labels and disagreement explanations for three answers, so a fresh full run requires user input.

Outputs are written under `<ARTIFACT_ROOT>/assignment_2b_outputs/`, by default `/home/group157/assignment_2b_outputs/`. They are generated on the persistent volume and are excluded from Git.

| Output location | Files and contents |
|---|---|
| Output root, Stage 0 | `environment_report.json` records resources/packages; `input_manifest.json` records corpus provenance; `stage0_summary.json` records setup checks |
| Output root, Stages 1–2 | `query_set_frozen.json` is the working copy of the frozen evaluation set; `embedder_facts.json` records embedding settings |
| `stage3/` | `chunks_100.jsonl`, `chunks_400.jsonl`, matching `embeddings_<size>.npy`, `index_<size>.faiss` and `dense_results_<size>.json`; chunk text, vectors, search indexes and per-query results for both sizes |
| `stage3/` | `final_chunks.jsonl`, `FINAL_CHUNKS_CONFIG.json`, `stage3_summary.json`, `stage3_manifest.sha256`; chosen chunks, configuration, comparison metrics and integrity record |
| `stage4/` | `stage4_results.json`; Dense, BM25 and Hybrid rankings, hit rates and latency |
| `stage5/` | `stage5_results.json`, `reranked_top3.json`, `stage5_manifest.sha256`; reranking metrics and the three full passages supplied to generation for each query |
| `stage6/` | `stage6_generation.json` and `stage6_manifest.sha256`; original 1A baseline answers and their provenance |
| `stage6/` | `stage6_fallback_generation.json` and `stage6_fallback_manifest.sha256`; selected generator's answers and their provenance |
| `stage7/final/` | `calibration.json`, `manual_spotcheck.json`, `judge_raw_verdicts.json`, `spotcheck_explanations.json`, `judge_records.json`, `manifest.sha256`; judge calibration, user labels, raw verdicts, disagreement notes and final records |
| `stage7/audit/` | Earlier run and superseded label records, when retained from an existing volume |

Some cells reuse saved records after provenance checks; others rebuild their outputs. Keep an existing run's files together because later stages verify upstream hashes. Only users with older Stage 7 filenames need `kubeflow/migrate_stage7_names.sh`; it is not a fresh-clone setup step.

To review without executing, open the saved HTML. To export after a new execution, use a terminal where Jupyter/nbconvert is installed, from the repository folder:

```bash
jupyter nbconvert --to html Group157-Assignment-2b.ipynb
```

This exports the notebook's saved outputs without running its cells. If using a fresh clone for a rerun, the files shown in the output table are produced by that run; they are not downloaded with the repository.

## Reading the results

The same ten held-out questions and frozen answer passages are used throughout. A retrieval hit requires the stored passage to be present in a returned chunk. U01 is a separate unanswerable query and is excluded from ten-question metrics. Ten questions give results in ten-percentage-point steps, so differences are indicative.

The submitted run selected 400-token chunks and Dense search. Reranking improved hit@1 from 4/10 to 5/10 but reduced hit@3 from 7/10 to 5/10. Phi improved citation and abstention behaviour over the 1A baseline, but strict D1 checks still failed on five answers. Stage 7's counts are judge-reported, not validated accuracy: calibration matched 9/12 cases and agreement with the user's three manual labels was 1/3. The notebook explains these limitations and preserves the raw outputs.

## License

[LICENSE](LICENSE) is copied unchanged from Assignment 1A. The MIT terms cover the project's software and documentation; the included RBI/SEBI source documents retain their publishers' rights. Downloaded models remain subject to their respective licenses.
