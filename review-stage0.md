# Stage 0 review — 2026-11-09

Status: **Stage 0 approved to proceed to Stage 1**, after reviewing saved Kubeflow outputs in commit `fb43f1c` on 2026-11-09. Earlier findings below are retained as the initial audit trail; their current disposition is recorded immediately below.
Scope: Stage 0 notebook cells 0–11 and kubeflow setup/check scripts. Sonnet remains the implementer; no notebook or setup code changed by this review. Cell indices below are zero-based and include stable cell IDs.

## Re-review of executed notebook — commit fb43f1c

**Verdict: PASS for Stage 0; proceed to Stage 1 only.** Fetched origin/main and fast-forwarded the local repository without altering notebook code. All eight code cells have execution counts 1–8 and saved outputs; no error outputs. The code sources are unchanged from the initial review. Approval is based on current successful execution evidence, not a claim that the defensive gate improvements were implemented.

Confirmed from saved outputs:
- Repository: `/home/group157/llm-assignment-2b/llm-rag`; artifact root `/home/group157`; output root `/home/group157/assignment_2b_outputs`.
- GPU is **NVIDIA L40S**, not the earlier 1A A100: 47.8 GB total / 39.4 GB free; bf16 supported. Python 3.11.11, torch 2.5.1+cu124; all listed package imports succeed. Container RAM limit is 19.3 GB; host-wide memory is not the container allocation.
- All 34 data files hash-match; PV corpus matches all 30 repository documents; full QA matches; 1,196 curated/submitted QA identities agree.
- Train/eval are 957/239, disjoint, with union equal to full QA. Original ordered split reproduction also passed the earlier independent local check.
- All eight repository adapter files, eight CPT backup files and eight PV adapter files hash-match. CPT used is `/home/group157/model-backups/cpt_model_1a`; config reports 8,192 positions. Adapter reports r16/alpha32/q_proj,v_proj/dropout0.05.
- Corpus load succeeds: 30 documents / 7,160,100 characters. Environment, input-manifest and summary JSON writes are evidenced in cell outputs, though the JSON files themselves were not retrieved.
- Metadata is reachable for retrieval models and later generator/judge candidates. Printed HF-cache filesystem free space (2,485.8 GB) exceeds the reported retrieval checkpoint sizes (0.27/0.30 GB); any per-user quota is not established by this filesystem figure. No large-model download is needed now.

Disposition of initial findings:
1. **Package/gate handling:** not a current blocker: every inventoried package imported and all setup checks ran. Defensive required-key/empty-manifest handling remains a suggested improvement, not an approval prerequisite for this successful run. No unused-package installation required.
2. **Access/budget:** sufficient for planning Stage 1; retain the narrower label **metadata reachable** for 0F. Llama is explicitly gated; permission to download weights is not proven by these outputs. Check actual retrieval-model loading at Stage 2/5, and resolve judge weight authorization or choose an accessible different judge before Stage 7. Save exact model revisions at load time. Do not claim all candidate weights are authorized.
3. The generic PASS summary does not supersede these explicit limitations. Model loading, generation performance and future memory use are not yet tested.

Sonnet next: implement only Stage 1 from the RAG plan: ten unchanged questions/expected answers from the verified evaluation set, sufficient raw answer spans with offsets/source IDs, frozen query provenance, and one separately tracked unanswerable query. No 16-intent subset is approved or needed by this RAG Stage 0 review; clarify any separate assignment context before treating it as a requirement.

## Initial review (superseded status; findings retained)

## Required corrections

### [P2, narrowed] Gate should reflect failures of current-stage requirements only

Location: Stage 0B, cell 5 (`6efcd4bc`); Stage 0G, cell 11 (`2452283b`).

The broad `PKGS` inventory includes packages for later stages. A missing package that Stage 0 does not need is informational and must not block Stage 0. Import inventories are not proof that every listed dependency is necessary now. The original review wording was too broad; narrowed after operator feedback.

