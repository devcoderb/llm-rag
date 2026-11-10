# NOTE: skeleton() is a masked short-prefix heuristic (first words after the first comma, or the first four words); it is not a complete template detector.
# Read-only audit of the 1A curated instruction dataset against the notice-board rules.
# Reads data files; writes only to notice-board-audit/. Standard library only.
import json, hashlib, random, re, statistics, collections, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent if (HERE.parent / "data/qa").exists() else HERE.parent / "assignment-2b"   # this folder inside the repository, or beside it
QA = REPO / "data/qa"; CORPUS = REPO / "data/corpus"
OLD = HERE.parent.parent / "assignment-1a/data/instruction/instruction_dataset_curated.jsonl"   # the 1A repository, only if present
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
load = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
full, cur = load(QA/"instruction_dataset.jsonl"), load(QA/"instruction_dataset_curated.jsonl")
train, ev = load(QA/"instruction_dataset_train.jsonl"), load(QA/"instruction_dataset_eval.jsonl")
out = {}
# 0. integrity
rec = [dict(r) for r in full]; random.Random(42).shuffle(rec); k = round(len(rec) * 0.80)
out["integrity"] = {"n_full": len(full), "n_cur": len(cur), "n_train": len(train), "n_eval": len(ev),
  "curated_sha_2b_equals_1a_copy": (sha(QA/"instruction_dataset_curated.jsonl") == sha(OLD)) if OLD.exists() else None,
  "full_pairs_equal_curated_pairs": [(r["instruction"], r["response"]) for r in full] == [(r["instruction"], r["response"]) for r in cur],
  "split_reproduced_by_seed42": rec[:k] == train and rec[k:] == ev}
