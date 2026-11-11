"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest
import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_weather_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "results": [{"name": "Hanoi", "latitude": 21.0285, "longitude": 105.8542, "country": "Vietnam"}],
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 65,
            "weather_code": 0,
            "wind_speed_10m": 12.0,
        },
        "daily": {
            "time": ["2026-11-10"],
            "weather_code": [0],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [22.0],
            "precipitation_probability_max": [10],
        },
    }))
    result = TOOL_FUNCTIONS["weather"](city="Hanoi", days=1)

    assert len(calls) == 2
    assert "geocoding-api.open-meteo.com" in calls[0]["url"]
    assert calls[0]["params"]["name"] == "Hanoi"
    assert "api.open-meteo.com" in calls[1]["url"]
    assert calls[1]["params"]["latitude"] == 21.0285
    assert calls[1]["params"]["forecast_days"] == 1
    assert calls[1]["params"]["timezone"] == "auto"
    assert result["city"] == "Hanoi"
    assert result["country"] == "Vietnam"
    assert result["temperature_c"] == 28.5
    assert result["humidity_pct"] == 65
    assert result["condition"] == "Trời quang đãng (Clear sky)"
    assert len(result["forecast"]) == 1
    assert result["forecast"][0]["temp_max_c"] == 30.0
    assert "Hanoi, Vietnam" in result["summary"]


def test_weather_forecast_days_regression_returns_multiple_days(fake_http) -> None:
    """Regression test for bug where days > 1 was ignored and only current weather was returned."""
    calls = fake_http(FakeResponse({
        "results": [{"name": "Da Nang", "latitude": 16.0544, "longitude": 108.2022, "country": "Vietnam"}],
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 80,
            "weather_code": 2,
            "wind_speed_10m": 15.0,
        },
        "daily": {
            "time": ["2026-11-11", "2026-11-12", "2026-11-13"],
            "weather_code": [2, 61, 80],
            "temperature_2m_max": [27.0, 26.0, 25.5],
            "temperature_2m_min": [22.0, 21.5, 21.0],
            "precipitation_probability_max": [20, 80, 75],
        },
    }))
    result = TOOL_FUNCTIONS["weather"](city="Da Nang", days=3)

    assert len(calls) == 2
    assert calls[1]["params"]["forecast_days"] == 3
    assert "daily" in calls[1]["params"]
    assert result["days"] == 3
    assert len(result["forecast"]) == 3
    assert result["forecast"][0]["date"] == "2026-11-11"
    assert result["forecast"][0]["temp_max_c"] == 27.0
    assert result["forecast"][1]["date"] == "2026-11-12"
    assert result["forecast"][1]["precipitation_probability_pct"] == 80
    assert "Dự báo 3 ngày tới" in result["summary"]


def test_weather_bad_input_from_model() -> None:
    # Model sends empty city
    result_empty = TOOL_FUNCTIONS["weather"](city="")
    assert result_empty["error"] == "ValueError"
    assert "city" in result_empty["message"].lower()

    # Model sends whitespace-only city
    result_space = TOOL_FUNCTIONS["weather"](city="   ")
    assert result_space["error"] == "ValueError"

    # Model sends None city
    result_none = TOOL_FUNCTIONS["weather"](city=None)
    assert result_none["error"] == "ValueError"


def test_weather_failure_returns_error_dict(fake_http) -> None:
    # HTTP/Connection error must return an error dict, not raise
    fake_http(requests.RequestException("Open-Meteo connection timed out"))
    result = TOOL_FUNCTIONS["weather"](city="Tokyo")
    assert result["tool"] == "weather"
    assert result["error"] == "RequestException"
    assert "timed out" in result["message"]

    # City not found returns not_found status dict, not crash
    fake_http(FakeResponse({"results": []}))
    result_not_found = TOOL_FUNCTIONS["weather"](city="NonExistentCity12345")
    assert result_not_found["status"] == "not_found"
    assert "Không tìm thấy" in result_not_found["message"]
