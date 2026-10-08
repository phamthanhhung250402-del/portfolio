# Công cụ báo cáo video & đề xuất mix nội dung

Chạy trên Mac, không cần biết code. Mỗi tháng chỉ cần **bỏ file vào thư mục rồi bấm đúp một file**.

Công cụ làm 2 việc:

1. **Cập nhật số liệu video vào tab 03**: ghép số từ file export TikTok / Meta vào đúng từng video,
   xuất ra các khối để dán vào Google Sheet. Không bao giờ đè cột công thức.
2. **Đề xuất mix nội dung tháng sau**: chấm điểm từng nhóm nội dung bằng quy tắc cố định (không dùng AI),
   chia số video, đề xuất thời lượng, kèm lý do bằng số liệu.

Chỉ phân tích video có **Người làm = Hưng** và **Status = Đã air**.

---

## Thư mục

```
bao-cao-video/
├── Chay-bao-cao.command          ← BẤM ĐÚP để chạy
├── Chay-thu-du-lieu-gia.command  ← bấm đúp để chạy thử trên dữ liệu giả
├── input/                        ← (tự tạo lần chạy đầu) bỏ file của bạn vào đây
│   ├── sheet/                    ← file .xlsx tải từ Google Sheet
│   ├── exports/                  ← file export TikTok Ads, Meta Ads, Business Suite
│   ├── thang-sau.yaml            ← lịch tháng sau (bạn điền)
│   └── tiktok-views-template.csv ← nhập tay TikTok views/likes/shares
├── output/2026-09/               ← kết quả, mỗi tháng một thư mục
│   ├── report.html
│   ├── cap-nhat-tab03/           ← các khối TSV + huong-dan-dan.txt
│   ├── de-xuat-mix-thang-sau.tsv
│   └── brief-cho-claude.md
├── config/
│   ├── mappings.yaml             ← tên cột của file export (sửa khi nền tảng đổi tên cột)
│   ├── weights.yaml              ← trọng số chấm điểm, quy tắc chia mix
│   └── brands/topzone/brand.yaml ← cột tab 03, giai đoạn, nhóm nội dung, công thức chỉ số
├── samples/headers/              ← file export chỉ giữ dòng tiêu đề (để kiểm tra tên cột)
└── samples/demo/                 ← dữ liệu GIẢ để chạy thử
```

`input/` và `output/` **không bao giờ được đưa lên GitHub** (đã chặn trong `.gitignore`). Số liệu thật chỉ nằm trên máy bạn.

---

## Bước 0 - Lấy công cụ về máy (làm 1 lần)

1. Vào trang GitHub của repo → nút xanh **Code** → **Download ZIP**.
2. Mở file ZIP vừa tải (trong Downloads). Bên trong thư mục `portfolio-main` có thư mục **bao-cao-video** -
   kéo thư mục này ra chỗ dễ tìm, vd **Tài liệu (Documents)**. Chỉ cần thư mục này, phần còn lại là website portfolio.
3. **Lần đầu** mở file `.command`, Mac sẽ chặn vì file tải từ internet:
   chuột phải (hoặc Control + bấm) vào `Chay-thu-du-lieu-gia.command` → **Mở** → bấm **Mở** lần nữa.
   Từ lần sau bấm đúp bình thường.
   - Nếu Mac vẫn không cho mở: **Cài đặt hệ thống → Quyền riêng tư & Bảo mật** → kéo xuống, bấm **Vẫn mở**.
   - Nếu báo "không có quyền thực thi": mở ứng dụng **Terminal**, gõ `chmod +x ` (có dấu cách cuối),
     kéo 2 file `.command` vào cửa sổ Terminal, bấm Enter.
4. Lần chạy đầu tiên tự cài thư viện (cần internet, 1-2 phút). Nếu máy chưa có Python, Mac sẽ hiện hộp thoại
   cài **Command Line Tools**: bấm **Cài đặt**, đợi xong rồi bấm đúp lại.

## Bước 1 - Chạy thử với dữ liệu giả

Bấm đúp **Chay-thu-du-lieu-gia.command**. Cửa sổ Terminal hiện tiến trình, xong sẽ tự mở `report.html`.
Kết quả nằm ở `samples/demo/output/2026-09/`. Không đụng gì tới dữ liệu thật.

---

## Mỗi tháng làm như sau

### Bước 2 - Tải Google Sheet thành .xlsx

1. Mở Google Sheet kế hoạch nội dung.
2. **Tệp → Tải xuống → Microsoft Excel (.xlsx)**.
3. Bỏ file vào `input/sheet/`. Nếu có nhiều file, tool dùng file **mới nhất**. Nên xoá file tháng cũ.

