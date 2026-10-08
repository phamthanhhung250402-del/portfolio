"""Lấy ID video TikTok / bài viết Facebook từ link hoặc ô bất kỳ."""
from __future__ import annotations

import re

RE_TIKTOK = re.compile(r"/(?:video|photo)/(\d{15,22})")
RE_TIKTOK_SO = re.compile(r"(?<!\d)(\d{18,20})(?!\d)")
RE_SO_DAI = re.compile(r"(?<![\d])(\d{8,25})(?![\d])")
RE_PFBID = re.compile(r"(pfbid0[0-9A-Za-z]{20,})")

# Mẫu link Facebook, theo thứ tự ưu tiên: bắt đúng ID bài/video, KHÔNG lấy ID Trang
RE_FB = [
    re.compile(r"/(?:posts|videos|reel|reels|permalink|photos?)/(?:[^/?#]+/)?(\d{8,})"),
    re.compile(r"[?&](?:v|story_fbid|fbid)=(\d{8,})"),
    re.compile(r"(?<!\d)\d{8,}_(\d{8,})(?!\d)"),
    re.compile(r"facebook\.com/(\d{8,})/?(?:[?#]|$)"),
    re.compile(r"fb\.watch/([0-9A-Za-z_-]+)"),
]


def tiktok_id(link) -> str | None:
    if not link:
        return None
    m = RE_TIKTOK.search(str(link))
    if m:
        return m.group(1)
    s = str(link).strip()
    if re.fullmatch(r"\d{15,22}", s):
        return s
    return None


def la_link_tiktok_rut_gon(link) -> bool:
    return bool(link) and bool(re.search(r"(vt|vm)\.tiktok\.com|tiktok\.com/t/", str(link)))


def fb_ids(link) -> set[str]:
    """Tập ID nhận diện bài Facebook: ID bài/video + mã pfbid (nếu có)."""
    if not link:
        return set()
    s = str(link).strip()
    ids: set[str] = set()
    if re.fullmatch(r"\d{8,}", s):
        ids.add(s)
    m = re.fullmatch(r"(\d{8,})_(\d{8,})", s)
    if m:
        ids.add(m.group(2))
    for r in RE_FB:
        for m in r.finditer(s):
            ids.add(m.group(1))
    ids.update(RE_PFBID.findall(s))
    return ids


def la_link_fb_rut_gon(link) -> bool:
    return bool(link) and bool(re.search(r"facebook\.com/share/|fb\.me/", str(link)))


def token_trong_o(v) -> set[str]:
    """Mọi dãy số dài và mã pfbid trong một ô export (dùng để ghép với ID đã biết)."""
    if v is None:
        return set()
    if isinstance(v, float) and v.is_integer():
        v = str(int(v))
    s = str(v)
    toks = set(RE_SO_DAI.findall(s)) | set(RE_PFBID.findall(s))
    m = re.search(r"(\d{8,})_(\d{8,})", s)
    if m:
        toks.add(m.group(2))
    return toks
