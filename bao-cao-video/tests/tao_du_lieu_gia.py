"""Tạo bộ dữ liệu GIẢ đúng cấu trúc để chạy thử toàn bộ luồng.

    python3 tests/tao_du_lieu_gia.py            -> ghi vào samples/demo/input
    python3 tests/tao_du_lieu_gia.py <thu_muc>  -> ghi vào thư mục khác (dùng trong test)

Mọi tên, số, link đều là bịa. Tiêu đề file export lấy từ samples/headers/GIA-DINH_*.csv.
"""
from __future__ import annotations

import csv
import datetime as dt
import random
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
from baocao.config import chu_sang_so  # noqa: E402

PAGE_ID = "100064123456789"

TIEU_DE_03 = ["Tuần", "Thời gian", "Kênh", "Pillar/Theme", "Loại nội dung", "Chủ đề/Deliverable", "Phase", "Status",
              "Ghi chú", "Link TikTok", "Ngày đăng", "Link FB", "Người làm", "Nhóm nội dung", "Thời lượng (s)",
              "TikTok views", "TikTok likes", "TikTok shares", "FB lượt xem 3s", "FB reach", "FB xem TB (s)",
              "FB chạy ads", "Tổng views", "Link YouTube", "YouTube views", "TikTok ER", "FB hook rate",
              "Campaign TikTok ads", "Chi phí TikTok ads phân bổ", "CPV TikTok", "FB người xem ≥3s", "Chi phí FB ads",
              "CPV FB 3s", "FB ads lượt phát", "FB ads xem 25%", "FB ads xem 50%", "Tỷ lệ xem 25%", "Tỷ lệ xem 50%"]

CONG_THUC = {
    "W": "=IFERROR(P{r}+S{r}+N(Y{r}),\"\")",
    "Z": "=IFERROR((Q{r}+R{r})/P{r},\"\")",
    "AA": "=IFERROR(S{r}/T{r},\"\")",
    "AD": "=IFERROR(AC{r}/P{r},\"\")",
    "AG": "=IFERROR(AF{r}/AE{r},\"\")",
    "AK": "=IFERROR(AI{r}/AH{r},\"\")",
    "AL": "=IFERROR(AJ{r}/AH{r},\"\")",
}

# nhóm -> (CPV TikTok gốc, xem TB gốc, tỷ lệ 50% gốc, ER gốc, views gốc, thời lượng tốt nhất)
NHOM = {
    "Promotion / Giá - trả chậm":          (11.0, 6.8, 0.22, 0.020, 180_000, 25),
    "Thu cũ đổi mới & Dịch vụ TopZone":    (13.5, 7.2, 0.24, 0.018, 120_000, 35),
    "Upgrade / Hướng dẫn (talking-head)":  (16.0, 9.5, 0.30, 0.026, 90_000, 50),
    "NPI - Announce / Sản phẩm mới":       (8.5, 8.0, 0.27, 0.035, 320_000, 30),
    "NPI - Đặt trước (CTA)":               (10.0, 6.0, 0.20, 0.022, 220_000, 18),
    "Mở bán / Sự kiện / Social proof":     (9.0, 7.5, 0.26, 0.040, 380_000, 28),
    "Motion KV":                           (14.0, 4.5, 0.15, 0.012, 110_000, 15),
    "Sketch hài - Ai Dè":                  (7.5, 10.5, 0.33, 0.055, 260_000, 55),
    "Workshop / Cộng đồng":                (12.0, 8.5, 0.28, 0.030, 140_000, 40),
}

