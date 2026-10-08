# Portfolio - Phạm Thành Hưng

Website portfolio Video & Social Content, một trang, HTML/CSS/JS thuần (không framework, không cần build).

**Link web:** https://phamthanhhung250402-del.github.io/portfolio/

```
index.html              Nội dung trang (hero, dịch vụ, kinh nghiệm, liên hệ...)
css/style.css           Giao diện
js/config.js            ← Zalo, email, LinkedIn, giá, thời gian giao, showreel
js/main.js              Lưới clip, bộ lọc, lightbox, hiệu ứng
data/clips.json         ← Danh sách clip
assets/                 Ảnh chia sẻ (og-image.jpg), favicon, showreel, thumbnail
scripts/fetch-thumbs.mjs  Script tải thumbnail từ TikTok
```

---

## 1. Thay Zalo, email, giá

Mở `js/config.js`, thay các giá trị `{{...}}`:

```js
zalo: "0901234567",          // số Zalo, viết liền
email: "ban@gmail.com",
services: {
  shortform: { price: "1.500.000đ", delivery: "2-3 ngày" },
  event:     { price: "3.000.000đ", delivery: "2-3 ngày sau sự kiện" },
  ads:       { price: "5.000.000đ", delivery: "5-7 ngày" },
  talking:   { price: "2.000.000đ", delivery: "3-5 ngày" }
}
```

- `shortform` = Dựng video short-form 9:16 · `event` = Quay + dựng sự kiện/khai trương · `ads` = Kịch bản + sản xuất video quảng cáo · `talking` = Video talking-head/giải thích sản phẩm.
- Khi chưa điền Zalo/email, các nút "Nhắn Zalo"/"Gửi Email" sẽ cuộn xuống mục Liên hệ thay vì mở link hỏng.
- Muốn sửa mô tả từng gói, quy trình, kinh nghiệm: sửa trực tiếp trong `index.html` (tìm theo chữ).

**Sửa nhanh trên GitHub (không cần cài gì):** vào repo → mở file `js/config.js` → bấm biểu tượng bút chì ✏️ → sửa → **Commit changes**. Khoảng 1 phút sau web tự cập nhật.

## 2. Thêm clip mới

Mở `data/clips.json`, thêm một dòng (nhớ dấu phẩy giữa các dòng):

```json
{"id":"7690000000000000000","category":"ads","title":"Tên clip","views":250000,"duration":30,"date":"2026-10-05","tiktok":"https://www.tiktok.com/@topzone.official/video/7690000000000000000","facebook":null}
```

| Trường | Ý nghĩa |
|---|---|
| `id` | Dãy số cuối link TikTok (dùng để phát video trong lightbox) |
| `category` | `launch` (Launch & Sự kiện) · `ads` (Quảng cáo sản phẩm) · `service` (Dịch vụ & Talking-head) · `creative` (Sáng tạo & Giải trí) |
| `title` | Tiêu đề hiển thị trên card |
| `views` | Tổng lượt xem TikTok + Facebook, ghi số đầy đủ (web tự đổi thành 1,8M / 520K) |
| `duration` | Thời lượng tính bằng giây |
| `date` | Ngày đăng, dạng `YYYY-MM-DD` |
| `tiktok` / `facebook` | Link clip; không có link Facebook thì để `null` (nút "Xem trên Facebook" tự ẩn) |
| `featured` | `true` = đưa vào slideshow ở khung điện thoại (nên giữ đúng 4 clip) |
| `placeholder` | `true` = **ẩn** khỏi trang (2 mục mẫu cho clip freelance vlog/hài đang dùng cái này) |
| `thumb` | Đường dẫn ảnh bìa - script ở mục 3 tự điền |

Clip được xếp theo lượt xem giảm dần. Với 2 mục mẫu `freelance-...`: thay `id`, `title`, `views`, link thật rồi **xoá** dòng `"placeholder":true` để hiện lên web.

> Kiểm tra file JSON có hợp lệ không: dán nội dung vào https://jsonlint.com

## 3. Tải thumbnail clip (chạy trên máy bạn)

Hiện các card đang dùng nền gradient + tiêu đề vì máy chủ dựng web bị chặn truy cập tiktok.com. Trên máy bạn:

