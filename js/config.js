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
    social: { price: null, delivery: "Theo tháng" },
    ads: { price: null, delivery: "Báo cáo hằng tuần" }
  },

  // Số liệu Paid Ads (TopZone Official). value: null => ô đó tự ẩn.
  // TUỲ BẠN: CPV/CPM là số liệu nội bộ của công ty, cân nhắc trước khi công khai.
  ads: {
    cpv: { value: null, label: "CPV trung bình" },   // ví dụ "45đ"
    cpm: { value: null, label: "CPM trung bình" }    // ví dụ "9.800đ"
  }
};
