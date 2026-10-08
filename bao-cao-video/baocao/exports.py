"""Đọc file export (CSV/XLSX), tự nhận loại file theo tên cột."""
from __future__ import annotations

import csv
import io
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import openpyxl

from .ids import token_trong_o
from .util import bo_don_vi, chuan_hoa, doc_so, la_trong

DUOI_HO_TRO = {".csv", ".tsv", ".txt", ".xlsx", ".xlsm"}


@dataclass
class FileExport:
    duong_dan: Path
    loai: str | None
    ten_loai: str
    tieu_de: list
    cot_map: dict                      # trường -> chỉ số cột
    dong: list = field(default_factory=list)   # [{'truong': {...}, 'token': set, 'tho': tuple, 'so_dong': int}]
    canh_bao: list = field(default_factory=list)
    thieu_truong: list = field(default_factory=list)

    @property
    def ten(self) -> str:
        return self.duong_dan.name


def _doc_bang_csv(p: Path) -> list[list]:
    b = p.read_bytes()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = b.decode("utf-16")
    else:
        for enc in ("utf-8-sig", "cp1258", "latin-1"):
            try:
                text = b.decode(enc)
                break
            except UnicodeDecodeError:
                continue
    mau = text[:5000]
    dong_dau = mau.splitlines()[0] if mau else ""
    dem = {d: dong_dau.count(d) for d in (",", ";", "\t")}
    delim = max(dem, key=dem.get) if max(dem.values()) > 0 else ","
    return [row for row in csv.reader(io.StringIO(text), delimiter=delim)]


def _doc_bang_xlsx(p: Path) -> list[list]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    # Lấy sheet có nhiều dòng nhất
    tot, nhieu = None, -1
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        if len(rows) > nhieu:
            tot, nhieu = rows, len(rows)
    wb.close()
    return tot or []


def doc_bang(p: Path) -> list[list]:
    if p.suffix.lower() in (".xlsx", ".xlsm"):
        return _doc_bang_xlsx(p)
    return _doc_bang_csv(p)


def _khop_tieu_de(tieu_de: list, truong: dict) -> dict:
    """Map trường -> chỉ số cột. So khớp chính xác (sau chuẩn hoá), bỏ đơn vị trong ngoặc ở cuối."""
    khoa_cot = []
    for i, h in enumerate(tieu_de):
        if la_trong(h):
            khoa_cot.append(set())
        else:
            khoa_cot.append({chuan_hoa(h), chuan_hoa(bo_don_vi(h))})
    da_dung, ket_qua = set(), {}
    for ten, cfg in truong.items():
        for alias in cfg.get("cot", []):
            a = chuan_hoa(alias)
            # ưu tiên khớp nguyên văn trước khi khớp bỏ đơn vị
            for i, keys in enumerate(khoa_cot):
                if i not in da_dung and keys and a == chuan_hoa(tieu_de[i]):
                    ket_qua[ten] = i
                    break
            else:
                for i, keys in enumerate(khoa_cot):
                    if i not in da_dung and a in keys:
                        ket_qua[ten] = i
                        break
            if ten in ket_qua:
                da_dung.add(ket_qua[ten])
                break
    return ket_qua


def nhan_dien(tieu_de: list, mappings: dict) -> tuple[str | None, dict, float]:
    tot_loai, tot_map, tot_diem = None, {}, 0.0
    for loai, cfg in mappings.get("loai_file", {}).items():
        m = _khop_tieu_de(tieu_de, cfg["truong"])
        if not all(b in m for b in cfg.get("bat_buoc", [])):
            continue
        diem = len(m) / max(1, len(cfg["truong"])) + len(m) * 0.001
        if diem > tot_diem:
            tot_loai, tot_map, tot_diem = loai, m, diem
    return tot_loai, tot_map, tot_diem


