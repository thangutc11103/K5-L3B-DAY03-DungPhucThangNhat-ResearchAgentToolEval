# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: DungPhucThangNhat (lớp L3B)
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:
  - `v0`, `v1`: OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free`
  - `v2`, `v3` (và `v4`, run group, chat live): Groq `openai/gpt-oss-120b`. Nhóm chuyển provider ở `v2` vì hết quota của model `:free` trên OpenRouter (lỗi 429). Ảnh hưởng của việc đổi model được ghi ở B1 và mục 5.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin trên web theo từ khóa, đọc tweet theo tài khoản hoặc chủ đề, đọc nội dung URL, tìm paper arXiv, tra thời tiết theo thành phố, tổng hợp thành bản tin và chỉ gửi lên Telegram sau khi người dùng xác nhận. Khi thiếu thông tin (tài khoản nào, URL nào, thành phố nào), agent hỏi lại thay vì tự đoán.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt      # đã có streamlit>=1.36.0
cp .env.example .env                 # điền GROQ_API_KEY và key của các tool
streamlit run app.py                 # → http://localhost:8501
```

UI ([`starter_v0/app.py`](../../starter_v0/app.py)) dùng lại vòng lặp tool nhiều lượt của `chat.py`. Thanh bên cho phép chọn provider/model và nhãn version; mỗi phiên tự lưu transcript vào `starter_v0/transcripts/`.

**Link dùng thử (deploy):**

Deploy bằng Cloudflare Tunnel (`cloudflared tunnel --url http://localhost:8501`).

URL: _(điền link `https://<random>.trycloudflare.com` sau khi chạy tunnel)_

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận (`yes_no`) | không |
| timeline | lấy các bài đăng gần đây của một tài khoản Twitter | không |
| social_search | tìm bài đăng trên Twitter theo từ khóa (`Latest` / `Top`) | không |
| lookup | tra cứu thông tin hoặc tin tức trên internet qua Tavily | không |
| fetch | đọc nội dung bài viết từ một địa chỉ URL qua Firecrawl | không |
| format | trình bày dữ liệu thành văn bản markdown digest | không |
| send | gửi tin nhắn lên Telegram, chỉ khi `confirmed=true` | không |
| policy | tra cứu chính sách công ty trong `company_policy/` | không |
| papers | tìm paper trên arXiv (sắp xếp theo độ liên quan hoặc ngày nộp) | không |
| paper_text | đọc toàn văn một paper arXiv | không |
| weather | tra cứu thời tiết hiện tại và dự báo 1–7 ngày theo tên thành phố (Open-Meteo) | CÓ (Nhật thêm) |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(query="AI", topic="news", timeframe="day")`
2. `Tóm tắt 3 tweet mới nhất giúp mình` → agent hỏi lại tweet của ai; trả lời `Của Andrej Karpathy` → `timeline(screenname="karpathy", limit=3)`
3. `Dự báo thời tiết Đà Nẵng 3 ngày tới?` → `weather(city="Da Nang", days=3)`
4. `Tìm 3 paper arXiv mới nộp gần đây nhất về diffusion models` → `papers(max_results=3, sort_by="submittedDate")`
5. `Đăng bản tin AI vừa rồi lên Telegram giúp mình` → agent hỏi xác nhận (`yes_no`) trước, chỉ gửi khi người dùng đồng ý

## 3. Giải pháp

**`system_prompt.md`** (v1, v3, Thắng):
- Bỏ các chỉ dẫn xấu của starter: tự đoán tài khoản (ví dụ đoán `sama`), "cứ làm luôn" khi gửi, ép làm xong trong một bước.
- Rule 1: thiếu tài khoản hoặc URL thì gọi `clarify(response_type="text")`, không đoán.
- Rule 2: mọi yêu cầu gửi/đăng Telegram phải qua `clarify(response_type="yes_no")`; coi bản tin là đã có sẵn trong phiên, không hỏi lại nội dung.
- Rule 3: định tuyến cho từng tool (`timeline`, `social_search`, `lookup`, `fetch`, `weather`), đổi tên người nổi tiếng sang handle (Sam Altman → `sama`), đổi cách nói thời gian sang `timeframe`.
- Rule 4: yêu cầu cả tin web lẫn tweet thì gọi cả hai tool trong cùng một lượt.
- Rule 5: `query` chỉ giữ chủ đề chính (`"AI"`), không thêm "news", "today"…
- Rule 6–7: câu ngoài phạm vi thì không gọi tool; giữ lại ngữ cảnh và áp dụng sửa đổi của người dùng qua nhiều lượt.

**`tools.yaml`** (v2, Thắng): viết lại `description` của từng tool và từng tham số theo dạng *WHEN TO USE / WHEN NOT TO USE*, nói rõ `social_search` chỉ gọi một lần cho mỗi chủ đề, chuẩn hoá `topic`, `timeframe`, `search_type`, và chỉ `send` khi `confirmed=true`.

**Tool mới `weather`** (Nhật): `starter_v0/tools/weather/`. Agent gọi tool này khi người dùng hỏi thời tiết hoặc dự báo của một thành phố cụ thể; nếu không nói thành phố thì hỏi lại. Tool lấy toạ độ qua Open-Meteo Geocoding rồi gọi Forecast API (`current` + `daily`). Mọi lỗi được trả về dưới dạng error dict, không raise.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Mọi run dưới đây có `provider_error_cases == 0` và `measured_cases == total_cases` (20/20). Metric là `case_accuracy` trên bộ base.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của starter trước khi sửa | – | 0.80 | `runs/v0_B_base_openrouter_20261110T184128540345.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn đoán mò và quy định `query` ngắn gọn thì sẽ sửa được R03, R10, R13 | 0.80 | 0.90 | `runs/v1_B_base_openrouter_20261110T184806291711.json` |
| v2 | `tools.yaml` (*và đổi model, xem ghi chú*) | Mô tả rõ khi nào dùng tool và quy định `social_search` chỉ gọi một lần thì sẽ sửa lỗi gọi thừa ở R02 | 0.90 | 0.90 | `runs/v2_B_base_groq_20261110T194443318119.json` |
| v3 | `system_prompt.md` | Bắt buộc `clarify(response_type="yes_no")` trước khi gửi và coi bản tin là đã có sẵn thì sẽ sửa được R12 | 0.90 | 0.95 | `runs/v3_B_base_groq_20261110T195252634110.json` |
| v4 | `system_prompt.md` + `tools.yaml` (thêm `weather`) | Thêm tool `weather` và rule định tuyến thì agent gọi đúng tool cho câu hỏi thời tiết mà không làm giảm điểm base | 0.95 | 0.95 | `runs/v4_B_base_groq_20261111T080154353341.json` |

