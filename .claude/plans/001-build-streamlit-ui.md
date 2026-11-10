# Plan 001: Step 2 — Streamlit UI `starter_v0/app.py`

- **Status**: In Progress
- **Date**: 2026-11-10 | **Subagents**: none (small, single-file task)
- **Target Components**: `starter_v0/app.py` (new), `starter_v0/requirements.txt`

---

## 1. Objective & Scope
Streamlit chat UI wrapping `chat.run_model_tool_loop` for the showdown (rubric C6 / CP5). Tool errors are always visible, and each turn is saved as a `transcripts/*.transcript.json` in the `chat.py` format.
- **Layers Affected**: UI only (reuses `chat.py`, `providers`, `tools`, `versioning`)
- **Observability Impact**: Transcripts per UI session (B4 evidence)

---

## 2. Implementation Steps
- [x] **Step 1: Dependency** - `streamlit` in `starter_v0/requirements.txt`
- [x] **Step 2: Reuse chat.py helpers** - imports, no duplicated loop
- [x] **Step 3: Sidebar config** - provider, model, version, history window, max rounds, New chat
- [x] **Step 4: Session state** - history, display turns, transcript
- [x] **Step 5: Chat turn** - run loop, append history, save transcript, provider_error handling
- [x] **Step 6: Tool visibility** - expander per tool call; errors shown via `st.error` outside the expander
- [x] **Step 7: Missing keys** - friendly provider init error

---

## 3. Verification Checklist
- [x] `streamlit run app.py` loads at http://localhost:8501
- [ ] Normal request, vague request then follow-up, and a "send to Telegram" request needing confirmation
- [x] Tool error visible without expanding; "New chat" makes a new transcript
- [x] `pytest` green; no `.env` or keys in `git status` / `transcripts/`

---

## 4. Completion Summary
- **Completed**: 2026-11-10 (code) | **Deliverables**: `starter_v0/app.py`, `starter_v0/requirements.txt`
- **Notes**: Verified with a fake provider (AppTest) + server boot + pytest 62 passed. Live 3-turn check with real keys still pending.
