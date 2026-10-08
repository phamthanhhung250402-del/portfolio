"""Chấm điểm nhóm nội dung, chuẩn so sánh theo giai đoạn, thời lượng, xu hướng, mix tháng sau."""
from __future__ import annotations

import bisect
import calendar
import datetime as dt
import math
from dataclasses import dataclass, field

from .config import Brand
from .merge import KetQuaGhep, gia_tri_phan_tich
from .mix import UngVien, phan_bo
from .sheet import LichNoiDung, da_air, la_cua_toi
from .util import (doc_ma_thang, doc_ngay, doc_so, doc_thoi_luong, fmt_gon, fmt_giay, fmt_pt, fmt_tien,
                   median, ten_thang, thang_ke)


# ====================================================================== dữ liệu

@dataclass
class Video:
    dong: int
    thang: str
    chu_de: str
    nhom: str
    phase: str
    loai_gd: str
    thoi_luong: float | None
    link_tiktok: str | None
    link_fb: str | None
    m: dict                                 # khoá chỉ số -> số
    diem: float | None = None               # điểm tổng hợp so với toàn bộ lịch sử
    moi_cap_nhat: bool = False


def chi_so_cau_hinh(brand: Brand) -> dict:
    """khoá -> {'nhom': ..., 'ten': ..., 'thap_tot': bool}"""
    ds = {}
    for nk, g in brand.weights["nhom_chi_so"].items():
        for k, c in g.get("chi_so", {}).items():
            ds[k] = {"nhom": nk, "ten": c.get("ten", k), "thap_tot": c.get("tot_khi", "cao") == "thap"}
    return ds


def xay_dung_video(lich: LichNoiDung, brand: Brand, kq: KetQuaGhep, canh_bao: list) -> list[Video]:
    lech: dict = {}
    ds = []
    khong_ro_gd = 0
    so_cot = [k for k in brand.cot if k not in ("tuan", "thoi_gian", "kenh", "pillar", "loai_noi_dung", "chu_de",
                                                  "phase", "status", "ghi_chu", "link_tiktok", "ngay_dang",
                                                  "link_fb", "nguoi_lam", "nhom_noi_dung", "link_youtube",
                                                  "campaign_tiktok", "fb_chay_ads")]
    mac_dinh_gd = brand.raw.get("giai_doan_mac_dinh", "bau")
    for khoi in lich.khoi:
        for v in khoi.videos:
            if not (la_cua_toi(v, brand) and da_air(v, brand)):
                continue
            moi = kq.cap_nhat.get(v.dong) if kq.thang == v.thang else None
            gt = gia_tri_phan_tich(v, brand, moi, lech)
            m = {k: doc_so(gt.get(k)) for k in so_cot}
            tl = doc_thoi_luong(v.gia_tri.get("thoi_luong"))
            if tl is None and kq.thang == v.thang:
                tl = kq.phu.get(v.dong, {}).get("thoi_luong")
            m["thoi_luong"] = tl
            phase = v.get("phase", "") or ""
            loai = brand.loai_giai_doan(phase)
            if loai is None:
                khong_ro_gd += 1
                loai = mac_dinh_gd
            nhom = v.get("nhom_noi_dung")
            ds.append(Video(v.dong, v.thang, str(v.get("chu_de", "") or "(không tiêu đề)"),
                            brand.ten_nhom_chuan(nhom) if nhom else "Khác",
                            str(phase), loai, tl, v.get("link_tiktok"), v.get("link_fb"), m,
                            moi_cap_nhat=bool(moi)))
    for k, dongs in lech.items():
        canh_bao.append(
            f"Cột '{brand.cot[k][1]}' ({len(dongs)} dòng, vd dòng {dongs[0]}): công thức trong sheet cho kết quả khác "
            f"cách tool tính ('{brand.raw['chi_so_tinh'][k]}'). Nếu công thức thật khác, sửa mục chi_so_tinh trong brand.yaml.")
    if khong_ro_gd:
        canh_bao.append(f"{khong_ro_gd} video có cột Phase trống/không nhận ra - tạm tính là giai đoạn "
                        f"'{brand.ten_giai_doan(mac_dinh_gd)}'. Thêm từ khoá vào brand.yaml nếu cần.")
    ten_cfg = {g["ten"] for g in brand.nhom_noi_dung}
    la = sorted({v.nhom for v in ds if v.nhom not in ten_cfg})
    if la:
        canh_bao.append(f"Nhóm nội dung chưa có trong brand.yaml: {', '.join(la)} - vẫn được phân tích như nhóm riêng.")
    return ds