> Lưu ý: tải xong thì **đừng sửa sheet** cho tới khi dán xong số liệu (bước 6), hoặc tải lại file rồi chạy lại.

### Bước 3 - Tải file export, bỏ vào `input/exports/`

Không cần đặt tên file: tool tự nhận loại file theo tên cột. Nhận cả `.csv` và `.xlsx`.
Mỗi tháng nên **xoá file export của tháng trước** trong `input/exports/` để không bị cộng trùng.
Tên menu có thể hơi khác tuỳ ngôn ngữ / phiên bản giao diện.

**a) TikTok Ads Manager** (chi phí quảng cáo TikTok)

1. Vào **ads.tiktok.com** → **Chiến dịch (Campaign)** → chọn tab **Quảng cáo (Ads)**.
2. Chọn khoảng ngày = cả tháng cần cập nhật.
3. **Cột (Columns) → Tuỳ chỉnh cột (Custom columns)**, cần có: *Campaign name, Ad name, Cost, Video views*
   (thêm *Ad ID* và cột ID bài đăng / Post ID nếu có).
4. Bấm biểu tượng **Xuất (Export / Download)** → chọn **CSV**.

Tool tìm **ID video TikTok** (dãy 19 số trong link) ở mọi ô của dòng quảng cáo, thường là trong **tên quảng cáo**.
Nên đặt tên quảng cáo có ID video, vd `SPARK_7686797298801626369_GiaTraCham`.
Quảng cáo không có ID: tool thử ghép theo **tên quảng cáo trùng tiêu đề video** và đánh dấu "nên kiểm tra lại".

**b) Meta Ads Manager** (chi phí + lượt phát quảng cáo Facebook)

1. Vào **adsmanager.facebook.com** → tab **Quảng cáo (Ads)**, chọn khoảng ngày cả tháng.
2. **Cột → Tuỳ chỉnh cột**, cần có: *Số tiền đã chi tiêu (VND), Lượt phát video liên tục 3 giây, Lượt phát video,
   Lượt phát video ở mức 25%, Lượt phát video ở mức 50%*, và *ID bài viết* nếu có.
3. **Báo cáo (Reports) → Xuất dữ liệu bảng (Export table data)** → chọn **.csv** hoặc **.xlsx**.

Chi phí phải là **VND** (tool cảnh báo nếu thấy USD).

**c) Meta Business Suite** (lượt xem 3 giây, reach, thời gian xem trung bình)

1. Vào **business.facebook.com** → **Thông tin chi tiết (Insights)** → **Nội dung (Content)**.
2. Chọn khoảng ngày bao trùm các video tháng cần cập nhật.
3. Bấm **Xuất dữ liệu (Export data)** → chọn dữ liệu **Bài viết / Nội dung**, định dạng **CSV** → Tạo.

Tool ghép theo ID bài viết trong cột **Liên kết vĩnh viễn (Permalink)** / **ID bài viết** với link FB ở cột L.

**d) TikTok views / likes / shares (nhập tay)**

TikTok không xuất được số liệu từng video, nên dùng file `input/tiktok-views-template.csv`.
Sau lần chạy đầu của tháng, tool **tự điền sẵn link** các video tháng đó vào file này.

1. Mở file bằng **Numbers** (hoặc Excel), điền cột `views`, `likes`, `shares` (số lấy trong TikTok Studio).
2. Lưu lại đúng dạng CSV: Numbers → **Tệp → Xuất ra → CSV**, lưu đè đúng tên `tiktok-views-template.csv` trong `input/`.
3. Chạy lại. Dòng bạn đã điền được giữ nguyên; tool chỉ thêm link mới còn thiếu.

### Bước 4 - Điền lịch tháng sau: `input/thang-sau.yaml`

File được tự tạo ở lần chạy đầu, có chú thích tiếng Việt từng dòng. Mở bằng **TextEdit**
(chuột phải → Mở bằng → TextEdit). Nên tắt dấu ngoặc thông minh: **Sửa → Thay thế → bỏ chọn Dấu ngoặc kép thông minh**.

Điền: tháng, tổng số video (bỏ trống = bằng tháng gần nhất), các giai đoạn và ngày, sản phẩm khuyến mãi,
sự kiện, nhóm muốn thử nghiệm. Ví dụ:

