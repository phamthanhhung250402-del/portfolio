"""Luồng chính: đọc sheet + export -> ghép -> TSV -> phân tích -> report/brief/mix."""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

from . import analysis, brief, exports, merge, report, sheet, tsv
from .config import GOC, LoiCauHinh, danh_sach_brand, doc_brand, doc_yaml
from .ids import tiktok_id
from .util import ten_thang

TEN_MAU_TIKTOK = "tiktok-views-template.csv"


def in_ra(*a):
    print(*a, flush=True)


def chon_brand(chi_dinh: str | None, goc: Path) -> str:
    ds = danh_sach_brand(goc)
    if not ds:
        raise LoiCauHinh("Chưa có hồ sơ thương hiệu nào trong config/brands/")
    if chi_dinh:
        if chi_dinh not in ds:
            raise LoiCauHinh(f"Không có thương hiệu '{chi_dinh}'. Đang có: {', '.join(ds)}")
        return chi_dinh
    if len(ds) == 1 or not sys.stdin.isatty():
        return ds[0]
    in_ra("Chọn thương hiệu:")
    for i, b in enumerate(ds, 1):
        in_ra(f"  {i}. {b}")
    while True:
        x = input("Gõ số rồi Enter: ").strip()
        if x.isdigit() and 1 <= int(x) <= len(ds):
            return ds[int(x) - 1]


def chuan_bi_thu_muc(inp: Path) -> None:
    (inp / "sheet").mkdir(parents=True, exist_ok=True)
    (inp / "exports").mkdir(parents=True, exist_ok=True)
    if not (inp / "thang-sau.yaml").exists():
        shutil.copy(GOC / "mau" / "thang-sau.yaml", inp / "thang-sau.yaml")
        in_ra(f"• Đã tạo file mẫu {inp.name}/thang-sau.yaml - điền lịch tháng sau rồi chạy lại để mix chính xác hơn.")


def tim_sheet(inp: Path) -> Path | None:
    ds = [p for p in (inp / "sheet").glob("*.xlsx") if not p.name.startswith(("~$", "."))]
    return max(ds, key=lambda p: p.stat().st_mtime) if ds else None


def cap_nhat_mau_tiktok(p: Path, ghep_kq, brand) -> bool:
    """Tạo/bổ sung file mẫu nhập tay TikTok views cho các video tháng đang cập nhật.
    Giữ nguyên dòng bạn đã nhập; chỉ thêm link còn thiếu."""
    cu, tieu_de = [], ["Link TikTok", "views", "likes", "shares", "Tiêu đề (tham khảo)"]
    if p.exists():
        bang = exports.doc_bang(p)
        if bang:
            tieu_de = bang[0] if len(bang[0]) >= 4 else tieu_de
            cu = bang[1:]
    da_co = {tiktok_id(r[0]) or r[0] for r in cu if r and r[0]}
    them = []
    for v in ghep_kq.muc_tieu:
        link = v.get("link_tiktok")
        tid = tiktok_id(link)
        if tid and tid not in da_co:
            them.append([link, "", "", "", str(v.get("chu_de", ""))])
            da_co.add(tid)
    if not them and p.exists():
        return False
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu_de)
        w.writerows(cu + them)
    return True


def kiem_tra_mau_header(brand, goc: Path) -> list[str]:
    """Đối chiếu file mẫu trong samples/headers/ với config/mappings.yaml."""
    cb = []
    tm = goc / "samples" / "headers"
    if not tm.exists():
        return cb
    for p in sorted(tm.glob("*")):
        if p.suffix.lower() not in exports.DUOI_HO_TRO:
            continue
        fe = exports.doc_export(p, brand.mappings)
        if fe.loai is None:
            cb.append(f"Mẫu header {p.name}: không nhận ra loại file - cột: {', '.join(h for h in fe.tieu_de if h)}")
        elif fe.thieu_truong:
            cb.append(f"Mẫu header {p.name} ({fe.ten_loai}): thiếu " + ", ".join(fe.thieu_truong) +
                      " - thêm tên cột thật vào config/mappings.yaml")
    return cb