# ====================================================================== điểm

class Chuan:
    """Tập video làm chuẩn so sánh: tính thứ hạng phần trăm cho từng chỉ số."""

    def __init__(self, videos: list[Video], cs: dict, weights: dict, mo_ta: str = ""):
        self.videos = videos
        self.cs = cs
        self.weights = weights
        self.mo_ta = mo_ta
        self.mang = {k: sorted(v.m[k] for v in videos if v.m.get(k) is not None) for k in cs}

    def pt(self, k: str, x):
        """Thứ hạng phần trăm 0-100 (100 = tốt nhất), có xét chiều tốt."""
        a = self.mang.get(k) or []
        if x is None or not a:
            return None
        if len(a) == 1:
            return 50.0
        nho = bisect.bisect_left(a, x)
        bang = bisect.bisect_right(a, x) - nho
        p = (nho + 0.5 * bang) / len(a) * 100
        return 100 - p if self.cs[k]["thap_tot"] else p

    def _gop(self, pt_chi_so: dict, do_phu_toi_thieu: float = 0.0):
        # độ phủ: tỷ lệ trọng số của các chỉ số có số liệu (thiếu quá nhiều -> không chấm)
        phu, tong_ts = 0.0, 0.0
        for g in self.weights["nhom_chi_so"].values():
            cs = list(g.get("chi_so", {}))
            for k in cs:
                tong_ts += float(g.get("trong_so", 0)) / len(cs)
                if pt_chi_so.get(k) is not None:
                    phu += float(g.get("trong_so", 0)) / len(cs)
        if tong_ts and phu / tong_ts < do_phu_toi_thieu:
            return None
        tong, ts = 0.0, 0.0
        for nk, g in self.weights["nhom_chi_so"].items():
            vals = [pt_chi_so[k] for k in g.get("chi_so", {}) if pt_chi_so.get(k) is not None]
            if vals:
                w = float(g.get("trong_so", 0))
                tong += w * sum(vals) / len(vals)
                ts += w
        return tong / ts if ts else None

    def diem_video(self, v: Video):
        """Video thiếu quá 40% số liệu (theo trọng số) thì không chấm điểm."""
        return self._gop({k: self.pt(k, v.m.get(k)) for k in self.cs}, 0.6)

    def diem_nhom(self, vids: list[Video]):
        """Median thứ hạng phần trăm của các video trong nhóm, cộng theo trọng số."""
        pt_k = {}
        for k in self.cs:
            pt_k[k] = median([self.pt(k, v.m.get(k)) for v in vids])
        return self._gop(pt_k), pt_k


def chon_chuan(loai: str, videos: list[Video], brand: Brand, cs: dict) -> Chuan:
    can = int(brand.weights.get("so_video_chuan_giai_doan", 15))
    toi_thieu = int(brand.weights.get("so_video_toi_thieu", 5))
    thu_tu = [loai] + [x for x in brand.giai_doan.get(loai, {}).get("tuong_tu", []) if x != loai]
    chon, mo_ta = [], []
    for l in thu_tu:
        vs = [v for v in videos if v.loai_gd == l]
        if vs:
            chon += vs
            mo_ta.append(f"{len(vs)} video {brand.ten_giai_doan(l)}")
        if len(chon) >= can:
            break
    if len(chon) < toi_thieu:
        return Chuan(videos, cs, brand.weights,
                     f"toàn bộ lịch sử ({len(videos)} video) - giai đoạn {brand.ten_giai_doan(loai)} và tương tự chưa đủ dữ liệu")
    return Chuan(chon, cs, brand.weights, " + ".join(mo_ta))


