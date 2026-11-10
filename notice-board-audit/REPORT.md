# Notice-board compliance audit: measurements and remediation proposal (2026-11-10)

Read-only. No dataset, split, adapter or frozen RAG query set was changed. Script: `audit.py` in this folder (standard library, reads `data/qa` and `data/corpus` of this repository, writes only `audit_results.json` in this folder). Rules are taken from the notice-board requirements supplied by the operator and an earlier review note; notice authenticity, date and scope are not verified. Counts below are reproducible by re-running the script. Machine measurements and the auditor's manual reading are kept separate; the manual reading is not an operator review.

## 1. Data integrity (so the numbers are about the right files)

| Check | Result |
|---|---|
| Curated file in 2B equals the 1A copy (SHA-256) | yes |
| Full Q/A file equals the curated pairs, same order | yes |
| 957 / 239 split reproduced exactly by `random.Random(42).shuffle` then `round(0.8*n)` | yes |
| Source documents named in the dataset missing from the corpus | 0 |

## 2. Response length (>= 30 words rule)

Words counted with `response.split()`.

| Set | Pairs | Min | Median | Mean | Max | Under 30 words | 30 or more |
|---|---|---|---|---|---|---|---|
| All | 1,196 | 6 | 26 | 27.2 | 62 | 758 (63.4%) | 438 |
| Train | 957 | 6 | 27 | 27.5 | 62 | 589 (61.5%) | 368 |
| Eval | 239 | 9 | 25 | 26.1 | 59 | 169 (70.7%) | 70 |

- Histogram (words): 0-9: 8, 10-19: 243, 20-29: 507, 30-39: 312, 40-49: 112, 50-59: 13, 60+: 1.
- 24 of 30 documents have at least half of their responses under 30 words.
- All ten frozen RAG evaluation answers come from this file. Eight of the ten have fewer than 30 words (Q01 19, Q03 15, Q04 25, Q06 18, Q07 21, Q08 26, Q09 28, Q10 11); Q02 (33) and Q05 (36) have 30 or more.
- Sentence counts use a simple punctuation-based splitter (heuristic, not an exhaustive proof; abbreviations and numbered clauses can mis-split): 1 sentence 1,004, 2 sentences 182, 3 sentences 10, none longer. By this count the responses are within 1-3 sentences.
- The two length requirements are compatible: a response of 30 or more words can still be 1-3 concise sentences. The practical concern is how to expand naturally short numeric answers (for example "No, unless ..." or a single figure) with useful, source-supported content instead of filler.

**Gap:** the >= 30-word filter is missing, and about two thirds of the data is below it.

## 3. Copying from the source

Normalisation: lower-case, whitespace collapsed. Evidence fields are verbatim by design and are not counted as copying.

| Measure | Count |
|---|---|
| Whole response is a contiguous substring of its source | 22 / 1,196 (1.8%): 7 in eval, 15 in train; 21 of them are under 30 words |
| At least 80% of the response's 6-word sequences occur in the source | 107 (8.9%): 28 eval, 79 train; 96 of them under 30 words |
| At least 50% of 6-word sequences occur in the source | 400 (33.4%) |
| Mean 6-word-sequence overlap | 0.381 |
| Evidence span found in the source | 1,181 / 1,196 (98.7%), 15 not found |

Exact copy row IDs (zero-based): 51, 55, 65, 119, 145, 189, 233, 274, 353, 381, 399, 491, 537, 563, 568, 599, 618, 691, 697, 844, 993, 1091. None of the ten frozen RAG answers is an exact copy; Q10 has a 6-word-sequence overlap of 1.0 (an 11-word answer).

How to read this: these are lower-bound screens for source copying. High overlap is expected for short numeric or definitional answers, so the 8.9% figure marks extractive style, not proof of a violation. The rest of the dataset is not shown to be paraphrased or independently authored either; that needs the generation record (section 7).

## 4. Random-pair quality check (10-15 pairs)

**Seed coupling (confirmed).** On the tested build (CPython 3.10.12), `random.Random(42).sample(range(1196), 15)` equals the last 15 values of `random.Random(42).shuffle(list(range(1196)))` in reverse order (checked in `audit.py`, stored under `seed_coupling`). The split puts positions 957 onward in the eval set, so those 15 rows are in the eval tail by construction: 15 of 15 are eval rows. The conditional probability under independent sampling would be about 2.3e-11, but this draw was not independent of the split construction, so the result is a coupling, not a coincidence and not a sign of misconduct. Using the same seed is not invalid for every algorithm; this exact pairing is the problem. Consequence: the earlier 15-row sample audits evaluation examples, not training quality. Other seeds tried gave 3, 4 and 0 of 15 in eval.

