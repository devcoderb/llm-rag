#!/usr/bin/env bash
# Moves the Stage 7 files on the Kubeflow volume to the final names used by the notebook.
# Nothing is deleted or rewritten: files are only moved (mv -n semantics), and existing targets are skipped.
# Usage: bash kubeflow/migrate_stage7_names.sh [STAGE7_DIR]
set -euo pipefail
S="${1:-/home/group157/assignment_2b_outputs/stage7}"
[ -d "$S" ] || { echo "No such folder: $S" >&2; exit 1; }
mkdir -p "$S/final" "$S/audit"

mvf() {   # mvf SOURCE TARGET
  if [ -e "$1" ]; then
    if [ -e "$2" ]; then echo "skip (target exists): ${2#$S/}"; else mv "$1" "$2"; echo "moved: ${1#$S/} -> ${2#$S/}"; fi
  fi
}

V="$S/v2"
# final records
mvf "$S/manual_spotcheck.json"            "$S/final/manual_spotcheck.json"
mvf "$V/stage7_v2_judge_raw.json"         "$S/final/judge_raw_verdicts.json"
mvf "$V/stage7_final_judge.json"          "$S/final/judge_records.json"
mvf "$V/spotcheck_explanations_v2.json"   "$S/final/spotcheck_explanations.json"
mvf "$V/stage7_final_calibration.json"    "$S/final/calibration.json"
mvf "$V/stage7_final_manifest.sha256"     "$S/final/manifest.sha256"   # stage 7F rewrites this file with the final paths

# everything else is audit evidence
for f in "$S"/*; do
  [ -f "$f" ] && mvf "$f" "$S/audit/$(basename "$f")"
done
if [ -d "$V" ]; then
  for f in "$V"/*; do
    [ -f "$f" ] && mvf "$f" "$S/audit/corrections_$(basename "$f")"
  done
  rmdir "$V" 2>/dev/null || true
fi

echo; echo "stage7/final:"; ls -1 "$S/final"
echo; echo "stage7/audit:"; ls -1 "$S/audit"
