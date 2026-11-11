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
- Chạy `--suite group` trên bản prompt/tools cuối (ban đầu dự kiến v3, thực tế chạy trên v4, xem 3.4); chat live ≥ 3 lượt bằng `chat.py`.
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

### 3.2. Phân tích lỗi run v0–v4 (`analysis/failure_analysis.csv`, `analysis/base_runs.csv`, `analysis/group_runs.csv`)

- `base_runs.csv`: xuất bằng `scripts/parse_runs.py` từ 6 run base trong `runs/` (120 dòng); `group_runs.csv`: run group v4 (10 dòng).
- `failure_analysis.csv`: 12 case FAIL qua các version (11 base + 1 group), mỗi case có loại lỗi được gán, tool call thực tế, chi tiết lỗi và nguyên nhân đối chiếu với prompt/tools của version đó.

Tóm tắt:

| Version | Model | Pass | Case FAIL (loại lỗi) |
|---|---|---|---|
| v0 | nemotron-3-ultra (OpenRouter) | 16/20 | R03 (wrong_arg_value), R10 (missing_info), R12 (wrong_boundary), R13 (wrong_arg_value) |
| v1 | nemotron-3-ultra (OpenRouter) | 18/20 | R02 (unnecessary_tool), R12 (wrong_boundary) |
| v2 | gpt-oss-120b (Groq) | 18/20 | R12 (wrong_boundary), R13 (wrong_tool) |
| v3 | gpt-oss-120b (Groq) | 19/20 | R13 (wrong_tool) |
| v4 | gpt-oss-120b (Groq) | 19/20 | R13 (wrong_tool) |

Nhận xét chính:

- R10 ở v0 do prompt starter dặn "pick a well-known account like Sam Altman"; R12 do "just go ahead and do it".
- R13 PASS ở v1 (nemotron) nhưng FAIL ở v2 và v3 (gpt-oss-120b) dù prompt v3 có rule bắt buộc gọi cả hai tool, nên lỗi gắn với việc đổi model nhiều hơn là prompt.

### 3.3. Kiểm tra chất lượng eval case

- Kiểm tra offline bằng chính hàm của `run_eval.py`: `load_cases` + `validate_expected_tools` không báo lỗi; đáp án đúng cho cả 10 case đều PASS; 7 câu trả lời sai điển hình (đoán Hanoi, giữ `@`, gửi khi user đã huỷ, …) đều FAIL đúng dự kiến.
- Run group chính thức trên v4 (`runs/v4_B_group_groq_20261111T080451202418.json`, Groq `openai/gpt-oss-120b`): 9/10 PASS, 0 provider error; routing 1.0, argument 0.9, multi-turn 0.8. G08 FAIL: model gọi `weather(city="Hanoi", days=5)`, tức lấy thành phố ở lượt 1 thay vì Tokyo ở lượt 2. Đây là đầu vào để sửa prompt (rule ưu tiên giá trị được nhắc gần nhất khi user đổi đối tượng). Kết quả giống run thử trước đó.

### 3.4. Hash v3 lệch và chạy v4

- Hash prompt/tools trong commit `d45ee0d` (`p413725f7051c+tfee9d0e2bf87`) không khớp với run v3 trong `version_log.csv` (`pe10bb3c111d9+t30f47204b30e`), kể cả khi chuẩn hoá CRLF/LF.
- Bỏ phần `weather` (1 dòng routing trong `system_prompt.md` và khối `weather` trong `tools.yaml`) khỏi file hiện tại thì hash khớp đúng v3. Kết luận: v2 và v3 được chạy trước khi merge tool `weather`; ngoài `weather` không có thay đổi nào khác.
- Vì eval group có case cần `weather` và bản cuối chưa có run base, mình chạy v4 = v3 + `weather` mà không sửa prompt/tools, rồi thêm dòng v4 vào `version_log.csv`: base 19/20 (0.95, bằng v3), tức thêm `weather` không làm hỏng case cũ. Chọn nhãn v4 thay vì chạy lại v3 để giữ nguyên tắc mỗi version một giả thuyết; v0–v3 giữ nguyên vì vẫn hợp lệ.

### 3.5. Chat live (`transcripts/v4_groq_20261111T081604991400.transcript.json`)

6 lượt trong một phiên, `artifact_version` `v4+p413725f7051c+tfee9d0e2bf87`:

| Lượt | Loại | Tool gọi | Kết quả |
|---|---|---|---|
| 1 | Research thường | `lookup(query=AI, topic=news, timeframe=day)` | Tóm tắt 5 tin |
| 2 | Thiếu thông tin | `clarify(response_type=text)` | Hỏi tweet của ai, không đoán |
| 3 | Bổ sung | `timeline(screenname=karpathy, limit=3)` | Routing đúng; tool lỗi 403 từ RapidAPI, agent báo lỗi trung thực |
| 4 | Yêu cầu gửi | `clarify(response_type=yes_no)` | Hỏi xác nhận, không gửi ngay |
| 5 | Xác nhận | `send(confirmed=true)` | Lỗi thiếu `TELEGRAM_BOT_TOKEN`, agent báo lỗi và đưa nội dung để đăng thủ công |
| 6 | Tool mới | `weather(city=Da Nang, days=3)` | Có vấn đề, xem bên dưới |

Phát hiện:

- Tool `weather` nhận `days=3` nhưng chỉ trả thời tiết hiện tại (request chỉ có tham số `current`, không lấy `daily`), nên agent tự đặt số liệu cho ngày 2 và 3. G01 vẫn PASS vì eval chỉ chấm args, nên đây là ví dụ eval đúng mà tool sai; cần sửa tool để lấy dự báo theo ngày.
- RapidAPI trả 403 cho `timeline`: lỗi key/quota, không ảnh hưởng eval vì eval không chấm kết quả tool.
- Agent ghi sai ngày (10/11 thay vì 11/11) vì prompt không cung cấp ngày hiện tại.

### 3.6. Việc còn lại

- [x] Run `--suite group` chính thức (trên v4) và cung cấp dữ liệu bảng B3.
- [x] Chat live ≥ 3 lượt bằng `chat.py`, lưu transcript, cung cấp dữ liệu bảng B4.

## 4. Bằng chứng

- File/commit:
  - `starter_v0/data/eval_group.json`: commit `22eb354` (`feat(eval): add 10 group eval cases`)
  - `starter_v0/analysis/base_runs.csv`, `starter_v0/analysis/group_runs.csv`, `starter_v0/analysis/failure_analysis.csv`
  - Run base v4: `starter_v0/runs/v4_B_base_groq_20261111T080154353341.json`; dòng v4 trong `starter_v0/artifacts/version_log.csv`
  - Run group v4: `starter_v0/runs/v4_B_group_groq_20261111T080451202418.json`
  - Transcript: `starter_v0/transcripts/v4_groq_20261111T081604991400.transcript.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Claude Code (Claude) để đọc mã nguồn, giải thích, soạn nháp eval case và báo cáo, viết script phân tích lỗi và chạy eval; mình duyệt và chỉnh nội dung, tự chạy chat live.
  - Tự kiểm tra: chạy bộ chấm thật của repo với đáp án đúng/sai giả lập cho từng case; chạy thử eval với Groq và đọc `actual_tool_calls` từng case; đối chiếu nguyên nhân lỗi với nội dung `system_prompt.md`/`tools.yaml` từng version qua `git show`; `pytest` 70 passed, 0 failed.

## 5. Tự đánh giá