**Independent sample (stored).** Seed 20261110, `random.Random(20261110).sample(range(1196), 15)`. Draw order: 612, 356, 1159, 965, 764, 653, 368, 1146, 670, 468, 671, 1088, 1116, 824, 1092 (sorted for display: 356, 368, 468, 612, 653, 670, 671, 764, 824, 965, 1088, 1092, 1116, 1146, 1159). Membership: 12 train, 3 eval (764, 468, 1116). IDs, split, source, question, response and measured fields are saved in `audit_results.json` under `random15_independent` (and regenerated by `audit.py`).

| Sample | Rows | In eval | Under 30 words | Exact copy | 6-gram overlap >= 0.8 |
|---|---|---|---|---|---|
| Seed 42 (earlier review; eval tail by construction) | 228, 51, 563, 501, 457, 285, 209, 1116, 178, 864, 65, 61, 191, 447, 476 | 15 | 12 | 51, 563, 65 | 51, 563, 65, 61, 191, 476 |
| Independent seed 20261110 (draw order above) | 612, 356, 1159, 965, 764, 653, 368, 1146, 670, 468, 671, 1088, 1116, 824, 1092 | 3 | 11 | none | 468 |

The two samples share row 1116, so they hold 30 draws but 29 distinct pairs.

Auditor's manual reading of the 30 draws (one pass each, not an operator review, and not a full source check):
- Every response read as responsive to its question and single-topic. All 30 evidence spans are found in the source; that shows the cited span exists, not that the whole answer is supported. Full answer support would need inspection of the full source passage for each row.
- No filler or padding was seen. Short answers are short because the fact is short (for example 1146: "No, unless it is allowed under extant statutory guidelines.", 9 words).
- Row 65 reproduces the source's grammar error ("crossed over a 100 billion transactions"), an example of copying that carries source errors into training data.
- Rows 191 ("seventy five per cent."), 476 and 468 follow the source wording closely; they are not exact copies only because of small edits.
- Rows 764 and 1092 are the only two-sentence answers in the independent sample; both are still concise.

Evidence of a pre-training random-pair review: none in the 1A notebook (Stage 8B prints one example). The workplan lists "Inspect random examples" as an unticked checklist item.

## 5. Question-type coverage (factual, procedural, comparative)

Automatic labelling by wording of the instruction (heuristic, not ground truth):

| Heuristic type | Instructions |
|---|---|
| Factual | 961 |
| Procedural | 153 |
| Comparative | 82 |

- By this heuristic, no document lacks factual questions; 2 documents have no procedural question (RBI Annual Report 2023-24, Payments Vision 2025) and 8 have no comparative question (for example the ARC Directions, Digital Lending Guidelines, Payments Vision 2028). Many more have fewer than three of a type.
- The heuristic is loose. Checking a random 8 per type showed false positives: "disputes between system participants" is labelled comparative, and "how does the Act define systemic risk" is labelled procedural (it is a definition). So the per-document gaps above are indicative, not established.
- All 30 documents have pairs (15 to 135 pairs each; four documents hold about 33% of the pairs).

**Gap:** type coverage across all sources is not verified. A claim that every source has all three types would be unsupported. Manual labelling is needed before any coverage statement.

## 6. Template repetition (> 20% flag)

No flag detector exists in the notebook. Two detectors were applied; their results differ, which is why a rule must be defined.

| Detector | Result |
|---|---|
| Opening frame: instruction begins "Under ..." | 592 / 1,196 (49.5%) |
| Opening two words "Under SEBI's" | 318 (26.6%) |
| Opening three words "Under the SEBI" | 167 (14.0%) |
| Masked short-prefix heuristic (regulation name masked; first three words after the first comma, or the first four words) | largest group 30 pairs (2.5%): "<ref>, what is the" |
| Question stem (first wh-word plus next word) | "what is" 92 (7.7%); no stem above 8% |
| Response opening three words | largest "the ARC must" 17 (1.4%) |