wc = lambda s: len(s.split())
words = [wc(r["response"]) for r in cur]
def stats(w): 
    s = sorted(w); return {"n": len(w), "min": s[0], "p10": s[len(s)//10], "median": statistics.median(s), "mean": round(statistics.mean(s), 2), "p90": s[int(len(s)*0.9)], "max": s[-1], "lt30": sum(x < 30 for x in w), "ge30": sum(x >= 30 for x in w), "lt30_pct": round(100*sum(x < 30 for x in w)/len(w), 1)}
key = lambda r: (r["instruction"], r["response"])
tset, eset = {key(r) for r in train}, {key(r) for r in ev}
out["length"] = {"all": stats(words), "train": stats([wc(r["response"]) for r in cur if key(r) in tset]), "eval": stats([wc(r["response"]) for r in cur if key(r) in eset])}
bins = [(0,9),(10,19),(20,29),(30,39),(40,49),(50,59),(60,999)]
out["length"]["histogram"] = {f"{a}-{b if b<999 else '+'}": sum(a <= w <= b for w in words) for a, b in bins}
sent = lambda s: len([x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'(])", s.strip()) if x])
sc = [sent(r["response"]) for r in cur]; out["sentences"] = dict(collections.Counter(min(x, 4) for x in sc))
# 1. source text + copying
norm = lambda s: re.sub(r"\s+", " ", s.lower()).strip()
src = {p.name: norm(p.read_text(encoding="utf-8")) for p in CORPUS.glob("*.txt")}
missing = sorted({r["source_document"] for r in cur} - set(src)); out["missing_sources"] = missing
tok = lambda s: re.findall(r"\w+", s.lower())
def ngrams(t, n): return {tuple(t[i:i+n]) for i in range(len(t)-n+1)}
srcg = {}
def src_ngrams(name, n=6):
    key_ = (name, n)
    if key_ not in srcg: srcg[key_] = ngrams(tok(src[name]), n)
    return srcg[key_]
rows = []
for i, r in enumerate(cur):
    resp, s = norm(r["response"]), src[r["source_document"]]
    t = tok(r["response"]); g = ngrams(t, 6)
    ov = (len(g & src_ngrams(r["source_document"])) / len(g)) if g else 0.0
    rows.append({"i": i, "words": wc(r["response"]), "exact": resp in s, "ov6": round(ov, 3), "evid": norm(r["evidence"]) in s})
out["copy"] = {"exact_whole_response_in_source": sum(x["exact"] for x in rows), "exact_ids": [x["i"] for x in rows if x["exact"]],
   "ov6_ge_0.8": sum(x["ov6"] >= 0.8 for x in rows), "ov6_ge_0.5": sum(x["ov6"] >= 0.5 for x in rows), "ov6_mean": round(statistics.mean(x["ov6"] for x in rows), 3),
   "evidence_found": sum(x["evid"] for x in rows), "evidence_not_found": sum(not x["evid"] for x in rows),
   "exact_by_length": {"lt30": sum(x["exact"] and x["words"] < 30 for x in rows), "ge30": sum(x["exact"] and x["words"] >= 30 for x in rows)},
   "ov6_ge_0.8_ids_count_lt30": sum(x["ov6"] >= 0.8 and x["words"] < 30 for x in rows)}
# 2. random 15 (seed 42, as in the compliance review)
ids = random.Random(42).sample(range(len(cur)), 15); out["random15_ids"] = ids
out["random15"] = [{"i": i, "split": "train" if key(cur[i]) in tset else "eval", "source": cur[i]["source_document"], "instruction": cur[i]["instruction"], "response": cur[i]["response"],
                    "words": rows[i]["words"], "sentences": sc[i], "exact_copy": rows[i]["exact"], "ov6": rows[i]["ov6"], "evidence_in_source": rows[i]["evid"]} for i in ids]
# 2b. seed coupling between sample(range(n), 15) and the split shuffle (checked on this Python build)
import platform
shuf = list(range(len(cur))); random.Random(42).shuffle(shuf)
samp42 = random.Random(42).sample(range(len(cur)), 15)
out["seed_coupling"] = {"python": platform.python_version(), "implementation": platform.python_implementation(),
  "sample42_equals_reversed_final15_of_shuffle42": samp42 == shuf[-15:][::-1],
  "final15_positions_are_in_eval_tail": all(p >= k for p in range(len(cur) - 15, len(cur))), "eval_tail_starts_at_position": k,
  "sample42_rows_in_eval_split": sum(key(cur[i]) not in tset for i in samp42),
  "note": "Same seed and the algorithms' shared random draws make this particular sample land in the eval tail by construction; same seed alone is not invalid for every algorithm. Not a claim of misconduct."}
# 2c. independent sample, stored in actual draw order (not sorted)
IND_SEED = 20261110
ind = random.Random(IND_SEED).sample(range(len(cur)), 15)
out["random15_independent"] = {"seed": IND_SEED, "ids_in_draw_order": ind, "ids_sorted": sorted(ind), "in_eval": sum(key(cur[i]) not in tset for i in ind), "in_train": sum(key(cur[i]) in tset for i in ind),
  "under30": sum(rows[i]["words"] < 30 for i in ind), "exact_copy_ids": [i for i in ind if rows[i]["exact"]], "ov6_ge_0.8_ids": [i for i in ind if rows[i]["ov6"] >= 0.8],
  "items": [{"i": i, "split": "train" if key(cur[i]) in tset else "eval", "source": cur[i]["source_document"], "instruction": cur[i]["instruction"], "response": cur[i]["response"],
             "words": rows[i]["words"], "sentences": sc[i], "exact_copy": rows[i]["exact"], "ov6": rows[i]["ov6"], "evidence_span_in_source": rows[i]["evid"]} for i in ind]}
both = set(out["random15_ids"]) | set(ind)
out["sample_overlap"] = {"shared_rows": sorted(set(out["random15_ids"]) & set(ind)), "draws": 30, "distinct_pairs": len(both)}
# 3. question types (heuristic, by instruction text)
def qtype(q):
    l = q.lower()
    if re.search(r"\b(compare|compared|comparison|differ|difference|versus|vs\.?|higher than|lower than|more than|less than|whereas|relative to|rather than|distinguish|contrast|both .* and|between .* and)\b", l): return "comparative"
    if re.search(r"\b(how (must|should|does|do|is|are|can|will)|what (steps|process|procedure)|in what manner|procedure|process for|steps|required to (do|follow)|must .* (follow|comply|ensure|file|submit|obtain)|what must|what should)\b", l): return "procedural"
    return "factual"
types = [qtype(r["instruction"]) for r in cur]; out["qtype_overall"] = dict(collections.Counter(types))
mat = collections.defaultdict(collections.Counter)
for r, t in zip(cur, types): mat[r["source_document"]][t] += 1
out["qtype_matrix"] = {d: dict(c) for d, c in sorted(mat.items())}
out["docs_missing_type"] = {t: sorted(d for d in mat if mat[d][t] == 0) for t in ("factual", "procedural", "comparative")}
out["docs_with_type_lt3"] = {t: sorted(d for d in mat if 0 < mat[d][t] < 3) for t in ("procedural", "comparative")}
out["pairs_per_doc"] = dict(sorted(collections.Counter(r["source_document"] for r in cur).items(), key=lambda kv: -kv[1]))
# 4. template repetition
ins = [r["instruction"] for r in cur]
def lead(q, n): return " ".join(q.lower().split()[:n])
out["lead_ngrams"] = {n: collections.Counter(lead(q, n) for q in ins).most_common(8) for n in (1, 2, 3, 4, 5)}
def stem(q):  # interrogative stem: first wh-word / aux plus next word
    m = re.search(r"\b(what|which|how many|how much|how|when|who|why|where|whom|is|are|does|do|can|must|should|under what)\b(\s+\w+)?", q.lower()); return (m.group(0).strip() if m else "other")
out["stems"] = collections.Counter(stem(q) for q in ins).most_common(15)
def frame(q):  # opening frame with the quoted regulation name masked: "<Under|According to|In> X, <stem>"
    m = re.match(r"^(under|according to|in|as per|for|per)\b", q.lower()); return m.group(1) if m else "other"
out["frames"] = collections.Counter(frame(q) for q in ins).most_common(8)
# 'Under ..., what/how ...' skeleton: collapse everything before the first comma
def skeleton(q):
    a, _, b = q.partition(", "); return ("<ref>, " + " ".join(b.lower().split()[:3])) if b and a.lower().startswith(("under", "according", "in ", "as per")) else " ".join(q.lower().split()[:4])
out["masked_short_prefix_groups"] = collections.Counter(skeleton(q) for q in ins).most_common(12)
out["masked_short_prefix_max_share_pct"] = round(100 * out["masked_short_prefix_groups"][0][1] / len(ins), 1)
out["resp_lead3"] = collections.Counter(lead(r["response"], 3) for r in cur).most_common(6)
out["under_sebi_prefix"] = sum(q.lower().startswith("under sebi") for q in ins)
out["under_any_prefix"] = sum(q.lower().startswith("under ") for q in ins)
# per-doc low-length share
bydoc = collections.defaultdict(list)
for r, w in zip(cur, words): bydoc[r["source_document"]].append(w)
out["lt30_by_doc"] = {d: [sum(x < 30 for x in v), len(v)] for d, v in sorted(bydoc.items(), key=lambda kv: -sum(x < 30 for x in kv[1])/len(kv[1]))}
json.dump(out, open(pathlib.Path(__file__).parent / "audit_results.json", "w"), indent=1, ensure_ascii=False, default=lambda o: list(o))
print(json.dumps({k: v for k, v in out.items() if k not in ("qtype_matrix", "random15", "pairs_per_doc", "lt30_by_doc")}, indent=1, ensure_ascii=False, default=lambda o: list(o)))
