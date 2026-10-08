/* Tạo ảnh placeholder (tông đỏ/bạc) cho các vị trí ảnh còn thiếu.
 * Chỉ dùng khi chưa có ảnh gốc. Cần Node + Playwright:
 *   NODE_PATH=$(npm root -g) node tools/make_placeholders.cjs /duong/dan/thu-muc-tam
 *   python3 tools/build_images.py --src /duong/dan/thu-muc-tam
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.resolve(process.argv[2] || path.join(ROOT, 'assets', 'raw-placeholders'));
const FONTS = 'file://' + path.join(ROOT, 'css', 'fonts.css');

const FIELDS = {
  gala: 'Gala & YEP', conference: 'Conference', launching: 'Launching Event',
  entertainment: 'Entertainment', esports: 'Esports & Sports', tv: 'TV Show & Virtual Event'
};
const SIZES = [[1800, 1200], [1440, 1800], [1800, 1350], [1200, 1800], [1800, 1800], [1800, 1013]];

function rand(seed) { let s = 0; for (const c of seed) s = (s * 31 + c.charCodeAt(0)) >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

function bokeh(seed, w, h, n) {
  const r = rand(seed); let out = '';
  for (let i = 0; i < n; i++) {
    const d = (0.03 + r() * 0.12) * Math.max(w, h);
    const silver = r() > 0.55;
    const a = (0.05 + r() * 0.16).toFixed(2);
    const col = silver ? `rgba(245,230,226,${a})` : `rgba(230,70,60,${a})`;
    out += `<i style="left:${(r() * 100).toFixed(1)}%;top:${(r() * 70).toFixed(1)}%;width:${d}px;height:${d}px;background:radial-gradient(circle,${col} 0 55%,transparent 70%)"></i>`;
  }
  return out;
}

const STAR = '<svg viewBox="0 0 24 24"><path fill="url(#sg)" d="M12 0c.9 7.4 4.6 11.1 12 12-7.4.9-11.1 4.6-12 12-.9-7.4-4.6-11.1-12-12C7.4 11.1 11.1 7.4 12 0Z"/><defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#D9C6C4"/></linearGradient></defs></svg>';

const BASE_CSS = `
@import url("${FONTS}");
*{box-sizing:border-box}html,body{margin:0;background:transparent}
.ph{position:relative;overflow:hidden;font-family:"Be Vietnam Pro",sans-serif;color:#F5EEEC}
.stage{background:radial-gradient(ellipse 60% 50% at 50% 38%,rgba(195,53,53,.6),transparent 70%),radial-gradient(ellipse 90% 80% at 50% 35%,#800606 0%,#5F0203 50%,#2D0102 100%)}
.beams{position:absolute;inset:0;background:linear-gradient(100deg,transparent 30%,rgba(255,230,222,.08) 42%,transparent 52%),linear-gradient(80deg,transparent 48%,rgba(255,230,222,.07) 58%,transparent 68%)}
.floor{position:absolute;left:0;right:0;bottom:0;height:22%;background:radial-gradient(ellipse 60% 60% at 50% 100%,rgba(195,53,53,.45),transparent 70%),linear-gradient(transparent,rgba(30,0,1,.6))}
.bokeh i{position:absolute;border-radius:50%;transform:translate(-50%,-50%);filter:blur(2px)}
.frame{position:absolute;inset:3.2%;border:1px solid rgba(217,198,196,.45)}
.frame:after{content:"";position:absolute;inset:10px;border:1px solid rgba(217,198,196,.18)}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:.5em;padding:10%}
.star{width:var(--star);height:var(--star);filter:drop-shadow(0 0 18px rgba(255,255,255,.55))}
.title{font-family:"Cormorant SC",serif;font-weight:500;text-transform:uppercase;letter-spacing:.1em;line-height:1.1;
  background:linear-gradient(180deg,#fff,#F5EEEC 45%,#D9C6C4);-webkit-background-clip:text;color:transparent}
.label{font-size:var(--label);letter-spacing:.32em;text-transform:uppercase;color:rgba(245,238,236,.62);margin-top:.6em}
.script{font-family:"Great Vibes",cursive;line-height:1.1;padding:0 .35em;background:linear-gradient(180deg,#fff,#F5EEEC 40%,#D9C6C4);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 0 40px rgba(255,220,214,.35))}
.velvet{position:absolute;top:0;bottom:0;background:linear-gradient(180deg,rgba(255,210,200,.07),transparent 28%,rgba(0,0,0,.4)),repeating-linear-gradient(90deg,#3a0102 0,#640405 14px,#94090b 26px,#b0171a 31px,#7d0607 40px,#4a0203 54px,#3a0102 64px);
  -webkit-mask-image:radial-gradient(ellipse 62% 40% at 100% 64%,transparent 98%,#000 100%)}
`;

function stageCard({ w, h, seed, title, label, titleSize }) {
  const m = Math.min(w, h);
  return `<div class="ph stage" style="width:${w}px;height:${h}px;--star:${m * 0.06}px;--label:${m * 0.022}px">
    <div class="bokeh">${bokeh(seed, w, h, 26)}</div><div class="beams"></div><div class="floor"></div><div class="frame"></div>
    <div class="center"><div class="star">${STAR}</div>
      <div class="title" style="font-size:${titleSize || m * 0.075}px">${title}</div>
      <div class="label">${label}</div></div></div>`;
}

const jobs = [];
// Hero: chân dung tách nền -> placeholder monogram trên nền trong suốt
jobs.push({
  file: 'hero.png', w: 1350, h: 1800, transparent: true,
  html: `<div class="ph" style="width:1350px;height:1800px">
    <div class="center" style="justify-content:flex-start;padding-top:22%">
      <div class="script" style="font-size:470px">TV</div>
      <div class="label" style="--label:30px;margin-top:-10px">Portrait · Ảnh chân dung</div></div></div>`
});
jobs.push({
  file: 'greeting.png', w: 1440, h: 1800,
  html: `<div class="ph stage" style="width:1440px;height:1800px;--label:30px">
    <div class="bokeh">${bokeh('greeting', 1440, 1800, 20)}</div><div class="beams"></div><div class="floor"></div>
    <div class="center"><div class="script" style="font-size:450px">TV</div>
      <div class="label">Ảnh chân dung · Portrait</div></div></div>`
});
jobs.push({
  file: 'showreel-poster.png', w: 1800, h: 1013,
  html: `<div class="ph stage" style="width:1800px;height:1013px">
    <div class="bokeh">${bokeh('reel', 1800, 1013, 30)}</div><div class="beams"></div><div class="floor"></div>
    <div class="velvet" style="left:0;width:15%"></div><div class="velvet" style="right:0;width:15%;transform:scaleX(-1)"></div>
    <div class="center" style="justify-content:flex-start;padding-top:7%"><div class="script" style="font-size:96px">MC Thúy Vy</div></div></div>`
});
for (const [id, title] of Object.entries(FIELDS)) {
  jobs.push({ file: `fields/${id}.png`, w: 1440, h: 1800, html: stageCard({ w: 1440, h: 1800, seed: id, title, label: 'Ảnh minh hoạ · Placeholder', titleSize: 118 }) });
  for (let n = 1; n <= 3; n++) {
    const [w, h] = SIZES[(Object.keys(FIELDS).indexOf(id) + n * 2) % SIZES.length];
    jobs.push({ file: `gallery/${id}-${n}.png`, w, h, html: stageCard({ w, h, seed: id + n, title, label: 'Ảnh sự kiện · Placeholder' }) });
  }
}

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const page = await browser.newPage();
  for (const j of jobs) {
    await page.setViewportSize({ width: j.w, height: j.h });
    const tmp = path.join(OUT, '_render.html');
    fs.mkdirSync(OUT, { recursive: true });
    fs.writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_CSS}</style></head><body>${j.html}</body></html>`);
    await page.goto('file://' + tmp, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const file = path.join(OUT, j.file);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    await page.screenshot({ path: file, omitBackground: !!j.transparent, clip: { x: 0, y: 0, width: j.w, height: j.h } });
    console.log('✓', j.file);
  }
  fs.unlinkSync(path.join(OUT, '_render.html'));
  await browser.close();
})();
