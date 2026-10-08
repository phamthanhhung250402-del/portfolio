Đặt ảnh gốc của Thúy Vy vào thư mục này (không được đưa lên website - xem .vercelignore).
Tên file theo vị trí trên trang - xem hướng dẫn chi tiết trong ../../README.md, mục "Thay ảnh".

  hero.png                 chân dung tách nền (PNG trong suốt)
  greeting.jpg             chân dung cạnh thư ngỏ
  showreel-poster.jpg      ảnh bìa showreel (ngang)
  logo.png hoặc logo.svg   logo chữ ký (nền trong suốt)
  fields/gala.jpg, fields/conference.jpg, fields/launching.jpg,
  fields/entertainment.jpg, fields/esports.jpg, fields/tv.jpg
  gallery/gala-1.jpg, gallery/gala-2.jpg ... (khớp với "img" trong data/content.*.json)

Sau đó chạy:  python3 tools/build_images.py