Sonnet: distinguish current-stage requirements from later-stage package inventory. Only a missing dependency actually needed for Stage 0 should block Stage 0. Packages used for embeddings, FAISS, BM25, generation or judging can be validated immediately before their relevant stage. If required setup cells are skipped or a current-stage operation fails, report that clearly in the summary. Do not add a blanket all-packages PASS requirement or install unused packages to satisfy the review.

Related integrity hardening: Stage 0D `check_dir` passes an empty manifest section as `PASS, 0 files`. Require a nonempty expected section with essential model/tokenizer files. Current committed manifest is populated; this is a reproduced false-pass edge case, not a missing-file finding about the real adapter.

Verification: a missing later-stage-only package must remain informational; a failed current-stage check or absent mandatory setup result must prevent claiming that setup is complete. Do not uninstall real packages for this check.

### [P2] Model metadata reachability is treated as a feasible model/download plan

Location: Stage 0F, cell 10 (`54408656`).

`any(r[4] == "reachable" for r in rows)` yields PASS even if only one candidate is reachable. Model-card metadata access does not establish authorization to read gated weights. The code prints cache free space but does not compare it with selected checkpoint downloads. It sums all `.bin` and `.safetensors` siblings, which can double-count alternative formats, and does not save model revisions or the model-access report. This does not yet satisfy the plan’s feasible model/download-budget check.

Sonnet: persist metadata, revision, gating/access status and one chosen weight format per candidate. Check required retrieval-model weight/config access without downloading weights. Mark Llama weight permission unresolved until authenticated access is established; do not label public metadata as granted access. Identify the actual HF cache filesystem and any PV quota caveat, then compare planned sequential cache occupancy with available capacity. Keep generator/judge feasibility explicitly deferred if unresolved; this need not stop retrieval work once its smaller required models fit. Do not download large fallback/judge models now.

Verification: distinguish metadata-only access, missing weight permission and available access in saved output; demonstrate the budget comparison for selected retrieval models. Freeze the exact model ID/revision actually selected. The two cross-encoder spellings need not be adjudicated from their names alone; use evidence from the actual repository/config fetched.

## Checks passed locally

- All 34 data-manifest entries exist and match SHA-256.
- All 30 corpus files and the full Q/A JSONL match the previously verified 1A deliverables ZIP byte-for-byte.
- Train/eval exports reproduce the exact original `random.Random(42).shuffle` and rounded 80/20 split: 957/239, including ordered Q/A membership.
- All eight repository adapter files match the model manifest. CPT weights are deliberately absent from this local repository and require the pod check, not another upload.
- Executed Stage 0C and 0E locally against repository data with temporary output/PV paths: corpus, QA, split and manifest checks pass; 30 documents / 7,160,100 characters load and a valid input manifest is saved.
- All eight notebook code cells parse; setup_env.sh passes bash syntax validation; check_env.py parses.
- Notebook stays within Stage 0 and explains CPT/SFT/LoRA/QLoRA/RAG plus the 100/400 decision.

## Runtime evidence and minor follow-ups

The supplied 2B notebook has execution_count=None in all eight code cells and zero saved outputs. It therefore cannot substantiate current GPU availability, CPT hashes, package imports, network/model access or gate completion. This is an evidence limitation, not a claim that the operator never ran the code. After corrections, run Stage 0 on Kubeflow, save the notebook with outputs and make environment_report.json, input_manifest.json and stage0_summary.json available for review.

Minor: Stage 0A currently seeds Python random only; seed NumPy and torch/CUDA before stochastic operations and record any deterministic-compute limits. Explicit REPO_ROOT/CPT_DIR overrides should take precedence or fail clearly rather than silently fall back to another valid directory. Expand first-use acronyms for the learner. These do not alter the verified data result.

Initial next action was to obtain executed outputs and resolve findings; see the re-review above for the current approval and deferred follow-ups. Stage 1 content and any 16-intent task remain unreviewed.
