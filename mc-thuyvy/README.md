# Website MC Thúy Vy

Website portfolio một trang, song ngữ Việt/English, để nhận booking MC. HTML/CSS/JS thuần, **không framework, không bước build** - sửa file là xong.

> ⚠️ **Ảnh hiện tại là ảnh TẠM (placeholder).** Lúc dựng site, repo chưa có ảnh gốc (`assets/raw/`) lẫn file profile PDF, nên mọi ảnh (chân dung, 6 thẻ lĩnh vực, 18 ảnh thư viện, ảnh bìa showreel, ảnh chia sẻ og-image) đang là khung đỏ - bạc có chữ "Placeholder". **Phải thay bằng ảnh thật trước khi công khai** - xem mục 3.

```
mc-thuyvy/
├── index.html               Khung trang (không chứa chữ - chữ nằm trong data/)
├── css/style.css            Giao diện   ·  css/fonts.css  font tự host (có tiếng Việt)
├── js/config.js             ← SĐT, Zalo, email, mạng xã hội, video, form   (mục 1)
├── js/main.js               Hiệu ứng, lightbox, carousel, form, đổi ngôn ngữ
├── data/content.vi.json     ← Toàn bộ chữ tiếng Việt                      (mục 5)
├── data/content.en.json     ← Toàn bộ chữ tiếng Anh
├── data/images.json         Kích thước ảnh (script tự tạo, không sửa tay)
├── assets/img/              Ảnh WebP đã nén (website dùng)
├── assets/raw/              ← Ảnh gốc đặt ở đây (KHÔNG đưa lên web)        (mục 3)
├── assets/icons/, og-image.jpg, fonts/
├── tools/                   Script nén ảnh, tạo og-image (KHÔNG đưa lên web)
├── vercel.json, .vercelignore
```

---

## 1. Danh sách placeholder cần điền

### a) `js/config.js` - thay từng `"{{...}}"` (giữ dấu ngoặc kép)

| Placeholder | Ví dụ | Dùng ở đâu |
|---|---|---|
| `{{PHONE}}` | `"0909 123 456"` | Mục Liên hệ, nút **Gọi** trên mobile, dữ liệu Google |
| `{{ZALO}}` | `"0909123456"` hoặc `"https://zalo.me/0909123456"` | Mục Liên hệ, nút **Zalo** trên mobile |
| `{{EMAIL}}` | `"booking@mcthuyvy.vn"` | Mục Liên hệ, form dự phòng (mở app email) |
| `{{FACEBOOK}}` | `"https://www.facebook.com/..."` | Liên hệ + icon ở footer |
| `{{TIKTOK}}` | `"https://www.tiktok.com/@..."` | Liên hệ + icon ở footer |
| `{{INSTAGRAM}}` | `"https://www.instagram.com/..."` | Liên hệ + icon ở footer |
| `{{SHOWREEL_URL}}` | `"https://www.youtube.com/watch?v=..."` | Khung showreel lớn + nút "Xem showreel" |
| `{{VIDEO_URLS}}` | danh sách link (xem dưới) | Lưới "Video chương trình" dưới showreel |
| `{{FORM_ENDPOINT}}` | `"https://formspree.io/f/abcdwxyz"` | Form đặt lịch (mục 6) |

Mục nào **chưa điền thì tự ẩn** (website vẫn đẹp, không lộ chữ `{{...}}`). Nút Gọi/Zalo trên mobile khi chưa có số sẽ cuộn xuống form.

`VIDEO_URLS` là danh sách, mỗi link một dòng:

```js
VIDEO_URLS: [
  "https://www.youtube.com/watch?v=AAAAAAAAAAA",
  "https://www.tiktok.com/@mcthuyvy/video/7234567890123456789",
  "https://www.facebook.com/watch/?v=1234567890"
],
```

Hỗ trợ: YouTube (cả Shorts), TikTok (link dạng `.../video/<số>`), Facebook video/reel, file `.mp4`. Video chỉ tải khi khách bấm Play (để trang nhẹ).