def _tim_dong_tieu_de(bang: list[list], mappings: dict) -> int:
    tat_ca_alias = set()
    for cfg in mappings.get("loai_file", {}).values():
        for t in cfg["truong"].values():
            tat_ca_alias.update(chuan_hoa(a) for a in t.get("cot", []))
    tot, diem_tot = 0, -1
    for i, row in enumerate(bang[:15]):
        diem = sum(1 for h in row if not la_trong(h) and
                   (chuan_hoa(h) in tat_ca_alias or chuan_hoa(bo_don_vi(h)) in tat_ca_alias))
        if diem > diem_tot:
            tot, diem_tot = i, diem
    return tot


def doc_export(p: Path, mappings: dict) -> FileExport:
    try:
        bang = doc_bang(p)
    except Exception as e:  # file hỏng / đang mở bởi Excel
        fe = FileExport(p, None, "Không đọc được", [], {})
        fe.canh_bao.append(f"{p.name}: không mở được file ({e}). File có đang mở trong Excel hay bị hỏng?")
        return fe
    if not bang:
        fe = FileExport(p, None, "File trống", [], {})
        fe.canh_bao.append(f"{p.name}: file trống.")
        return fe
    i_td = _tim_dong_tieu_de(bang, mappings)
    tieu_de = [("" if h is None else str(h).strip()) for h in bang[i_td]]
    loai, cot_map, _ = nhan_dien(tieu_de, mappings)
    if loai is None:
        fe = FileExport(p, None, "Không nhận ra", tieu_de, {})
        fe.canh_bao.append(
            f"{p.name}: không nhận ra loại file. Các cột trong file: {', '.join(h for h in tieu_de if h)}. "
            f"Thêm tên cột phù hợp vào config/mappings.yaml.")
        return fe
    cfg = mappings["loai_file"][loai]
    fe = FileExport(p, loai, cfg.get("ten", loai), tieu_de, cot_map)
    fe.thieu_truong = [t for t, c in cfg["truong"].items() if c.get("ghi") and t not in cot_map]
    if fe.thieu_truong:
        ten_cot = [cfg["truong"][t]["cot"][0] for t in fe.thieu_truong]
        fe.canh_bao.append(f"{p.name} ({fe.ten_loai}): thiếu cột {', '.join(ten_cot)} - các số này không được cập nhật.")
    if "chi_phi" in cot_map and "usd" in chuan_hoa(tieu_de[cot_map["chi_phi"]]):
        fe.canh_bao.append(f"{p.name}: chi phí đang tính bằng USD - CPV sẽ lệch. Hãy xuất lại bằng VND.")

    for j, row in enumerate(bang[i_td + 1:], start=i_td + 2):
        if not row or all(la_trong(v) for v in row):
            continue
        gia_tri = {}
        for t, i in cot_map.items():
            v = row[i] if i < len(row) else None
            kieu = cfg["truong"][t].get("kieu", "chu")
            if kieu in ("so", "dem"):
                gia_tri[t] = doc_so(v, nguyen=(kieu == "dem"))
            else:
                gia_tri[t] = None if la_trong(v) else str(v).strip()
        token = set()
        for v in row:
            token |= token_trong_o(v)
            if isinstance(v, float) and v > 1e15:
                fe.canh_bao.append(f"{p.name} dòng {j}: ID dạng số quá dài bị Excel làm tròn - hãy xuất CSV thay vì XLSX.")
        tien_te = gia_tri.get("tien_te")
        if tien_te and str(tien_te).upper() not in ("VND", "VNĐ"):
            fe.canh_bao.append(f"{p.name}: tiền tệ {tien_te} (không phải VND) - CPV sẽ lệch.")
        fe.dong.append({"truong": gia_tri, "token": token,
                        "tho": tuple("" if v is None else str(v) for v in row), "so_dong": j})
    # chỉ báo trùng cảnh báo 1 lần
    fe.canh_bao = list(dict.fromkeys(fe.canh_bao))
    return fe


def doc_tat_ca(thu_muc: Path, mappings: dict, them: list[Path] | None = None) -> list[FileExport]:
    ds = []
    files = sorted(p for p in thu_muc.glob("*") if p.is_file() and p.suffix.lower() in DUOI_HO_TRO
                   and not p.name.startswith(("~$", ".")))
    for p in files + list(them or []):
        ds.append(doc_export(p, mappings))
    return ds