TIEU_DE_MAU = {
    "Promotion / Giá - trả chậm": ["iPhone 16 giảm sâu trả chậm 0%", "MacBook Air M4 giá sốc cuối tuần", "Trả chậm 0đ trả trước iPad",
                                   "AirPods Pro 3 giảm thêm 500K", "Apple Watch giá tốt nhất tháng"],
    "Thu cũ đổi mới & Dịch vụ TopZone": ["Lên đời iPhone trợ giá 2 triệu", "Thu cũ MacBook giá cao", "Dịch vụ dán màn hình miễn phí",
                                         "Bảo hành 1 đổi 1 tại TopZone"],
    "Upgrade / Hướng dẫn (talking-head)": ["5 mẹo iOS ít người biết", "Có nên lên iPhone 17 Pro?", "So sánh MacBook Air và Pro",
                                           "Cách chụp đêm đẹp bằng iPhone", "Chuyển dữ liệu Android sang iPhone"],
    "NPI - Announce / Sản phẩm mới": ["iPhone 17 Pro chính thức ra mắt", "Màu mới iPhone 17 có gì", "Apple Watch Series 11 lộ diện",
                                      "Tóm tắt sự kiện Apple 3 phút"],
    "NPI - Đặt trước (CTA)": ["Đặt trước iPhone 17 nhận quà 3 triệu", "Cọc 500K giữ máy sớm nhất", "Đặt trước - giao máy tận nhà"],
    "Mở bán / Sự kiện / Social proof": ["Khách xếp hàng từ 5h sáng", "Mở bán iPhone 17 tại TopZone", "Người đầu tiên cầm iPhone 17",
                                        "Không khí đêm mở bán"],
    "Motion KV": ["KV khuyến mãi tháng", "Motion giá iPad", "KV Apple Watch"],
    "Sketch hài - Ai Dè": ["Ai dè mua iPhone được tặng thêm", "Ai dè đổi máy cũ lời to"],
    "Workshop / Cộng đồng": ["Workshop chụp ảnh iPhone", "Lớp Mac cho người mới", "Workshop Apple Watch chạy bộ"],
}

# Lịch: (tháng, tiêu đề khối, [(phase, từ ngày, đến ngày, {nhóm: số video})])
LICH = [
    ("2026-07", "JULY 2026 - BAU / Back to School · 25 video", [
        ("T7 - BAU", 1, 31, {"Promotion / Giá - trả chậm": 7, "Thu cũ đổi mới & Dịch vụ TopZone": 5,
                             "Upgrade / Hướng dẫn (talking-head)": 5, "Motion KV": 3, "Mở bán / Sự kiện / Social proof": 2,
                             "Workshop / Cộng đồng": 2, "Sketch hài - Ai Dè": 1})]),
    ("2026-08", "AUGUST 2026 - BAU + Before Announce · 26 video", [
        ("T8 - BAU", 1, 17, {"Promotion / Giá - trả chậm": 5, "Thu cũ đổi mới & Dịch vụ TopZone": 3,
                             "Upgrade / Hướng dẫn (talking-head)": 3, "Motion KV": 2, "Workshop / Cộng đồng": 1}),
        ("Before Announce", 18, 31, {"NPI - Announce / Sản phẩm mới": 4, "Upgrade / Hướng dẫn (talking-head)": 3,
                                     "Promotion / Giá - trả chậm": 2, "Sketch hài - Ai Dè": 1, "Thu cũ đổi mới & Dịch vụ TopZone": 2})]),
    ("2026-09", "SEPTEMBER 2026 - Launch iPhone 17 · 28 video", [
        ("Announce", 1, 10, {"NPI - Announce / Sản phẩm mới": 5, "Upgrade / Hướng dẫn (talking-head)": 2}),
        ("Pre-order", 11, 18, {"NPI - Đặt trước (CTA)": 5, "Thu cũ đổi mới & Dịch vụ TopZone": 2, "Promotion / Giá - trả chậm": 1}),
        ("Mở bán", 19, 24, {"Mở bán / Sự kiện / Social proof": 5, "Motion KV": 1}),
        ("Sau mở bán", 25, 30, {"Promotion / Giá - trả chậm": 2, "Thu cũ đổi mới & Dịch vụ TopZone": 1,
                                "Mở bán / Sự kiện / Social proof": 1, "Sketch hài - Ai Dè": 1, "Workshop / Cộng đồng": 1})]),
]

THANG_CAP_NHAT = "2026-09"


def doc_tieu_de(ten: str) -> list[str]:
    with open(GOC / "samples" / "headers" / ten, encoding="utf-8-sig") as f:
        return next(csv.reader(f))


