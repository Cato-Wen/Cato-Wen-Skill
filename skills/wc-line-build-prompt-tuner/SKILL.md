---
name: wc-line-build-prompt-tuner
description: |
  Iteratively tune the WC_LINE_BUILD_AGENT system prompt by running real menu items through the local /bo/agent/generate-wc-line-build endpoint and comparing LLM output to prod baseline. Use when the user mentions "tune prompt", "调 prompt", "compare LLM vs prod line build", "wc line build 准确率", "generate-wc-line-build 准确率", "迭代 prompt", or provides a sheet like Activity_Classification.

  Triggers when user says:
  - "测试 prompt 准确性"
  - "跑下 wc line build 准确率"
  - "对比 LLM 输出和 prod 配置"
  - "迭代修改 prompt 直到准确"
  - "调 wc-line-build-agent 的 prompt"
---

# WC Line Build Agent Prompt Tuner

End-to-end loop: **read prod baseline → call local API → compare → adjust prompt → reseed → re-run** until LLM output matches prod line build config.

## Hard rules (read first)

1. **prod (`mongodb-prod_*`) is READ-ONLY**. Never call any prod write tool (`insert/update/delete/aggregate-with-out`). All writes go to `mongodb-local_*` only.
2. **Local agent collections live in `mongodb-local` db = `recipe-agent`**; prod menu data lives in `mongodb-prod` db = `recipe-v2`.
3. **Each HTTP request needs a unique `chat_session_id`** (use `uuid.uuid4().hex[:12]` per call). Reusing one ID makes ADK reuse session memory → wrong test.
4. **The three target brands**: `Royal Greens` / `Limesalt` / `Yasas by Michael Symon`. Only menu items whose `brand_names` intersect with these are valid inputs.
5. **Prompt `_id`** in `recipe-agent.agent_instruction_configs` is `7b4f1c9a-1d8e-4f2a-9c3b-5e6f7a8b9c0d` (`instruction_name = LINE_BUILD_FILLER`).
6. Refresh after each prompt update: `curl -sk -X PUT https://127.0.0.1:5097/bo/agent/refresh`. If service has prompt cache issues, ask user to restart instead.

## Standard loop (one iteration)

```
1. Pick test set
   └─ Use wc_item=true menu items from recipe-agent.item_version_line_build_cook_methods
      (60 items covers all three brands proportionally; sufficient for prompt regression)

2. Pull prod baseline
   └─ Export recipe-v2.item_versions for the selected _id list, keeping item_line_build
   └─ Save raw export + compact baseline (first line_build's first task only) for diffing

3. Seed current prompt draft into local mongo + refresh
   └─ scripts/seed_prompt.py reads prompt md file and updates the instruction text
   └─ Then curl PUT /bo/agent/refresh

4. Run the endpoint in parallel (8 workers ≈ 160s for 60 items)
   └─ scripts/runner_parallel.py calls PUT /bo/agent/generate-wc-line-build
      (unique chat_session_id per call), polls generate_wc_line_build_logs until
      succeed_time != null, then dumps llm_response_json + skeleton_json to JSON

5. Compare LLM output vs baseline
   └─ scripts/compare.py:
      - GARNISH / COMPLETE: positional match within activity bucket
      - COOK: match by first procedure_step.related_item_number (skeleton vs prod may
        order COOK procedures differently); fall back to positional for placeholder COOKs
      - title comparison is case-insensitive, trimmed
   └─ Outputs per-field accuracy table + grouped mismatch list

6. Inspect mismatches → adjust prompt md
   └─ Categorize by activity+field; prioritize highest-volume systematic issues
   └─ Patch the prompt md file (RULE 1 / RULE 2 / brand priority etc.)

7. Repeat from step 3 until accuracy plateaus
```

Salad-heavy traffic: this endpoint's live requests are dominated by salad menus. Always sanity-check `BYO Greens Bowl, Royal Greens` + `Salad (BYO), Limesalt` + Yasas spreads before declaring a prompt version stable.

## Quick Usage

All scripts read/write a single output directory. By default that's `./prompt-tuner-out/`
relative to wherever you run python from; override with the `PROMPT_TUNER_OUT_DIR`
environment variable for any other layout.

```bash
# Pick your output directory (one-time, optional)
export PROMPT_TUNER_OUT_DIR=/path/to/your/workspace/tuner-out
```

The skill assumes the agent service is running locally at
`https://127.0.0.1:5097` with MongoDB at `mongodb://localhost:27017`. Adjust the
constants at the top of each script if your setup differs.

### Pull baseline