Ghi chú:
- **v2 đổi hai thứ cùng lúc.** Từ v1 sang v2, nhóm đổi cả `tools.yaml` lẫn model (nemotron → gpt-oss-120b) vì hết quota OpenRouter. v2 sửa được R02 nhưng R13 lại FAIL trên model mới, nên không tách được tác động riêng của `tools.yaml`.
- **Run phụ v2 không đưa vào chuỗi chính.** `runs/v2_B_base_openrouter_20261110T191547076247.json` chạy bằng `openai/gpt-4o-mini` (0.95, chỉ FAIL R01). Đây là run thử khi đang xử lý lỗi 429, không đưa vào `version_log.csv` để chuỗi v2→v4 dùng chung một model.
- **v4 tách ra từ v3.** v2 và v3 được chạy *trước khi* merge tool `weather`; hash của artifact đã commit khác với hash của v3. Nhóm chạy v4 = v3 + `weather` để đo bản cuối, thay vì đổi nhãn v3. Hash v4 được tính trên file xuống dòng kiểu CRLF (máy Windows). Nội dung giống hệt file trong git (LF), nên chạy lại trên macOS/Linux sẽ ra hash khác dù nội dung không đổi.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON. Bảng đầy đủ, có nguyên nhân chi tiết, nằm ở [`starter_v0/analysis/failure_analysis.csv`](../../starter_v0/analysis/failure_analysis.csv).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing (v0) | wrong_arg_value | `lookup(query="AI news today artificial intelligence breakthrough", topic="news", timeframe="day")` | `query` bị mở rộng thành câu dài, mong đợi `"AI"` | v1: thêm rule 5 trong prompt (`query` chỉ giữ chủ đề chính) → PASS |
| R10_missing_handle (v0) | missing_info | `timeline(screenname="sama", limit=5)` | Tự đoán tài khoản thay vì gọi `clarify` | v1: bỏ chỉ dẫn "pick a well-known account", thêm rule 1 → PASS |
| R12_confirm_before_send (v0, v1, v2) | wrong_boundary | `clarify(question="Bạn muốn đăng nội dung gì…", response_type="text")` | Hỏi lại nội dung bằng `text` thay vì xin xác nhận bằng `yes_no` | v3: rule 2 bắt buộc `clarify(yes_no)` và coi bản tin là đã có sẵn → PASS |
| R13_parallel_web_and_tweets (v0) | wrong_arg_value | `lookup(query="AI news today…")` + `social_search(query="AI artificial intelligence")` | Gọi đúng hai tool nhưng cả hai `query` đều bị mở rộng | v1: rule 5 → PASS |
| R02_search_tweets_routing (v1) | unnecessary_tool | `social_search(query="GPT-5", search_type="Latest")` + `social_search(query="GPT-5", search_type="Top")` | Gọi `social_search` 2 lần cho cùng một chủ đề | v2: `tools.yaml` quy định chỉ gọi một lần và mô tả rõ `search_type` → PASS |
| R13_parallel_web_and_tweets (v2, v3, v4) | wrong_tool | `lookup(query="AI", topic="news", timeframe="day")` | Thiếu `social_search`; chỉ gọi một trong hai tool | v3: thêm rule 4 (bắt buộc gọi cả hai) nhưng **vẫn FAIL**. Case này PASS trên nemotron (v1) và gpt-4o-mini, nên lỗi gắn với cách gpt-oss-120b gọi nhiều tool song song |
| G08_weather_carryover_city (v4, group) | wrong_arg_value | `weather(city="Hanoi", days=5)` | Lấy thành phố ở lượt 1 (Hà Nội) thay vì lượt 2 (Tokyo) | Chưa sửa. Đề xuất cho vòng sau: thêm rule ưu tiên giá trị được nhắc gần nhất khi người dùng đổi đối tượng |

