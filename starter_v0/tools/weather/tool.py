from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err

WEATHER_CODES: dict[int, str] = {
    0: "Trời quang đãng (Clear sky)",
    1: "Chủ yếu quang đãng (Mainly clear)",
    2: "Có mây rải rác (Partly cloudy)",
    3: "Nhiều mây u ám (Overcast)",
    45: "Sương mù (Fog)",
    48: "Sương mù đóng băng (Depositing rime fog)",
    51: "Mưa phùn nhẹ (Light drizzle)",
    53: "Mưa phùn vừa (Moderate drizzle)",
    55: "Mưa phùn dày (Dense drizzle)",
    61: "Mưa nhỏ (Slight rain)",
    63: "Mưa vừa (Moderate rain)",
    65: "Mưa to (Heavy rain)",
    71: "Tuyết rơi nhẹ (Slight snow)",
    73: "Tuyết rơi vừa (Moderate snow)",
    75: "Tuyết rơi dày (Heavy snow)",
    80: "Mưa rào nhẹ (Slight rain showers)",
    81: "Mưa rào vừa (Moderate rain showers)",
    82: "Mưa rào dữ dội (Violent rain showers)",
    95: "Dông bão (Thunderstorm)",
    96: "Dông bão kèm mưa đá nhỏ (Thunderstorm with slight hail)",
    99: "Dông bão kèm mưa đá lớn (Thunderstorm with heavy hail)",
}


def get_weather(city: str = "", days: int = 1) -> dict[str, Any]:
    """Tra cứu thông tin thời tiết hiện tại và dự báo thời tiết qua Open-Meteo API (không cần API key)."""
    try:
        city_str = str(city or "").strip()
        if not city_str:
            raise ValueError("Tham số 'city' không được để trống")

        try:
            days_int = int(days) if days is not None else 1
        except (ValueError, TypeError):
            days_int = 1
        days_int = max(1, min(7, days_int))

        # Bước 1: Geocoding để lấy kinh độ, vĩ độ
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = requests.get(
            geo_url,
            params={"name": city_str, "count": 1, "language": "en", "format": "json"},
            timeout=TIMEOUT,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        results = geo_data.get("results") or []
        if not results:
            return {
                "tool": "weather",
                "status": "not_found",
                "city": city_str,
                "message": f"Không tìm thấy tọa độ cho thành phố '{city_str}'",
            }

        location = results[0]
        lat = location.get("latitude")
        lon = location.get("longitude")
        matched_name = location.get("name", city_str)
        country = location.get("country", "")

        # Bước 2: Gọi Forecast API
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        forecast_resp = requests.get(
            forecast_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "forecast_days": days_int,
            },
            timeout=TIMEOUT,
        )
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
        current = forecast_data.get("current") or {}

        code = current.get("weather_code", 0)
        condition = WEATHER_CODES.get(code, "Thời tiết bình thường")

        return {
            "tool": "weather",
            "city": matched_name,
            "country": country,
            "days": days_int,
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": code,
            "condition": condition,
            "summary": f"Thời tiết tại {matched_name}, {country}: {condition}, nhiệt độ {current.get('temperature_2m')}°C, độ ẩm {current.get('relative_humidity_2m')}%, gió {current.get('wind_speed_10m')} km/h.",
        }
    except Exception as exc:
        return err("weather", exc)