### b) `index.html` - `{{SITE_URL}}` (mọi chỗ trong phần `<head>`)

Dùng cho ảnh chia sẻ Facebook/Zalo (og-image) và Google. Sau khi có tên miền (mục 8), mở `index.html`, dùng **Tìm & thay thế tất cả** (Replace All): `{{SITE_URL}}` → `https://mcthuyvy.vn` (không có dấu `/` ở cuối). Nếu chưa có tên miền riêng thì dùng tên miền Vercel, ví dụ `https://mc-thuyvy.vercel.app`.

---

## 2. Chạy thử trên máy

```bash
cd mc-thuyvy
npx serve .          # hoặc: python3 -m http.server 8080
```

Mở `http://localhost:3000` (hoặc `:8080`). **Không mở trực tiếp file `index.html`** bằng double-click - trình duyệt chặn đọc file JSON.

---

## 3. Thay ảnh (quan trọng)

### Cách nhanh nhất
Bỏ ảnh gốc vào `mc-thuyvy/assets/raw/` (đặt tên như bảng dưới), push lên GitHub và nhắn Claude: *"Tôi đã upload ảnh vào assets/raw, hãy xử lý và cập nhật website"*.

### Tự làm
1. Đặt ảnh gốc vào `assets/raw/` theo đúng tên (đuôi `.jpg`, `.png`, `.webp` đều được):

| Tên file | Vị trí trên trang | Gợi ý chọn ảnh |
|---|---|---|
| `hero.png` | Chân dung trong khung vòm đầu trang | **PNG tách nền trong suốt**, dọc, từ đầu tới ít nhất ngang hông, mặt nằm ở 1/3 trên |
| `greeting.jpg` | Cạnh thư "Kính chào quý đối tác" | Chân dung dọc, sang trọng (váy dạ hội) |
| `showreel-poster.jpg` | Ảnh bìa khung showreel | Ảnh ngang đứng trên sân khấu, khoảng giữa thoáng |
| `fields/gala.jpg` … `fields/tv.jpg` | 6 thẻ lĩnh vực (`gala`, `conference`, `launching`, `entertainment`, `esports`, `tv`) | Ảnh dọc tiêu biểu nhất của từng mảng |
| `gallery/gala-1.jpg`, `gallery/gala-2.jpg`, … | Thư viện sự kiện | Ảnh ngang/dọc tuỳ ý - lưới tự xếp |
| `logo.png` hoặc `logo.svg` | Logo chữ ký ở header & footer | Nền trong suốt, chữ màu trắng/bạc |

2. Nén ảnh (cần Python 3 và Pillow - cài 1 lần: `pip install pillow`):

```bash
cd mc-thuyvy
python3 tools/build_images.py
```

Script tự xoay theo EXIF, cắt đúng khung cho hero/greeting/showreel/thẻ lĩnh vực, giới hạn cạnh dài 1800px, tạo thêm bản 480px và 960px cho điện thoại, rồi ghi kích thước vào `data/images.json`. Ảnh PNG tách nền giữ nguyên nền trong suốt.

3. Cập nhật ảnh chia sẻ og-image (1200×630) và favicon theo ảnh hero mới (cần Node + Playwright):

```bash
npm i -g playwright && npx playwright install chromium     # cài 1 lần
NODE_PATH=$(npm root -g) node tools/render_brand.cjs
```

4. **Thêm/bớt ảnh thư viện**: thêm file vào `assets/raw/gallery/`, chạy lại bước 2, rồi thêm một dòng vào mảng `gallery.items` trong **cả hai** file `data/content.vi.json` và `data/content.en.json`:

```json
{ "img": "gallery/gala-4", "field": "gala", "caption": "Lotteria 25th Anniversary" }
```

