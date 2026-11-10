# Team

## Thông tin nhóm

- Tên nhóm: DungPhucThangNhat
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-DungPhucThangNhat-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/thangutc11103/K5-L3B-DAY03-DungPhucThangNhat-ResearchAgentToolEval.git

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Nguyễn Đức Thắng|2A202603798|26ai.thangnd3@vinuni.edu.vn|[thangutc11103](https://github.com/thangutc11103)|Trưởng nhóm|
|   2 |Nguyễn Minh Phúc|2A202603894|26ai.phucnm2@vinuni.edu.vn|[NgMinPhuc](https://github.com/NgMinPhuc)|Thành viên|
|   3 |Phạm Quang Dũng|2A202603896|26ai.dungpq3@vinuni.edu.vn|[quanggpham](https://github.com/quanggpham)|Thành viên|
|   4 |Chu Văn Nhật|2A202603848|26ai.nhatcv@vinuni.edu.vn|[moyymochi11](https://github.com/moyymochi11)|Thành viên|




## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenDucThang-2A202603798

### Phần việc phụ trách

**Phần 1 — Tối ưu prompt & tool declaration (v0 → v3)**

- File sở hữu: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`
- Chạy preflight và baseline `v0`; liệt kê case FAIL và gán loại lỗi (`wrong_tool`, `wrong_arg_value`, `missing_info`, ...)
- Bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước)
- Thêm rule routing (`timeline` / `social_search` / `lookup` / `fetch` / `clarify`); viết lại `description` mỗi tool (khi nào dùng / không dùng, convention args, `send` chỉ khi `confirmed=true`)
- Chạy `v1`, `v2`, `v3`, mỗi version một giả thuyết, ghi metric trước/sau vào `version_log.csv`
- Nhận từ thành viên khác: entry `tools.yaml` của tool mới (Phúc), kết quả phân tích case FAIL (Dũng)
- Mốc: `v0` trước 15:00, `v1` trước 15:30, `v3` trước 17:30

### Đóng góp cụ thể

-

### Bằng chứng

-

## ChuVanNhat-2A202603848

### Phần việc phụ trách

**Phần 2 — Tool mới & unit test (CP3)**

- File sở hữu: `tools/<tên_tool_mới>/tool.py` + `TOOL.md`, `tools/__init__.py`, `tests/test_tools_todo.py`
- Viết ít nhất 1 tool mới, đăng ký trong `TOOL_FUNCTIONS`; gửi đoạn khai báo `tools.yaml` cho Thắng dán vào
- Viết ≥ 3 unit test/tool mới: happy path, input xấu (chuỗi rỗng, sai kiểu, ngoài enum), nhánh lỗi trả error dict không raise
- Giữ `pytest` xanh, gồm `test_tool_contract.py`
- Bonus (tuỳ chọn): điền hết stub `pytest.skip` (0 skipped), tìm bug bằng input biên và giữ regression test, hoặc viết ≥ 4 tool mới
- Mốc: tool đăng ký xong trước 15:30

### Đóng góp cụ thể

- Tạo tool `starter_v0/tools/weather/tool.py` tra cứu thời tiết qua Open-Meteo API.
- Tạo `starter_v0/tools/weather/TOOL.md` theo contract frontmatter.
- Đăng ký tool trong `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml`.
- Viết 3 unit tests trong `starter_v0/tests/test_tools_todo.py` (happy path, bad input, failure path).
- Giữ toàn bộ test suite pytest xanh: 70 passed, 0 failed.

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603848_ChuVanNhat.md`
- Output pytest: `pytest tests/test_tool_contract.py` (60 passed), `pytest tests/test_tools_todo.py -k weather` (3 passed).

## PhamQuangDung-2A202603896

### Phần việc phụ trách

**Phần 3 — Eval nhóm, chat live & phân tích lỗi**

- File sở hữu: `data/eval_group.json`, `transcripts/*.transcript.json`, `analysis/*.csv`
- Viết đúng 10 case (5 single turn + 5 multi turn) phủ các `failure_type`; ít nhất 1 case route tới tool mới của Phúc
- Chạy `--suite group` trên `v3` (và `extension` nếu có thời gian)
- Chat live ≥ 3 lượt bằng `chat.py`: research bình thường, thiếu thông tin rồi bổ sung, yêu cầu gửi Telegram
- Dùng `scripts/parse_runs.py` để phân tích lỗi, cung cấp số liệu cho Phần B của báo cáo
- Bonus (tuỳ chọn): Small Local Model Challenge (Ollama ≥ 2 model, 2 vòng `v4-local`/`v5-local`, mục B7)
- Mốc: eval nhóm sẵn sàng trước 16:00

### Đóng góp cụ thể

-

### Bằng chứng

-

## NguyenMinhPhuc-2A202603894

### Phần việc phụ trách

**Phần 4 — UI, deploy & báo cáo**

- File sở hữu: `app.py` (Streamlit hoặc Vercel), `requirements.txt`, `report/team/group_report.md`, `report/team/poster.html` (tuỳ chọn)
- Xây UI chạy được trên `agent.py`; expose bằng `cloudflared tunnel --url http://localhost:8501`, dán link vào mục A1
- Viết Phần A của `group_report.md` (agent làm gì, tool gì, câu hỏi mẫu) trước 16:30; poster HTML/SVG nếu kịp
- Tổng hợp Phần B (bảng v0–v3, failure analysis, eval cases, live chat, reflection) từ log của các thành viên
- Duy trì `TEAM.md` và rà checklist `SUBMISSION.md` trước khi nộp
- Mốc: Phần A trước 16:30, Phần B trước deadline

### Đóng góp cụ thể

-

### Bằng chứng

-
