# Báo cáo cá nhân — ChuVanNhat-2A202603848

## 1. Thông tin thành viên

- Họ tên: Chu Văn Nhật
- MSSV: 2A202603848
- Email: nhat.cv.2026@vinuni.edu.vn (hoặc email trường của bạn)
- Lớp: L3B

## 2. Phần việc phụ trách

**Phần 2 — Tool mới & Unit Test (CP3)**
- File sở hữu: `starter_v0/tools/weather/tool.py`, `starter_v0/tools/weather/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/tests/test_tools_todo.py`.
- Xây dựng ít nhất 1 tool mới cho Research Agent, đăng ký vào `TOOL_FUNCTIONS` và khai báo schema vào `artifacts/tools.yaml`.
- Viết $\ge 3$ unit tests cho tool mới trong `tests/test_tools_todo.py`: happy path, input xấu từ model, nhánh lỗi trả về dict lỗi không raise exception.
- Đảm bảo toàn bộ suite `pytest` đạt 0 failed, bao gồm `test_tool_contract.py`.

## 3. Đóng góp cụ thể

1. **Xây dựng Tool mới `weather`:**
   - Tạo module `starter_v0/tools/weather/tool.py` với hàm `get_weather(city, days)`.
   - Sử dụng Open-Meteo Geocoding & Forecast API (hoàn toàn miễn phí, không phụ thuộc API key).
   - Thiết kế an toàn: Bọc toàn bộ xử lý trong `try...except`, chuẩn hóa mã thời tiết WMO sang mô tả dễ hiểu, trả về dict lỗi chuẩn nếu thành phố không tồn tại hoặc lỗi mạng.
2. **Soạn thảo hợp đồng `TOOL.md` & Đăng ký Registry:**
   - Viết `starter_v0/tools/weather/TOOL.md` đầy đủ YAML frontmatter (`name: weather`, inputs, outputs, side_effect).
   - Đăng ký hàm `get_weather` vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py`.
   - Cung cấp đoạn khai báo YAML cho Thắng đưa vào `starter_v0/artifacts/tools.yaml`.
3. **Viết Unit Tests & Sửa lỗi Regression:**
   - `test_weather_happy_path`: Mock fake HTTP với dữ liệu tọa độ và thời tiết chuẩn, kiểm tra request gửi đi và dữ liệu trả về.
   - `test_weather_forecast_days_regression_returns_multiple_days` (Regression test): Khắc phục lỗi tool chỉ trả `current` khi `days > 1` khiến agent phải tự bịa số liệu. Bổ sung `daily` forecast vào Open-Meteo API và test trả về đúng 3 ngày với đầy đủ min/max temp, xác suất mưa.
   - `test_weather_bad_input_from_model`: Kiểm tra khi model gửi chuỗi rỗng `city=""`, khoảng trắng, hoặc `None` $\rightarrow$ trả về dict lỗi `ValueError` êm đẹp.
   - `test_weather_failure_returns_error_dict`: Giả lập lỗi mạng `RequestException` và trường hợp không tìm thấy thành phố $\rightarrow$ trả về dict lỗi, không crash chương trình.
4. **Phối hợp nhóm:**
   - Cung cấp schema YAML cho Thắng để chạy `test_tool_contract.py` luôn xanh.
   - Cung cấp tên tool và tham số cho Dũng để viết test case route vào `weather` trong `eval_group.json`.

## 4. Bằng chứng

- **Files tạo và chỉnh sửa:**
  - `starter_v0/tools/weather/tool.py`
  - `starter_v0/tools/weather/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tests/test_tools_todo.py`
- **Output Pytest:**
  - `pytest tests/test_tool_contract.py` $\rightarrow$ **60 passed in 0.35s** (100% xanh).
  - `pytest tests/test_tools_todo.py -k weather` $\rightarrow$ **4 passed** (0 failed).
  - Toàn bộ suite `pytest` $\rightarrow$ **71 passed, 0 failed**.
- **Công cụ AI đã dùng:**
  - Antigravity / Gemini hỗ trợ scaffold cấu trúc thư mục, tra cứu API format Open-Meteo, và viết fixture mock offline `fake_http`.
  - Tự kiểm tra kết quả bằng cách chạy lệnh `pytest` thực tế trên môi trường local.

## 5. Tự đánh giá

- Hoàn thành đầy đủ 100% yêu cầu của CP3 trước mốc thời gian quy định.
- Code sạch, tuân thủ đúng hợp đồng, xử lý lỗi ngoại lệ chặt chẽ, test bao phủ cả happy path và nhánh lỗi.
- Đánh giá: **Đạt yêu cầu xuất sắc (10/10 điểm phần việc phụ trách)**.
