"""Compare LLM output vs prod baseline per field.

Baseline source: each entry's first line_build's first task procedures (canonical
build for the menu). Both sides are grouped by activity (GARNISH / COOK / COMPLETE).

Matching policy:
- COOK: match by first procedure_step.related_item_number when present (skeleton may
  reorder COOK procedures differently from prod). Placeholder COOKs (related_item =
  null) fall back to positional matching.
- GARNISH / COMPLETE: positional within activity bucket.
- step_title: case-insensitive trimmed string equality.

Writes per-field accuracy table to stdout and dumps detailed mismatches to JSON.
"""
import argparse
import json
import os
from collections import Counter, defaultdict


def default_out_dir():
    """Output directory for shared baseline + LLM run files.

    Resolution order:
      1. PROMPT_TUNER_OUT_DIR environment variable (absolute or relative path)
      2. ./prompt-tuner-out under the current working directory

    Keeping the path relative makes the skill portable across machines — the user
    just `cd`s into their workspace and runs the scripts, with all artifacts landing
    under one folder they can git-ignore or share.
    """
    return os.environ.get("PROMPT_TUNER_OUT_DIR") or os.path.join(os.getcwd(), "prompt-tuner-out")


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def baseline_first_task(raw_path):
    """Reduce the raw prod export to {_id -> {name, procedures of first line_build's first task}}."""
    with open(raw_path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    out = {}
    for d in docs:
        lbs = (d.get("item_line_build") or {}).get("line_builds") or []
        if not lbs:
            continue
        tasks = lbs[0].get("tasks") or []
        if not tasks:
            continue
        out[d["_id"]] = {"name": d.get("name"), "procedures": tasks[0].get("procedures") or []}
    return out


def title_norm(s):
    return (s or "").strip().lower()


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

    base = baseline_first_task(args.baseline_raw)
    llm_out = load(args.llm_output)

    total = Counter()
    matched = Counter()
    mismatches = []

    for entry in llm_out:
        if entry["status"] != "ok":
            continue
        ivid = entry["item_version_id"]
        b = base.get(ivid)
        if not b:
            continue
        name = b["name"]
        llm = entry["llm_response_json"]
        if isinstance(llm, str):
            llm = json.loads(llm)

        llm_groups = defaultdict(list)
        for p in sorted(llm.get("procedures") or [], key=lambda x: x.get("order") or 0):
            llm_groups[p.get("activity")].append(p)
        base_groups = defaultdict(list)
        for p in sorted(b["procedures"], key=lambda x: x.get("order") or 0):
            base_groups[p.get("activity")].append(p)

        for act in ("GARNISH", "COOK", "COMPLETE"):
            la = llm_groups.get(act, [])
            ba = base_groups.get(act, [])

            if act == "COOK":
                pairs = _pair_cook(la, ba)
            else:
                n = min(len(la), len(ba))
                pairs = [(i, la[i], ba[i]) for i in range(n)]

            for i, lp, bp in pairs:
                if bp is None:
                    continue
                _diff_fields(act, i, lp, bp, total, matched, mismatches, name)
                _diff_step_titles(act, i, lp, bp, total, matched, mismatches, name)

    _print_report(total, matched)
    with open(args.mismatches_out, "w", encoding="utf-8") as f:
        json.dump(mismatches, f, ensure_ascii=False, indent=2)
    print(f"\n{len(mismatches)} mismatches written to {args.mismatches_out}")


def _pair_cook(la, ba):
    """Match COOK procedures by first step's related_item_number; fall back to positional."""
    def rel_of(p):
        steps = p.get("procedure_steps") or []
        return steps[0].get("related_item_number") if steps else None

    base_by_rel = defaultdict(list)
    for bp in ba:
        r = rel_of(bp)
        if r is not None:
            base_by_rel[r].append(bp)
    remaining_base = [b for b in ba if rel_of(b) is None]
    rb_iter = iter(remaining_base)

    pairs = []
    for i, lp in enumerate(la):
        r = rel_of(lp)
        if r is not None and base_by_rel.get(r):
            pairs.append((i, lp, base_by_rel[r].pop(0)))
        else:
            pairs.append((i, lp, next(rb_iter, None)))
    return pairs


def _diff_fields(act, i, lp, bp, total, matched, mismatches, name):
    fields = ["step_usage_seconds"]
    if act == "COMPLETE":
        fields += ["hold_usage_seconds", "parking_spot"]
    elif act == "COOK":
        fields += ["appliance", "cooking_usage_seconds", "batch_limit"]
        if lp.get("appliance") in {"PIZZA_CONVEYOR_OVEN", "TURBO_OVEN"} \
                or bp.get("appliance") in {"PIZZA_CONVEYOR_OVEN", "TURBO_OVEN"}:
            fields.append("appliance_config_id")
    for f in fields:
        total[(act, f)] += 1
        if lp.get(f) == bp.get(f):
            matched[(act, f)] += 1
        else:
            mismatches.append({"item": name, "activity": act, "i": i, "field": f,
                               "llm": lp.get(f), "baseline": bp.get(f)})


def _diff_step_titles(act, i, lp, bp, total, matched, mismatches, name):
    lps = lp.get("procedure_steps") or []
    bps = bp.get("procedure_steps") or []
    m = min(len(lps), len(bps))
    for j in range(m):
        total[(act, "step_title")] += 1
        if title_norm(lps[j].get("title")) == title_norm(bps[j].get("title")):
            matched[(act, "step_title")] += 1
        else:
            mismatches.append({"item": name, "activity": act, "i": i, "step_j": j,
                               "field": "step_title",
                               "llm": lps[j].get("title"),
                               "baseline": bps[j].get("title")})


def _print_report(total, matched):
    print(f"\n{'activity':10s} {'field':25s} {'m/total':>15s}  pct")
    print("-" * 65)
    for k in sorted(total.keys()):
        m, t = matched[k], total[k]
        pct = 100 * m / t if t else 0
        print(f"{k[0]:10s} {k[1]:25s} {m:>7d}/{t:<7d}  {pct:5.1f}%")


if __name__ == "__main__":
    main()
