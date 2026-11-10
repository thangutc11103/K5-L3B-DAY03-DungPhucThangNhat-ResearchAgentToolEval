"""Streamlit UI for the Research Agent.

Run:  cd starter_v0 && streamlit run app.py
Reuses the multi-turn tool loop from chat.py (tools executed, results fed back,
clarify pauses for the user). Tool errors are always rendered, never hidden.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Importing chat also loads .env via load_lab_env(ROOT).
from chat import (
    ARTIFACTS_DIR,
    ROOT,
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import PROVIDER_CHOICES, make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDERS = PROVIDER_CHOICES  # "groq" first = default
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

STATUS_LABELS = {
    "answered": "✅ answered",
    "waiting_for_user": "❓ waiting for your reply",
    "max_tool_rounds": "⚠️ stopped: max tool rounds",
    "provider_error": "❌ provider error",
}

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_provider(name: str) -> Any:
    return make_provider(name)


@st.cache_resource(show_spinner=False)
def get_openai_tools(tools_path: str, _mtime: float) -> list[dict[str, Any]]:
    return to_openai_tools(load_tool_declarations(Path(tools_path)))


def tool_error(result: Any) -> str | None:
    """Return an error description if a tool result signals failure."""
    if not isinstance(result, dict):
        return None
    if result.get("error"):
        message = result.get("message") or ""
        return f"{result['error']}: {message}".rstrip(": ")
    if result.get("ok") is False or str(result.get("status", "")).lower() == "error":
        return str(result.get("message") or result.get("detail") or json_text(result, max_chars=500))
    return None


def new_transcript(provider: str, model: str | None, version: str, history_window: int, max_rounds: int) -> None:
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider), "ui", timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "source": "streamlit_app",
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.history = []
    st.session_state.display = []
    st.session_state.config_key = (provider, model, version, history_window, max_rounds)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        for round_record in turn.get("rounds", []):
            for event in round_record.get("tool_results", []):
                name = event.get("tool", "?")
                args = event.get("args", {})
                result = event.get("result")
                error = tool_error(result)
                if error:
                    # Shown outside the expander so tool errors are never hidden.
                    st.error(f"Tool `{name}` failed: {error}")
                with st.expander(f"🔧 {name}({json_text(args, max_chars=120)})", expanded=bool(error)):
                    st.markdown("**Args**")
                    st.code(json_text(args), language="json")
                    st.markdown("**Result**")
                    st.code(json_text(result, max_chars=20000), language="json")
        if turn.get("status") == "provider_error":
            st.error(f"Provider error: {turn.get('error')}")
        else:
            st.markdown(turn.get("assistant_text") or "_(empty response)_")
        st.caption(STATUS_LABELS.get(turn.get("status", ""), turn.get("status", "")))


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (blank = provider default)", value="").strip() or None
    version_label = st.text_input("Artifact version", value="v3").strip() or "v3"
    history_window = st.number_input("History window (turn pairs)", min_value=0, max_value=20, value=5)
    max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=10, value=4)
    new_chat = st.button("🆕 New chat", use_container_width=True)

config_key = (provider_name, model_input, version_label, int(history_window), int(max_tool_rounds))
if new_chat or "transcript" not in st.session_state or st.session_state.get("config_key") != config_key:
    new_transcript(provider_name, model_input, version_label, int(history_window), int(max_tool_rounds))

try:
    provider = get_provider(provider_name)
    provider_error: str | None = None
except Exception as exc:  # missing API key / SDK
    provider = None
    provider_error = f"{type(exc).__name__}: {exc}"

selected_model = model_input or getattr(provider, "default_model", None)
st.session_state.transcript["model"] = selected_model

with st.sidebar:
    st.caption(f"Model: `{selected_model}`")
    st.caption(f"artifact_version: `{st.session_state.transcript.get('artifact_version')}`")
    st.caption(f"Transcript: `{st.session_state.transcript_path.relative_to(ROOT)}`")

# ---------------- Main ----------------
st.title("🔎 Research Agent")
st.caption("Ask for research on accounts, keywords or URLs. Tool calls and their results (including errors) are shown below each answer.")

if provider_error:
    st.error(
        f"Cannot start provider `{provider_name}`: {provider_error}\n\n"
        "Check `starter_v0/.env` (copy from `.env.example`) and that the provider SDK is installed."
    )

for past_turn in st.session_state.display:
    render_turn(past_turn)

user_text = st.chat_input("Type your request…", disabled=provider is None)
if user_text and provider is not None:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tools = get_openai_tools(str(TOOLS_PATH), TOOLS_PATH.stat().st_mtime)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(history_window)),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    with st.spinner("Agent is working…"):
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=model_input,
                max_tool_rounds=int(max_tool_rounds),
            )
            turn.update(result)
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:
            turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn["ended_at"] = now_iso()

    st.session_state.transcript["turns"].append(turn)
    st.session_state.display.append(turn)
    try:
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    except OSError as exc:
        st.warning(f"Could not save transcript: {exc}")
    render_turn(turn)
