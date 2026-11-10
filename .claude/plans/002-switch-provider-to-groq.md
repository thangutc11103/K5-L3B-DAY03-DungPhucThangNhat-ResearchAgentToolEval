# Plan 002: Switch default provider to Groq (`openai/gpt-oss-120b`)

- **Status**: Completed
- **Date**: 2026-11-10 | **Subagents**: none
- **Target Components**: `starter_v0/providers/`, `chat.py`, `run_eval.py`, `scripts/preflight_provider.py`, `app.py`, `.env.example`, docs

---

## 1. Objective & Scope
Make Groq + `openai/gpt-oss-120b` the default model provider everywhere. Keep the other providers selectable.
- **Layers Affected**: provider adapter, CLI/UI entry points, docs
- **Observability Impact**: runs/transcripts record `provider=groq`, `model=openai/gpt-oss-120b`

---

## 2. Implementation Steps
- [x] **Step 1: Adapter** - new `providers/groq_provider.py`. It subclasses `OpenAIProvider` (Groq has an OpenAI-compatible API), with `GROQ_API_KEY`, base URL `GROQ_BASE_URL` (default `https://api.groq.com/openai/v1`) and default model `openai/gpt-oss-120b`. Register `"groq"` in `make_provider`.
- [x] **Step 2: Entry points** - add `groq` first in the `--provider` choices and make `default="groq"` (no longer required) in `chat.py`, `run_eval.py` and `scripts/preflight_provider.py`. In `app.py`, put `groq` first in `PROVIDERS`.
- [x] **Step 3: Env** - in `.env.example`, add `GROQ_API_KEY=` + `# GROQ_BASE_URL=` as the recommended provider. You add the real key to `.env` yourself; I will not touch `.env`.
- [x] **Step 4: Docs** - change `--provider openrouter` → `--provider groq` in `README.md`, `starter_v0/README.md`, `CHECKPOINTS.md` and `docs/TOOL-SETUP.md`, and add `GROQ_API_KEY` to the key lists (`RULES.md`, `docs/TOOL-SETUP.md`).

---

## 3. Verification Checklist
- [x] `pytest` green
- [x] `python -c "from providers import make_provider; p=make_provider('groq'); print(p.default_model)"`
- [x] `python scripts/preflight_provider.py --provider groq` passes (needs `GROQ_API_KEY` in `.env`)
- [x] `streamlit run app.py --server.headless true` shows provider `groq`, model `openai/gpt-oss-120b`

---

## 4. Completion Summary
- **Completed**: 2026-11-10 | **Deliverables**: `providers/groq_provider.py`, `providers/__init__.py` (PROVIDER_CHOICES/DEFAULT_PROVIDER), chat.py, run_eval.py, preflight, app.py, .env.example, docs
- **Notes**: Live preflight OK (groq, openai/gpt-oss-120b, tool=timeline). pytest 62 passed. Model overridable via GROQ_MODEL or --model.
