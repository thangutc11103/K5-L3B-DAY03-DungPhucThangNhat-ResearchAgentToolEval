"""Streamlit UI for the Research Agent (ChatGPT-style layout).

Run:  cd starter_v0 && streamlit run app.py
Reuses the multi-turn tool loop from chat.py (tools executed, results fed back,
clarify pauses for the user). Tool errors are always rendered, never hidden.
"""
from __future__ import annotations

import html
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
DEFAULT_VERSION = "v4"

# Shown only when a turn did not end normally; "answered" needs no label.
STATUS_NOTES = {
    "waiting_for_user": "Đang chờ bạn trả lời",
    "max_tool_rounds": "Đã dừng: vượt quá số vòng gọi tool",
}

SUGGESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tóm tắt 3 tweet mới nhất của Andrej Karpathy",
    "Dự báo thời tiết Đà Nẵng 3 ngày tới?",
    "Tìm 3 paper arXiv mới nhất về diffusion models",
]

CSS = """
<style>
.block-container { max-width: 48rem; padding-top: 2.5rem; padding-bottom: 7rem; }
header[data-testid="stHeader"] { background: transparent; }

.user-row { display: flex; justify-content: flex-end; margin: 1.25rem 0 0.75rem; }
.user-bubble {
    background: var(--secondary-background-color);
    padding: 0.6rem 1.1rem;
    border-radius: 1.4rem;
    max-width: 75%;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.55;
}

.tool-error {
    color: #f87171;
    font-size: 0.875rem;
    margin: 0.25rem 0 0.5rem;
}
.status-note {
    color: rgba(236, 236, 236, 0.5);
    font-size: 0.8rem;
    margin-top: -0.25rem;
}

div[data-testid="stExpander"] details {
    border: none;
    background: transparent;
}
div[data-testid="stExpander"] summary {
    padding: 0.15rem 0;
    font-size: 0.85rem;
    opacity: 0.6;
}
div[data-testid="stExpander"] summary:hover { opacity: 1; }

.empty-title {
    text-align: center;
    font-size: 1.75rem;
    font-weight: 600;
    margin: 18vh 0 2rem;
}
div[data-testid="stButton"] button {
    border-radius: 0.9rem;
    text-align: left;
    justify-content: flex-start;
}
div[data-testid="stChatInput"] textarea { font-size: 1rem; }
section[data-testid="stSidebar"] .stCaption code { font-size: 0.72rem; }
</style>
"""

st.set_page_config(page_title="Research Agent", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)


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


def render_user(text: str) -> None:
    # User text is escaped: the app may be exposed through a public tunnel.
    st.markdown(
        f'<div class="user-row"><div class="user-bubble">{html.escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


def render_error(text: str) -> None:
    st.markdown(f'<div class="tool-error">{html.escape(text)}</div>', unsafe_allow_html=True)


def render_assistant(turn: dict[str, Any]) -> None:
    for round_record in turn.get("rounds", []):
        for event in round_record.get("tool_results", []):
            name = event.get("tool", "?")
            args = event.get("args", {})
            result = event.get("result")
            error = tool_error(result)
            if error:
                # Rendered outside the expander so tool errors are never hidden.
                render_error(f"Lỗi khi dùng {name}: {error}")
            with st.expander(f"Đã dùng {name}", expanded=False):
                st.caption("Tham số")
                st.code(json_text(args), language="json")
                st.caption("Kết quả")
                st.code(json_text(result, max_chars=20000), language="json")
    if turn.get("status") == "provider_error":
        render_error(f"Lỗi provider: {turn.get('error')}")
    else:
        st.markdown(turn.get("assistant_text") or "_(không có phản hồi)_")
    note = STATUS_NOTES.get(turn.get("status", ""))
    if note:
        st.markdown(f'<div class="status-note">{note}</div>', unsafe_allow_html=True)


def queue_prompt(text: str) -> None:
    st.session_state.pending_prompt = text


# ---------------- Sidebar ----------------
with st.sidebar:
    new_chat = st.button("Cuộc trò chuyện mới", use_container_width=True)
    with st.expander("Cài đặt", expanded=False):
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        model_input = st.text_input("Model (để trống = mặc định)", value="").strip() or None
        version_label = st.text_input("Artifact version", value=DEFAULT_VERSION).strip() or DEFAULT_VERSION
        history_window = st.number_input("Số lượt nhớ (cặp hỏi–đáp)", min_value=0, max_value=20, value=5)
        max_tool_rounds = st.number_input("Số vòng gọi tool tối đa", min_value=1, max_value=10, value=4)

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
    st.caption(f"Version: `{st.session_state.transcript.get('artifact_version')}`")
    st.caption(f"Transcript: `{st.session_state.transcript_path.relative_to(ROOT)}`")

# ---------------- Main ----------------
if provider_error:
    render_error(
        f"Không khởi tạo được provider {provider_name}: {provider_error}. "
        "Kiểm tra starter_v0/.env (copy từ .env.example) và SDK của provider."
    )

user_text = st.chat_input("Hỏi bất kỳ điều gì", disabled=provider is None)
if not user_text and st.session_state.get("pending_prompt"):
    user_text = st.session_state.pop("pending_prompt")

if not st.session_state.display and not user_text:
    st.markdown('<div class="empty-title">Tôi có thể giúp gì cho bạn?</div>', unsafe_allow_html=True)
    columns = st.columns(2)
    for index, suggestion in enumerate(SUGGESTIONS):
        columns[index % 2].button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True,
            disabled=provider is None,
            on_click=queue_prompt,
            args=(suggestion,),
        )

for past_turn in st.session_state.display:
    render_user(past_turn["user"])
    render_assistant(past_turn)

if user_text and provider is not None:
    render_user(user_text)
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
    with st.spinner("Đang suy nghĩ…"):
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
        render_error(f"Không lưu được transcript: {exc}")
    render_assistant(turn)