# ====================================================================== tháng sau

def doc_thang_sau(raw: dict, brand: Brand, thang_moi_nhat: str, n_mac_dinh: int) -> dict:
    ghi_chu = []
    thang = doc_ma_thang(raw.get("thang")) or thang_ke(thang_moi_nhat)
    if not raw.get("thang"):
        ghi_chu.append(f"Chưa điền 'thang' - dùng {ten_thang(thang)}.")
    tong = raw.get("tong_so_video")
    tong = int(doc_so(tong)) if doc_so(tong) else None
    if tong is None:
        tong = n_mac_dinh
        ghi_chu.append(f"Chưa điền 'tong_so_video' - dùng {tong} (bằng tháng gần nhất).")
    nam, th = map(int, thang.split("-"))
    ngay_dau, ngay_cuoi = dt.date(nam, th, 1), dt.date(nam, th, calendar.monthrange(nam, th)[1])
    gds = []
    for g in raw.get("giai_doan") or []:
        if not isinstance(g, dict) or not g.get("ten"):
            continue
        loai = g.get("loai") or brand.loai_giai_doan(g["ten"])
        if loai not in brand.giai_doan:
            ghi_chu.append(f"Giai đoạn '{g['ten']}': không nhận ra loại - tính là {brand.ten_giai_doan(brand.raw.get('giai_doan_mac_dinh', 'bau'))}.")
            loai = brand.raw.get("giai_doan_mac_dinh", "bau")
        tu, den = doc_ngay(g.get("tu_ngay")), doc_ngay(g.get("den_ngay"))
        gds.append({"ten": g["ten"], "loai": loai, "tu": tu, "den": den, "so_video": doc_so(g.get("so_video"))})
    if not gds:
        gds = [{"ten": "BAU (cả tháng)", "loai": brand.raw.get("giai_doan_mac_dinh", "bau"), "tu": None, "den": None, "so_video": None}]
    # số ngày mỗi giai đoạn
    co_ngay = all(g["tu"] and g["den"] for g in gds)
    for g in gds:
        if co_ngay:
            g["so_ngay"] = max(1, (g["den"] - g["tu"]).days + 1)
        elif len(gds) == 1:
            g["tu"], g["den"], g["so_ngay"] = ngay_dau, ngay_cuoi, (ngay_cuoi - ngay_dau).days + 1
        else:
            g["so_ngay"] = 1
    if not co_ngay and len(gds) > 1:
        ghi_chu.append("Các giai đoạn thiếu ngày - chia đều trọng số giữa các giai đoạn.")
    if all(g["so_video"] for g in gds):
        tong_w = sum(g["so_video"] for g in gds)
        for g in gds:
            g["ty_le"] = g["so_video"] / tong_w
    else:
        tong_w = sum(g["so_ngay"] for g in gds)
        for g in gds:
            g["ty_le"] = g["so_ngay"] / tong_w
    su_kien = []
    for s in raw.get("su_kien") or []:
        if isinstance(s, dict) and s.get("ten"):
            su_kien.append({"ten": str(s["ten"]), "ngay": doc_ngay(s.get("ngay"))})
        elif isinstance(s, str) and s.strip():
            su_kien.append({"ten": s.strip(), "ngay": None})
    return {
        "thang": thang, "tong": tong, "giai_doan": gds, "ghi_chu": ghi_chu,
        "khuyen_mai": [str(x) for x in (raw.get("san_pham_khuyen_mai") or []) if x],
        "su_kien": su_kien,
        "thu_nghiem": [brand.ten_nhom_chuan(str(x)) for x in (raw.get("nhom_thu_nghiem") or []) if x],
    }


