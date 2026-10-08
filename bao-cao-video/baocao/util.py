"""Hàm tiện ích dùng chung: chuẩn hoá chữ, đọc số, tháng, định dạng số kiểu Việt Nam."""
from __future__ import annotations

import datetime as dt
import math
import re
import statistics
import unicodedata

THANG_EN = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def bo_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def chuan_hoa(s) -> str:
    """'FB người xem ≥3s' -> 'fb nguoi xem 3s'. Dùng để so khớp tên cột / tên nhóm."""
    if s is None:
        return ""
    s = bo_dau(str(s)).lower()
    s = re.sub(r"[^a-z0-9%]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def bo_don_vi(s: str) -> str:
    """'Amount spent (VND)' -> 'Amount spent'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", str(s)).strip()


def la_trong(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "") or (isinstance(v, float) and math.isnan(v))


def doc_so(v, nguyen: bool = False):
    """Đọc số từ ô bất kỳ: 1.234.567 | 1,234,567 | 12,5 | 1.2K | 3,4M | 45% | 9,9đ | '-'.
    Trả về float hoặc None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)
    s = str(v).strip().lower()
    if s in ("", "-", "--", "n/a", "na", "#n/a", "#div/0!", "none", "null"):
        return None
    he_so = 1.0
    if s.endswith("%"):
        he_so = 0.01
        s = s[:-1]
    s = re.sub(r"(vnd|vnđ|usd|đ|₫|\$|\s)", "", s)
    m = re.match(r"^([0-9.,]+)([kmb])$", s)
    if m:
        s, hau_to = m.group(1), m.group(2)
        he_so *= {"k": 1e3, "m": 1e6, "b": 1e9}[hau_to]
        nguyen = False
    am = s.startswith("-")
    s = s.lstrip("-+")
    if not re.fullmatch(r"[0-9.,]+", s or "x"):
        return None
    co_cham, co_phay = "." in s, "," in s
    if co_cham and co_phay:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif co_phay:
        # "1,234,567" / "123,456" (không bắt đầu bằng 0) = phân cách nghìn; "9,9" / "0,045" = thập phân
        if s.count(",") > 1 or nguyen or re.fullmatch(r"[1-9]\d{0,2},\d{3}", s):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    elif co_cham:
        if s.count(".") > 1 or (nguyen and re.fullmatch(r"\d{1,3}(\.\d{3})+", s)):
            s = s.replace(".", "")
    try:
        x = float(s) * he_so
    except ValueError:
        return None
    return -x if am else x


def doc_thoi_luong(v):
    """45 | '45' | '0:45' | '1:05' -> giây."""
    if isinstance(v, dt.time):
        return v.hour * 3600 + v.minute * 60 + v.second
    if isinstance(v, str) and re.fullmatch(r"\s*\d{1,2}:\d{2}(:\d{2})?\s*", v):
        phan = [int(p) for p in v.strip().split(":")]
        tong = 0
        for p in phan:
            tong = tong * 60 + p
        return float(tong)
    return doc_so(v)


def ma_thang(nam: int, thang: int) -> str:
    return f"{nam:04d}-{thang:02d}"


def thang_ke(ma: str, buoc: int = 1) -> str:
    nam, thang = map(int, ma.split("-"))
    idx = nam * 12 + (thang - 1) + buoc
    return ma_thang(idx // 12, idx % 12 + 1)


def doc_ma_thang(v) -> str | None:
    """'2026-10' | date | '10/2026' | 'T10/2026' -> '2026-10'."""
    if v is None or v == "":
        return None
    if isinstance(v, (dt.date, dt.datetime)):
        return ma_thang(v.year, v.month)
    s = str(v).strip()
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})", s)
    if m:
        return ma_thang(int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r"[tT]?(?:háng\s*)?(\d{1,2})[-/.\s](\d{4})", s)
    if m:
        return ma_thang(int(m.group(2)), int(m.group(1)))
    return None


def nhan_dien_dong_thang(text) -> str | None:
    """Nhận ra dòng tiêu đề khối tháng: 'JULY 2026 - BAU / Back to School · 25 ...',
    'THÁNG 7/2026 - ...', 'T7/2026 ...'. Trả về '2026-07' hoặc None."""
    if not isinstance(text, str):
        return None
    s = bo_dau(text).strip().lower()
    m = re.match(r"^([a-z]{3,9})\.?\s+(\d{4})\b", s)
    if m and m.group(1) in THANG_EN:
        return ma_thang(int(m.group(2)), THANG_EN[m.group(1)])
    m = re.match(r"^(?:thang|t)\s*(\d{1,2})\s*[/\-.\s]\s*(\d{4})\b", s)
    if m and 1 <= int(m.group(1)) <= 12:
        return ma_thang(int(m.group(2)), int(m.group(1)))
    return None


def ten_thang(ma: str) -> str:
    nam, thang = ma.split("-")
    return f"Tháng {int(thang)}/{nam}"


def doc_ngay(v) -> dt.date | None:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str):
        s = v.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
            try:
                return dt.datetime.strptime(s, fmt).date()
            except ValueError:
                pass
    return None


def median(ds):
    ds = [x for x in ds if x is not None]
    return statistics.median(ds) if ds else None


# ---------------- định dạng hiển thị kiểu Việt Nam ----------------

def _nhom_nghin(so_nguyen: str) -> str:
    return f"{int(so_nguyen):,}".replace(",", ".")


def fmt_so(x, thap_phan: int = 0) -> str:
    if x is None:
        return "-"
    if thap_phan == 0:
        return _nhom_nghin(str(int(round(x))))
    s = f"{x:.{thap_phan}f}"
    nguyen, le = s.split(".")
    am = nguyen.startswith("-")
    nguyen = _nhom_nghin(nguyen.lstrip("-"))
    return ("-" if am else "") + nguyen + "," + le


def fmt_gon(x) -> str:
    """1.250.000 -> 1,25M ; 85.400 -> 85,4K"""
    if x is None:
        return "-"
    for nguong, hau_to in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(x) >= nguong:
            v = x / nguong
            return fmt_so(v, 2 if v < 10 else 1).rstrip("0").rstrip(",") + hau_to
    return fmt_so(x)


def fmt_tien(x) -> str:
    if x is None:
        return "-"
    return fmt_so(x, 1 if abs(x) < 100 else 0) + "đ"


def fmt_pt(x, thap_phan: int = 1) -> str:
    return "-" if x is None else fmt_so(x * 100, thap_phan) + "%"


def fmt_giay(x) -> str:
    return "-" if x is None else fmt_so(x, 1) + "s"


def so_tsv(v, dau_thap_phan: str = ",") -> str:
    """Giá trị ô -> chữ trong TSV để dán vào Google Sheet."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, (int, float)):
        if isinstance(v, float) and math.isnan(v):
            return ""
        if float(v).is_integer():
            return str(int(v))
        s = repr(round(float(v), 10))
        if "e" in s:
            s = f"{v:.10f}".rstrip("0")
        return s.replace(".", dau_thap_phan)
    s = str(v)
    return s.replace("\t", " ").replace("\r", " ").replace("\n", " ")