```yaml
thang: 2026-11
tong_so_video: 26
giai_doan:
  - ten: "BAU"
    tu_ngay: 2026-11-01
    den_ngay: 2026-11-20
  - ten: "Black Friday"
    loai: mo_ban
    tu_ngay: 2026-11-21
    den_ngay: 2026-11-30
su_kien:
  - ten: "Khai trương TopZone Quận 7"
    ngay: 2026-11-15
nhom_thu_nghiem:
  - "Sketch hài - Ai Dè"
```

### Bước 5 - Chạy

Bấm đúp **Chay-bao-cao.command**. Xong sẽ tự mở `report.html`. Kết quả nằm trong `output/<năm-tháng>/`.

Đọc mục **Cảnh báo dữ liệu** cuối report: danh sách video không ghép được (thiếu link, link rút gọn,
sai ID...), dòng export không khớp video nào. Sửa link trong Google Sheet → tải lại .xlsx → chạy lại.

### Bước 6 - Dán số liệu vào tab 03

Cách dễ nhất: trong `report.html`, mục **Cập nhật tab 03**:

1. Bấm **Sao chép khối 1**.
2. Trên Google Sheet, tab 03, bấm chọn **đúng một ô** ghi bên cạnh (vd **P46**).
3. Bấm **Cmd + Shift + V** (dán chỉ giá trị, giữ định dạng của sheet).
4. Lặp lại với khối 2, 3...

Hoặc dùng file trong `cap-nhat-tab03/` theo `huong-dan-dan.txt` ("Dán khối 1 vào ô P46", "Dán khối 2 vào ô AE46"...).

Vì sao an toàn:
- Mỗi khối **chỉ gồm cột gõ tay**; cột có công thức (W, Z, AA, AD...) được tách ra ngoài nên không bị đè.
- Mỗi khối phủ **trọn dải dòng của tháng**; dòng không có số mới được xuất lại **giá trị cũ**.
- Cột chữ (Campaign TikTok ads, FB chạy ads, Link YouTube) chỉ được điền khi ô đang trống.
- Mặc định chỉ cập nhật video của bạn (đổi `cap_nhat_tat_ca_nguoi_lam` trong `brand.yaml` nếu muốn cập nhật cả nhóm).

Nếu số thập phân dán vào bị sai (vd 6,1 thành 61): sheet đang dùng định dạng Hoa Kỳ → mở `config/brands/topzone/brand.yaml`,
đổi `dau_thap_phan: ","` thành `dau_thap_phan: "."` rồi chạy lại.

### Bước 7 - Lưu mix đề xuất vào sheet

Mở `de-xuat-mix-thang-sau.tsv` bằng TextEdit → Cmd + A, Cmd + C → bấm vào ô đầu bảng muốn dán trong sheet → Cmd + V.
Cột: Nhóm nội dung | Số video | Tỷ trọng | Thời lượng mục tiêu | Lý do | Độ tin cậy.

### Bước 8 - Lấy ý tưởng từ Claude

Mở `brief-cho-claude.md` bằng TextEdit → Cmd + A, Cmd + C → dán vào Claude. Brief đã có sẵn số liệu từng nhóm,
top/bottom 5 video mỗi nhóm, thay đổi so với tháng trước, lịch tháng sau, bảng mix và câu yêu cầu
"đề xuất 3 ý tưởng cho mỗi nhóm... CHƯA viết kịch bản".

---

## Công cụ tính như thế nào

**Điểm nhóm (0-100)** = trung bình có trọng số của **thứ hạng phần trăm**:

| Nhóm chỉ số | Trọng số | Chỉ số |
|---|---|---|
| Hiệu quả chi phí | 40% | CPV TikTok, CPV FB 3s (thấp = tốt) |
| Giữ chân | 30% | FB xem TB (s), tỷ lệ xem 50%, FB hook rate |
| Tương tác | 15% | TikTok ER |
| Quy mô | 15% | TikTok views |

- Mỗi video được xếp hạng phần trăm theo từng chỉ số so với các video cùng chuẩn; điểm nhóm lấy **MEDIAN**
  của video trong nhóm (không dùng tổng, để nhóm được đổ nhiều ngân sách ads không bị "đẹp" giả).
- Nhóm **dưới 5 video** → "Thử nghiệm - chưa đủ dữ liệu", không xếp hạng.
- **Chuẩn theo giai đoạn**: mỗi giai đoạn trong `thang-sau.yaml` so với video lịch sử cùng loại giai đoạn
  (cần ≥15 video; thiếu thì thêm giai đoạn tương tự trong `brand.yaml`). Tháng không có launch thì không lấy
  số giai đoạn Mở bán làm chuẩn. Report ghi rõ chuẩn đang dùng.
