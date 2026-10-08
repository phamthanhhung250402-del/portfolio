"""Đọc cấu hình: hồ sơ thương hiệu, trọng số, map cột export."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .util import chuan_hoa

GOC = Path(__file__).resolve().parent.parent  # thư mục bao-cao-video/


class LoiCauHinh(Exception):
    pass


def doc_yaml(p: Path) -> dict:
    try:
        text = p.read_text(encoding="utf-8-sig")
        # TextEdit hay tự đổi " thành “ ” - đổi lại cho đúng cú pháp
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("\t", "  ")
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        dong = getattr(getattr(e, "problem_mark", None), "line", None)
        vi_tri = f" (khoảng dòng {dong + 1})" if dong is not None else ""
        raise LoiCauHinh(
            f"File {p.name} viết sai cú pháp{vi_tri}. Kiểm tra dấu cách đầu dòng, "
            f"dấu hai chấm, ngoặc kép.\nChi tiết: {e}") from None


def chu_sang_so(chu: str) -> int:
    n = 0
    for c in chu.upper():
        n = n * 26 + (ord(c) - 64)
    return n


def so_sang_chu(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


@dataclass
class Brand:
    id: str
    thu_muc: Path
    raw: dict
    weights: dict
    mappings: dict
    goc: Path = GOC

    @property
    def ten(self) -> str:
        return self.raw.get("ten", self.id)

    @property
    def input_dir(self) -> Path:
        return self.goc / self.raw.get("thu_muc_input", "input")

    @property
    def output_dir(self) -> Path:
        return self.goc / self.raw.get("thu_muc_output", "output")

    @property
    def cot(self) -> dict[str, tuple[str, str]]:
        return {k: (v[0], v[1]) for k, v in self.raw["cot"].items()}

    @property
    def nhom_noi_dung(self) -> list[dict]:
        ds = []
        for g in self.raw.get("nhom_noi_dung", []):
            if isinstance(g, str):
                g = {"ten": g}
            gd = g.get("giai_doan", "tat_ca")
            ds.append({
                "ten": g["ten"],
                "giai_doan": "tat_ca" if gd in (None, "tat_ca") else list(gd),
                "de_xuat": g.get("de_xuat", True),
            })
        return ds

    def ten_nhom_chuan(self, ten: str) -> str:
        """Đưa tên nhóm gõ trong sheet về đúng tên trong cấu hình (bỏ qua hoa/thường, dấu)."""
        k = chuan_hoa(ten)
        for g in self.nhom_noi_dung:
            if chuan_hoa(g["ten"]) == k:
                return g["ten"]
        return str(ten).strip()

    @property
    def giai_doan(self) -> dict:
        return self.raw.get("giai_doan", {})

    def loai_giai_doan(self, ten) -> str | None:
        """'T7 - BAU' -> 'bau'; 'Sau mở bán' -> 'sau_mo_ban'. Từ khoá dài nhất thắng."""
        if ten is None:
            return None
        s = chuan_hoa(ten)
        if s in self.giai_doan:
            return s
        if s.replace(" ", "_") in self.giai_doan:
            return s.replace(" ", "_")
        tot, dai = None, 0
        for loai, cfg in self.giai_doan.items():
            for tk in cfg.get("tu_khoa", []):
                tk_c = chuan_hoa(tk)
                if tk_c and re.search(r"(^|\s)" + re.escape(tk_c) + r"(\s|$)", s) and len(tk_c) > dai:
                    tot, dai = loai, len(tk_c)
        return tot

    def ten_giai_doan(self, loai: str) -> str:
        return self.giai_doan.get(loai, {}).get("ten", loai)


def danh_sach_brand(goc: Path = GOC) -> list[str]:
    thu_muc = goc / "config" / "brands"
    return sorted(p.name for p in thu_muc.iterdir()
                  if p.is_dir() and not p.name.startswith(("_", ".")) and (p / "brand.yaml").exists())


def doc_brand(brand_id: str, goc: Path = GOC) -> Brand:
    tm = goc / "config" / "brands" / brand_id
    if not (tm / "brand.yaml").exists():
        raise LoiCauHinh(f"Không thấy hồ sơ thương hiệu config/brands/{brand_id}/brand.yaml")
    raw = doc_yaml(tm / "brand.yaml")
    w_path = tm / "weights.yaml" if (tm / "weights.yaml").exists() else goc / "config" / "weights.yaml"
    m_path = tm / "mappings.yaml" if (tm / "mappings.yaml").exists() else goc / "config" / "mappings.yaml"
    b = Brand(brand_id, tm, raw, doc_yaml(w_path), doc_yaml(m_path), goc)
    kiem_tra_brand(b, goc)
    return b


def kiem_tra_brand(b: Brand, goc: Path = GOC) -> None:
    for k in ("cot", "nhom_noi_dung"):
        if k not in b.raw:
            raise LoiCauHinh(f"brand.yaml của {b.id} thiếu mục '{k}'")
    tong = sum(float(g.get("trong_so", 0)) for g in b.weights.get("nhom_chi_so", {}).values())
    if tong <= 0:
        raise LoiCauHinh("weights.yaml: tổng trọng số phải lớn hơn 0")
    for g in b.weights["nhom_chi_so"].values():
        for k in g.get("chi_so", {}):
            if k not in b.cot:
                raise LoiCauHinh(f"weights.yaml dùng chỉ số '{k}' nhưng brand.yaml không có cột này")
    # Tách biệt dữ liệu: không thương hiệu nào được dùng chung thư mục input/output
    for khac in danh_sach_brand(goc):
        if khac == b.id:
            continue
        raw2 = doc_yaml(goc / "config" / "brands" / khac / "brand.yaml")
        for kk, mac_dinh in (("thu_muc_input", "input"), ("thu_muc_output", "output")):
            if raw2.get(kk, mac_dinh) == b.raw.get(kk, mac_dinh):
                raise LoiCauHinh(
                    f"Thương hiệu '{b.id}' và '{khac}' đang dùng chung thư mục {kk} = "
                    f"'{b.raw.get(kk, mac_dinh)}'. Mỗi thương hiệu phải có thư mục riêng.")
