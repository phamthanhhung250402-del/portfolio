"""Dựng report.html (một trang) bằng Jinja2."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .analysis import fmt_chi_so, ten_ngan
from .util import fmt_gon, fmt_giay, fmt_pt, fmt_so, fmt_tien, ten_thang

CHART_JS = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"


def _delta(k, moi, truoc, thap_tot=False):
    """Trả về (mũi tên, lớp màu, chữ) cho ô KPI."""
    if moi is None or truoc is None or truoc == 0:
        return None
    d = (moi - truoc) / abs(truoc)
    if abs(d) < 0.005:
        return {"mui": "→", "lop": "phang", "chu": "không đổi"}
    tot = (d < 0) if thap_tot else (d > 0)
    return {"mui": "▲" if d > 0 else "▼", "lop": "tot" if tot else "xau",
            "chu": f"{'+' if d > 0 else '−'}{fmt_so(abs(d) * 100, 0)}% so với tháng trước"}


def _trung_tinh(d):
    """Chi phí tăng/giảm không phải tốt hay xấu -> màu xám."""
    if d:
        d["lop"] = "phang"
    return d


def dung_report(pt: dict, brand, ghep, khoi_tsv, canh_bao: list, nguon: dict, p: Path) -> None:
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"),
                      autoescape=select_autoescape(["html", "j2"]))
    env.filters.update(gon=fmt_gon, tien=fmt_tien, pt=fmt_pt, giay=fmt_giay, so=fmt_so)
    tq = pt["tong_quan"]
    moi, truoc = tq["moi"], tq["truoc"] or {}
    kpi = [
        ("Video đã air", str(moi["n"]), _trung_tinh(_delta("n", moi["n"], truoc.get("n"))), "của bạn trong tháng"),
        ("TikTok views", fmt_gon(moi["tiktok_views"]), _delta("v", moi["tiktok_views"], truoc.get("tiktok_views")), "tổng"),
        ("FB lượt xem 3s", fmt_gon(moi["fb_xem_3s"]), _delta("v", moi["fb_xem_3s"], truoc.get("fb_xem_3s")), "tổng"),
        ("Chi phí ads", fmt_gon(moi["chi_phi"]) + "đ" if moi["chi_phi"] is not None else "-",
         _trung_tinh(_delta("c", moi["chi_phi"], truoc.get("chi_phi"))),
         "TikTok + FB"),
        ("CPV TikTok", fmt_tien(moi["cpv_tiktok"]), _delta("c", moi["cpv_tiktok"], truoc.get("cpv_tiktok"), True), "median"),
        ("CPV FB 3s", fmt_tien(moi["cpv_fb_3s"]), _delta("c", moi["cpv_fb_3s"], truoc.get("cpv_fb_3s"), True), "median"),
        ("FB xem TB", fmt_giay(moi["fb_xem_tb"]), _delta("x", moi["fb_xem_tb"], truoc.get("fb_xem_tb")), "median"),
        ("Tỷ lệ xem 50%", fmt_pt(moi["ty_le_xem_50"]), _delta("x", moi["ty_le_xem_50"], truoc.get("ty_le_xem_50")), "median, FB ads"),
    ]

    nhom_bang = sorted([g for g in pt["nhom"] if g["n"]],
                       key=lambda g: (g["hang"] is None, g["ngoai_giai_doan"], g["hang"] or 0, -(g["diem"] or g["diem_ls"] or 0)))
    tl_chart = {
        "nhan": [x["nhan"] for x in pt["tl_kenh"]],
        "diem": [round(x["diem"], 1) if x["diem"] is not None else None for x in pt["tl_kenh"]],
        "n": [x["n"] for x in pt["tl_kenh"]],
        "cpv": [round(x["cpv"], 2) if x["cpv"] is not None else None for x in pt["tl_kenh"]],
        "xem_tb": [round(x["xem_tb"], 2) if x["xem_tb"] is not None else None for x in pt["tl_kenh"]],
    }
    ts = pt["thang_sau"]
    html = env.get_template("report.html.j2").render(
        brand=brand, pt=pt, ts=ts, kpi=kpi, nhom_bang=nhom_bang, ghep=ghep, khoi_tsv=khoi_tsv,
        canh_bao=list(dict.fromkeys(canh_bao)), nguon=nguon, tl_chart_json=json.dumps(tl_chart),
        chart_js=CHART_JS, ten_thang=ten_thang, fmt_chi_so=fmt_chi_so, ten_ngan=ten_ngan,
        tao_luc=dt.datetime.now().strftime("%H:%M %d/%m/%Y"),
        tong_mix=sum(d["so_video"] for d in pt["mix"]),
        max_mix=max([d["so_video"] for d in pt["mix"]] or [1]) or 1,
    )
    p.write_text(html, encoding="utf-8")