`field` là một trong: `gala`, `conference`, `launching`, `entertainment`, `esports`, `tv` (quyết định bộ lọc và ảnh hiện trong popup lĩnh vực). Xoá ảnh: xoá dòng tương ứng.

> Ảnh thật nên có độ phân giải ≥ 1800px cạnh dài. Ảnh do trình duyệt lưu đệm 1 tuần - sau khi thay ảnh cùng tên, nhấn Ctrl/Cmd+Shift+R để thấy ngay.

---

## 4. Video

Điền `SHOWREEL_URL` và `VIDEO_URLS` trong `js/config.js` (mục 1). Chưa có showreel thì khung hiện "Showreel đang được cập nhật" kèm nút liên hệ.

---

## 5. Sửa nội dung & bản dịch

- Tất cả chữ trên trang nằm trong `data/content.vi.json` (tiếng Việt, mặc định) và `data/content.en.json` (tiếng Anh). Hai file có **cùng cấu trúc** - sửa chỗ nào ở file này thì sửa chỗ tương ứng ở file kia.
- Sửa trên GitHub: mở file → biểu tượng bút chì ✏️ → sửa → **Commit changes**. Vercel tự cập nhật sau khoảng 30 giây.
- Lưu ý cú pháp JSON: chữ nằm trong `"..."`; muốn có dấu ngoặc kép bên trong thì viết `\"`; các mục cách nhau bằng dấu phẩy, mục cuối không có dấu phẩy. Kiểm tra nhanh tại https://jsonlint.com nếu trang bị trống chữ.
- Một số vị trí tiêu biểu:
  - `hero` - tên, phụ đề, tagline, chữ trên nút
  - `stats.items` - 4 con số (`value` là số, `suffix` là `+`); `stats.specs` - giọng, chiều cao
  - `greeting.body` - thư "Kính chào quý đối tác"
  - `highlights.items` - danh sách thông tin nổi bật
  - `fields.items` - 6 lĩnh vực, mỗi lĩnh vực có `events` (3 sự kiện đầu hiện trên thẻ, đầy đủ trong popup)
  - `clients.list` - tên khách hàng; `testimonials.items` - phản hồi khách hàng
  - `meta.title`, `meta.description` - tiêu đề tab & mô tả khi đổi ngôn ngữ (bản tiếng Việt cho Google nằm ở `<head>` của `index.html`)
- Màu sắc, font: biến ở đầu `css/style.css` (`--deep`, `--wine`, `--stage`, `--accent`, `--ivory`, `--silver`).

---

## 6. Form đặt lịch (Formspree - miễn phí 50 lượt/tháng)

1. Vào https://formspree.io → đăng ký bằng email nhận booking.
2. **+ New Form** → đặt tên "Booking MC Thúy Vy" → tạo.
3. Copy endpoint dạng `https://formspree.io/f/abcdwxyz` → dán vào `FORM_ENDPOINT` trong `js/config.js`.
4. Gửi thử 1 lần trên website thật, mở email xác nhận của Formspree để kích hoạt.

Chưa có endpoint thì nút "Gửi yêu cầu" sẽ mở ứng dụng email của khách với nội dung điền sẵn, gửi tới `EMAIL`. Nếu Formspree lỗi, website hiện thêm nút "Gửi qua email".

---

## 7. Deploy lên Vercel (repo private vẫn dùng được, gói Hobby miễn phí)

1. Vào https://vercel.com → **Sign Up** → **Continue with GitHub** (dùng tài khoản GitHub sở hữu repo `portfolio`).
2. Ở Dashboard bấm **Add New… → Project**.
3. Mục **Import Git Repository**: nếu không thấy repo `portfolio`, bấm **Adjust GitHub App Permissions** → chọn repo `portfolio` → **Save**. Quay lại và bấm **Import** cạnh repo.
4. Màn hình **Configure Project**:
   - **Project Name**: `mc-thuyvy` (tên này thành địa chỉ `mc-thuyvy.vercel.app` nếu còn trống)
   - **Framework Preset**: `Other`
   - **Root Directory**: bấm **Edit** → chọn thư mục **`mc-thuyvy`** → **Continue** ← *quan trọng*
   - **Build and Output Settings**: để trống hết (không có build command)