- The "Under ..." opening is a source-qualifier frame that makes each question self-contained; it is not proof of a harmful repetitive question template.
- The 2.5% figure is a masked short-prefix heuristic only. It looks at a few words, so it cannot show that no complete template exceeds 20%, and it cannot exclude 2-3 repeating semantic templates. The question-stem distribution (top stem 7.7%) is also a surface measure.
- Template compliance therefore stays unverified until a definition and manual grouping are supplied.

## 7. Generation provenance

| Evidence searched | Finding |
|---|---|
| 1A notebook Stage 8B text | States pairs "were written from" each document by reading it; says automatic paragraph-to-question conversion was avoided |
| 1A notebook, README, workplan, git history, `deliverables.zip` | No generation prompt, script, chat export or per-pair authorship record. The workplan checklist items "Decide manual, heuristic or synthetic generation" and "If using an external LLM, save exact generation prompt" are unticked |
| Git history of the curated file | Built in two commits on 2026-10-08: 711 pairs ("Add 14 corpus PDFs, 711 curated instruction pairs"), then 485 more ("Update: instruction dataset to 1196"). Commit messages carry no method |
| Notice requirement for an LLM-generation instruction | Not evidenced either way |

Conclusion: whether the pairs were human-written or LLM-assisted cannot be established from the files. No historical prompt may be reconstructed or invented. The operator has to state the true method and supply any real prompt or chat export that exists; otherwise the record should read "generation prompt not retained".

## 8. Compliance summary

| Notice requirement | Status |
|---|---|
| 40-50 or more pairs | Met by count (1,196); quality shown only by the checks below |
| Random 10-15 pair review | Not recorded before training; the seed-42 sample is coupled to the split shuffle and lies wholly in eval; an independent sample is stored here, but it is not an operator review |
| Own-words, concise 1-3 sentence responses | 1-3 sentences met by a heuristic count; own-words not established (1.8% exact copies, 8.9% near-copies are screens only) |
| Question types across sources | Not verified (heuristic only, known false positives) |
| LLM prompt instruction recorded | Not evidenced |
| >= 30-word filter | Missing; 63.4% of responses fall below it |
| Template flag over 20% | Unverified: no detector in the notebook; the masked short-prefix heuristic (2.5%) and the opening-frame figure (49.5%) are not a template definition |
| Avoid 2-3 phrasings cycling | Not established; the surface stem distribution is broad but does not test semantic repetition |

## 9. What depends on the dataset (conditional; nothing is being rebuilt)

Only if the training responses are corrected and the corrected set must be the model's training source:
- The 1A QLoRA adapter would need retraining. The cleaned corpus is unchanged, so CPT would not need to be repeated.
- A new split or ten new evaluation questions is not inherently required; keep the existing split membership and row IDs where possible.
- Unchanged query text, answer spans and corpus keep the earlier 2B retrieval and reranking measurements valid; recompute them only if their actual inputs or ground truth change.
- A new model or changed expected answers would affect generation and judging, as applicable.
- List the exact affected artifacts before undertaking any change.

Not implied by this audit: that the notice requires every question type in every document. That interpretation needs faculty confirmation.

## 10. Proposed remediation (nothing done; any dataset change is a separate explicit decision)

1. **Document, no data change:** add a read-only validator and a dated compliance note stating the measured gaps and that the historical files are unchanged. New validation documents the current state; it does not show the trained model used filtered data.
2. **Fill the evidence gaps without touching data:** (a) record the true generation method and any real prompt (section 7); (b) a review of 15 rows drawn with an independent seed, with the sampling restricted to the training split if training quality is the question (the stored independent sample has 12 train and 3 eval rows, so it is a mixed sample, not a train-only sample), with the operator's per-row decisions (understandable, supported by the source passage, responsive, formatted, no leakage) and a timestamp; (c) manual type labels for a per-document matrix, if faculty want one; (d) a written template rule with manual grouping of any flagged group.
3. **If faculty require retrospective compliance:** build a separately named corrected dataset with a documented method and recorded prompt: expand answers under 30 words only with source-supported content, keep 1-3 concise sentences, replace exact copies with own-words answers that keep the fact, keep split membership where possible. Section 9 lists what that would and would not affect.
4. **Questions for faculty:** does the notice apply retrospectively to 1A and to 2B's reuse of the 1A model; does "own words" allow short numeric answers that quote the source; is every question type required in every document.

Historical compliance must not be claimed retroactively from newly added validation. Retrospective applicability and method provenance remain unresolved.
