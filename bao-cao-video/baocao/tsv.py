"""Xuất TSV theo từng khối cột nhập tay liên tiếp (KHÔNG BAO GIỜ gồm cột công thức)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import Brand, so_sang_chu
from .merge import KetQuaGhep
from .sheet import LichNoiDung
from .util import so_tsv, ten_thang


@dataclass
class KhoiTSV:
    so: int
    cot_dau: int
    cot_cuoi: int
    dong_dau: int
    dong_cuoi: int
    ten_cot: list
    noi_dung: str
    ten_file: str

    @property
    def o_dau(self) -> str:
        return f"{so_sang_chu(self.cot_dau)}{self.dong_dau}"

    @property
    def vung(self) -> str:
        return f"{so_sang_chu(self.cot_dau)}{self.dong_dau}:{so_sang_chu(self.cot_cuoi)}{self.dong_cuoi}"


def phan_loai_cot(lich: LichNoiDung, brand: Brand, dong_dau: int, dong_cuoi: int):
    """Trả về (cột nhập tay, cột công thức, cảnh báo) trong dải cột số liệu."""
    k_dau, k_cuoi = brand.raw.get("dai_cot_so_lieu", ["tiktok_views", "ty_le_xem_50"])
    c_dau, c_cuoi = lich.cot[k_dau], lich.cot[k_cuoi]
    nhap_tay, cong_thuc, canh_bao = [], [], []
    for c in range(c_dau, c_cuoi + 1):
        dong_ct = [r for r in range(dong_dau, dong_cuoi + 1) if lich.la_cong_thuc(r, c)]
        if dong_ct:
            cong_thuc.append(c)
            if len(dong_ct) < (dong_cuoi - dong_dau + 1):
                so_dong_ct = len(dong_ct)
                canh_bao.append(
                    f"Cột {so_sang_chu(c)} vừa có công thức ({so_dong_ct} ô) vừa có ô gõ tay trong dòng "
                    f"{dong_dau}-{dong_cuoi} - tool coi cả cột là công thức và KHÔNG xuất cột này.")
        else:
            nhap_tay.append(c)
    return nhap_tay, cong_thuc, canh_bao


def xuat(lich: LichNoiDung, brand: Brand, kq: KetQuaGhep, thu_muc: Path) -> tuple[list[KhoiTSV], list[str]]:
    thu_muc.mkdir(parents=True, exist_ok=True)
    for f in thu_muc.glob("*"):
        if f.is_file():
            f.unlink()
    khoi_thang = lich.khoi_thang(kq.thang)
    if khoi_thang is None or not kq.cap_nhat:
        (thu_muc / "huong-dan-dan.txt").write_text(
            f"Không có số liệu mới cho {ten_thang(kq.thang)} - không cần dán gì vào sheet.\n"
            "Kiểm tra lại: đã bỏ file export vào input/exports/ chưa? Xem mục 'Cảnh báo dữ liệu' trong report.html.\n",
            encoding="utf-8")
        return [], []
    d1, d2 = khoi_thang.dong_dau, khoi_thang.dong_cuoi
    nhap_tay, cong_thuc, canh_bao = phan_loai_cot(lich, brand, d1, d2)

    # cột -> khoá
    khoa_cua_cot = {c: k for k, c in lich.cot.items()}
    dau_tp = brand.raw.get("dau_thap_phan", ",")

    # Gom cột nhập tay liên tiếp thành khối
    nhom: list[list[int]] = []
    for c in nhap_tay:
        if nhom and nhom[-1][-1] == c - 1:
            nhom[-1].append(c)
        else:
            nhom.append([c])

    ds: list[KhoiTSV] = []
    for i, cols in enumerate(nhom, start=1):
        dong_txt = []
        for r in range(d1, d2 + 1):
            moi = kq.cap_nhat.get(r, {})
            o = []
            for c in cols:
                k = khoa_cua_cot.get(c)
                if k is not None and k in moi:
                    o.append(so_tsv(moi[k], dau_tp))
                else:
                    o.append(so_tsv(lich.gia_tri_o(r, c), dau_tp))  # giữ nguyên giá trị cũ
            dong_txt.append("\t".join(o))
        ten_file = f"khoi-{i}_{so_sang_chu(cols[0])}{d1}-{so_sang_chu(cols[-1])}{d2}.tsv"
        noi_dung = "\n".join(dong_txt) + "\n"
        (thu_muc / ten_file).write_text(noi_dung, encoding="utf-8")
        ten_cot = [lich.ws_v.cell(brand.raw.get("dong_tieu_de", 5), c).value or so_sang_chu(c) for c in cols]
        ds.append(KhoiTSV(i, cols[0], cols[-1], d1, d2, ten_cot, noi_dung, ten_file))

    # Hướng dẫn dán
    dong = [
        f"HƯỚNG DẪN DÁN SỐ LIỆU {ten_thang(kq.thang).upper()} VÀO TAB '{lich.ten_tab}'",
        "=" * 70,
        f"Dải dòng của tháng: {d1} đến {d2} ({len(kq.cap_nhat)} video có số mới).",
        "Dòng không có số mới vẫn được xuất lại GIÁ TRỊ CŨ, nên dán đè cả khối là an toàn.",
        "Các cột CÔNG THỨC đã được bỏ ra ngoài, dán đúng ô dưới đây sẽ không đè công thức.",
        "",
        "Cách dán mỗi khối:",
        "  1. Mở file .tsv bằng TextEdit (chuột phải > Open With > TextEdit)",
        "     HOẶC bấm nút 'Sao chép khối' trong report.html (dễ hơn).",
        "  2. Cmd+A rồi Cmd+C để sao chép toàn bộ.",
        "  3. Trên Google Sheet, bấm chọn ĐÚNG MỘT Ô ghi bên dưới.",
        "  4. Bấm Cmd+Shift+V (dán chỉ giá trị, giữ định dạng sheet).",
        "",
    ]
    for k in ds:
        dong.append(f"Dán khối {k.so} vào ô {k.o_dau}   (file {k.ten_file}; phủ vùng {k.vung}; "
                    f"cột: {', '.join(str(x) for x in k.ten_cot)})")
    if cong_thuc:
        dong += ["", "Cột công thức được giữ nguyên (KHÔNG dán vào): " +
                 ", ".join(f"{so_sang_chu(c)} ({lich.ws_v.cell(brand.raw.get('dong_tieu_de', 5), c).value})" for c in cong_thuc)]
    dong += ["", "Lưu ý: nếu sau khi tải file .xlsx bạn đã sửa tay ô nào trong các vùng trên,",
             "hãy tải lại file .xlsx và chạy lại tool trước khi dán để không mất chỉnh sửa đó.",
             f"Số thập phân dùng dấu '{dau_tp}' (đổi trong brand.yaml: dau_thap_phan)."]
    (thu_muc / "huong-dan-dan.txt").write_text("\n".join(dong) + "\n", encoding="utf-8")
    return ds, canh_bao