5. Bấm **Deploy**. Khoảng 30 giây sau có link dạng `https://mc-thuyvy.vercel.app`.
6. Vào **Settings → Git → Production Branch**: đặt nhánh chứa website (thường là `main` sau khi merge). Từ đó mỗi lần push/commit, Vercel tự cập nhật; các nhánh khác có link xem trước riêng.
7. Điền `{{SITE_URL}}` trong `index.html` bằng link vừa có (mục 1b), commit.

`vercel.json` đã cấu hình sẵn cache cho font/ảnh và header bảo mật; `.vercelignore` loại `assets/raw/`, `tools/`, PDF và README khỏi website.

---

## 8. Gắn tên miền riêng (ví dụ `mcthuyvy.vn`)

1. Mua tên miền (Mắt Bão, PA Vietnam, Tenten, Namecheap…).
2. Vercel → Project `mc-thuyvy` → **Settings → Domains** → nhập `mcthuyvy.vn` → **Add**. Chọn phương án Vercel đề xuất (thường thêm cả `www.mcthuyvy.vn` và chuyển hướng về một bản).
3. Vào trang quản lý DNS của nơi mua tên miền, thêm đúng các bản ghi Vercel hiển thị, thường là:

| Loại | Tên (Host) | Giá trị |
|---|---|---|
| `A` | `@` | `76.76.21.21` |
| `CNAME` | `www` | `cname.vercel-dns.com` |

   (Luôn lấy giá trị **chính xác đang hiển thị** trong Vercel - có thể khác bảng trên.) Xoá bản ghi `A`/`CNAME` cũ trùng tên nếu có.
4. Chờ 5 phút - vài giờ. Vercel tự cấp HTTPS khi dấu ✓ chuyển xanh.
5. Thay `{{SITE_URL}}` (hoặc link vercel.app đã điền) trong `index.html` bằng `https://mcthuyvy.vn`, commit.
6. Kiểm tra ảnh chia sẻ: dán link vào https://developers.facebook.com/tools/debug/ → **Scrape Again**.

---

## 9. Kiểm tra trước khi công khai

- [ ] Đã thay toàn bộ ảnh placeholder (mục 3) và tạo lại og-image
- [ ] Đã điền liên hệ, showreel, Formspree trong `js/config.js`
- [ ] Đã thay `{{SITE_URL}}` trong `index.html`
- [ ] Gửi thử form, bấm thử nút Gọi/Zalo trên điện thoại
- [ ] Xem lại bản tiếng Anh (nút EN) - bản dịch do Claude soạn, nên nhờ người đọc lại các trích dẫn khách hàng
- [ ] Hỏi ý kiến các khách hàng có tên trong mục "Khách hàng nói gì" nếu cần

## Ghi chú kỹ thuật

- Font Cormorant SC, Cormorant Garamond, Be Vietnam Pro, Great Vibes được **tự host** (subset latin + vietnamese) - không phụ thuộc Google Fonts, hiển thị dấu tiếng Việt đầy đủ.
- Đổi ngôn ngữ lưu vào trình duyệt; có thể gửi thẳng link tiếng Anh: `https://mcthuyvy.vn/?lang=en`.
- Tôn trọng chế độ giảm chuyển động (prefers-reduced-motion): tắt rèm, đếm số, lấp lánh.
- Lighthouse (mô phỏng mobile, có nén như Vercel): Performance 94 · Accessibility 100 · Best Practices 100 · SEO 92 (SEO lên 100 sau khi điền `{{SITE_URL}}`). Desktop: 100 · 100 · 100 · 92.
- `tools/make_placeholders.cjs` chỉ dùng để tạo lại ảnh tạm - không cần khi đã có ảnh thật.
