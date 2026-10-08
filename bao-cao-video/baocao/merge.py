"""Ghép số liệu export vào từng video theo ID; tính lại các chỉ số phái sinh."""
from __future__ import annotations

import ast
import operator
from dataclasses import dataclass, field

from .config import Brand
from .exports import FileExport
from .ids import fb_ids, la_link_fb_rut_gon, la_link_tiktok_rut_gon, tiktok_id
from .sheet import DongVideo, LichNoiDung, da_air, la_cua_toi
from .util import chuan_hoa, doc_so, la_trong


@dataclass
class KetQuaGhep:
    thang: str
    muc_tieu: list                         # [DongVideo] video được cập nhật
    cap_nhat: dict                         # dòng -> {khoá cột: giá trị mới}
    nguon: dict                            # dòng -> set(loại file đã ghép)
    khong_ghep_video: list                 # [(DongVideo, [lý do])]
    khong_ghep_dong: list                  # [(tên file, mô tả dòng, chi phí)]
    canh_bao: list = field(default_factory=list)
    ghep_theo_ten: list = field(default_factory=list)
    phu: dict = field(default_factory=dict)  # dòng -> số phụ không ghi vào sheet (vd thời lượng từ export FB)


# ---------------------------------------------------------------- biểu thức

_OP = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def tinh_bieu_thuc(bt: str, gia_tri: dict):
    """Tính 'tiktok_likes + tiktok_shares) / tiktok_views' an toàn. Thiếu số hoặc chia 0 -> None.
    Phép cộng: ô trống tính là 0 nếu còn ít nhất 1 số (vd tổng views khi chưa có YouTube)."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.BinOp) and type(n.op) in _OP:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, (ast.Add, ast.Sub)):
                if a is None and b is None:
                    return None
                return _OP[type(n.op)](a or 0.0, b or 0.0)
            if a is None or b is None:
                return None
            if isinstance(n.op, ast.Div) and b == 0:
                return None
            return _OP[type(n.op)](a, b)
        if isinstance(n, ast.Name):
            return doc_so(gia_tri.get(n.id))
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        raise ValueError(f"Biểu thức không hợp lệ: {bt}")
    return ev(ast.parse(bt, mode="eval"))


def gia_tri_phan_tich(v: DongVideo, brand: Brand, moi: dict | None = None, canh_bao_lech: dict | None = None) -> dict:
    """Giá trị dùng để phân tích: số trong sheet + số mới ghép, rồi tính lại chỉ số phái sinh."""
    gt = dict(v.gia_tri)
    if moi:
        gt.update(moi)
    for k, bt in brand.raw.get("chi_so_tinh", {}).items():
        tinh = tinh_bieu_thuc(bt, gt)
        cu = doc_so(v.gia_tri.get(k))
        if tinh is None:
            continue  # không đủ số -> giữ giá trị sẵn có trong sheet
        if canh_bao_lech is not None and cu is not None and not moi and v.cong_thuc.get(k):
            if abs(tinh - cu) > max(1e-9, 0.02 * abs(cu)):
                canh_bao_lech.setdefault(k, []).append(v.dong)
        gt[k] = tinh
    return gt


# ---------------------------------------------------------------- ghép

def _chi_muc(lich: LichNoiDung) -> dict[str, list]:
    idx: dict[str, list] = {}
    for khoi in lich.khoi:
        for v in khoi.videos:
            keys = set()
            t = tiktok_id(v.get("link_tiktok"))
            if t:
                keys.add(t)
            keys |= fb_ids(v.get("link_fb"))
            for k in keys:
                idx.setdefault(k, []).append(v)
    return idx


def chon_thang_cap_nhat(lich: LichNoiDung, brand: Brand, chi_dinh: str | None) -> str:
    if chi_dinh:
        return chi_dinh
    co_video = [k.thang for k in lich.khoi if any(la_cua_toi(v, brand) and da_air(v, brand) for v in k.videos)]
    return max(co_video) if co_video else max(k.thang for k in lich.khoi)


def ghep(lich: LichNoiDung, brand: Brand, files: list[FileExport], thang: str) -> KetQuaGhep:
    mappings = brand.mappings["loai_file"]
    khoi = lich.khoi_thang(thang)
    tat_ca = brand.raw.get("cap_nhat_tat_ca_nguoi_lam", False)
    muc_tieu = [v for v in (khoi.videos if khoi else [])
                if da_air(v, brand) and (tat_ca or la_cua_toi(v, brand))]
    dong_muc_tieu = {v.dong: v for v in muc_tieu}
    idx = _chi_muc(lich)
    kq = KetQuaGhep(thang, muc_tieu, {}, {}, [], [])

    co_loai = {}
    for f in files:
        if f.loai:
            co_loai.setdefault(f.loai, []).append(f)
    for loai, ds in co_loai.items():
        if len(ds) > 1 and not mappings[loai].get("tich_luy"):
            kq.canh_bao.append(
                f"Có {len(ds)} file {mappings[loai]['ten']} ({', '.join(f.ten for f in ds)}): số liệu sẽ được CỘNG lại. "
                f"Hãy chắc chắn các file không trùng khoảng ngày (dòng trùng y hệt đã tự bỏ).")

    # (dòng video, loại) -> danh sách dòng export đã khớp
    khop: dict[tuple[int, str], list] = {}
    tho_da_thay: dict[str, set] = {}
    for f in sorted([f for f in files if f.loai], key=lambda f: f.duong_dan.stat().st_mtime):
        cfg = mappings[f.loai]
        la_ads = not cfg.get("tich_luy")
        for d in f.dong:
            if la_ads:
                if d["tho"] in tho_da_thay.setdefault(f.loai, set()):
                    continue
                tho_da_thay[f.loai].add(d["tho"])
            co_so = any(v is not None for t, v in d["truong"].items() if cfg["truong"][t].get("kieu") in ("so", "dem"))
            if not co_so:
                continue
            token = set(d["token"])
            if f.loai == "tiktok_organic":
                t = tiktok_id(d["truong"].get("link"))
                token = {t} if t else set()
            videos = {id(v): v for tok in token for v in idx.get(tok, [])}
            cach = "id"
            if not videos and la_ads:
                ten = chuan_hoa(d["truong"].get("ten_quang_cao"))
                if len(ten) >= 8:
                    ung_vien = [v for v in muc_tieu if chuan_hoa(v.get("chu_de")) and (
                        chuan_hoa(v.get("chu_de")) == ten or
                        (len(ten) >= 15 and (ten in chuan_hoa(v.get("chu_de")) or chuan_hoa(v.get("chu_de")) in ten)))]
                    if len(ung_vien) == 1:
                        videos = {id(ung_vien[0]): ung_vien[0]}
                        cach = "ten"
            if len(videos) > 1:
                kq.canh_bao.append(f"{f.ten} dòng {d['so_dong']}: khớp nhiều video cùng lúc (dòng sheet "
                                   f"{', '.join(str(v.dong) for v in videos.values())}) - bỏ qua dòng này.")
                continue
            if not videos:
                if f.loai == "tiktok_organic" and not token:
                    kq.khong_ghep_dong.append((f.ten, f"dòng {d['so_dong']}: link '{d['truong'].get('link') or ''}' không có ID video", None))
                elif token or la_ads:
                    mo_ta = d["truong"].get("ten_quang_cao") or d["truong"].get("tieu_de") or d["truong"].get("lien_ket") or d["truong"].get("link") or ""
                    kq.khong_ghep_dong.append((f.ten, f"dòng {d['so_dong']}: {mo_ta}", d["truong"].get("chi_phi")))
                continue
            v = next(iter(videos.values()))
            if v.dong not in dong_muc_tieu:
                continue  # video tháng khác / người khác: bỏ qua, không báo lỗi
            if cach == "ten":
                kq.ghep_theo_ten.append((f.ten, d["truong"].get("ten_quang_cao"), v))
            khop.setdefault((v.dong, f.loai), []).append((f, d))

    # Gộp số theo từng video
    cot_chu_trong = set(brand.raw.get("cot_chu_chi_dien_khi_trong", []))
    for (dong, loai), ds in khop.items():
        cfg = mappings[loai]
        v = dong_muc_tieu[dong]
        if cfg.get("tich_luy"):  # số trọn đời: chỉ lấy file mới nhất có video này
            moi_nhat = max(f.duong_dan.stat().st_mtime for f, _ in ds)
            ds = [(f, d) for f, d in ds if f.duong_dan.stat().st_mtime == moi_nhat]
        cn = kq.cap_nhat.setdefault(dong, {})
        kq.nguon.setdefault(dong, set()).add(loai)
        for t, tcfg in cfg["truong"].items():
            dich = tcfg.get("ghi")
            vals = [d["truong"].get(t) for _, d in ds if d["truong"].get(t) is not None]
            if not vals:
                continue
            if not dich:
                if t == "thoi_luong":
                    kq.phu.setdefault(dong, {})["thoi_luong"] = max(vals)
                continue
            if tcfg.get("kieu") in ("so", "dem"):
                gia_tri = max(vals) if tcfg.get("gop") == "lon_nhat" else sum(vals)
                gia_tri = round(gia_tri, 4)
                if float(gia_tri).is_integer():
                    gia_tri = int(gia_tri)
            else:
                gia_tri = ", ".join(dict.fromkeys(str(x) for x in vals))
            if dich in cot_chu_trong and not la_trong(v.gia_tri.get(dich)):
                continue
            cn[dich] = gia_tri
        if loai == "meta_ads" and "fb_chay_ads" in brand.cot and la_trong(v.gia_tri.get("fb_chay_ads")):
            cn["fb_chay_ads"] = _gia_tri_fb_chay_ads(kq.muc_tieu, brand)

    # Tính lại chỉ số phái sinh cho dòng có số mới (để điền vào cột nhập tay nếu cột đó không có công thức)
    for dong, cn in kq.cap_nhat.items():
        v = dong_muc_tieu[dong]
        gt = gia_tri_phan_tich(v, brand, cn)
        for k in brand.raw.get("chi_so_tinh", {}):
            if gt.get(k) is not None and gt.get(k) != v.gia_tri.get(k):
                cn.setdefault(k, round(gt[k], 6) if isinstance(gt[k], float) else gt[k])

    _ly_do_khong_ghep(kq, files, brand)
    return kq


def _gia_tri_fb_chay_ads(videos, brand):
    for v in videos:
        x = v.gia_tri.get("fb_chay_ads")
        if isinstance(x, bool):
            return True  # cột dạng ô tích (checkbox)
    return brand.raw.get("gia_tri_fb_chay_ads", "Có")


def _ly_do_khong_ghep(kq: KetQuaGhep, files: list[FileExport], brand: Brand) -> None:
    co = {f.loai for f in files if f.loai}
    for v in kq.muc_tieu:
        ly_do = []
        nguon = kq.nguon.get(v.dong, set())
        lt = v.get("link_tiktok")
        if not lt:
            ly_do.append("Thiếu link TikTok (cột J)")
        elif la_link_tiktok_rut_gon(lt):
            ly_do.append("Link TikTok dạng rút gọn (vt.tiktok.com) - mở link rồi copy link đầy đủ có /video/...")
        elif not tiktok_id(lt):
            ly_do.append("Link TikTok không có ID video (dãy số sau /video/)")
        else:
            if "tiktok_organic" in co and "tiktok_organic" not in nguon:
                ly_do.append(f"Chưa có TikTok views cho ID {tiktok_id(lt)} (file nhập tay/export)")
            if "tiktok_ads" in co and "tiktok_ads" not in nguon:
                ly_do.append(f"Không thấy ID {tiktok_id(lt)} trong export TikTok Ads")
        lf = v.get("link_fb")
        if not lf:
            ly_do.append("Thiếu link FB (cột L)")
        elif la_link_fb_rut_gon(lf) and not fb_ids(lf):
            ly_do.append("Link FB dạng chia sẻ (facebook.com/share/...) - mở bài, bấm vào giờ đăng rồi copy link đầy đủ")
        elif not fb_ids(lf):
            ly_do.append("Link FB không có ID bài viết")
        else:
            if "meta_business_suite" in co and "meta_business_suite" not in nguon:
                ly_do.append("Không thấy bài trong export Business Suite")
            if "meta_ads" in co and "meta_ads" not in nguon:
                ly_do.append("Không thấy bài trong export Meta Ads")
        if ly_do:
            kq.khong_ghep_video.append((v, ly_do))
