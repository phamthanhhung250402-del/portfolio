"""brief-cho-claude.md và de-xuat-mix-thang-sau.tsv"""
from __future__ import annotations

from pathlib import Path

from .analysis import fmt_chi_so, ten_ngan
from .util import fmt_gon, fmt_pt, fmt_so, fmt_tien, fmt_giay, so_tsv, ten_thang

YEU_CAU = ("Dựa trên dữ liệu trên, đề xuất 3 ý tưởng cho mỗi nhóm theo đúng số lượng trong mix, "
           "kèm hook 2 giây đầu và lý do gắn với số liệu. Chỉ đưa idea để tôi chọn, CHƯA viết kịch bản.")


def xuat_mix_tsv(pt: dict, brand, p: Path) -> None:
    dau = brand.raw.get("dau_thap_phan", ",")
    dong = ["\t".join(["Nhóm nội dung", "Số video", "Tỷ trọng", "Thời lượng mục tiêu", "Lý do", "Độ tin cậy"])]
    for d in pt["mix"]:
        dong.append("\t".join([
            d["ten"], str(d["so_video"]), fmt_pt(d["ty_trong"]) if dau == "," else f"{d['ty_trong'] * 100:.1f}%",
            d["thoi_luong"], so_tsv(d["ly_do"]), d["do_tin_cay"]]))
    dong.append("\t".join(["Tổng", str(sum(d["so_video"] for d in pt["mix"])), "100%", "", "", ""]))
    p.write_text("\n".join(dong) + "\n", encoding="utf-8")


def _video_dong(v) -> str:
    phan = [f"\"{v.chu_de}\""]
    if v.thoi_luong:
        phan.append(f"{fmt_so(v.thoi_luong)}s")
    for k, nhan, f in (("tiktok_views", "views TikTok", fmt_gon), ("cpv_tiktok", "CPV TikTok", fmt_tien),
                       ("cpv_fb_3s", "CPV FB 3s", fmt_tien), ("fb_xem_tb", "xem TB", fmt_giay)):
        if v.m.get(k) is not None:
            phan.append(f"{f(v.m[k])} {nhan}" if k == "tiktok_views" else f"{nhan} {f(v.m[k])}")
    if v.diem is not None:
        phan.append(f"điểm {v.diem:.0f}")
    return " - ".join(phan)


def _mui_ten(x, nguong=0.0):
    if x is None:
        return "-"
    return "▲" if x > nguong else ("▼" if x < -nguong else "→")