def tao(thu_muc: Path, seed: int = 42) -> dict:
    rnd = random.Random(seed)
    thu_muc = Path(thu_muc)
    (thu_muc / "sheet").mkdir(parents=True, exist_ok=True)
    (thu_muc / "exports").mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()
    wb.active.title = "01 Tổng quan"
    wb["01 Tổng quan"]["A1"] = "DỮ LIỆU GIẢ - chỉ để chạy thử"
    ws = wb.create_sheet("03 Content Calendars")
    ws["A1"] = "CONTENT CALENDAR - TOPZONE (DỮ LIỆU GIẢ)"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A3"] = "Bảng mẫu tạo tự động để kiểm thử công cụ."
    for i, h in enumerate(TIEU_DE_03, 1):
        c = ws.cell(5, i, h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DDDDDD")

    r = 6
    dem_id = 0
    videos = []          # mọi video (để tạo export)
    for thang, tieu_de_khoi, gds in LICH:
        nam, th = map(int, thang.split("-"))
        ws.cell(r, 1, tieu_de_khoi).font = Font(bold=True)
        r += 1
        for phase, d1, d2, nhom_sl in gds:
            ds = [n for n, sl in nhom_sl.items() for _ in range(sl)]
            rnd.shuffle(ds)
            for nhom in ds:
                dem_id += 1
                ngay = dt.date(nam, th, rnd.randint(d1, d2))
                cpv0, xem0, x50_0, er0, views0, tl_tot = NHOM[nhom]
                tl = max(8, int(rnd.gauss(tl_tot, 14)))
                # thời lượng lệch xa mức tốt nhất -> kém hơn
                lech = min(1.0, abs(tl - tl_tot) / 40)
                he_so = rnd.lognormvariate(0, 0.28) * (1 + 0.6 * lech)
                tid = str(7_540_000_000_000_000_000 + dem_id * 7_919_331 + rnd.randint(0, 999))
                post = str(1_200_000_000_000_000 + dem_id * 104_729)
                kieu_fb = dem_id % 3
                if kieu_fb == 0:
                    link_fb = f"https://www.facebook.com/topzone.vn/videos/{post}/"
                elif kieu_fb == 1:
                    link_fb = f"https://www.facebook.com/reel/{post}"
                else:
                    link_fb = f"https://www.facebook.com/{PAGE_ID}/posts/{post}"
                nguoi = rnd.choices(["Hưng", "Vy", "Hùng", "Hưng, Vy"], [0.72, 0.12, 0.08, 0.08])[0]
                status = "Đã air" if rnd.random() > 0.06 else rnd.choice(["Đang edit", "Lên kịch bản"])
                views = int(views0 * rnd.lognormvariate(0, 0.45) / (0.7 + 0.5 * lech))
                cp_tt = views * cpv0 * he_so
                fb_3s = int(views * rnd.uniform(0.35, 0.7))
                reach = int(fb_3s / rnd.uniform(0.25, 0.45))
                plays = int(fb_3s * rnd.uniform(1.4, 1.9))
                v = {
                    "dong": r, "thang": thang, "nhom": nhom, "phase": phase, "ngay": ngay, "nguoi": nguoi, "status": status,
                    "tieu_de": rnd.choice(TIEU_DE_MAU[nhom]) + f" #{dem_id}", "tid": tid, "post": post,
                    "link_tt": f"https://www.tiktok.com/@topzone.official/video/{tid}", "link_fb": link_fb, "tl": tl,
                    "views": views, "likes": int(views * er0 * rnd.uniform(0.6, 1.3) * 0.85),
                    "shares": int(views * er0 * rnd.uniform(0.6, 1.3) * 0.15),
                    "fb_3s": fb_3s, "reach": reach,
                    "xem_tb": round(xem0 * rnd.uniform(0.8, 1.2) / (1 + 0.4 * lech), 1),
                    "cp_tt": round(cp_tt), "campaign": f"TZ_{thang}_{phase.split(' - ')[-1]}".replace(" ", "_"),
                    "ads_3s": int(fb_3s * rnd.uniform(0.5, 0.8)),
                    "cp_fb": round(fb_3s * rnd.uniform(0.5, 0.8) * cpv0 * 0.9 * he_so),
                    "plays": plays, "p25": int(plays * rnd.uniform(0.35, 0.55)),
                    "p50": int(plays * x50_0 * rnd.uniform(0.8, 1.2) / (1 + 0.4 * lech)),
                }
                videos.append(v)
                ghi_dong(ws, r, v, day_du=(thang != THANG_CAP_NHAT))
                r += 1
    # Vài lỗi cố ý trong tháng cập nhật (để kiểm tra danh sách "không ghép được")
    cua_toi_t9 = [v for v in videos if v["thang"] == THANG_CAP_NHAT and v["nguoi"].startswith("Hưng") and v["status"] == "Đã air"]
    loi = {}
    loi["thieu_link_tt"] = cua_toi_t9[2]
    ws.cell(cua_toi_t9[2]["dong"], chu_sang_so("J")).value = None
    loi["link_rut_gon"] = cua_toi_t9[5]
    ws.cell(cua_toi_t9[5]["dong"], chu_sang_so("J"), "https://vt.tiktok.com/ZSabc123/")
    loi["fb_share"] = cua_toi_t9[7]
    ws.cell(cua_toi_t9[7]["dong"], chu_sang_so("L"), "https://www.facebook.com/share/r/1AbCdEfGh/")
    loi["sai_id"] = cua_toi_t9[9]
    sai = cua_toi_t9[9]["link_tt"][:-3] + "000"
    ws.cell(cua_toi_t9[9]["dong"], chu_sang_so("J"), sai)
    # một video tháng 9 đã có số cũ (để kiểm tra "giữ giá trị cũ")
    giu_cu = cua_toi_t9[0]
    ghi_dong(ws, giu_cu["dong"], giu_cu, day_du=True)
    ws.column_dimensions["F"].width = 40

    # Các tab khác
    ws5 = wb.create_sheet("05 Phase Plan")
    for i, h in enumerate(["Giai đoạn", "Từ ngày", "Đến ngày", "Mục tiêu"], 1):
        ws5.cell(1, i, h).font = Font(bold=True)
    for i, (p, a, b, m) in enumerate([("T7 - BAU", "01/07/2026", "31/07/2026", "Doanh số BAU"),
                                      ("Before Announce", "18/08/2026", "08/09/2026", "Khơi gợi"),
                                      ("Announce", "09/09/2026", "10/09/2026", "Thông tin sản phẩm"),
                                      ("Pre-order", "11/09/2026", "18/09/2026", "Đặt cọc"),
                                      ("Mở bán", "19/09/2026", "24/09/2026", "Mở bán"),
                                      ("Sau mở bán", "25/09/2026", "15/10/2026", "Duy trì")], 2):
        for j, x in enumerate((p, a, b, m), 1):
            ws5.cell(i, j, x)
    ws6 = wb.create_sheet("06 Performance")
    ws6["A1"], ws6["B1"] = "Tổng TikTok views", "=SUM('03 Content Calendars'!P:P)"
    ws6["A2"], ws6["B2"] = "Tổng chi phí TikTok", "=SUM('03 Content Calendars'!AC:AC)"
    ws7 = wb.create_sheet("07 Paid Ads")
    for i, h in enumerate(["Campaign", "Nền tảng", "Ngân sách", "Từ", "Đến"], 1):
        ws7.cell(1, i, h).font = Font(bold=True)
    ws7.append(["TZ_2026-09_Mở_bán", "TikTok", 150_000_000, "19/09/2026", "24/09/2026"])
    p_sheet = thu_muc / "sheet" / "Ke-hoach-noi-dung-TopZone-DU-LIEU-GIA.xlsx"
    wb.save(p_sheet)

    t9 = [v for v in videos if v["thang"] == THANG_CAP_NHAT and v["status"] == "Đã air"]
    t8 = [v for v in videos if v["thang"] == "2026-08" and v["status"] == "Đã air"][:3]

    # ---------------- TikTok Ads Manager (CSV, tiêu đề tiếng Anh)
    td = doc_tieu_de("GIA-DINH_tiktok-ads-manager.csv")
    dong = []
    for i, v in enumerate(t9 + t8):
        if v is loi["thieu_link_tt"]:
            continue
        ten_qc = f"SPARK_{v['tid']}_{v['nhom'][:10]}" if i % 6 != 3 else v["tieu_de"]  # vài QC chỉ có tên
        tach = 2 if i % 4 == 0 else 1
        for k in range(tach):
            cp = v["cp_tt"] / tach
            vv = int(v["views"] * 0.6 / tach)
            dong.append({"Campaign name": v["campaign"], "Ad group name": f"AG_{k + 1}", "Ad name": ten_qc,
                         "Ad ID": str(1_810_000_000_000_000 + i * 10 + k), "Currency": "VND", "Cost": f"{cp:.0f}",
                         "Impressions": str(int(vv * 2.4)), "Reach": str(int(vv * 1.6)), "Video views": str(vv),
                         "2-second video views": str(int(vv * 0.55)), "6-second video views": str(int(vv * 0.3)),
                         "Video views at 25%": str(int(vv * 0.25)), "Video views at 50%": str(int(vv * 0.14)),
                         "Average play time per video view": f"{v['xem_tb'] * 0.8:.2f}"})
    dong.append({"Campaign name": "TZ_2026-09_Test", "Ad group name": "AG_X", "Ad name": "SPARK_7999999999999999999_khong_co",
                 "Ad ID": "1819999999999999", "Currency": "VND", "Cost": "1250000", "Video views": "90000"})
    dong.append({"Campaign name": "Total of 60 results", "Cost": f"{sum(v['cp_tt'] for v in t9):.0f}"})
    ghi_csv(thu_muc / "exports" / "tiktok-ads-thang9.csv", td, dong)

    # ---------------- Meta Ads Manager (XLSX, tiêu đề tiếng Việt)
    td = doc_tieu_de("GIA-DINH_meta-ads-manager.csv")
    wbm = openpyxl.Workbook()
    wsm = wbm.active
    wsm.title = "Raw Data Report"
    wsm.append(td)
    for i, v in enumerate(t9):
        if v is loi["fb_share"]:
            continue
        co_id = i % 7 != 4
        hang = {"Bắt đầu báo cáo": "2026-09-01", "Kết thúc báo cáo": "2026-09-30", "Tên chiến dịch": v["campaign"],
                "Tên nhóm quảng cáo": "Nhóm QC 1",
                "Tên quảng cáo": f"Bài viết: \"{v['tieu_de']}\"" if not co_id else f"Boost {v['tieu_de'][:20]}",
                "ID bài viết": f"{PAGE_ID}_{v['post']}" if co_id else "",
                "Số tiền đã chi tiêu (VND)": v["cp_fb"], "Lượt hiển thị": v["plays"] * 2, "Người tiếp cận": v["reach"],
                "Lượt phát video liên tục 3 giây": v["ads_3s"], "Lượt phát video": v["plays"],
                "Lượt phát video ở mức 25%": v["p25"], "Lượt phát video ở mức 50%": v["p50"],
                "Lượt phát video ở mức 75%": int(v["p50"] * 0.6), "ThruPlay": int(v["p50"] * 0.5)}
        wsm.append([hang.get(h, "") for h in td])
    wbm.save(thu_muc / "exports" / "meta-ads-thang9.xlsx")

    # ---------------- Meta Business Suite (CSV, tiêu đề tiếng Việt)
    td = doc_tieu_de("GIA-DINH_meta-business-suite.csv")
    dong = []
    for v in t9 + t8:
        if v is loi["fb_share"]:
            continue
        dong.append({"ID bài viết": f"{PAGE_ID}_{v['post']}", "ID Trang": PAGE_ID, "Tên Trang": "TopZone (giả)",
                     "Tiêu đề": v["tieu_de"], "Mô tả": v["tieu_de"], "Thời lượng (giây)": v["tl"],
                     "Thời gian đăng": v["ngay"].strftime("%m/%d/%Y 10:00"),
                     "Liên kết vĩnh viễn": f"https://www.facebook.com/{PAGE_ID}/posts/{v['post']}",
                     "Loại bài viết": "Thước phim" if v["dong"] % 2 else "Video", "Ngày": "Trọn đời",
                     "Lượt xem": v["fb_3s"] * 2, "Người tiếp cận": v["reach"], "Lượt xem video 3 giây": v["fb_3s"],
                     "Số giây xem trung bình": str(v["xem_tb"]).replace(".", ","),
                     "Lượt chia sẻ": int(v["shares"] * 0.3)})
    ghi_csv(thu_muc / "exports" / "business-suite-noi-dung.csv", td, dong)

    # ---------------- TikTok views nhập tay (đã điền)
    with open(thu_muc / "tiktok-views-template.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Link TikTok", "views", "likes", "shares", "Tiêu đề (tham khảo)"])
        for v in t9:
            if v is loi["thieu_link_tt"] or v is loi["link_rut_gon"]:
                continue
            w.writerow([v["link_tt"], f"{v['views']:,}".replace(",", "."), v["likes"], v["shares"], v["tieu_de"]])

    # ---------------- Lịch tháng sau
    (thu_muc / "thang-sau.yaml").write_text(THANG_SAU_DEMO, encoding="utf-8")
    return {"sheet": p_sheet, "videos": videos, "loi": loi, "giu_cu": giu_cu}


