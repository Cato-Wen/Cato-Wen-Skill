"""Parallel runner for /bo/agent/generate-wc-line-build.

Reads a baseline JSON list (each element has `_id` + `name`), fires up to `--workers`
concurrent PUT requests, polls `recipe-agent.generate_wc_line_build_logs` for each
chat_session_id until succeed_time / fail_time appears, and writes the per-item LLM
response + skeleton + log metadata into a single output JSON.

Each call uses a unique chat_session_id (uuid4 hex prefix) — required by ADK to avoid
session memory reuse.

Resumable: if `--output` already exists and contains items with status=ok, those are
skipped on the next run.
"""
import argparse
import json
import os
import ssl
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pymongo import MongoClient  # type: ignore

ENDPOINT = "https://127.0.0.1:5097/bo/agent/generate-wc-line-build"
LOCAL_MONGO_URI = "mongodb://localhost:27017"
DB = "recipe-agent"
LOG_COLL = "generate_wc_line_build_logs"
POLL_INTERVAL_SEC = 3
POLL_TIMEOUT_SEC = 300

USER_INFO = {
    "user_id": "12345600",
    "user_name": "1145600",
    "user_email": "224560",
    "user_permission": {
        "is_super_admin": True,
        "is_admin": False,
        "owner_app_codes": [],
        "roles": [],
        "permission_codes": [],
    },
}


def call(ivid: str, csid: str):
    body = json.dumps({
        "item_version_id": ivid,
        "user_info": USER_INFO,
        "chat_session_id": csid,
    }).encode("utf-8")
    req = Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="PUT")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urlopen(req, context=ctx, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except URLError as e:
        return -1, f"URLError: {e}"


def process_item(item: dict, mongo_uri: str) -> tuple[str, dict]:
    """Run one item end-to-end: PUT + poll mongo log until terminal status."""
    ivid = item["_id"]
    csid = f"v5p-{uuid.uuid4().hex[:12]}"
    code, body = call(ivid, csid)
    if code not in (200, 202, 204):
        return ivid, {"item_version_id": ivid, "name": item.get("name"),
                      "chat_session_id": csid, "status": "http_error",
                      "http_code": code, "http_body": body[:1000]}
    # Each thread uses its own MongoClient — avoids pool contention on the global default client.
    cli = MongoClient(mongo_uri)
    coll = cli[DB][LOG_COLL]
    end = time.time() + POLL_TIMEOUT_SEC
    log = None
    while time.time() < end:
        doc = coll.find_one({"chat_session_id": csid}, sort=[("created_time", -1)])
        if doc and (doc.get("succeed_time") or doc.get("fail_time")):
            log = doc
            break
        time.sleep(POLL_INTERVAL_SEC)
    cli.close()
    if log is None:
        return ivid, {"item_version_id": ivid, "name": item.get("name"),
                      "chat_session_id": csid, "status": "timeout"}
    base = {
        "item_version_id": ivid, "name": item.get("name"),
        "chat_session_id": csid,
        "retry_count": log.get("retry_count"),
        "validation_errors": log.get("validation_errors"),
        "llm_response_json": log.get("llm_response_json"),
        "skeleton_json": log.get("skeleton_json"),
    }
    base["status"] = "ok" if log.get("succeed_time") else "failed"
    return ivid, base


def default_out_dir():
    """Output directory for shared baseline + LLM run files.

    Resolution order:
      1. PROMPT_TUNER_OUT_DIR environment variable (absolute or relative path)
      2. ./prompt-tuner-out under the current working directory
    """
    return os.environ.get("PROMPT_TUNER_OUT_DIR") or os.path.join(os.getcwd(), "prompt-tuner-out")


def main():
    out_dir = default_out_dir()
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=os.path.join(out_dir, "baseline.json"),
                    help="JSON list of {_id, name} test items (default: $PROMPT_TUNER_OUT_DIR/baseline.json)")
    ap.add_argument("--output", default=os.path.join(out_dir, "llm-output.json"),
                    help="Per-item LLM result dump (default: $PROMPT_TUNER_OUT_DIR/llm-output.json)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="Process at most N items (0 = all)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    with open(args.baseline, "r", encoding="utf-8") as f:
        baseline = json.load(f)
    targets = baseline[: args.limit] if args.limit > 0 else baseline

    existing: dict[str, dict] = {}
    if os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            existing = {r["item_version_id"]: r for r in json.load(f)}

    pending = [it for it in targets if existing.get(it["_id"], {}).get("status") != "ok"]
    cached = len(targets) - len(pending)
    print(f"pending: {len(pending)}/{len(targets)} (already-ok: {cached})  workers={args.workers}",
          flush=True)

    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process_item, it, LOCAL_MONGO_URI): it for it in pending}
        for fut in as_completed(futures):
            ivid, entry = fut.result()
            existing[ivid] = entry
            done += 1
            print(f"[{done}/{len(pending)}] {entry['status']:8s} "
                  f"retry={entry.get('retry_count', '-')}  {entry['name']}",
                  flush=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(list(existing.values()), f, ensure_ascii=False, indent=2)
    ok = sum(1 for r in existing.values() if r["status"] == "ok")
    print(f"\nDONE: {ok}/{len(existing)} ok in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
