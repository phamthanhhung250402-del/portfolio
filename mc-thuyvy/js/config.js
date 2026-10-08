/*
 * CẤU HÌNH LIÊN HỆ & VIDEO - chỉ cần sửa file này.
 * Thay mỗi "{{...}}" bằng thông tin thật (giữ nguyên dấu ngoặc kép).
 * Mục nào còn để "{{...}}" hoặc để trống "" sẽ tự ẩn trên website.
 */
window.SITE_CONFIG = {
  // Số điện thoại, dạng quốc tế hoặc nội địa. Vd: "0909 123 456" hoặc "+84 909 123 456"
  PHONE: "{{PHONE}}",

  // Số Zalo (thường trùng số điện thoại) hoặc link zalo.me. Vd: "0909123456" hoặc "https://zalo.me/0909123456"
  ZALO: "{{ZALO}}",

  // Email nhận booking. Vd: "booking@mcthuyvy.vn"
  EMAIL: "{{EMAIL}}",

  // Link mạng xã hội đầy đủ, bắt đầu bằng https://
  FACEBOOK: "{{FACEBOOK}}",
  TIKTOK: "{{TIKTOK}}",
  INSTAGRAM: "{{INSTAGRAM}}",

  // Link showreel chính: YouTube, TikTok, Facebook video hoặc file .mp4
  // Vd: "https://www.youtube.com/watch?v=XXXXXXXXXXX"
  SHOWREEL_URL: "{{SHOWREEL_URL}}",

  // Các video chương trình khác (không giới hạn số lượng), mỗi link một dòng:
  // VIDEO_URLS: [
  //   "https://www.youtube.com/watch?v=AAAAAAAAAAA",
  //   "https://www.tiktok.com/@mcthuyvy/video/1234567890123456789",
  // ],
  VIDEO_URLS: ["{{VIDEO_URLS}}"],

  // Endpoint Formspree cho form đặt lịch. Vd: "https://formspree.io/f/abcdwxyz"
  // Chưa có thì form sẽ mở ứng dụng email (gửi tới EMAIL ở trên).
  FORM_ENDPOINT: "{{FORM_ENDPOINT}}"
};
