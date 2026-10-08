# Portfolio - Phạm Thành Hưng

Website portfolio Video & Social Content, một trang, HTML/CSS/JS thuần (không framework, không cần build).

**Link web:** https://phamthanhhung250402-del.github.io/portfolio/

```
index.html              Nội dung trang (hero, dịch vụ, kinh nghiệm, liên hệ...)
css/style.css           Giao diện
js/config.js            ← Facebook, Zalo, email, giá, số CPV/CPM, showreel
js/main.js              Lưới video, bộ lọc, lightbox, nhúng bài Facebook, hiệu ứng
data/clips.json         ← Video đã edit (mục "Video đã edit" + số liệu đầu trang)
data/posts.json         ← Bài đăng Facebook (mục "Social")
data/ads.json           ← Video quảng cáo TopZone (mục "Paid Ads")
assets/                 Ảnh chia sẻ (og-image.jpg), favicon, ảnh cá nhân (photos/), showreel, thumbnail
scripts/fetch-thumbs.mjs  Script tải thumbnail từ TikTok
```

---

## 1. Liên hệ, giá, số liệu Paid Ads

Mở `js/config.js`:

```js
facebook: "https://www.facebook.com/thanhhung250402/",
messenger: "https://m.me/thanhhung250402",   // nút "Nhắn Facebook" mở thẳng Messenger
zalo: "+84 559 641 425",
email: null,                                  // điền email nếu muốn hiện, vd "ban@gmail.com"
services: {
  edit:   { price: null, delivery: "1-3 ngày/video" },   // price: "500.000đ/video"
  script: { price: null, delivery: "2-3 ngày/kịch bản" },
  social: { price: null, delivery: "Theo tháng" },
  ads:    { price: null, delivery: "Báo cáo hằng tuần" }
},
ads: {
  cpmBest: { value: "7.425đ", label: "CPM tốt nhất", note: "chiến dịch video TikTok tốt nhất" },
  cpm:     { value: "15.574đ", label: "CPM trung bình", note: "toàn bộ chiến dịch T7-T9, gồm cả quảng cáo ảnh" }
}
```

- `price: null` → hiện "Liên hệ báo giá". Điền giá → hiện "Giá từ ...".
- Ô CPM nào để `value: null` thì tự ẩn. **Lưu ý:** CPV/CPM là số liệu nội bộ của TopZone - nên hỏi lại quản lý trước khi công khai.
- Sửa mô tả gói dịch vụ, kỹ năng, quy trình, kinh nghiệm: sửa trực tiếp trong `index.html` (tìm theo chữ).
- Đổi ảnh cá nhân: thay file cùng tên trong `assets/photos/` (`hung-main.webp` 900×1200, 3 ảnh nhỏ `hung-podium/talk/ballot.webp` 600×750, `hung-avatar.webp` vuông 192×192, ảnh sự kiện `event-*.webp` 1200×800, banner `collage.webp`).

**Sửa nhanh trên GitHub (không cần cài gì):** vào repo → mở file → bấm biểu tượng bút chì ✏️ → sửa → **Commit changes**. Khoảng 1 phút sau web tự cập nhật.

## 2. Thêm video, bài đăng, video quảng cáo

Mỗi dòng trong file JSON là một mục (nhớ dấu phẩy giữa các dòng). Mục có `"placeholder":true` sẽ **bị ẩn** - dùng cho dòng mẫu.

### Video đã edit - `data/clips.json`

```json
{"id":"7690000000000000000","brand":"Future Mobile","channel":"@future.mobile.official","title":"Tên video","views":1250000,"tiktok":"https://www.tiktok.com/@future.mobile.official/video/7690000000000000000"}
```

| Trường | Ý nghĩa |
|---|---|
| `id` | Dãy số cuối link TikTok |
| `brand` | Tên thương hiệu - **tab lọc được tạo tự động** theo trường này (gõ giống nhau thì gộp chung một tab) |
| `title` | Tiêu đề trên card |
| `views` | Lượt xem, ghi số đầy đủ (web tự đổi thành 1,2M / 520K) |
| `tiktok` | Link video |
| `duration` | (tuỳ chọn) thời lượng tính bằng giây |
| `date` | (tuỳ chọn) ngày đăng `YYYY-MM-DD` |
| `facebook` | (tuỳ chọn) link bản Facebook của video |
| `featured` | (tuỳ chọn) `true` = đưa vào slideshow khung điện thoại; không có thì tự lấy 4 video view cao nhất |
| `thumb` | Ảnh bìa - script ở mục 3 tự điền |

