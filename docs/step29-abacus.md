# Step 29 — Abacus RouteLLM

SkyFlow now supports Abacus alongside OpenAI. Abacus uses its self-serve endpoint at `https://routellm.abacus.ai/v1/chat/completions`, a separate `ABACUS_API_KEY`, and default model `route-llm`. Enterprise workspace endpoints are not configured by this adapter.

## Setup on this Mac

```bash
cd ~/Projects/skyflow
source .venv/bin/activate
python scripts/configure_abacus.py
```

Paste your Abacus RouteLLM API key at the hidden prompt. It is saved to the private, Git-ignored `.env` file. Do not paste keys into chat. Existing OpenAI credentials are not repurposed or sent to Abacus.

First test the API with synthetic evidence:

```bash
unset ABACUS_API_KEY
python src/agent/diagnose.py --demo --ai --provider abacus
```

Then read live BigQuery monitoring and generate an explanation:

```bash
python src/agent/diagnose.py --ai --provider abacus
```

Expected fields: `ai_status: completed` and `provider: abacus`. Calls consume Abacus API credits/quota. Demo and live-monitoring calls were confirmed in user-provided screenshots on November 15, 2026. These validate the diagnostic integration, not a fresh batch or streaming run.

Your previously shown custom router can be selected explicitly if it still exists in your account:

```bash
python src/agent/diagnose.py --ai --provider abacus --model custom_rishi-s-coding-assistant
```

The default route-llm avoids depending on that unverified custom router. OpenAI continues to work with `--provider openai` and `OPENAI_API_KEY`.

## Scope

Only the bounded diagnostic findings are sent to the selected provider. No raw flight rows, API keys, raw error logs or Terraform state are included in the prompt. Requests have timeouts, a 1,000-token output limit and a strict JSON schema. Incomplete results, refusals and tool calls are rejected. No tools or server-side Abacus tools are supplied. Data processing/retention follows the selected provider's policies; this adapter does not promise zero retention.

Tests cover the two API formats, provider credential separation, incomplete replies and safe authentication messages. Mocked tests do not prove account access or available credits.

Official reference: https://api.abacus.ai/help/route-llm/chat-completions/