def xuat_brief(pt: dict, brand, p: Path) -> str:
    ts = pt["thang_sau"]
    cs = pt["cs"]
    L = []
    L.append(f"# Brief nội dung {brand.ten} - đề xuất {ten_thang(ts['thang'])}")
    L.append("")
    L.append("## 1. Bối cảnh")
    L.append(f"- Chuỗi bán lẻ Apple, kênh TikTok + Facebook, video dọc 9:16, toàn bộ video chạy paid ads.")
    L.append(f"- Dữ liệu: {len(pt['videos'])} video của tôi đã air, {ten_thang(pt['thang_ds'][0])} - {ten_thang(pt['thang_moi'])}. "
             f"Tháng gần nhất: {len(pt['v_moi'])} video.")
    w = brand.weights["nhom_chi_so"]
    L.append("- Điểm nhóm (0-100) = trung bình có trọng số của thứ hạng phần trăm (median video trong nhóm): "
             + ", ".join(f"{g['ten']} {g['trong_so']}%" for g in w.values()) + ".")
    L.append(f"- Nhóm dưới {pt['toi_thieu']} video = thử nghiệm, chưa xếp hạng.")
    L.append("")
    L.append("## 2. Số liệu từng nhóm (median)")
    L.append("")
    L.append("| Nhóm | Video | Điểm | Hạng | CPV TikTok | CPV FB 3s | Xem TB | Xem 50% | Hook | ER | Median views | Thời lượng tốt nhất |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for g in sorted(pt["nhom"], key=lambda g: (g["hang"] is None, g["hang"] or 0, -g["n"])):
        if not g["n"]:
            continue
        tv = g["trung_vi"]
        L.append("| " + " | ".join([
            g["ten"], str(g["n"]), f"{(g['diem'] if g['diem'] is not None else g['diem_ls']):.0f}" if (g["diem"] if g["diem"] is not None else g["diem_ls"]) is not None else "-",
            str(g["hang"]) if g["hang"] else ("không thuộc giai đoạn tháng sau" if g["ngoai_giai_doan"] else "thử nghiệm"),
            fmt_tien(tv.get("cpv_tiktok")), fmt_tien(tv.get("cpv_fb_3s")), fmt_giay(tv.get("fb_xem_tb")),
            fmt_pt(tv.get("ty_le_xem_50")), fmt_pt(tv.get("fb_hook_rate")), fmt_pt(tv.get("tiktok_er"), 2),
            fmt_gon(tv.get("tiktok_views")), g["muc_tieu_tl"] or "-"]) + " |")
    L.append("")
    L.append("## 3. Top / bottom 5 video mỗi nhóm")
    for g in pt["nhom"]:
        vs = sorted([v for v in g["videos"] if v.diem is not None], key=lambda v: -v.diem)
        if not vs:
            continue
        L.append("")
        L.append(f"### {g['ten']} ({len(vs)} video)")
        L.append("Top:")
        for v in vs[:5]:
            L.append(f"- {_video_dong(v)}")
        con_lai = vs[5:]
        if con_lai:
            L.append("Bottom:")
            for v in list(reversed(con_lai))[:5]:
                L.append(f"- {_video_dong(v)}")
    L.append("")
    L.append(f"## 4. Thay đổi so với tháng trước ({ten_thang(pt['thang_truoc']) if pt['thang_truoc'] else 'không có'} → {ten_thang(pt['thang_moi'])})")
    tq = pt["tong_quan"]
    if tq["truoc"]:
        for k, ten in (("n", "Số video"), ("tiktok_views", "Tổng TikTok views"), ("cpv_tiktok", "CPV TikTok (median)"),
                       ("cpv_fb_3s", "CPV FB 3s (median)"), ("fb_xem_tb", "FB xem TB (median)"),
                       ("ty_le_xem_50", "Tỷ lệ xem 50% (median)")):
            a, b = tq["truoc"].get(k), tq["moi"].get(k)
            if a is None or b is None:
                continue
            L.append(f"- {ten}: {fmt_chi_so(k, a) if k != 'n' else a} → {fmt_chi_so(k, b) if k != 'n' else b} {_mui_ten(b - a)}")
        ng = pt["nguong_xu_huong"]
        for g in pt["nhom"]:
            if g["xu_huong"] is not None and abs(g["xu_huong"]) >= ng:
                L.append(f"- Nhóm {g['ten']}: điểm {g['diem_truoc']:.0f} → {g['diem_moi']:.0f} {_mui_ten(g['xu_huong'])}")
    else:
        L.append("- Chưa có tháng trước để so sánh.")
    L.append("")
    L.append(f"## 5. Lịch {ten_thang(ts['thang'])}")
    L.append(f"- Tổng số video dự kiến: {ts['tong']}")
    for g in ts["giai_doan"]:
        ngay = f"{g['tu']:%d/%m} - {g['den']:%d/%m}" if g.get("tu") and g.get("den") else "chưa có ngày"
        L.append(f"- Giai đoạn {g['ten']} ({brand.ten_giai_doan(g['loai'])}): {ngay}; chuẩn so sánh: {pt['chuan_gd'][g['loai']].mo_ta}")
    if ts["khuyen_mai"]:
        L.append("- Sản phẩm / khuyến mãi: " + "; ".join(ts["khuyen_mai"]))
    if ts["su_kien"]:
        L.append("- Sự kiện: " + "; ".join(s["ten"] + (f" ({s['ngay']:%d/%m})" if s["ngay"] else "") for s in ts["su_kien"]))
    if ts["thu_nghiem"]:
        L.append("- Nhóm muốn thử nghiệm: " + "; ".join(ts["thu_nghiem"]))
    L.append("")
    L.append("## 6. Mix đề xuất")
    L.append("")
    L.append("| Nhóm nội dung | Số video | Tỷ trọng | Thời lượng mục tiêu | Lý do | Độ tin cậy |")
    L.append("|---|---|---|---|---|---|")
    for d in pt["mix"]:
        if d["so_video"] == 0:
            continue
        L.append(f"| {d['ten']} | {d['so_video']} | {fmt_pt(d['ty_trong'], 0)} | {d['thoi_luong']} | {d['ly_do']} | {d['do_tin_cay']} |")
    if len(ts["giai_doan"]) > 1:
        L.append("")
        L.append("Chia theo giai đoạn: " + "; ".join(
            f"{gd['ten']}: " + ", ".join(f"{t} {pt['theo_gd'][t][gd['ten']]}" for t in pt["theo_gd"] if pt["theo_gd"][t][gd["ten"]])
            for gd in ts["giai_doan"]))
    L.append("")
    L.append("## Yêu cầu")
    L.append(YEU_CAU)
    text = "\n".join(L) + "\n"
    p.write_text(text, encoding="utf-8")
    return text
