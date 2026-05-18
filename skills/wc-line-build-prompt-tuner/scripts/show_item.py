"""Inspect one item's skeleton + LLM output side-by-side with the prod baseline."""
import argparse
import json
import os
import sys


def default_out_dir():
    return os.environ.get("PROMPT_TUNER_OUT_DIR") or os.path.join(os.getcwd(), "prompt-tuner-out")


def main():
    out_dir = default_out_dir()
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="Substring match against item name")
    ap.add_argument("--id", help="Exact item_version_id")
    ap.add_argument("--llm-output", default=os.path.join(out_dir, "llm-output.json"),
                    help="LLM run output (default: $PROMPT_TUNER_OUT_DIR/llm-output.json)")
    ap.add_argument("--baseline", default=os.path.join(out_dir, "baseline.json"),
                    help="Compact baseline (default: $PROMPT_TUNER_OUT_DIR/baseline.json)")
    args = ap.parse_args()

    if not args.name and not args.id:
        print("ERROR: provide --name or --id", file=sys.stderr)
        sys.exit(2)

    with open(args.llm_output, "r", encoding="utf-8") as f:
        out = json.load(f)
    with open(args.baseline, "r", encoding="utf-8") as f:
        base_list = json.load(f)
    base = {b["_id"]: b for b in base_list}

    matches = []
    for r in out:
        if args.id and r["item_version_id"] == args.id:
            matches.append(r)
        elif args.name and args.name.lower() in (r.get("name") or "").lower():
            matches.append(r)

    if not matches:
        print("no matches found")
        return

    for r in matches:
        ivid = r["item_version_id"]
        b = base.get(ivid)
        print(f"\n=== {r['name']}  ({ivid})  status={r['status']}  retry={r.get('retry_count')}")

        sk_raw = r.get("skeleton_json")
        if sk_raw:
            sk = json.loads(sk_raw) if isinstance(sk_raw, str) else sk_raw
            print("\n  --- SKELETON ---")
            for lb in sk.get("line_builds", []):
                for t in lb.get("tasks", []):
                    for p in t.get("procedures", []):
                        steps = [(s.get("related_item_number"), s.get("related_item_name"))
                                 for s in p.get("procedure_steps", [])]
                        print(f"    {p['activity']:8s} order={p.get('order')} steps={steps}")

        llm = r.get("llm_response_json")
        if llm:
            llm = json.loads(llm) if isinstance(llm, str) else llm
            print("\n  --- LLM RESPONSE ---")
            for p in llm.get("procedures", []):
                extras = " ".join(f"{k}={v}" for k, v in p.items()
                                  if k in ("hold_usage_seconds", "parking_spot",
                                           "appliance", "cooking_usage_seconds",
                                           "batch_limit", "appliance_config_id") and v is not None)
                titles = [s.get("title") for s in p.get("procedure_steps", [])]
                print(f"    {p['activity']:8s} step={p.get('step_usage_seconds')} "
                      f"{extras}  titles={titles}")

        if b:
            print("\n  --- PROD BASELINE (first line_build only) ---")
            for p in b["procedures"][:25]:
                extras = " ".join(f"{k}={v}" for k, v in p.items()
                                  if k in ("hold_usage_seconds", "parking_spot",
                                           "appliance", "cooking_usage_seconds",
                                           "batch_limit", "appliance_config_id") and v is not None)
                titles = [s.get("title") for s in p.get("procedure_steps", [])]
                print(f"    {p['activity']:8s} order={p.get('order'):>2} step={p.get('step_usage_seconds')} "
                      f"{extras}  titles={titles[:3]}{'...' if len(titles) > 3 else ''}")


if __name__ == "__main__":
    main()
