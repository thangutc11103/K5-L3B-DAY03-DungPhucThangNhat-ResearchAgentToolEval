# Báo cáo cá nhân — NguyenMinhPhuc-2A202603894

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Phúc
- MSSV: 2A202603894
- Email: 26ai.phucnm2@vinuni.edu.vn

## 2. Phần việc phụ trách

**Phần 4 — UI, deploy & báo cáo**

- File sở hữu: `starter_v0/app.py`, `starter_v0/requirements.txt`, `report/team/group_report.md`, `TEAM.md`.
- Xây UI chạy trên agent của nhóm và expose ra link public bằng Cloudflare Tunnel.
- Viết Phần A của group report và tổng hợp Phần B từ log, run và transcript của các thành viên.
- Duy trì `TEAM.md` và rà checklist `SUBMISSION.md` trước khi nộp.

## 3. Đóng góp cụ thể

1. **UI Streamlit (`starter_v0/app.py`):**
   - Dùng lại vòng lặp tool nhiều lượt `run_model_tool_loop` của `chat.py`: tool được thực thi, kết quả đưa lại cho model, `clarify` dừng lại chờ người dùng trả lời.
   - Mỗi câu trả lời hiện kèm danh sách tool call (tên, tham số, kết quả) trong expander; trạng thái lượt (`answered`, `waiting_for_user`, `max_tool_rounds`, `provider_error`) hiện bên dưới.
   - **Không che lỗi tool:** lỗi tool hiện bằng `st.error` bên ngoài expander, expander tự mở khi có lỗi. Thiếu API key thì hiện lỗi provider và khoá ô nhập.
   - Thanh bên cho chọn provider, model, nhãn version, độ dài lịch sử và số vòng tool tối đa; hiện `artifact_version` và đường dẫn transcript.
   - Mỗi phiên tự lưu transcript vào `starter_v0/transcripts/*.transcript.json` cùng hash của prompt/tools.
2. **Provider Groq (`starter_v0/providers/groq_provider.py`):** thêm provider Groq (OpenAI-compatible, mặc định `openai/gpt-oss-120b`), đăng ký trong `providers/__init__.py` và cập nhật `chat.py`, `run_eval.py`, `scripts/preflight_provider.py`, `.env.example`. Khi OpenRouter hết quota `:free`, nhóm chuyển sang Groq để chạy v2–v4, run group và chat live.
3. **Dependency và tài liệu:** thêm `streamlit>=1.36.0` vào `requirements.txt`; cập nhật `README.md`, `docs/TOOL-SETUP.md`, `CHECKPOINTS.md`, `RULES.md` cho provider mới.
4. **Báo cáo nhóm (`report/team/group_report.md`):** viết Phần A (A1–A3, mục 3) và tổng hợp Phần B: B1 từ `version_log.csv`, B2 từ `analysis/failure_analysis.csv`, B3 từ `data/eval_group.json` + `analysis/group_runs.csv`, B4 từ transcript chat live, cùng mục 5 (Khó khăn) và mục 7 (Reflection).
5. **Quản lý nhóm:** điền thông tin nhóm và phân công trong `TEAM.md`; đối chiếu từng con số trong report với file run JSON.

## 4. Bằng chứng

- File/commit/PR:
  - Commit `8dc0251` (`update UI, API provider (groq vs openai-oss-120b)`): `starter_v0/app.py`, `starter_v0/providers/groq_provider.py`, `starter_v0/requirements.txt`, …
  - Commit `9242200`, `39cb98b`, `fa08978`: `TEAM.md`
  - `report/team/group_report.md`
  - Lệnh chạy UI và link deploy: mục A1 của group report
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Claude Code để đọc mã nguồn, đối chiếu run JSON với `version_log.csv`, phát hiện chỗ lệch trong báo cáo và soạn nháp group report.
  - Tự kiểm tra: chạy `streamlit run app.py` và chat thử nhiều lượt; xác nhận lỗi tool hiện rõ trên UI; chạy `pytest` (71 passed, 0 failed); đối chiếu số liệu B1–B4 với `summary` và `results` trong từng file run.

## 5. Tự đánh giá

- Hoàn thành UI có hiện lỗi tool và lưu transcript, thêm provider Groq giúp nhóm tiếp tục chạy eval khi OpenRouter hết quota, và tổng hợp group report có trỏ tới run, transcript, commit.
- Hạn chế: link Cloudflare Tunnel là tạm thời, chỉ hoạt động khi máy chạy UI đang bật; chưa deploy lên nền tảng cố định (Streamlit Cloud).