### B3. Team Eval Cases

10 case trong [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json) (5 single turn + 5 multi turn). Run: `runs/v4_B_group_groq_20261111T080451202418.json`. Kết quả 9/10 PASS (`case_accuracy` 0.90, `tool_routing_accuracy` 1.0, `argument_accuracy` 0.9, `multiturn_accuracy` 0.8), 0 provider error.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_weather_forecast_routing | Gọi tool mới `weather` (không phải `lookup`) và lấy `days=3` từ "3 ngày tới" | `weather(city="London", days=3)` | PASS |
| G02_weather_missing_city | Hỏi thời tiết nhưng không nói thành phố → hỏi lại, không đoán | `clarify(response_type="text")` | PASS |
| G03_handle_with_at_sign | Handle có `@` → bỏ `@`, giữ đúng `limit` | `timeline(screenname="karpathy", limit=4)` | PASS |
| G04_out_of_scope_booking | Đặt vé máy bay (ngoài khả năng) dù có từ khoá gần tool | Không gọi tool, từ chối | PASS |
| G05_papers_sort_and_limit | "mới nộp gần đây nhất" → `sort_by=submittedDate`; "3 paper" → `max_results=3` | `papers(max_results=3, sort_by="submittedDate")` | PASS |
| G06_send_after_confirmation | 2 lượt: người dùng đã xác nhận → gửi luôn, không hỏi lại | `send(confirmed=true)` | PASS |
| G07_send_cancelled | 2 lượt: người dùng huỷ yêu cầu gửi | Không gọi tool | PASS |
| G08_weather_carryover_city | 3 lượt: giữ thành phố Tokyo từ lượt 2, `days=5` | `weather(city="Tokyo", days=5)` | **FAIL**: gọi `city="Hanoi"` |
| G09_switch_web_to_twitter_top | 3 lượt: chuyển từ web sang Twitter, giữ chủ đề, "nổi bật nhất" → `Top` | `social_search(query="Anthropic", search_type="Top")` | PASS |
| G10_no_tool_after_done | 2 lượt: lượt cuối chỉ là lời cảm ơn → không gọi lại tool | Không gọi tool | PASS |

### B4. Live Chat Evidence

Transcript: [`starter_v0/transcripts/v4_groq_20261111T081604991400.transcript.json`](../../starter_v0/transcripts/v4_groq_20261111T081604991400.transcript.json): 6 lượt trong một phiên, Groq `openai/gpt-oss-120b`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | `v4+p413725f7051c+tfee9d0e2bf87` | Tóm tắt 5 tin |
| 2 | Tóm tắt 3 tweet mới nhất giúp mình | `clarify(response_type="text")` | v4 | Hỏi tweet của ai, không đoán |
| 3 | Của Andrej Karpathy nhé | `timeline(screenname="karpathy", limit=3)` | v4 | Gọi đúng tool; tool lỗi 403 từ RapidAPI và agent báo lỗi trung thực |
| 4 | Đăng bản tin AI vừa rồi lên Telegram giúp mình | `clarify(response_type="yes_no")` | v4 | Hỏi xác nhận trước, không gửi ngay |
| 5 | Có, mình xác nhận đăng | `send(confirmed=true, text=…)` | v4 | Lỗi thiếu `TELEGRAM_BOT_TOKEN`; agent báo lỗi và đưa nội dung để đăng thủ công |
| 6 | Dự báo thời tiết Đà Nẵng 3 ngày tới? | `weather(city="Da Nang", days=3)` | v4 | Gọi đúng tool, nhưng lúc đó tool chỉ trả thời tiết hiện tại nên agent tự đặt số liệu ngày 2–3. Lỗi này đã sửa sau đó (xem B5) |