1. Cài [Node.js](https://nodejs.org) bản 18 trở lên (bản LTS).
2. Tải repo về: `git clone https://github.com/phamthanhhung250402-del/portfolio.git` rồi `cd portfolio`
3. (Tuỳ chọn, để ra file `.webp` nhẹ hơn) `npm install sharp` - hoặc máy có sẵn `ffmpeg` cũng được.
4. Chạy:
   ```bash
   node scripts/fetch-thumbs.mjs
   ```
   Script gọi `https://www.tiktok.com/oembed?url=...`, lưu ảnh vào `assets/thumbs/{id}.webp` và tự ghi trường `thumb` vào `data/clips.json`. Chạy lại khi thêm clip mới (chỉ tải clip chưa có ảnh; thêm `--force` để tải lại hết).
5. Đẩy lên GitHub:
   ```bash
   git add assets/thumbs data/clips.json
   git commit -m "Thêm thumbnail clip"
   git push
   ```

Không có sharp/ffmpeg thì ảnh được lưu dạng `.jpg` - web vẫn hiển thị bình thường. Nếu `sharp` cài lỗi, bỏ qua bước 3.

## 4. Thay showreel

1. Xuất video dọc **9:16, MP4 (H.264)**, khoảng 720×1280, 15-30 giây, **không cần tiếng** (web phát tắt tiếng), nên dưới 8 MB để tải nhanh trên 4G.
2. Đặt tên `showreel.mp4`, chép vào thư mục `assets/`.
3. Trong `js/config.js` đổi `showreel: null` thành `showreel: "assets/showreel.mp4"`.

Video tự phát, lặp, tắt tiếng trong khung điện thoại. Khi `showreel` là `null` (hoặc file lỗi) web tự hiển thị slideshow 4 clip `featured`.

## 5. Xem thử trên máy

Trang tải `data/clips.json` nên cần chạy qua server (mở thẳng file `index.html` sẽ không thấy clip):

```bash
npx serve .            # hoặc: python3 -m http.server 8000
```

Rồi mở địa chỉ hiện ra (vd. http://localhost:3000).

## 6. Deploy GitHub Pages

1. Đảm bảo code nằm ở nhánh `main` (merge Pull Request nếu code đang ở nhánh khác).
2. Vào repo trên GitHub → **Settings** → **Pages**.
3. Mục **Build and deployment** → Source: **Deploy from a branch** → Branch: **main**, thư mục **/ (root)** → **Save**.
4. Đợi 1-2 phút, link web hiện ở đầu trang Pages: `https://phamthanhhung250402-del.github.io/portfolio/`

Từ đó mỗi lần sửa và commit vào `main`, web tự cập nhật sau khoảng 1 phút (file `.nojekyll` đã có sẵn để GitHub phục vụ nguyên trạng).

## 7. Gắn tên miền riêng (vd. `hungpham.vn`)

1. Mua tên miền (Mắt Bão, PA Vietnam, Tenten, Namecheap...).
2. Trong trang quản lý DNS của nhà cung cấp, thêm:

   | Loại | Tên (Host) | Giá trị |
   |---|---|---|
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | phamthanhhung250402-del.github.io |

3. GitHub → **Settings → Pages → Custom domain** → nhập `hungpham.vn` → **Save** (GitHub tự tạo file `CNAME`). Đợi DNS cập nhật (vài phút đến vài giờ) rồi tích **Enforce HTTPS**.
4. Trong `index.html`, thay toàn bộ `https://phamthanhhung250402-del.github.io/portfolio/` bằng `https://hungpham.vn/` (các thẻ `canonical`, `og:url`, `og:image`, `twitter:image`) để ảnh xem trước khi gửi link vẫn đúng.

## 8. Ảnh xem trước khi gửi link (Zalo/Facebook)

- Ảnh: `assets/og-image.jpg` (1200×630). Muốn đổi thì thay file cùng tên, cùng kích thước.
- Tiêu đề/mô tả: các thẻ `og:title`, `og:description` trong `index.html`.
- Facebook lưu bộ nhớ đệm: sau khi đổi, dán link vào https://developers.facebook.com/tools/debug/ và bấm **Scrape Again**. Zalo cũng lưu đệm một thời gian, có thể thêm `?v=2` vào cuối link khi gửi để buộc tải lại.

## 9. Cập nhật số liệu hero

Ba số liệu và dòng ghi chú nằm trong `index.html`, phần `<!-- HERO -->`. Mỗi số có thuộc tính `data-to` (giá trị để chạy hiệu ứng đếm) và chữ hiển thị - sửa cả hai cho khớp, ví dụ `data-to="20.5"` và `20,5M+`. Nhớ sửa luôn mô tả trong `<meta name="description">` / `og:description` nếu có nhắc số.
