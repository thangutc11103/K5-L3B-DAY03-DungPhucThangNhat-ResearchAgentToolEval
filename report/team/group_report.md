# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy các bài đăng gần đây của một tài khoản Twitter | không |
| social_search | tìm bài đăng trên Twitter theo từ khóa | không |
| lookup | tra cứu thông tin trên internet qua Tavily | không |
| fetch | đọc nội dung bài viết từ một địa chỉ URL qua Firecrawl | không |
| format | trình bày dữ liệu thành văn bản markdown digest | không |
| send | gửi tin nhắn lên Telegram khi có xác nhận | không |
| weather | tra cứu thời tiết hiện tại và dự báo theo tên thành phố | CÓ (Nhật thêm) |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/weather/`) | `starter_v0/tools/weather/tool.py`, `TOOL.md` | Tra cứu thời tiết hiện tại và dự báo 1-7 ngày qua Open-Meteo API (không cần API key), tự động map mã WMO sang tiếng Việt và trả danh sách forecast chi tiết | Bọc toàn bộ trong try/except, trả về dict lỗi `{"tool": "weather", "error": ...}` không raise exception |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `pytest` output (0 failed) | 4 unit tests: Happy path, Regression test forecast nhiều ngày (days=3), Bad input (city rỗng, None), Failure path (mạng timeout, không tìm thấy thành phố) | Mock hoàn toàn bằng fixture `fake_http`, kiểm tra bắt đúng lỗi mà không để sập agent |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: Đã viết 4 tests cho tool `weather` (gồm 1 regression test). Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: Khi model truyền `city=""` hoặc mạng bị timeout, nếu tool không bọc `try/except` thì sẽ `raise Exception` làm sập toàn bộ Agent; unit test bắt buộc tool phải trả về dictionary lỗi `{"tool": "weather", "error": "ValueError", ...}` giúp Agent tiếp tục hoạt động.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py::test_weather_forecast_days_regression_returns_multiple_days` | Bắt và sửa bug logic: Tool nhận tham số `days > 1` nhưng chỉ gọi `current` mà bỏ quên `daily`, khiến agent phải tự bịa số liệu cho các ngày sau. Đã sửa và có regression test chứng minh. | Đảm bảo tính toán đúng ngày, min/max temp, xác suất mưa và timezone tự động |

Test challenge: Đã tìm và sửa 1 bug logic thực tế trong tool `weather`:
- **Hiện tượng:** Khi user yêu cầu "dự báo thời tiết 3 ngày" (`days=3`), tool chỉ lấy thời tiết hiện tại (`current`) từ Open-Meteo mà không truyền tham số `daily`, kết quả trả về thiếu danh sách `forecast` khiến Agent trong live chat phải tự suy đoán/bịa số liệu cho ngày 2 và ngày 3.
- **Cách sửa:** Bổ sung `daily: weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max` và `timezone: auto` vào request tới Open-Meteo Forecast API; trích xuất danh sách `forecast` gồm từng ngày (nhiệt độ min/max, tình trạng thời tiết, xác suất mưa) và tổng hợp vào `summary`.
- **Regression test:** Viết test `test_weather_forecast_days_regression_returns_multiple_days` gọi `days=3`, kiểm tra `len(forecast) == 3`, đầy đủ ngày và nhiệt độ min/max, xác nhận bug được khắc phục triệt để.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