Nhận xét: lượt 3 và 5 cho thấy agent không che lỗi tool. Lượt 6 là ví dụ eval chấm đúng (G01 PASS vì chỉ chấm tham số) trong khi tool trả sai dữ liệu, nên vẫn cần kiểm tra bằng chat live.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/weather/`) | `starter_v0/tools/weather/tool.py`, `TOOL.md` | Tra cứu thời tiết hiện tại và dự báo 1-7 ngày qua Open-Meteo API (không cần API key), tự động map mã WMO sang tiếng Việt và trả danh sách forecast chi tiết | Bọc toàn bộ trong try/except, trả về dict lỗi `{"tool": "weather", "error": ...}` không raise exception |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `pytest` output (0 failed) | 4 unit tests: Happy path, Regression test forecast nhiều ngày (days=3), Bad input (city rỗng, None), Failure path (mạng timeout, không tìm thấy thành phố) | Mock hoàn toàn bằng fixture `fake_http`, kiểm tra bắt đúng lỗi mà không để sập agent |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `starter_v0/requirements.txt` (`streamlit`); lệnh chạy và link ở mục A1 | Streamlit chat nhiều lượt dùng lại `run_model_tool_loop` của `chat.py`; hiện từng tool call kèm tham số và kết quả; chọn provider/model/version ở thanh bên; tự lưu transcript cùng `artifact_version` | Lỗi tool luôn hiện bằng `st.error` bên ngoài expander, không bị che; lỗi provider (thiếu API key) hiện rõ và khoá ô nhập; API key chỉ đọc từ `.env` |

Tool unit tests: Đã viết 4 tests cho tool `weather` (gồm 1 regression test). Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: Khi model truyền `city=""` hoặc mạng bị timeout, nếu tool không bọc `try/except` thì sẽ `raise Exception` làm sập toàn bộ Agent; unit test bắt buộc tool phải trả về dictionary lỗi `{"tool": "weather", "error": "ValueError", ...}` giúp Agent tiếp tục hoạt động.

Toàn bộ suite: `cd starter_v0 && pytest` → **71 passed, 14 skipped, 0 failed**.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | Không làm | – |
| Hơn 3 tool mới (≥ 4) | – | Không làm (nhóm có 1 tool mới) | – |
| `send` gửi thật lên Telegram sau xác nhận | transcript | Chưa đạt: luồng hỏi lại → xác nhận → `send(confirmed=true)` đúng, nhưng thiếu `TELEGRAM_BOT_TOKEN` nên không có `status: sent` | Không commit token vào repo |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py::test_weather_forecast_days_regression_returns_multiple_days` | Bắt và sửa bug logic: Tool nhận tham số `days > 1` nhưng chỉ gọi `current` mà bỏ quên `daily`, khiến agent phải tự bịa số liệu cho các ngày sau. Đã sửa và có regression test chứng minh. | Đảm bảo tính toán đúng ngày, min/max temp, xác suất mưa và timezone tự động |

Test challenge: Đã tìm và sửa 1 bug logic thực tế trong tool `weather`:
- **Hiện tượng:** Khi user yêu cầu "dự báo thời tiết 3 ngày" (`days=3`), tool chỉ lấy thời tiết hiện tại (`current`) từ Open-Meteo mà không truyền tham số `daily`, kết quả trả về thiếu danh sách `forecast` khiến Agent trong live chat phải tự suy đoán/bịa số liệu cho ngày 2 và ngày 3.
- **Cách sửa:** Bổ sung `daily: weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max` và `timezone: auto` vào request tới Open-Meteo Forecast API; trích xuất danh sách `forecast` gồm từng ngày (nhiệt độ min/max, tình trạng thời tiết, xác suất mưa) và tổng hợp vào `summary`.
- **Regression test:** Viết test `test_weather_forecast_days_regression_returns_multiple_days` gọi `days=3`, kiểm tra `len(forecast) == 3`, đầy đủ ngày và nhiệt độ min/max, xác nhận bug được khắc phục triệt để.

