/*
 * CẤU HÌNH WEBSITE - sửa file này để thay thông tin liên hệ, giá, số liệu Paid Ads.
 * Giá trị để null hoặc còn dạng {{...}} sẽ tự ẩn / hiện chữ mặc định.
 */
window.SITE_CONFIG = {
  // Facebook cá nhân - nút liên hệ chính (mở Messenger)
  facebook: "https://www.facebook.com/thanhhung250402/",
  messenger: "https://m.me/thanhhung250402",

  // Số Zalo hiển thị ở mục Liên hệ
  zalo: "+84 559 641 425",

  // Email (để null nếu không muốn hiện)
  email: null,

  linkedin: "https://www.linkedin.com/in/hung-pham2002/",

  // Fanpage có bài đăng trong mục Social
  socialPage: { name: "Future Mobile", url: "https://www.facebook.com/Future.Mobile.Official" },

  // Showreel trong khung điện thoại. null = slideshow 4 clip nổi bật.
  // Có file thì chép vào assets/showreel.mp4 và đổi thành "assets/showreel.mp4".
  showreel: null,

  // Giá từng gói. price: null => hiện "Liên hệ báo giá". Ví dụ price: "800.000đ/video"
  services: {
    edit: { price: null, delivery: "1-3 ngày/video" },
    script: { price: null, delivery: "2-3 ngày/kịch bản" },
    social: { price: null, delivery: "Theo tháng" },
    ads: { price: null, delivery: "Báo cáo hằng tuần" }
  },

  // Số liệu Paid Ads (TopZone Official, T7-T9/2026). value: null => ô đó tự ẩn.
  ads: {
    cpmBest: { value: "7.425đ", label: "CPM tốt nhất", note: "chiến dịch video TikTok tốt nhất" },
    cpm: { value: "15.574đ", label: "CPM trung bình", note: "toàn bộ chiến dịch T7-T9, gồm cả quảng cáo ảnh" }
  }
};