def chay(brand_id: str | None = None, demo: bool = False, mo_report: bool = True, goc: Path = GOC,
         thu_muc_input: Path | None = None, thu_muc_output: Path | None = None) -> dict:
    brand = doc_brand(chon_brand(brand_id, goc), goc)
    inp = goc / "samples" / "demo" / "input" if demo else brand.input_dir
    out_goc = goc / "samples" / "demo" / "output" if demo else brand.output_dir
    inp, out_goc = Path(thu_muc_input or inp), Path(thu_muc_output or out_goc)
    in_ra(f"Thương hiệu: {brand.ten}{'  (DỮ LIỆU GIẢ - chạy thử)' if demo else ''}")
    chuan_bi_thu_muc(inp)

    p_sheet = tim_sheet(inp)
    if p_sheet is None:
        if sys.platform == "darwin":
            subprocess.run(["open", str(inp / "sheet")], check=False)  # mở sẵn thư mục cho bạn bỏ file vào
        raise LoiCauHinh(f"Chưa có file .xlsx trong {inp}/sheet/. "
                         "Tải Google Sheet: Tệp > Tải xuống > Microsoft Excel (.xlsx) rồi bỏ vào thư mục đó.")
    in_ra(f"• Đọc sheet: {p_sheet.name}")
    lich = sheet.doc_lich(p_sheet, brand)
    canh_bao = list(lich.canh_bao)

    raw_ts = doc_yaml(inp / "thang-sau.yaml") if (inp / "thang-sau.yaml").exists() else {}
    from .util import doc_ma_thang
    thang = merge.chon_thang_cap_nhat(lich, brand, doc_ma_thang(raw_ts.get("thang_cap_nhat")))
    if lich.khoi_thang(thang) is None:
        raise LoiCauHinh(f"Không có khối tháng {thang} trong tab 03 (thang_cap_nhat trong thang-sau.yaml).")
    in_ra(f"• Tháng cập nhật: {ten_thang(thang)}")

    p_mau = inp / TEN_MAU_TIKTOK
    files = exports.doc_tat_ca(inp / "exports", brand.mappings, [p_mau] if p_mau.exists() else [])
    for f in files:
        in_ra(f"• {f.ten}: {f.ten_loai} ({len(f.dong)} dòng)")
        canh_bao.extend(f.canh_bao)
    kq = merge.ghep(lich, brand, files, thang)
    canh_bao.extend(kq.canh_bao)

    co_tiktok_export = any(f.loai == "tiktok_organic" and f.duong_dan != p_mau for f in files)
    if not co_tiktok_export:
        if cap_nhat_mau_tiktok(p_mau, kq, brand):
            in_ra(f"• Đã tạo/bổ sung {inp.name}/{TEN_MAU_TIKTOK}: điền views, likes, shares rồi chạy lại.")
        if not any(f.loai == "tiktok_organic" and f.dong for f in files):
            canh_bao.append(f"Chưa có số TikTok views/likes/shares: điền file {inp.name}/{TEN_MAU_TIKTOK} (đã có sẵn link video tháng này) rồi chạy lại.")

    out = out_goc / thang
    out.mkdir(parents=True, exist_ok=True)
    khoi, cb_tsv = tsv.xuat(lich, brand, kq, out / "cap-nhat-tab03")
    canh_bao.extend(cb_tsv)
    canh_bao.extend(kiem_tra_mau_header(brand, goc))

    pt = analysis.phan_tich(lich, brand, kq, raw_ts, canh_bao)
    brief.xuat_mix_tsv(pt, brand, out / "de-xuat-mix-thang-sau.tsv")
    brief.xuat_brief(pt, brand, out / "brief-cho-claude.md")
    nguon = {"sheet": p_sheet.name, "tab": lich.ten_tab, "exports": [f for f in files]}
    report.dung_report(pt, brand, kq, khoi, canh_bao, nguon, out / "report.html")

    in_ra("")
    in_ra(f"XONG. Kết quả trong: {out}/")
    in_ra(f"  - report.html                 ({len(kq.cap_nhat)}/{len(kq.muc_tieu)} video có số mới, {len(khoi)} khối TSV)")
    in_ra(f"  - cap-nhat-tab03/             (dán vào sheet theo huong-dan-dan.txt)")
    in_ra(f"  - de-xuat-mix-thang-sau.tsv   ({ts_tong(pt)} video {ten_thang(pt['thang_sau']['thang'])})")
    in_ra(f"  - brief-cho-claude.md")
    if kq.khong_ghep_video:
        in_ra(f"  ! {len(kq.khong_ghep_video)} video chưa ghép được số liệu - xem mục Cảnh báo dữ liệu trong report.")
    if mo_report and sys.platform == "darwin":
        subprocess.run(["open", str(out / "report.html")], check=False)
    return {"out": out, "lich": lich, "ghep": kq, "khoi": khoi, "phan_tich": pt, "brand": brand, "canh_bao": canh_bao}


def ts_tong(pt):
    return sum(d["so_video"] for d in pt["mix"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cập nhật số liệu video + đề xuất mix nội dung tháng sau")
    ap.add_argument("--brand", help="mã thương hiệu (tên thư mục trong config/brands)")
    ap.add_argument("--demo", action="store_true", help="chạy trên dữ liệu giả trong samples/demo")
    ap.add_argument("--khong-mo", action="store_true", help="không tự mở report.html")
    a = ap.parse_args(argv)
    try:
        chay(a.brand, a.demo, not a.khong_mo)
        return 0
    except LoiCauHinh as e:
        in_ra("")
        in_ra("LỖI: " + str(e))
        return 2
    except Exception as e:  # lỗi bất ngờ: ghi chi tiết để gửi kèm khi nhờ sửa
        in_ra("")
        in_ra(f"LỖI BẤT NGỜ: {e}")
        log = GOC / "loi-gan-nhat.txt"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        in_ra(f"Chi tiết đã lưu vào {log.name} - gửi file này khi cần nhờ sửa.")
        return 1
