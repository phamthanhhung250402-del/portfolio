"""Chia số video tháng sau theo điểm hiệu quả (hàm thuần, dễ kiểm thử)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class UngVien:
    ten: str
    diem: float | None = None          # 0-100
    xep_hang: bool = False             # đủ dữ liệu (>= ngưỡng video)
    dang_chay: bool = False            # có video trong N tháng gần nhất
    uu_tien_thu_nghiem: bool = False   # bạn ghi trong nhom_thu_nghiem
    toi_thieu_them: int = 0            # vd nhóm sự kiện: số sự kiện
    so_video_lich_su: int = 0


@dataclass
class KetQuaMix:
    so_video: dict                     # tên -> tổng số video
    hieu_qua: dict                     # tên -> phần theo điểm
    thu_nghiem: dict                   # tên -> phần slot thử nghiệm
    cham_tran: set = field(default_factory=set)
    giu_toi_thieu: set = field(default_factory=set)   # nhóm chỉ nhận đúng số tối thiểu
    canh_bao: list = field(default_factory=list)
    tran: int = 0


def phan_bo(tong: int, ung_vien: list[UngVien], ty_le_thu_nghiem=0.2, toi_thieu=2,
            toi_da_ty_trong=0.35, do_doc=2.0) -> KetQuaMix:
    tong = max(0, int(tong))
    tran = max(1, math.floor(toi_da_ty_trong * tong + 1e-9))
    canh_bao: list[str] = []
    hq = [u for u in ung_vien if u.xep_hang]
    tn = [u for u in ung_vien if (not u.xep_hang) or u.uu_tien_thu_nghiem]
    # Thứ tự slot thử nghiệm: nhóm có tối thiểu bắt buộc (sự kiện) -> bạn đăng ký -> nhóm có dữ liệu, điểm cao
    tn.sort(key=lambda u: (-(u.toi_thieu_them > 0 and not u.xep_hang), -u.uu_tien_thu_nghiem,
                           -(u.diem if u.diem is not None else -1), -u.so_video_lich_su, u.ten))

    so_tn = round(ty_le_thu_nghiem * tong) if tn else 0
    if not hq:
        so_tn = tong
    if tn and so_tn == 0 and any(u.uu_tien_thu_nghiem for u in tn) and tong >= 3:
        so_tn = 1
    so_hq = tong - so_tn

    phan_hq = {u.ten: 0 for u in hq}
    if hq and so_hq > 0:
        # 1) tối thiểu cho nhóm đang chạy (và nhóm có sự kiện)
        min_ = {}
        for u in sorted(hq, key=lambda u: -(u.diem or 0)):
            m = (toi_thieu if u.dang_chay else 0)
            m = max(m, u.toi_thieu_them)
            min_[u.ten] = min(m, tran)
        if sum(min_.values()) > so_hq:
            canh_bao.append(f"Tổng {so_hq} video không đủ để mỗi nhóm đang chạy có {toi_thieu} video - "
                            f"ưu tiên nhóm điểm cao.")
            con = so_hq
            for u in sorted(hq, key=lambda u: -(u.diem or 0)):
                m = min(min_[u.ten], con)
                min_[u.ten] = m
                con -= m
        phan_hq.update(min_)
        giu_toi_thieu = {k for k, v in min_.items() if v > 0}

        # 2) chia phần còn lại theo điểm^do_doc, có trần (water-filling)
        con_lai = so_hq - sum(min_.values())
        trong_so = {u.ten: max(u.diem or 0.0, 1.0) ** do_doc for u in hq}
        thuc = {k: float(v) for k, v in phan_hq.items()}
        tu_do = {k for k in thuc if thuc[k] < tran}
        while con_lai > 1e-9 and tu_do:
            tong_ts = sum(trong_so[k] for k in tu_do)
            tran_moi = set()
            da_chia = 0.0
            for k in list(tu_do):
                them = con_lai * trong_so[k] / tong_ts
                if thuc[k] + them >= tran:
                    them = tran - thuc[k]
                    tran_moi.add(k)
                thuc[k] += them
                da_chia += them
            con_lai -= da_chia
            if not tran_moi:
                break
            tu_do -= tran_moi
        # 3) làm tròn: phần nguyên + chia phần dư lớn nhất, không vượt trần
        nguyen = {k: int(math.floor(v + 1e-9)) for k, v in thuc.items()}
        du = so_hq - sum(nguyen.values())
        thu_tu = sorted(thuc, key=lambda k: (-(thuc[k] - nguyen[k]), -trong_so[k]))
        while du > 0:
            tien = False
            for k in thu_tu:
                if du > 0 and nguyen[k] < tran:
                    nguyen[k] += 1
                    du -= 1
                    tien = True
            if not tien:
                break
        phan_hq = nguyen
        giu_toi_thieu = {k for k in giu_toi_thieu if phan_hq[k] <= min_[k]}
        if du > 0:
            if tn:
                so_tn += du
                canh_bao.append(f"Các nhóm hiệu quả đã chạm trần {int(toi_da_ty_trong * 100)}% - "
                                f"chuyển {du} video sang slot thử nghiệm.")
            else:
                canh_bao.append(f"Ít nhóm nên vượt trần {int(toi_da_ty_trong * 100)}%: cộng {du} video cho nhóm điểm cao nhất.")
                top = max(hq, key=lambda u: u.diem or 0).ten
                phan_hq[top] += du
            du = 0
    else:
        giu_toi_thieu = set()
        if hq:
            so_tn = tong

    # 4) slot thử nghiệm: chia vòng tròn
    phan_tn = {u.ten: 0 for u in tn}
    con = so_tn
    if tn:
        # nhóm sự kiện chưa xếp hạng nhận đủ số tối thiểu trước
        for u in tn:
            if not u.xep_hang and u.toi_thieu_them:
                m = min(u.toi_thieu_them, con, tran)
                phan_tn[u.ten] += m
                con -= m
        while con > 0:
            tien = False
            for u in tn:
                tong_nhom = phan_tn[u.ten] + phan_hq.get(u.ten, 0)
                if con > 0 and tong_nhom < tran:
                    phan_tn[u.ten] += 1
                    con -= 1
                    tien = True
            if not tien:
                break
    if con > 0:
        # tất cả đã chạm trần: trả về nhóm có thể nhận, hoặc nhóm điểm cao nhất
        canh_bao.append(f"Không chia hết slot thử nghiệm vì trần {int(toi_da_ty_trong * 100)}% - cộng {con} video vào nhóm điểm cao nhất.")
        dich = max(ung_vien, key=lambda u: (u.diem or 0)).ten if ung_vien else None
        if dich is not None:
            if dich in phan_hq:
                phan_hq[dich] += con
            else:
                phan_tn[dich] = phan_tn.get(dich, 0) + con
        con = 0

    tong_nhom = {}
    for u in ung_vien:
        tong_nhom[u.ten] = phan_hq.get(u.ten, 0) + phan_tn.get(u.ten, 0)
    assert sum(tong_nhom.values()) == tong or not ung_vien, (tong_nhom, tong)
    cham_tran = {k for k, v in tong_nhom.items() if v >= tran and tong > 0}
    return KetQuaMix(tong_nhom, phan_hq, phan_tn, cham_tran, giu_toi_thieu, canh_bao, tran)
