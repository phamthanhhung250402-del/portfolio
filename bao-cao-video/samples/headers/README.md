# Mẫu dòng tiêu đề file export

Thư mục này chứa file export **chỉ giữ dòng tiêu đề** (không có số liệu) để tool
kiểm tra tên cột trong `config/mappings.yaml` có khớp không.

- `GIA-DINH_*.csv`: tiêu đề **giả định** theo giao diện TikTok/Meta phổ biến, dùng để
  tạo dữ liệu giả. Khi có file thật, bỏ file thật (đã xoá hết dòng số liệu) vào đây.
  Có thể xoá file GIA-DINH tương ứng sau khi đã bỏ file thật.
- Mỗi lần chạy, tool đọc mọi file trong thư mục này. Nếu file nào không nhận ra loại,
  hoặc thiếu cột cần thiết, mục **Cảnh báo dữ liệu** trong report.html sẽ ghi rõ cột
  nào - thêm tên cột đó vào `config/mappings.yaml`.

Cách tạo file chỉ có tiêu đề: mở file export bằng Numbers/Excel, xoá mọi dòng trừ dòng
đầu tiên, lưu lại (giữ đuôi .csv hoặc .xlsx).
