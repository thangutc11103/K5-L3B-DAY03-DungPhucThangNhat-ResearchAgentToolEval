# Báo cáo cá nhân — PhamQuangDung-2A202603896

## 1. Thông tin thành viên

- Họ tên: Phạm Quang Dũng
- MSSV: 2A202603896
- Email: 26ai.dungpq3@vinuni.edu.vn
- Lớp: L3B

## 2. Phần việc phụ trách

**Phần 3 — Eval nhóm, chat live & phân tích lỗi**

- File sở hữu: `starter_v0/data/eval_group.json`, `starter_v0/transcripts/*.transcript.json`, `starter_v0/analysis/*.csv`.
- Viết đúng 10 eval case (5 single turn + 5 multi turn), có ít nhất 1 case route tới tool mới `weather` của Nhật.
- Chạy `--suite group` trên v3; chat live ≥ 3 lượt bằng `chat.py`.
- Phân tích lỗi từ run JSON, cung cấp số liệu cho bảng B2/B3 của group report và kết quả case FAIL cho Thắng.

## 3. Đóng góp cụ thể

### 3.1. 10 eval case nhóm (`data/eval_group.json`)

| ID | Loại | Kiểm tra | Expect |
|---|---|---|---|
| G01 | single | Route tới tool mới `weather`, trích `days` | `weather(city=London, days=3)` |
| G02 | single | Thiếu thành phố → hỏi lại, không đoán | `clarify(response_type=text)` |
| G03 | single | Handle có `@` → bỏ `@` | `timeline(screenname=karpathy, limit=4)` |
| G04 | single | Hành động ngoài phạm vi (đặt vé) có từ khoá gần tool | no tool, refuse |
| G05 | single | "mới nộp gần đây nhất" → sort theo ngày nộp | `papers(max_results=3, sort_by=submittedDate)` |
| G06 | multi | Đã xác nhận ở lượt sau → gửi | `send(confirmed=true)` |
| G07 | multi | User huỷ yêu cầu gửi | no tool |
| G08 | multi | Carry thành phố mới nhất (Tokyo, không phải Hà Nội) | `weather(city=Tokyo, days=5)` |
| G09 | multi | Chuyển web → Twitter, carry chủ đề, "nổi bật" → Top | `social_search(query=Anthropic, search_type=Top)` |
| G10 | multi | Lời cảm ơn kết thúc → không gọi lại tool | no tool |

Nguyên tắc thiết kế:

- Không trùng 20 case base và 10 case extension; G06/G07 bổ sung nhánh *đã xác nhận* và *huỷ* mà R12 chưa test, G09 là chiều ngược của M06.
- Phủ đủ 6 `failure_type`: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.
- Bộ chấm (`compare_subset` trong `run_eval.py`) so khớp chuỗi chính xác sau khi lowercase và tính FAIL nếu có tool call thừa. Vì vậy `expect` chỉ kiểm tra arg có giá trị xác định (số, enum, handle, tên thành phố), không ép `query` dạng câu, tránh lỗi do bộ chấm như R03/R13 ở v0.

### 3.2. Phân tích lỗi base run v0–v3 (`analysis/failure_analysis.csv`, `analysis/base_runs.csv`)

- `base_runs.csv`: xuất bằng `scripts/parse_runs.py` từ 5 run base trong `runs/` (100 dòng).
- `failure_analysis.csv`: 10 case FAIL qua các version, mỗi case có loại lỗi được gán, tool call thực tế, chi tiết lỗi và nguyên nhân đối chiếu với prompt/tools của version đó.

Tóm tắt:

| Version | Model | Pass | Case FAIL (loại lỗi) |
|---|---|---|---|
| v0 | nemotron-3-ultra (OpenRouter) | 16/20 | R03 (wrong_arg_value), R10 (missing_info), R12 (wrong_boundary), R13 (wrong_arg_value) |
| v1 | nemotron-3-ultra (OpenRouter) | 18/20 | R02 (unnecessary_tool), R12 (wrong_boundary) |
| v2 | gpt-oss-120b (Groq) | 18/20 | R12 (wrong_boundary), R13 (wrong_tool) |
| v3 | gpt-oss-120b (Groq) | 19/20 | R13 (wrong_tool) |

Nhận xét chính:

- R10 ở v0 do prompt starter dặn "pick a well-known account like Sam Altman"; R12 do "just go ahead and do it".
- R13 PASS ở v1 (nemotron) nhưng FAIL ở v2 và v3 (gpt-oss-120b) dù prompt v3 có rule bắt buộc gọi cả hai tool, nên lỗi gắn với việc đổi model nhiều hơn là prompt.

### 3.3. Kiểm tra chất lượng eval case

- Kiểm tra offline bằng chính hàm của `run_eval.py`: `load_cases` + `validate_expected_tools` không báo lỗi; đáp án đúng cho cả 10 case đều PASS; 7 câu trả lời sai điển hình (đoán Hanoi, giữ `@`, gửi khi user đã huỷ, …) đều FAIL đúng dự kiến.
- Chạy thử với Groq `openai/gpt-oss-120b` trên prompt/tools hiện tại (run thử, không đưa vào `runs/`): 9/10 PASS, 0 provider error. G08 FAIL: model gọi `weather(city="Hanoi", days=5)`, tức lấy thành phố ở lượt 1 thay vì Tokyo ở lượt 2. Đây là đầu vào để sửa prompt (rule carry giá trị được nhắc gần nhất).

### 3.4. Phối hợp nhóm

- Phát hiện hash prompt/tools trong commit `d45ee0d` (`p413725f7051c+tfee9d0e2bf87`, kể cả khi chuẩn hoá CRLF/LF) không khớp với run v3 trong `version_log.csv` (`pe10bb3c111d9+t30f47204b30e`), tức artifact đã commit khác artifact tạo ra run v3. Đề xuất chạy lại v3 base trên artifact đã commit trước khi chạy group chính thức.

### 3.5. Việc còn lại

- [ ] Run `--suite group` chính thức trên v3 (sau khi v3 được chốt lại) và điền bảng B3.
- [ ] Chat live ≥ 3 lượt bằng `chat.py`, lưu `transcripts/*.transcript.json`, điền bảng B4.

## 4. Bằng chứng

- File/commit:
  - `starter_v0/data/eval_group.json`: commit `22eb354` (`feat(eval): add 10 group eval cases`)
  - `starter_v0/analysis/base_runs.csv`, `starter_v0/analysis/failure_analysis.csv`
  - Run group v3: _(điền đường dẫn `runs/v3_B_group_groq_*.json` sau khi chạy)_
  - Transcript: _(điền sau khi chat live)_
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Claude Code (Claude) để đọc mã nguồn bộ chấm `run_eval.py`, soạn nháp eval case, viết script tổng hợp lỗi và kiểm tra hash artifact.
  - Tự kiểm tra: chạy bộ chấm thật của repo với đáp án đúng/sai giả lập cho từng case; chạy thử eval với Groq và đọc `actual_tool_calls` từng case; đối chiếu nguyên nhân lỗi với nội dung `system_prompt.md`/`tools.yaml` từng version qua `git show`; `pytest` 70 passed, 0 failed.

## 5. Tự đánh giá