# ====================================================================== định dạng

def fmt_chi_so(k: str, x) -> str:
    if x is None:
        return "-"
    if k.startswith("cpv") or k.startswith("chi_phi"):
        return fmt_tien(x)
    if k in ("fb_xem_tb", "thoi_luong"):
        return fmt_giay(x)
    if "views" in k or k.startswith("fb_xem_3s") or k.startswith("fb_reach") or "luot" in k:
        return fmt_gon(x)
    return fmt_pt(x)


def ten_ngan(k: str, cs: dict) -> str:
    return {"cpv_tiktok": "CPV TikTok", "cpv_fb_3s": "CPV FB 3s", "fb_xem_tb": "xem TB",
            "ty_le_xem_50": "xem 50%", "fb_hook_rate": "hook rate", "tiktok_er": "ER",
            "tiktok_views": "median views"}.get(k, cs.get(k, {}).get("ten", k))


# ====================================================================== phân tích chính

def khoang_thoi_luong(x, moc) -> str | None:
    if x is None:
        return None
    nhan = nhan_khoang(moc)
    for i, m in enumerate(moc):
        if x <= m:
            return nhan[i]
    return nhan[-1]


def nhan_khoang(moc) -> list[str]:
    ds = [f"≤{moc[0]}s"]
    for a, b in zip(moc, moc[1:]):
        ds.append(f"{a + 1}-{b}s")
    ds.append(f">{moc[-1]}s")
    return ds