def ghi_dong(ws, r, v, day_du: bool):
    def o(chu, x):
        ws.cell(r, chu_sang_so(chu), x)
    o("A", f"W{(v['ngay'].day - 1) // 7 + 1}")
    o("B", v["ngay"].strftime("%d/%m"))
    o("C", "TikTok + FB")
    o("D", "Sales" if "Promotion" in v["nhom"] else "Brand")
    o("E", "Video 9:16")
    o("F", v["tieu_de"])
    o("G", v["phase"])
    o("H", v["status"])
    o("J", v["link_tt"])
    o("K", v["ngay"])
    ws.cell(r, chu_sang_so("K")).number_format = "dd/mm/yyyy"
    o("L", v["link_fb"])
    o("M", v["nguoi"])
    o("N", v["nhom"])
    o("O", v["tl"])
    for chu, ct in CONG_THUC.items():
        o(chu, ct.format(r=r))
    if not day_du or v["status"] != "Đã air":
        return
    o("P", v["views"]); o("Q", v["likes"]); o("R", v["shares"])
    o("S", v["fb_3s"]); o("T", v["reach"]); o("U", v["xem_tb"]); o("V", "Có")
    o("AB", v["campaign"]); o("AC", v["cp_tt"]); o("AE", v["ads_3s"]); o("AF", v["cp_fb"])
    o("AH", v["plays"]); o("AI", v["p25"]); o("AJ", v["p50"])


def ghi_csv(p: Path, tieu_de: list[str], dong: list[dict]):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu_de)
        for d in dong:
            w.writerow([d.get(h, "") for h in tieu_de])


THANG_SAU_DEMO = """# DỮ LIỆU GIẢ - lịch tháng sau dùng để chạy thử
thang: 2026-10
tong_so_video: 26
giai_doan:
  - ten: "Sau mở bán iPhone 17"
    tu_ngay: 2026-10-01
    den_ngay: 2026-10-12
  - ten: "BAU"
    tu_ngay: 2026-10-13
    den_ngay: 2026-10-31
san_pham_khuyen_mai:
  - "iPhone 17 trả chậm 0%"
  - "Thu cũ đổi mới trợ giá 2 triệu"
su_kien:
  - ten: "Khai trương TopZone Quận 7"
    ngay: 2026-10-18
nhom_thu_nghiem:
  - "Sketch hài - Ai Dè"
  - "Unboxing ASMR"
thang_cap_nhat:
"""


if __name__ == "__main__":
    dich = Path(sys.argv[1]) if len(sys.argv) > 1 else GOC / "samples" / "demo" / "input"
    kq = tao(dich)
    print(f"Đã tạo dữ liệu giả trong {dich}")
