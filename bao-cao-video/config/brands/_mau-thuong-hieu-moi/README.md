# Thêm thương hiệu mới

1. Chép thư mục `_mau-thuong-hieu-moi` thành `config/brands/ten-brand` (chữ thường, không dấu, không dấu cách, KHÔNG bắt đầu bằng `_`).
2. Mở `brand.yaml` trong thư mục mới, sửa: `ten`, `thu_muc_input`, `thu_muc_output` (phải khác mọi thương hiệu khác - tool sẽ báo lỗi nếu trùng), `nguoi_lam`, tên tab, tên cột, danh sách nhóm nội dung.
3. (Tuỳ chọn) Muốn trọng số riêng: chép `config/weights.yaml` vào thư mục thương hiệu rồi sửa. Muốn map cột export riêng: chép `config/mappings.yaml` tương tự.
4. Bấm đúp `Chay-bao-cao.command`: khi có từ 2 thương hiệu trở lên, cửa sổ sẽ hỏi chọn thương hiệu (gõ số rồi Enter).

Mỗi thương hiệu đọc file từ thư mục input riêng và ghi kết quả vào thư mục output riêng, không dùng chung số liệu.