def phan_tich(lich: LichNoiDung, brand: Brand, kq: KetQuaGhep, raw_thang_sau: dict, canh_bao: list) -> dict:
    cs = chi_so_cau_hinh(brand)
    W = brand.weights
    toi_thieu = int(W.get("so_video_toi_thieu", 5))
    videos = xay_dung_video(lich, brand, kq, canh_bao)
    if not videos:
        raise ValueError("Không có video nào của bạn ở trạng thái 'Đã air' trong tab 03 - kiểm tra brand.yaml (nguoi_lam, status_da_air).")
    thang_ds = sorted({v.thang for v in videos})
    thang_moi = kq.thang if kq.thang in thang_ds else thang_ds[-1]
    thang_truoc = max([t for t in thang_ds if t < thang_moi], default=None)

    # điểm từng video so với toàn bộ lịch sử
    chuan_all = Chuan(videos, cs, W, f"toàn bộ lịch sử ({len(videos)} video)")
    for v in videos:
        v.diem = chuan_all.diem_video(v)

    v_moi = [v for v in videos if v.thang == thang_moi]
    v_truoc = [v for v in videos if v.thang == thang_truoc] if thang_truoc else []

    # ---------------- tháng sau
    ts = doc_thang_sau(raw_thang_sau or {}, brand, thang_moi, len(v_moi))
    cfg_nhom = {g["ten"]: g for g in brand.nhom_noi_dung}
    ten_nhom = list(dict.fromkeys([g["ten"] for g in brand.nhom_noi_dung] + sorted({v.nhom for v in videos})
                                  + ts["thu_nghiem"]))
    so_thang_chay = int(W.get("phan_bo", {}).get("so_thang_dang_chay", 2))
    thang_gan = [t for t in thang_ds if t <= thang_moi][-so_thang_chay:]

    chuan_gd = {}
    for g in ts["giai_doan"]:
        if g["loai"] not in chuan_gd:
            chuan_gd[g["loai"]] = chon_chuan(g["loai"], videos, brand, cs)

    moc = W.get("thoi_luong", {}).get("moc", [20, 40, 60])
    nhan_tl = nhan_khoang(moc)
    min_khoang = int(W.get("thoi_luong", {}).get("so_video_toi_thieu_moi_khoang", 2))

    nhom_kq = []
    for ten in ten_nhom:
        cfg = cfg_nhom.get(ten, {"ten": ten, "giai_doan": "tat_ca", "de_xuat": True})
        vs = [v for v in videos if v.nhom == ten]
        phu_hop = 0.0
        diem_gd, chi_tiet_gd = {}, []
        for g in ts["giai_doan"]:
            ok = cfg["giai_doan"] == "tat_ca" or g["loai"] in cfg["giai_doan"]
            if ten == brand.raw.get("nhom_su_kien") and ts["su_kien"]:
                ok = True
            if not ok:
                continue
            phu_hop += g["ty_le"]
            chuan = chuan_gd[g["loai"]]
            vs_c = [v for v in chuan.videos if v.nhom == ten]
            if vs_c:
                d, _ = chuan.diem_nhom(vs_c)
                diem_gd[g["ten"]] = (d, len(vs_c), False)
            elif vs:
                d, _ = chuan_all.diem_nhom(vs)
                diem_gd[g["ten"]] = (d, len(vs), True)
        # điểm trộn theo tỷ lệ ngày của giai đoạn
        tong_w, tong_d = 0.0, 0.0
        for g in ts["giai_doan"]:
            if g["ten"] in diem_gd and diem_gd[g["ten"]][0] is not None:
                tong_w += g["ty_le"]
                tong_d += g["ty_le"] * diem_gd[g["ten"]][0]
        diem = tong_d / tong_w if tong_w else None
        # chuẩn chính để trích số liệu lý do: giai đoạn chiếm nhiều ngày nhất
        gd_chinh = max(ts["giai_doan"], key=lambda g: g["ty_le"])
        chuan_chinh = chuan_gd[gd_chinh["loai"]]
        vs_chinh = [v for v in chuan_chinh.videos if v.nhom == ten] or vs
        _, pt_k = (chuan_chinh if [v for v in chuan_chinh.videos if v.nhom == ten] else chuan_all).diem_nhom(vs_chinh) if vs else (None, {})
        trung_vi = {k: median([v.m.get(k) for v in vs_chinh]) for k in list(cs) + ["thoi_luong", "chi_phi_tiktok", "chi_phi_fb"]}

        # thời lượng
        tl = {}
        for nh in nhan_tl:
            vv = [v for v in vs if khoang_thoi_luong(v.thoi_luong, moc) == nh]
            tl[nh] = {"n": len(vv), "diem": median([v.diem for v in vv]),
                      "cpv": median([v.m.get("cpv_tiktok") for v in vv]),
                      "xem_tb": median([v.m.get("fb_xem_tb") for v in vv])}
        du = [(nh, x) for nh, x in tl.items() if x["n"] >= min_khoang and x["diem"] is not None]
        if du:
            tot = max(du, key=lambda t: t[1]["diem"])
            muc_tieu_tl = tot[0]
            ly_do_tl = f"{tot[0]}: điểm {tot[1]['diem']:.0f} ({tot[1]['n']} video)"
        elif any(x["n"] for x in tl.values()):
            tot = max(tl.items(), key=lambda t: t[1]["n"])
            muc_tieu_tl = tot[0]
            ly_do_tl = f"{tot[0]}: nhiều video nhất, chưa đủ dữ liệu so sánh"
        else:
            muc_tieu_tl, ly_do_tl = None, "chưa có dữ liệu"

        d_moi = median([v.diem for v in vs if v.thang == thang_moi])
        d_truoc = median([v.diem for v in vs if v.thang == thang_truoc]) if thang_truoc else None
        n_moi = sum(1 for v in vs if v.thang == thang_moi)
        n_truoc = sum(1 for v in vs if v.thang == thang_truoc)
        nhom_kq.append({
            "ten": ten, "cfg": cfg, "videos": vs, "n": len(vs), "n_moi": n_moi, "n_truoc": n_truoc,
            "xep_hang": len(vs) >= toi_thieu, "dang_chay": any(v.thang in thang_gan for v in vs),
            "phu_hop": phu_hop, "de_xuat": cfg.get("de_xuat", True), "diem": diem, "diem_gd": diem_gd,
            "pt": pt_k, "trung_vi": trung_vi, "thoi_luong": tl, "muc_tieu_tl": muc_tieu_tl, "ly_do_tl": ly_do_tl,
            "diem_moi": d_moi, "diem_truoc": d_truoc,
            "xu_huong": (d_moi - d_truoc) if (d_moi is not None and d_truoc is not None and n_moi >= 2 and n_truoc >= 2) else None,
            "thu_nghiem_dang_ky": ten in ts["thu_nghiem"],
        })

    # điểm so với toàn bộ lịch sử (cho nhóm không thuộc giai đoạn tháng sau)
    for g in nhom_kq:
        g["diem_ls"] = chuan_all.diem_nhom(g["videos"])[0] if g["videos"] else None
        if g["phu_hop"] <= 0 and g["diem"] is None:
            g["ngoai_giai_doan"] = True
        else:
            g["ngoai_giai_doan"] = False

    # hạng trong các nhóm đủ dữ liệu và thuộc giai đoạn tháng sau
    xh = sorted([g for g in nhom_kq if g["xep_hang"] and g["diem"] is not None], key=lambda g: -g["diem"])
    for i, g in enumerate(xh, start=1):
        g["hang"] = i
    for g in nhom_kq:
        g.setdefault("hang", None)

    # nhóm không có số liệu chỉ số nào nhưng đủ video -> coi như chưa xếp hạng
    for g in nhom_kq:
        if g["xep_hang"] and g["diem"] is None and not g["ngoai_giai_doan"]:
            g["xep_hang"] = False

    # ---------------- mix
    pb = W.get("phan_bo", {})
    so_su_kien = len(ts["su_kien"])
    ung_vien = []
    for g in nhom_kq:
        if not g["de_xuat"]:
            continue
        if g["phu_hop"] <= 0 and not g["thu_nghiem_dang_ky"]:
            continue
        ung_vien.append(UngVien(
            ten=g["ten"], diem=g["diem"], xep_hang=g["xep_hang"], dang_chay=g["dang_chay"],
            uu_tien_thu_nghiem=g["thu_nghiem_dang_ky"],
            toi_thieu_them=so_su_kien if g["ten"] == brand.raw.get("nhom_su_kien") else 0,
            so_video_lich_su=g["n"]))
    mix = phan_bo(ts["tong"], ung_vien, float(pb.get("ty_le_thu_nghiem", 0.2)), int(pb.get("toi_thieu_moi_nhom", 2)),
                  float(pb.get("toi_da_ty_trong", 0.35)), float(pb.get("do_doc", 2)))
    canh_bao.extend(mix.canh_bao)

    hang_tong = len(xh)
    dong_mix = []
    for u in ung_vien:
        g = next(x for x in nhom_kq if x["ten"] == u.ten)
        so = mix.so_video.get(u.ten, 0)
        dong_mix.append({
            "ten": u.ten, "so_video": so, "ty_trong": so / ts["tong"] if ts["tong"] else 0,
            "hieu_qua": mix.hieu_qua.get(u.ten, 0), "thu_nghiem": mix.thu_nghiem.get(u.ten, 0),
            "thoi_luong": g["muc_tieu_tl"] or _tl_toan_kenh(videos, moc, min_khoang),
            "ly_do": ly_do(g, so, mix, cs, xh, hang_tong, ts, brand),
            "do_tin_cay": ("Thử nghiệm - chưa đủ dữ liệu" if not g["xep_hang"] else
                           ("Cao" if g["n"] >= 3 * toi_thieu else "Trung bình")),
            "nhom": g,
        })
    dong_mix.sort(key=lambda d: (-d["so_video"], -(d["nhom"]["diem"] or -1)))

    # phân theo giai đoạn
    theo_gd = phan_theo_giai_doan(dong_mix, ts)

    # ---------------- tổng quan tháng
    tq = {"moi": tong_quan(v_moi), "truoc": tong_quan(v_truoc) if v_truoc else None}
    xep = sorted([v for v in v_moi if v.diem is not None], key=lambda v: -v.diem)
    k = min(10, len(xep) // 2) if len(xep) < 20 else 10
    top, bottom = xep[:k], list(reversed(xep[-k:])) if k else []

    # thời lượng toàn kênh
    tl_kenh = []
    for nh in nhan_tl:
        vv = [v for v in videos if khoang_thoi_luong(v.thoi_luong, moc) == nh]
        tl_kenh.append({"nhan": nh, "n": len(vv), "diem": median([v.diem for v in vv]),
                        "cpv": median([v.m.get("cpv_tiktok") for v in vv]),
                        "xem_tb": median([v.m.get("fb_xem_tb") for v in vv])})
    thieu_tl = sum(1 for v in videos if v.thoi_luong is None)
    if thieu_tl:
        canh_bao.append(f"{thieu_tl} video chưa có thời lượng (cột O) - không được tính trong phân tích thời lượng.")

    return {
        "videos": videos, "v_moi": v_moi, "thang_moi": thang_moi, "thang_truoc": thang_truoc,
        "thang_ds": thang_ds, "cs": cs, "nhom": nhom_kq, "xep_hang": xh, "mix": dong_mix, "mix_kq": mix,
        "theo_gd": theo_gd, "thang_sau": ts, "chuan_gd": chuan_gd, "chuan_all": chuan_all,
        "tong_quan": tq, "top": top, "bottom": bottom, "tl_kenh": tl_kenh, "nhan_tl": nhan_tl,
        "nguong_xu_huong": float(W.get("nguong_xu_huong", 5)), "toi_thieu": toi_thieu,
    }


def _tl_toan_kenh(videos, moc, min_khoang):
    tot, d = None, -1
    for nh in nhan_khoang(moc):
        vv = [v.diem for v in videos if khoang_thoi_luong(v.thoi_luong, moc) == nh and v.diem is not None]
        if len(vv) >= min_khoang and median(vv) > d:
            tot, d = nh, median(vv)
    return f"{tot} (theo toàn kênh)" if tot else "-"


def tong_quan(vs: list[Video]) -> dict:
    def tong(k):
        x = [v.m.get(k) for v in vs if v.m.get(k) is not None]
        return sum(x) if x else None
    cp_tt, cp_fb = tong("chi_phi_tiktok"), tong("chi_phi_fb")
    return {
        "n": len(vs),
        "tiktok_views": tong("tiktok_views"), "fb_xem_3s": tong("fb_xem_3s"),
        "chi_phi": (cp_tt or 0) + (cp_fb or 0) if (cp_tt is not None or cp_fb is not None) else None,
        "cpv_tiktok": median([v.m.get("cpv_tiktok") for v in vs]),
        "cpv_fb_3s": median([v.m.get("cpv_fb_3s") for v in vs]),
        "fb_xem_tb": median([v.m.get("fb_xem_tb") for v in vs]),
        "ty_le_xem_50": median([v.m.get("ty_le_xem_50") for v in vs]),
        "tiktok_er": median([v.m.get("tiktok_er") for v in vs]),
        "diem": median([v.diem for v in vs]),
    }


def ly_do(g, so, mix, cs, xh, hang_tong, ts, brand) -> str:
    """Một câu lý do bằng số liệu."""
    tv, pt = g["trung_vi"], g["pt"] or {}

    def mo_ta(k):
        val = tv.get(k)
        if val is None:
            return None
        s = f"{ten_ngan(k, cs)} {fmt_chi_so(k, val)}"
        if g["xep_hang"] and len(xh) >= 2:
            ds = [x["trung_vi"].get(k) for x in xh if x["trung_vi"].get(k) is not None]
            if len(ds) >= 2:
                tot_nhat = min(ds) if cs[k]["thap_tot"] else max(ds)
                te_nhat = max(ds) if cs[k]["thap_tot"] else min(ds)
                if val == tot_nhat:
                    s += " - thấp nhất" if cs[k]["thap_tot"] else " - cao nhất"
                elif val == te_nhat:
                    s += " - cao nhất" if cs[k]["thap_tot"] else " - thấp nhất"
        return s

    manh = sorted([k for k in cs if pt.get(k) is not None and tv.get(k) is not None], key=lambda k: -pt[k])
    phan = [x for x in (mo_ta(k) for k in manh[:2]) if x]
    yeu = mo_ta(manh[-1]) if len(manh) > 2 and pt[manh[-1]] < 40 else None
    cau = []
    if g["xep_hang"]:
        dau = f"Điểm {g['diem']:.0f}/100 (hạng {g['hang']}/{hang_tong})"
        if so == 0:
            cau.append(f"{dau}: {yeu or ', '.join(phan)}; điểm thấp và không có video gần đây")
        elif g["ten"] in mix.giu_toi_thieu:
            cau.append(f"{dau}: {', '.join(phan)}" + (f"; yếu ở {yeu}" if yeu else "") + "; giữ tối thiểu vì đang chạy")
        else:
            cau.append(f"{dau}: {', '.join(phan)}" + (f"; yếu ở {yeu}" if yeu else ""))
        if g["ten"] in mix.cham_tran:
            cau.append(f"chạm trần {int(round(mix.tran / ts['tong'] * 100)) if ts['tong'] else 35}% tổng video")
    else:
        if g["n"]:
            cau.append(f"Mới có {g['n']} video" + (f" ({', '.join(phan)})" if phan else ""))
        else:
            cau.append("Chưa có dữ liệu")
        if g["thu_nghiem_dang_ky"]:
            cau.append("bạn đăng ký thử nghiệm")
        cau.append("slot thử nghiệm" if so else "chưa có slot thử nghiệm tháng này")
    if g["thu_nghiem_dang_ky"] and g["xep_hang"] and mix.thu_nghiem.get(g["ten"]):
        cau.append(f"+{mix.thu_nghiem[g['ten']]} slot thử nghiệm theo đăng ký")
    if g["ten"] == brand.raw.get("nhom_su_kien") and ts["su_kien"]:
        cau.append(f"{len(ts['su_kien'])} sự kiện: " + ", ".join(s["ten"] for s in ts["su_kien"]))
    if g["diem_gd"] and any(x[2] for x in g["diem_gd"].values()):
        cau.append("chưa có video ở giai đoạn tương tự nên so với toàn bộ lịch sử")
    s = "; ".join(cau)
    return s[0].upper() + s[1:] + "."


def phan_theo_giai_doan(dong_mix, ts) -> dict:
    """Chia số video mỗi nhóm cho các giai đoạn nhóm đó phù hợp (theo tỷ lệ ngày)."""
    gds = ts["giai_doan"]
    kq = {d["ten"]: {g["ten"]: 0 for g in gds} for d in dong_mix}
    if len(gds) == 1:
        for d in dong_mix:
            kq[d["ten"]][gds[0]["ten"]] = d["so_video"]
        return kq
    for d in dong_mix:
        cfg = d["nhom"]["cfg"]
        w = {g["ten"]: g["ty_le"] for g in gds
             if cfg["giai_doan"] == "tat_ca" or g["loai"] in cfg["giai_doan"] or d["nhom"]["thu_nghiem_dang_ky"]}
        if not w:
            w = {g["ten"]: g["ty_le"] for g in gds}
        tong_w = sum(w.values())
        thuc = {k: d["so_video"] * x / tong_w for k, x in w.items()}
        nguyen = {k: int(math.floor(x)) for k, x in thuc.items()}
        du = d["so_video"] - sum(nguyen.values())
        for k in sorted(thuc, key=lambda k: -(thuc[k] - nguyen[k]))[:du]:
            nguyen[k] += 1
        kq[d["ten"]].update(nguyen)
    return kq