```bash
# 1. Pull the wc_item=true menu list from your local mongo (one-off setup helper):
python -c "from pymongo import MongoClient; \
  c = MongoClient('mongodb://localhost:27017')['recipe-agent']['item_version_line_build_cook_methods']; \
  ids = sorted({m['menu_item_number'] for r in c.find({}) for m in r['methods'] if m.get('wc_item')}); \
  import json, os; \
  os.makedirs(os.environ.get('PROMPT_TUNER_OUT_DIR', 'prompt-tuner-out'), exist_ok=True); \
  open(os.path.join(os.environ.get('PROMPT_TUNER_OUT_DIR', 'prompt-tuner-out'), 'wc_item_numbers.json'), 'w').write(json.dumps(ids))"

# 2. Use mongo-prod MCP tool (or pull_baseline.py with --prod-uri) to resolve those
#    item_numbers to current effective item_version_ids, save as <out>/ivids.json
#    (a JSON list of strings — one item_version_id per element).

# 3. Pull the baseline from prod (read-only):
python scripts/pull_baseline.py --ivids "$PROMPT_TUNER_OUT_DIR/ivids.json" --prod-uri "$PROD_MONGO_URI"
# Produces: <out>/baseline-raw.json + <out>/baseline.json
```

### Seed prompt md → mongo + refresh

```bash
python scripts/seed_prompt.py --prompt path/to/your-prompt.md
curl -sk -X PUT https://127.0.0.1:5097/bo/agent/refresh
```

### Parallel run + compare

```bash
rm -f "$PROMPT_TUNER_OUT_DIR/llm-output.json"
python scripts/runner_parallel.py --workers 8
python scripts/compare.py
```

### Inspect a single item

```bash
python scripts/show_item.py --name "Salad (BYO), Limesalt"
```

## Common Gotchas

- **HTTP method is `PUT` not POST** on `/bo/agent/generate-wc-line-build`. Returns 204 + async kafka.
- **Endpoint is async**: polling `generate_wc_line_build_logs.{succeed_time|fail_time}` is the only way to know when done. Default poll = 3s, timeout = 300s.
- **brand_names mismatch ≠ multi-brand bug**: a menu item routinely belongs to 5+ brands; the rule is first-match in priority order (`Limesalt > Yasas > Royal Greens`). Salad menus override to Royal Greens by default.
- **Placeholder COOK procedures** (where `related_item_number = null`) cannot be inferred from cook_methods samples — LLM will guess wrong (e.g. Quesadilla family). Either add a hardcoded fallback to the prompt or change the skeleton builder.
- **Schema constraint**: Gemini's controlled generation rejects `anyOf` siblings — see `LineBuildFillResultSchema.procedureSchema()`. Don't add `type`/`description` next to `anyOf`.
- **`cook_methods` regeneration**: if you change `TARGET_ACTIVITIES` / `HDR_OBJECT_TYPES` in `InitItemVersionLineBuildCookMethodController`, restart the service and call `PUT /_app/agent/item-version-line-build-cook-method/init` before running the loop.
- **`wc_item=true` filter**: the init script tags a method with `wc_item=true` iff its brand_names intersects with `["Royal Greens", "Limesalt", "Yasas by Michael Symon"]`. Pre-filter your test set with this flag.

## Output directory layout

Everything the scripts read/write lives under one directory (default `./prompt-tuner-out/`,
override via `PROMPT_TUNER_OUT_DIR`):

| File | Producer | Purpose |
|---|---|---|
| `ivids.json` | user / one-off helper | JSON list of `item_version_id` to test |
| `baseline-raw.json` | `pull_baseline.py` | Full prod `item_versions` documents (for skeleton checks) |
| `baseline.json` | `pull_baseline.py` | Compact view used by runner + compare |
| `llm-output.json` | `runner_parallel.py` | Per-item LLM response + skeleton + log metadata |
| `mismatches.json` | `compare.py` | Per-field mismatch dump |

Backend code locations the scripts reference (paths inside the consuming repo):

| Relative path | Purpose |
|---|---|
| `backend/master-data-agent-service/src/main/java/app/agent/builder/WCLineBuildBuilder.java` | Skeleton generation (COOK / GARNISH / COMPLETE) |
| `backend/master-data-agent-service/src/main/java/app/agent/service/WCLineBuildCookMethodResolver.java` | Loads cook_methods hits + appliance catalog |
| `backend/master-data-agent-service/src/main/java/app/agent/web/controller/InitItemVersionLineBuildCookMethodController.java` | Builds `item_version_line_build_cook_methods` from prod menu items |
| `backend/master-data-agent-service/src/main/java/app/agent/agent/schema/LineBuildFillResultSchema.java` | Gemini response schema (anyOf per activity) |

## First-Time Setup (If Not Configured)

1. Ensure local service is running on `https://127.0.0.1:5097` with mongo on `mongodb://localhost:27017`.
2. Confirm `recipe-agent.agent_instruction_configs` has the LINE_BUILD_FILLER document (`_id = 7b4f1c9a-...`).
3. Confirm `recipe-agent.item_version_line_build_cook_methods` is populated. If empty, call `PUT /_app/agent/item-version-line-build-cook-method/init`.
4. `pip install --user pymongo` (the only Python dep; uses stdlib `urllib` + `ssl` for HTTP).
5. Set prod mongo MCP credentials in agent config (read-only).