- **Chia video**: 80% theo điểm (mỗi nhóm đang chạy tối thiểu 2 video, không nhóm nào quá 35%),
  20% cho slot thử nghiệm (nhóm bạn đăng ký trước, rồi nhóm ít dữ liệu). Nhóm chỉ hợp với giai đoạn launch
  (NPI) không được chia video ở tháng BAU. Mỗi sự kiện đảm bảo nhóm Sự kiện có ít nhất 1 video.
- **Thời lượng mục tiêu**: chia video theo ≤20s, 21-40s, 41-60s, >60s; chọn khoảng có điểm median cao nhất
  (cần ≥2 video trong khoảng).
- **Xu hướng**: điểm tháng gần nhất so với tháng trước, ▲/▼ khi lệch từ 5 điểm.

Mọi con số trên đều sửa được trong `config/weights.yaml`.

**Quan trọng - kiểm tra 1 lần**: các chỉ số phái sinh (ER, hook rate, CPV, tỷ lệ xem...) được tool **tự tính lại**
theo mục `chi_so_tinh` trong `brand.yaml` (vì file .xlsx tải về chưa tính lại công thức sau khi có số mới).
Hãy so với công thức thật trong sheet của bạn và sửa cho khớp. Nếu lệch, report sẽ cảnh báo
"công thức trong sheet cho kết quả khác cách tool tính".

---

## Khi TikTok / Meta đổi tên cột

1. Report sẽ báo "không nhận ra loại file" kèm danh sách cột trong file, hoặc "thiếu cột ...".
2. Mở `config/mappings.yaml` bằng TextEdit, tìm trường tương ứng, thêm tên cột mới vào danh sách trong ngoặc vuông,
   vd: `chi_phi: { cot: ["Cost", "Chi phí", "Tên cột mới"], ...`
3. Chạy lại.

Để kiểm tra trước: bỏ file export thật (đã xoá hết dòng số, chỉ giữ dòng tiêu đề) vào `samples/headers/`.
Mỗi lần chạy, tool đối chiếu các file này với `mappings.yaml` và báo trong mục Cảnh báo dữ liệu nếu thiếu cột.

## Thêm thương hiệu khác

Xem `config/brands/_mau-thuong-hieu-moi/README.md`. Mỗi thương hiệu có thư mục input/output, trọng số,
nhóm nội dung riêng; tool báo lỗi nếu 2 thương hiệu dùng chung thư mục dữ liệu.

## Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| "Chưa có file .xlsx trong input/sheet" | Làm bước 2. Thư mục được mở sẵn. |
| "Không tìm thấy dòng tiêu đề tháng" | Dòng tiêu đề tháng ở cột A phải bắt đầu bằng tên tháng + năm, vd `JULY 2026 - ...` |
| "Không thấy tiêu đề ... ở dòng 5" | Tên cột trong sheet khác `brand.yaml` → sửa tên trong `brand.yaml` (mục `cot`). |
| Video nằm trong "không ghép được" | Link TikTok phải có `/video/<dãy số>`; link FB không dùng dạng `facebook.com/share/...` (mở bài → bấm vào giờ đăng → copy link). |
| "viết sai cú pháp" ở file .yaml | Kiểm tra dấu cách đầu dòng và dấu `:`; chữ có dấu `:` phải để trong ngoặc kép. |
| "LỖI BẤT NGỜ" | Gửi file `loi-gan-nhat.txt` (trong thư mục công cụ) cho người hỗ trợ. |

## Dành cho người kỹ thuật

- Python 3.9+, thư viện trong `requirements.txt` (openpyxl, PyYAML, Jinja2), môi trường `.venv` tự tạo.
- Chạy tay: `.venv/bin/python -m baocao [--demo] [--brand topzone] [--khong-mo]`
- Tạo lại dữ liệu giả: `python3 tests/tao_du_lieu_gia.py`
- Test: `python3 -m unittest discover -s tests -v` - kiểm tra không đè cột công thức (mô phỏng dán TSV),
  ghép ID đúng, báo video không ghép được, mix cộng đủ tổng số video (kể cả 3.000 trường hợp ngẫu nhiên),
  tách biệt thương hiệu.
- Mã nguồn trong `baocao/`: `sheet.py` (đọc tab 03, phát hiện ô công thức), `exports.py` (nhận diện file),
  `merge.py` (ghép ID), `tsv.py` (khối dán), `analysis.py` + `mix.py` (chấm điểm, chia mix), `report.py`, `brief.py`.