### B7. Small Local Model Challenge (bonus)

Nhóm không làm bonus này.

## 5. Khó khăn và cách xử lý

- **Hết quota OpenRouter.** Model `:free` trả lỗi 429 ở giữa chừng v2. Nhóm thêm provider Groq (`starter_v0/providers/groq_provider.py`, commit `8dc0251`) và chạy v2–v4 trên `openai/gpt-oss-120b`. Hệ quả: từ v1 sang v2 đổi cả model lẫn `tools.yaml` (ghi ở B1).
- **Hash v3 không khớp file đã commit.** Dũng phát hiện file đang commit khác file đã tạo ra run v3. Bỏ phần `weather` khỏi file hiện tại thì hash khớp đúng v3, tức v2 và v3 được chạy trước khi merge `weather`. Nhóm chạy thêm v4 để đo bản cuối thay vì đổi nhãn.
- **Lỗi tool khi chat live.** `timeline` bị RapidAPI trả 403 (key/quota) và `send` thiếu `TELEGRAM_BOT_TOKEN`. Không ảnh hưởng eval (eval chỉ chấm tool call), và UI/agent báo lỗi rõ ràng (B4).
- **Tool `weather` bỏ qua tham số `days`.** Phát hiện qua chat live (lượt 6) chứ không phải qua eval. Nhật đã sửa và thêm regression test (commit `6ce5140`).
- **R13 không sửa được bằng prompt trên gpt-oss-120b.** Đã thêm rule bắt buộc gọi cả hai tool ở v3 nhưng model vẫn chỉ gọi `lookup`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

| Thành viên | Phần phụ trách |
|---|---|
| Nguyễn Đức Thắng | Phần 1: prompt và `tools.yaml`, vòng lặp v0→v3, `version_log.csv` |
| Chu Văn Nhật | Phần 2: tool `weather`, unit test, sửa lỗi dự báo nhiều ngày |
| Phạm Quang Dũng | Phần 3: 10 eval case nhóm, run v4 base/group, chat live, phân tích lỗi |
| Nguyễn Minh Phúc | Phần 4: UI Streamlit, provider Groq, deploy, group report, TEAM.md |

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** Các lỗi về *hành vi*: tự đoán thay vì hỏi lại (R10), ranh giới xác nhận trước khi gửi (R12), cách viết `query` (R03, R13 ở v0), và giữ ngữ cảnh qua nhiều lượt (G08). Đây là quy tắc chung cho cả phiên, không gắn với một tool.
- **Fix nào thuộc `tools.yaml`?** Các lỗi về *cách dùng từng tool*: gọi `social_search` hai lần (R02), ý nghĩa của `search_type`, `timeframe`, `topic`, và điều kiện `confirmed=true` của `send`. Model đọc `description` ngay lúc chọn tool, nên quy ước tham số đặt ở đây hiệu quả hơn đặt trong prompt.
- **Failure nào cần review thủ công thay vì chấm tự động?** (1) Nội dung tool trả về: G01 PASS nhưng tool `weather` từng trả sai dữ liệu nên agent tự đặt số liệu (B4 lượt 6). (2) Câu trả lời khi tool lỗi (403, thiếu token): eval không chấm agent có báo lỗi trung thực hay không. (3) Ngày tháng trong bản tin: agent ghi 10/11 thay vì 11/11 vì prompt không có ngày hiện tại.
- **Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?** (1) Thêm rule "khi người dùng đổi đối tượng, dùng giá trị được nhắc gần nhất" để sửa G08. (2) Đưa ngày hiện tại vào system prompt. (3) Chạy lại v0–v1 trên Groq để cả chuỗi dùng một model, tách được tác động của `tools.yaml` ở v2. (4) Với R13, thử thêm một ví dụ few-shot có hai tool call song song.

## 8. Tài liệu tham khảo

- [README.md](../../README.md) của lab (Step 1–7, hướng dẫn Cloudflare Tunnel), [RUBRIC.md](../../RUBRIC.md), [SUBMISSION.md](../../SUBMISSION.md)
- Open-Meteo Geocoding & Forecast API: https://open-meteo.com/en/docs
- Groq API (OpenAI-compatible): https://console.groq.com/docs
- Streamlit chat elements: https://docs.streamlit.io/develop/api-reference/chat
- Cloudflare Tunnel (`trycloudflare`): https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
