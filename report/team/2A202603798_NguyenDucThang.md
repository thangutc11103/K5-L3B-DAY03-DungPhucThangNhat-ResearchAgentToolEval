# Báo cáo cá nhân — NguyenDucThang-2A202603798

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Thắng
- MSSV: 2A202603798
- Email: 26ai.thangnd3@vinuni.edu.vn
- Lớp: L3B

## 2. Phần việc phụ trách

**Phần 1 — Tối ưu prompt & tool declaration (`v0` → `v3`) (CP1 & CP2)**

- File sở hữu: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/*.json`.
- Chạy preflight và baseline `v0`; liệt kê các case FAIL và phân loại lỗi (`wrong_tool`, `wrong_arg_value`, `missing_info`, `wrong_boundary`).
- Loại bỏ các chỉ dẫn xấu cố ý trong `system_prompt.md` của starter (đoán mò handle/URL thay vì hỏi lại, tự ý gửi tin nhắn không cần xác nhận, ép hoàn thành trong một bước).
- Bổ sung quy tắc phân luồng công cụ (`timeline`, `social_search`, `lookup`, `fetch`, `clarify`) và viết lại `description` của từng tool cũng như từng tham số trong `tools.yaml` (nêu rõ khi nào dùng / khi nào không dùng, quy ước tham số, và ranh giới xác nhận `confirmed=true` cho `send`).
- Thực hiện vòng lặp tối ưu `v1`, `v2`, `v3` theo từng giả thuyết và ghi nhận metric trước/sau vào `artifacts/version_log.csv`; sau đó gộp khai báo tool `weather` của Nhật (được đo kiểm chứng ở `v4`).

## 3. Đóng góp cụ thể

1. **Thiết lập môi trường & Chạy Baseline `v0`:**
   - Cấu hình API keys và kiểm tra kết nối qua `scripts/preflight_provider.py`.
   - Chạy bộ đánh giá gốc `eval_base.json` ở phiên bản `v0` với model `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter) khi chưa chỉnh sửa prompt/tools, đạt `case_accuracy = 0.80` (16/20 PASS) và xác định 4 case lỗi: `R03_web_news_routing` (`wrong_arg_value` do mở rộng từ khóa `query`), `R10_missing_handle` (`missing_info` do đoán mò tài khoản `sama`), `R12_confirm_before_send` (`wrong_boundary` do dùng `response_type="text"` thay vì `"yes_no"`), và `R13_parallel_web_and_tweets` (`wrong_arg_value`).
2. **Tối ưu vòng `v1` (`artifacts/system_prompt.md`):**
   - Giả thuyết: Xóa các chỉ dẫn đoán mò của starter, bổ sung quy tắc gọi `clarify` khi thiếu thông tin, quy tắc ánh xạ tên người nổi tiếng sang handle X/Twitter (`sama`, `elonmusk`, `karpathy`) và quy tắc giữ `query` ngắn gọn đúng chủ đề gốc.
   - Kết quả: Chạy trên cùng model `nemotron-3-ultra-550b-a55b:free`, tăng `case_accuracy` từ **0.80 lên 0.90** (18/20 PASS), khắc phục hoàn toàn `R03`, `R10`, `R13`; chỉ còn FAIL ở `R02_search_tweets_routing` (gọi `social_search` 2 lần cả `Latest` và `Top`) và `R12_confirm_before_send`.
3. **Tối ưu vòng `v2` (`artifacts/tools.yaml`) & Đổi sang Groq (`openai/gpt-oss-120b`):**
   - Giả thuyết: Viết lại toàn bộ `description` của các tool và các tham số theo cấu trúc `WHEN TO USE` / `WHEN NOT TO USE`, quy định rõ `social_search` chỉ gọi 1 lần mỗi chủ đề và chuẩn hóa `topic`, `timeframe`, `search_type`.
   - Lưu ý thực nghiệm (Confounding factor khi đổi model): Khi chạy `v2`, nhóm chạm giới hạn 50 requests/ngày của các model `:free` trên OpenRouter nên phải chuyển sang provider Groq (`openai/gpt-oss-120b`) từ `v2` trở đi. Vì từ `v1` sang `v2` thay đổi đồng thời cả `tools.yaml` lẫn model (`nemotron-3-ultra` → `gpt-oss-120b`), không thể tách bạch hoàn toàn tác động riêng của từng yếu tố.
   - Kết quả: Điểm giữ ở **0.90 (18/20 PASS)** — sửa được `R02_search_tweets_routing` (không còn gọi lặp `social_search`), nhưng `R13_parallel_web_and_tweets` lại bị FAIL trên `gpt-oss-120b` (model chỉ gọi `lookup` mà bỏ sót `social_search`), và `R12_confirm_before_send` vẫn FAIL.
   - Giải thích về file `runs/v2_B_base_openrouter_20261110T191547076247.json`: Đây là lượt chạy thử nghiệm phụ bằng `openai/gpt-4o-mini` trên OpenRouter trong lúc xử lý lỗi rate-limit 429 của endpoint `:free` (đạt 19/20 = 0.95, chỉ FAIL `R13`). Nhóm không đưa file này vào chuỗi chính thức trong `version_log.csv` để giữ tính nhất quán dùng chung provider/model Groq (`openai/gpt-oss-120b`) xuyên suốt từ `v2` → `v3` → `v4`.
4. **Tối ưu vòng `v3` (`artifacts/system_prompt.md`) & Merge Tool mới (`weather`) sau khi chạy `v3`:**
   - Giả thuyết: Làm rõ quy tắc trong `system_prompt.md` rằng khi người dùng yêu cầu đăng/gửi bản tin lên Telegram, coi nội dung bản tin đã sẵn sàng trong phiên và bắt buộc gọi `clarify(response_type="yes_no")` để xin xác nhận trước khi gửi; đồng thời nhấn mạnh quy tắc gọi song song 2 tool.
   - Kết quả: Chạy trên Groq (`openai/gpt-oss-120b`), khắc phục thành công `R12_confirm_before_send`, nâng điểm `case_accuracy` từ **0.90 lên 0.95 (19/20 PASS)**, `tool_routing_accuracy = 0.95`, `argument_accuracy = 0.95`, `multiturn_accuracy = 1.0` (chỉ còn `R13` do hạn chế gọi parallel tool của `gpt-oss-120b`).
   - Lưu ý về thời điểm tích hợp `weather`: Các bản `v2` và `v3` được chạy **trước khi** merge khai báo tool `weather` của Nhật. Ngay sau khi chạy xong `v3`, mình mới gộp thêm entry `weather` vào `tools.yaml` và 1 dòng routing `weather` vào `system_prompt.md` để commit lên nhánh chính; bản sau khi merge `weather` được Dũng đo lại ở **`v4`** (vẫn giữ nguyên 19/20 = 0.95 trên bộ base).

## 4. Bằng chứng

- **Files tạo và chỉnh sửa:**
  - `starter_v0/artifacts/system_prompt.md`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/artifacts/version_log.csv`
  - `starter_v0/runs/v0_B_base_openrouter_20261110T184128540345.json` (`0.80`, `nemotron-3-ultra`)
  - `starter_v0/runs/v1_B_base_openrouter_20261110T184806291711.json` (`0.90`, `nemotron-3-ultra`)
  - `starter_v0/runs/v2_B_base_groq_20261110T194443318119.json` (`0.90`, `gpt-oss-120b` — bản chính thức trong `version_log.csv`)
  - `starter_v0/runs/v2_B_base_openrouter_20261110T191547076247.json` (`0.95`, `gpt-4o-mini` — bản chạy thử phụ khi gặp rate-limit OpenRouter `:free`, không ghi vào `version_log.csv`)
  - `starter_v0/runs/v3_B_base_groq_20261110T195252634110.json` (`0.95`, `gpt-oss-120b`, trước khi merge `weather`)
- **Kiểm tra hợp đồng công cụ (Contract Test):**
  - Chạy `pytest tests/test_tool_contract.py` đạt 100% PASS (60/60) sau khi merge tool `weather` vào `tools.yaml`.
- **Công cụ AI đã dùng:**
  - Sử dụng Antigravity / Gemini để hỗ trợ đọc log JSON của các lượt chạy eval, phân tích `observed_mismatch` và rà soát cú pháp YAML trong `tools.yaml`. Kiểm chứng lại bằng cách chạy trực tiếp `run_eval.py` và `pytest` trên máy local.

## 5. Tự đánh giá

- Hoàn thành đầy đủ nhiệm vụ phụ trách (CP1 & CP2), thực hiện đúng phương pháp tối ưu dựa trên bằng chứng (evidence-driven) qua các mốc `v0` → `v1` → `v2` → `v3` từ 80% lên 95% (và 100% multi-turn), đồng thời ghi nhận minh bạch ảnh hưởng của việc đổi model ở `v2` và thời điểm merge tool `weather` ở `v4`.
