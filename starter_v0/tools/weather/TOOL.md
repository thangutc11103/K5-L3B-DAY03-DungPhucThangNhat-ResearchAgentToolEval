---
name: weather
track: bonus
kind: live_api
provider: Open-Meteo
requires_env: []
inputs: [city, days]
outputs: [city, country, days, temperature_c, humidity_pct, wind_speed_kmh, weather_code, condition, summary]
side_effect: false
---
# weather

Tra cứu thời tiết hiện tại và dự báo theo tên thành phố qua Open-Meteo API.

## When to use
- Khi người dùng hỏi thông tin thời tiết, nhiệt độ, khí hậu, hoặc dự báo mưa/nắng của một thành phố hoặc địa phương cụ thể.
- Ví dụ: "Thời tiết Hà Nội hôm nay thế nào?", "Mai Tokyo có mưa không?", "Dự báo thời tiết Đà Nẵng 3 ngày tới".

## When NOT to use
- Không dùng khi người dùng hỏi tin tức thời sự chung (dùng `lookup`).
- Không dùng khi người dùng tìm kiếm bài viết, tài liệu nghiên cứu (dùng `fetch` hoặc `lookup`).
