"""Seed a prompt markdown file into local mongo's LINE_BUILD_FILLER instruction.

Usage:
    python seed_prompt.py --prompt <path-to-md-file>

Extracts the prompt body starting at the heading
"# WC Line Build Filler — System Prompt (V4)" (skipping any front-matter / metadata
section above it) and writes it to:
    recipe-agent.agent_instruction_configs._id = 7b4f1c9a-1d8e-4f2a-9c3b-5e6f7a8b9c0d

Caller is expected to PUT /bo/agent/refresh afterwards (or restart the service).
"""
import argparse
import json
import sys

from pymongo import MongoClient  # type: ignore

INSTRUCTION_ID = "7b4f1c9a-1d8e-4f2a-9c3b-5e6f7a8b9c0d"
LOCAL_MONGO_URI = "mongodb://localhost:27017"
DB = "recipe-agent"
COLL = "agent_instruction_configs"
PROMPT_MARKER = "# WC Line Build Filler — System Prompt (V4)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="Path to the prompt markdown file")
    ap.add_argument("--marker", default=PROMPT_MARKER,
                    help="Heading marker that starts the prompt body (everything before it is dropped)")
    args = ap.parse_args()

    with open(args.prompt, "r", encoding="utf-8") as f:
        md = f.read()
    idx = md.find(args.marker)
    if idx < 0:
        print(f"ERROR: marker not found in prompt file: {args.marker!r}", file=sys.stderr)
        sys.exit(2)
    text = md[idx:].rstrip() + "\n"

    client = MongoClient(LOCAL_MONGO_URI)
    res = client[DB][COLL].update_one(
        {"_id": INSTRUCTION_ID},
        {"$set": {"text": text}},
    )
    client.close()
    print(json.dumps({
        "matched": res.matched_count,
        "modified": res.modified_count,
        "text_len": len(text),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
