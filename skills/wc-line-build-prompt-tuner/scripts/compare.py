"""Compare LLM output vs prod baseline, print stdout summary, dump mismatches.json.

Shares all matching/diff logic with excel_report.py so terminal stats are identical
to what excel_report.py writes into the Summary sheet.

Matching policy (applies to both procedure-level and step-level pairing):
  Phase 1: pair by related_item_number when present on both sides.
  Phase 2: positional fallback on whatever's left.

Note on related_item_number:
  - prod's `procedure_steps[].related_item_number` is authoritative (anchor to ingredient/menu)
  - LLM's `procedure_steps[].related_item_number` is ALWAYS null in the raw response (the
    Gemini schema doesn't ask the LLM to fill it). excel_report.build_data() enriches the
    LLM procs in-place with rels from `generate_wc_line_build_logs.skeleton_json` before
    running comparisons. Without this enrichment the rel-first pairing degrades to pure
    positional and you get false positives (e.g. '4oz Portion Cup' vs 'Queso Blanco').

Verdict tiers (matches excel_report.py):
  match       - llm == prod
  严重预警    - functional fields off (hold_usage_seconds, parking_spot, appliance,
                cooking_usage_seconds, batch_limit, appliance_config_id)
  轻量预警    - cosmetic / minor (step_usage_seconds, step_title with rel)
  参考        - COOK/GARNISH step_title where one side has no rel → excluded from stats
                (packaging / sleeve naming drift is allowed)
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

# Same directory import — both scripts live in skill/scripts/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_report import (  # type: ignore
    build_data,
    MATCH_VERDICT, SEVERE_VERDICT, LIGHT_VERDICT, REFERENCE_VERDICT,
)


def default_out_dir():
    return os.environ.get("PROMPT_TUNER_OUT_DIR") or os.path.join(os.getcwd(), "prompt-tuner-out")


def main():
    out_dir = default_out_dir()
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-raw", default=os.path.join(out_dir, "baseline-raw.json"),
                    help="Prod baseline raw export (default: $PROMPT_TUNER_OUT_DIR/baseline-raw.json)")
    ap.add_argument("--llm-output", default=os.path.join(out_dir, "llm-output.json"),
                    help="LLM run output (default: $PROMPT_TUNER_OUT_DIR/llm-output.json)")
    ap.add_argument("--mismatches-out", default=os.path.join(out_dir, "mismatches.json"),
                    help="Per-field mismatch dump (default: $PROMPT_TUNER_OUT_DIR/mismatches.json)")
    args = ap.parse_args()

    data = build_data(args.baseline_raw, args.llm_output)

    # ---- Per-field accuracy (matches Summary sheet of excel_report.py) -----
    bucket = defaultdict(lambda: [0, 0])  # (activity, field) -> [match, total_excluding_reference]
    ref_count = 0
    severe_total = light_total = match_total = 0
    for r in data["details"]:
        v = r["verdict"]
        if v == REFERENCE_VERDICT:
            ref_count += 1
            continue
        # collapse step_title[N] / step_title[+N] / step_title[N] (LLM missing ...) -> step_title
        field_key = r["field"].split("[")[0].strip()
        bucket[(r["activity"], field_key)][1] += 1
        if v == MATCH_VERDICT:
            bucket[(r["activity"], field_key)][0] += 1
            match_total += 1
        elif v == SEVERE_VERDICT:
            severe_total += 1
        elif v == LIGHT_VERDICT:
            light_total += 1

    total_items = len(data["per_item"])
    fully_match = sum(1 for r in data["per_item"] if r["completely_match"])

    print(f"Items: {total_items}    完全一致: {fully_match}/{total_items} = {100*fully_match/total_items:.1f}%")
    print()
    print(f"{'activity':10s} {'field':25s} {'m/total':>15s}  pct")
    print("-" * 65)
    for k in sorted(bucket.keys()):
        m, t = bucket[k]
        pct = 100 * m / t if t else 0
        print(f"{k[0]:10s} {k[1]:25s} {m:>7d}/{t:<7d}  {pct:5.1f}%")
    print()
    print(f"verdict totals: match={match_total}  严重={severe_total}  轻量={light_total}  参考(excluded)={ref_count}")
    print(f"LLM-Unmatched (extra LLM procs): {len(data['llm_unmatched'])}")
    print(f"Prod-NotMatched (unpaired prod procs): {len(data['prod_notmatched'])}")

    # Dump mismatches (severe + light only) to JSON for further analysis
    mismatches = [r for r in data["details"] if r["verdict"] in (SEVERE_VERDICT, LIGHT_VERDICT)]
    with open(args.mismatches_out, "w", encoding="utf-8") as f:
        json.dump(mismatches, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n{len(mismatches)} mismatches written to {args.mismatches_out}")


if __name__ == "__main__":
    main()
