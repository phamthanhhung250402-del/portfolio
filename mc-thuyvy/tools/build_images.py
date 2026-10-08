#!/usr/bin/env python3
"""Nén ảnh gốc sang WebP cho website MC Thúy Vy.

Cách dùng (cần Python 3 + Pillow:  pip install pillow):
    python3 tools/build_images.py                 # đọc assets/raw/, ghi assets/img/
    python3 tools/build_images.py --src thu-muc-khac

Đặt tên file trong assets/raw/ theo "vị trí" trên trang (đuôi .jpg/.jpeg/.png/.webp đều được):
    hero.png                    chân dung tách nền (PNG trong suốt) trong khung vòm ở hero
    greeting.jpg                chân dung cạnh thư "Kính chào quý đối tác"
    showreel-poster.jpg         ảnh bìa khung showreel (ngang 16:9)
    fields/gala.jpg ... fields/tv.jpg   ảnh 6 thẻ lĩnh vực (gala, conference, launching,
                                entertainment, esports, tv)
    gallery/gala-1.jpg ...      ảnh thư viện sự kiện (tên phải khớp "img" trong data/content.*.json)
    logo.png / logo.svg         logo chữ ký nền trong suốt (svg chép nguyên, png nhúng vào logo.svg)

Mỗi ảnh tạo ra: ten.webp (cạnh dài tối đa 1800px) + ten-480.webp, ten-960.webp cho srcset.
Kích thước được ghi vào data/images.json để website tự điền width/height/srcset.
"""
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_EDGE = 1800
WIDTHS = (480, 960)

# Vị trí có khung cố định trên trang: (rộng, cao, cách xử lý, tâm cắt theo chiều dọc 0..1)
SLOTS = {
    "hero": (1350, 1800, "contain-bottom", 0.0),
    "greeting": (1440, 1800, "cover", 0.25),
    "showreel-poster": (1800, 1013, "cover", 0.4),
}
FIELD_SLOT = (1440, 1800, "cover", 0.3)


def slot_for(key):
    if key in SLOTS:
        return SLOTS[key]
    if key.startswith("fields/"):
        return FIELD_SLOT
    return None


def fit(im, slot):
    w, h, mode, focus = slot
    if mode == "cover":
        return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, focus))
    # contain-bottom: giữ nguyên toàn bộ ảnh tách nền, canh giữa - sát đáy, nền trong suốt
    im = im.convert("RGBA")
    im.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(im, ((w - im.width) // 2, h - im.height), im)
    return canvas


def has_alpha(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").getchannel("A")
        return alpha.getextrema()[0] < 255
    return False


def save(im, path, alpha):
    path.parent.mkdir(parents=True, exist_ok=True)
    if alpha:
        im.convert("RGBA").save(path, "WEBP", quality=86, alpha_quality=90, method=6)
    else:
        im.convert("RGB").save(path, "WEBP", quality=80, method=6)


def process(src_file, key, out_dir):
    im = Image.open(src_file)
    im = ImageOps.exif_transpose(im)
    alpha = has_alpha(im)
    if not alpha:
        im = im.convert("RGB")
    slot = slot_for(key)
    if slot:
        im = fit(im, slot)
        alpha = alpha or slot[2] == "contain-bottom"
    else:
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

    base = out_dir / key
    for old in base.parent.glob(base.name + "-*.webp"):
        if old.stem[len(base.name) + 1:].isdigit():
            old.unlink()
    save(im, base.with_suffix(".webp"), alpha)
    widths = []
    for w in WIDTHS:
        if w < im.width:
            h = round(im.height * w / im.width)
            save(im.resize((w, h), Image.LANCZOS), out_dir / f"{key}-{w}.webp", alpha)
            widths.append(w)
    return {"w": im.width, "h": im.height, "widths": widths}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=str(ROOT / "assets" / "raw"))
    ap.add_argument("--out", default=str(ROOT / "assets" / "img"))
    ap.add_argument("--manifest", default=str(ROOT / "data" / "images.json"))
    args = ap.parse_args()

    src, out = Path(args.src), Path(args.out)
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}

    files = sorted(p for p in src.rglob("*") if p.is_file() and not p.name.startswith((".", "_")))
    count = 0
    for f in files:
        rel = f.relative_to(src)
        key = rel.with_suffix("").as_posix().lower().replace(" ", "-")
        if f.suffix.lower() == ".svg" and key == "logo":
            shutil.copyfile(f, out / "logo.svg")
            print("logo.svg  (chép nguyên)")
            count += 1
            continue
        if f.suffix.lower() not in EXTS:
            continue
        if key == "logo":
            # Logo PNG/JPG -> logo.svg nhúng ảnh (base64) để HTML không phải đổi
            import base64, io
            im = Image.open(f).convert("RGBA")
            im.thumbnail((720, 720), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=90, alpha_quality=95, method=6)
            data = base64.b64encode(buf.getvalue()).decode()
            (out / "logo.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {im.width} {im.height}">'
                f'<image width="{im.width}" height="{im.height}" href="data:image/webp;base64,{data}"/></svg>', "utf-8")
            print(f"logo  -> logo.svg ({im.width}x{im.height})")
            count += 1
            continue
        info = process(f, key, out)
        manifest[key] = info
        print(f"{key:32s} {info['w']}x{info['h']}  srcset {info['widths']}")
        count += 1

    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=1, ensure_ascii=False) + "\n", "utf-8")
    print(f"\nĐã xử lý {count} ảnh. Manifest: {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
