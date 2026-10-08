#!/usr/bin/env node
/**
 * Tải thumbnail cho từng video trong data/clips.json và data/ads.json qua TikTok oEmbed,
 * lưu vào assets/thumbs/{id}.webp và ghi trường "thumb" vào file JSON.
 *
 * Cách chạy (cần Node 18+), đứng ở thư mục gốc dự án:
 *   node scripts/fetch-thumbs.mjs          # chỉ tải clip chưa có ảnh
 *   node scripts/fetch-thumbs.mjs --force  # tải lại tất cả
 *
 * Chuyển ảnh sang .webp bằng một trong các công cụ sau (dùng cái nào có trước):
 *   1. thư viện sharp   (npm install sharp)
 *   2. ffmpeg           (https://ffmpeg.org)
 *   3. cwebp            (https://developers.google.com/speed/webp)
 * Nếu máy không có công cụ nào, ảnh được giữ nguyên định dạng .jpg - web vẫn chạy bình thường.
 */
import { readFile, writeFile, mkdir, access, unlink } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DATA_FILES = ["clips.json", "ads.json"].map((f) => path.join(ROOT, "data", f));
const OUT_DIR = path.join(ROOT, "assets", "thumbs");
const FORCE = process.argv.includes("--force");
const WIDTH = 540; // khớp width/height khai báo trên thẻ <img> (540x960)

const exists = (p) => access(p).then(() => true, () => false);
const hasCmd = (cmd) => spawnSync(cmd, ["-version"], { stdio: "ignore" }).error === undefined;

let sharp = null;
try { sharp = (await import("sharp")).default; } catch { /* không có sharp */ }

async function toWebp(buf, dest) {
  if (sharp) {
    await sharp(buf).resize({ width: WIDTH, height: WIDTH * 16 / 9, fit: "cover" }).webp({ quality: 78 }).toFile(dest);
    return true;
  }
  const tmp = dest.replace(/\.webp$/, ".tmp.jpg");
  await writeFile(tmp, buf);
  try {
    if (hasCmd("ffmpeg")) {
      const r = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", tmp,
        "-vf", `scale=${WIDTH}:${WIDTH * 16 / 9}:force_original_aspect_ratio=increase,crop=${WIDTH}:${WIDTH * 16 / 9}`,
        "-quality", "78", dest]);
      if (r.status === 0) return true;
    }
    if (hasCmd("cwebp")) {
      const r = spawnSync("cwebp", ["-quiet", "-q", "78", "-resize", String(WIDTH), "0", tmp, "-o", dest]);
      if (r.status === 0) return true;
    }
    return false;
  } finally {
    await unlink(tmp).catch(() => {});
  }
}

async function fetchThumb(clip) {
  const res = await fetch("https://www.tiktok.com/oembed?url=" + encodeURIComponent(clip.tiktok));
  if (!res.ok) throw new Error(`oEmbed HTTP ${res.status}`);
  const { thumbnail_url: url } = await res.json();
  if (!url) throw new Error("oEmbed không trả về thumbnail_url");
  const img = await fetch(url);
  if (!img.ok) throw new Error(`Tải ảnh HTTP ${img.status}`);
  const buf = Buffer.from(await img.arrayBuffer());

  const webp = path.join(OUT_DIR, `${clip.id}.webp`);
  if (await toWebp(buf, webp)) return `assets/thumbs/${clip.id}.webp`;

  const jpg = path.join(OUT_DIR, `${clip.id}.jpg`);
  await writeFile(jpg, buf);
  return `assets/thumbs/${clip.id}.jpg`;
}

await mkdir(OUT_DIR, { recursive: true });
if (!sharp && !hasCmd("ffmpeg") && !hasCmd("cwebp")) {
  console.log("! Không tìm thấy sharp/ffmpeg/cwebp - ảnh sẽ được lưu dạng .jpg.");
}

let ok = 0, skipped = 0, failed = 0;
for (const file of DATA_FILES) {
  if (!(await exists(file))) continue;
  console.log(`\n== ${path.relative(ROOT, file)}`);
  const clips = JSON.parse(await readFile(file, "utf8"));
  for (const clip of clips) {
    if (clip.placeholder || !/\/video\/\d+/.test(clip.tiktok || "")) { skipped++; continue; }
    if (!FORCE && clip.thumb && await exists(path.join(ROOT, clip.thumb))) { skipped++; continue; }
    try {
      clip.thumb = await fetchThumb(clip);
      ok++;
      console.log(`✓ ${clip.id}  ${clip.title}`);
    } catch (err) {
      failed++;
      console.log(`✗ ${clip.id}  ${clip.title}  (${err.message})`);
    }
  }
  // Giữ định dạng mỗi video một dòng cho dễ sửa tay
  await writeFile(file, "[\n" + clips.map((c) => "  " + JSON.stringify(c)).join(",\n") + "\n]\n");
}
console.log(`\nXong: ${ok} ảnh mới, ${skipped} bỏ qua, ${failed} lỗi.`);
if (failed) process.exitCode = 1;
