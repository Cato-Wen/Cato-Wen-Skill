"""Pull the prod baseline for a list of item_version_ids and write two files:
  - <out>-raw.json  : full prod item_versions documents (kept for skeleton comparison)
  - <out>.json      : compact view (id, item_number, name, flattened procedures across line_builds)

⚠️ This script requires READ-ONLY MongoDB access to prod. Provide the connection
string via --prod-uri (or set PROD_MONGO_URI env). Default uses no auth — adjust to
your env (typically read-only credentials are needed).
"""
import argparse
import json
import os

from pymongo import MongoClient  # type: ignore


def fetch(prod_uri: str, ivids: list[str]) -> list[dict]:
    cli = MongoClient(prod_uri)
    try:
        coll = cli["recipe-v2"]["item_versions"]
        docs = list(coll.find(
            {"_id": {"$in": ivids}},
            projection={"_id": 1, "item_number": 1, "name": 1, "item_line_build": 1},
        ))
        return docs
    finally:
        cli.close()


def compact(d: dict) -> dict:
    out = {"_id": d["_id"], "item_number": d.get("item_number"),
           "name": d.get("name"), "procedures": []}
    lb = d.get("item_line_build") or {}
    for line in (lb.get("line_builds") or []):
        for task in (line.get("tasks") or []):
            for p in (task.get("procedures") or []):
                steps = [{"id": s.get("id"),
                          "title": s.get("title"),
                          "related_item_number": s.get("related_item_number")}
                         for s in (p.get("procedure_steps") or [])]
                out["procedures"].append({
                    "id": p.get("id"), "order": p.get("order"), "activity": p.get("activity"),
                    "step_usage_seconds": p.get("step_usage_seconds"),
                    "hold_usage_seconds": p.get("hold_usage_seconds"),
                    "parking_spot": p.get("parking_spot"),
                    "appliance": p.get("appliance"),
                    "cooking_usage_seconds": p.get("cooking_usage_seconds"),
                    "batch_limit": p.get("batch_limit"),
                    "appliance_config_id": p.get("appliance_config_id"),
                    "procedure_steps": steps,
                })
    return out


def default_out_dir():
    """Output directory for shared baseline + LLM run files.

    Resolution order:
      1. PROMPT_TUNER_OUT_DIR environment variable
      2. ./prompt-tuner-out under the current working directory
    """
    return os.environ.get("PROMPT_TUNER_OUT_DIR") or os.path.join(os.getcwd(), "prompt-tuner-out")


def main():
    out_dir = default_out_dir()
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod-uri", default=os.environ.get("PROD_MONGO_URI", ""),
                    help="Read-only prod MongoDB URI (or set PROD_MONGO_URI env)")
    ap.add_argument("--ivids", required=True,
                    help="JSON file with a top-level list of item_version_ids (strings)")
    ap.add_argument("--out", default=os.path.join(out_dir, "baseline"),
                    help="Output path prefix (writes <out>-raw.json and <out>.json; "
                         "default: $PROMPT_TUNER_OUT_DIR/baseline)")
    args = ap.parse_args()

    if not args.prod_uri:
        raise SystemExit("ERROR: provide --prod-uri or PROD_MONGO_URI env (read-only)")

    with open(args.ivids, "r", encoding="utf-8") as f:
        ivids = json.load(f)
    if not isinstance(ivids, list) or not ivids:
        raise SystemExit("ERROR: --ivids file must contain a non-empty JSON list of strings")

    docs = fetch(args.prod_uri, ivids)
    raw_path = f"{args.out}-raw.json"
    out_path = f"{args.out}.json"
    os.makedirs(os.path.dirname(raw_path) or ".", exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2, default=str)
    compact_list = [compact(d) for d in docs]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(compact_list, f, ensure_ascii=False, indent=2)
    print(f"wrote {raw_path} ({len(docs)} docs)")
    print(f"wrote {out_path} ({sum(len(b['procedures']) for b in compact_list)} procedures)")


if __name__ == "__main__":
    main()
