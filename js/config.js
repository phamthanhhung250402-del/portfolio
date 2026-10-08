/*
 * CẤU HÌNH WEBSITE - chỉ cần sửa file này để thay thông tin liên hệ & giá.
 * Thay các giá trị dạng {{...}} rồi lưu lại, không cần sửa HTML.
 */
window.SITE_CONFIG = {
  // Số điện thoại Zalo, viết liền, ví dụ: "0901234567"
  zalo: "{{ZALO}}",

  // Email nhận brief, ví dụ: "hungpham@gmail.com"
  email: "{{EMAIL}}",

  linkedin: "https://www.linkedin.com/in/hung-pham2002/",

  // Showreel trong khung điện thoại ở đầu trang.
  // Khi đã chép file vào assets/showreel.mp4 thì đổi null thành "assets/showreel.mp4".
  // Để null: hiển thị slideshow 4 clip nổi bật (featured: true trong data/clips.json).
  showreel: null,

  // Giá & thời gian giao của 4 gói dịch vụ. Ví dụ price: "1.500.000đ"
  services: {
    shortform: { price: "{{PRICE_1}}", delivery: "2-3 ngày" },
    event: { price: "{{PRICE_2}}", delivery: "2-3 ngày sau sự kiện" },
    ads: { price: "{{PRICE_3}}", delivery: "5-7 ngày" },
    talking: { price: "{{PRICE_4}}", delivery: "3-5 ngày" }
  }
};