Video tự xếp theo lượt xem giảm dần. **Số liệu đầu trang (tổng lượt xem, clip cao nhất) tự tính từ file này.**

### Bài đăng Facebook - `data/posts.json`

```json
{"url":"https://www.facebook.com/Future.Mobile.Official/posts/pfbid0...","title":"Poster ra mắt iPhone 17"}
```

- `url`: mở bài trên Facebook → bấm vào **giờ đăng** của bài → copy link trên thanh địa chỉ. Bài phải ở chế độ **Công khai**.
- Bài được nhúng thẳng từ Facebook (người xem thấy ảnh, caption, lượt tương tác thật).
- (tuỳ chọn) `"height":700` nếu khung bài bị cắt hoặc thừa khoảng trắng.
- (tuỳ chọn) `"image":"assets/posts/ten-anh.jpg"` để hiện ảnh chụp thay vì nhúng (chép ảnh vào `assets/posts/`, tỉ lệ 4:5).

### Video quảng cáo - `data/ads.json`

Giống `clips.json`, thêm `cpv`, `cpm` (dạng chữ, vd `"cpv":"35đ"`). Có số thì hiện nhãn cam trên card; `null` thì ẩn. Nên chọn 4 video có CPV/CPM đẹp nhất.

## 3. Tải thumbnail clip (chạy trên máy bạn)

Khi chưa có ảnh, card dùng nền gradient + tiêu đề. Để có ảnh bìa thật, chạy trên máy bạn:

1. Cài [Node.js](https://nodejs.org) bản 18 trở lên (bản LTS).
2. Tải repo về: `git clone https://github.com/phamthanhhung250402-del/portfolio.git` rồi `cd portfolio`
3. (Tuỳ chọn, để ra file `.webp` nhẹ hơn) `npm install sharp` - hoặc máy có sẵn `ffmpeg` cũng được.
4. Chạy:
   ```bash
   node scripts/fetch-thumbs.mjs
   ```
   Script gọi `https://www.tiktok.com/oembed?url=...`, lưu ảnh vào `assets/thumbs/{id}.webp` và tự ghi trường `thumb` vào `data/clips.json` và `data/ads.json`. Chạy lại khi thêm clip mới (chỉ tải clip chưa có ảnh; thêm `--force` để tải lại hết).
5. Đẩy lên GitHub:
   ```bash
   git add assets/thumbs data
   git commit -m "Thêm thumbnail clip"
   git push
   ```

Không có sharp/ffmpeg thì ảnh được lưu dạng `.jpg` - web vẫn hiển thị bình thường. Nếu `sharp` cài lỗi, bỏ qua bước 3.

## 4. Thay showreel

1. Xuất video dọc **9:16, MP4 (H.264)**, khoảng 720×1280, 15-30 giây, **không cần tiếng** (web phát tắt tiếng), nên dưới 8 MB để tải nhanh trên 4G.
2. Đặt tên `showreel.mp4`, chép vào thư mục `assets/`.
3. Trong `js/config.js` đổi `showreel: null` thành `showreel: "assets/showreel.mp4"`.

Video tự phát, lặp, tắt tiếng trong khung điện thoại. Khi `showreel` là `null` (hoặc file lỗi) web tự hiển thị slideshow 4 video nổi bật.

## 5. Xem thử trên máy

Trang tải các file trong `data/` nên cần chạy qua server (mở thẳng file `index.html` sẽ không thấy clip):

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

## 9. Cập nhật số liệu

- **Đầu trang:** tổng lượt xem + clip cao nhất tự tính từ `data/clips.json`. Ô "50–70 video edit mỗi tháng" sửa trong `index.html`, phần `<!-- HERO -->`.
- **Paid Ads:** các ô 14,8M+ / ×5,1 / 1,8M nằm trong `index.html`, phần `<!-- PAID ADS -->`. Mỗi số có `data-to` (giá trị chạy hiệu ứng đếm) và chữ hiển thị - sửa cả hai cho khớp. CPV/CPM sửa trong `js/config.js`.
