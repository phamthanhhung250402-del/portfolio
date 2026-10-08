/* Tạo ảnh chia sẻ og-image.jpg (1200x630) + favicon PNG từ ảnh hero hiện tại.
 * Chạy lại sau khi thay ảnh hero:
 *   NODE_PATH=$(npm root -g) node tools/render_brand.cjs
 * (cần Node + Playwright: npm i -g playwright && npx playwright install chromium)
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const TMP = path.join(ROOT, '_brand-render.html');

const OG = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="css/fonts.css">
<style>
*{box-sizing:border-box}html,body{margin:0}
.og{position:relative;width:1200px;height:630px;overflow:hidden;color:#F5EEEC;font-family:"Be Vietnam Pro",sans-serif;
  background:radial-gradient(ellipse 50% 60% at 70% 40%,rgba(195,53,53,.55),transparent 70%),radial-gradient(ellipse 90% 90% at 60% 30%,#800606 0%,#5F0203 45%,#2D0102 90%)}
.beam{position:absolute;inset:0;background:linear-gradient(100deg,transparent 50%,rgba(255,230,222,.07) 62%,transparent 72%)}
.velvet{position:absolute;top:0;bottom:0;width:70px;background:linear-gradient(180deg,rgba(255,210,200,.07),transparent 28%,rgba(0,0,0,.4)),repeating-linear-gradient(90deg,#3a0102 0,#640405 10px,#94090b 18px,#b0171a 21px,#7d0607 27px,#4a0203 36px,#3a0102 42px);
  -webkit-mask-image:radial-gradient(ellipse 62% 40% at 100% 64%,transparent 98%,#000 100%)}
.text{position:absolute;left:120px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center}
.eyebrow{font-size:15px;letter-spacing:.34em;text-transform:uppercase;color:#D9C6C4;display:flex;align-items:center;gap:14px}
.eyebrow:after{content:"";width:48px;height:1px;background:#D9C6C4;opacity:.6}
.mc{font-family:"Cormorant SC",serif;font-weight:500;font-size:30px;letter-spacing:.5em;color:#D9C6C4;margin-top:26px}
.name{font-family:"Cormorant SC",serif;font-weight:500;font-size:112px;line-height:1.02;letter-spacing:.05em;text-transform:uppercase;
  background:linear-gradient(180deg,#fff,#F5EEEC 45%,#D9C6C4);-webkit-background-clip:text;color:transparent;padding-top:8px}
.full{font-family:"Cormorant Garamond",serif;font-style:italic;font-size:30px;color:rgba(245,238,236,.85);margin-top:4px}
.sub{margin-top:26px;font-size:15px;letter-spacing:.24em;text-transform:uppercase;color:#D9C6C4}
.tag{margin-top:8px;font-family:"Cormorant Garamond",serif;font-style:italic;font-size:28px}
.arch{position:absolute;right:120px;top:62px;bottom:0;width:340px;border:1px solid rgba(217,198,196,.7);border-bottom:0;border-radius:999px 999px 0 0;padding:9px 9px 0}
.arch .in{height:100%;border-radius:999px 999px 0 0;overflow:hidden;background:radial-gradient(ellipse 60% 45% at 50% 28%,rgba(255,196,186,.28),transparent 70%),radial-gradient(ellipse 80% 70% at 50% 35%,#a51416,#800606 45%,#3c0102)}
.arch img{width:100%;height:100%;object-fit:cover;object-position:50% 0}
.star{position:absolute;right:281px;top:50px;width:24px;height:24px;filter:drop-shadow(0 0 8px rgba(255,255,255,.7))}
</style></head><body>
<div class="og"><div class="beam"></div>
<div class="velvet" style="left:0"></div><div class="velvet" style="right:0;transform:scaleX(-1)"></div>
<div class="text"><div class="eyebrow">Master of Ceremonies</div><div class="mc">MC</div><div class="name">Thúy Vy</div>
<div class="full">Nguyễn Ngọc Thúy Vy</div><div class="sub">MC sự kiện · Song ngữ · Không kịch bản</div>
<div class="tag">Đa sắc - Chuyên nghiệp - Chân thành</div></div>
<div class="arch"><div class="in"><img src="assets/img/hero.webp" alt=""></div></div>
<svg class="star" viewBox="0 0 24 24"><path fill="#F5EEEC" d="M12 0c.9 7.4 4.6 11.1 12 12-7.4.9-11.1 4.6-12 12-.9-7.4-4.6-11.1-12-12C7.4 11.1 11.1 7.4 12 0Z"/></svg>
</div></body></html>`;

const ICON = (size, rounded) => `<!doctype html><html><head><style>html,body{margin:0;background:transparent}
img{width:${size}px;height:${size}px;display:block${rounded ? '' : ';clip-path:inset(0)'}}</style></head>
<body>${rounded ? '<img src="assets/icons/favicon.svg">' : `<div style="width:${size}px;height:${size}px;background:#2D0102"><img src="assets/icons/favicon.svg" style="transform:scale(1.28)"></div>`}</body></html>`;

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const page = await browser.newPage();
  async function shot(html, w, h, out, opts) {
    fs.writeFileSync(TMP, html);
    await page.setViewportSize({ width: w, height: h });
    await page.goto('file://' + TMP, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot(Object.assign({ path: path.join(ROOT, out), clip: { x: 0, y: 0, width: w, height: h } }, opts));
    console.log('✓', out);
  }
  await shot(OG, 1200, 630, 'assets/og-image.jpg', { type: 'jpeg', quality: 86 });
  await shot(ICON(32, true), 32, 32, 'assets/icons/favicon-32.png', { omitBackground: true });
  await shot(ICON(180, false), 180, 180, 'assets/icons/apple-touch-icon.png', {});
  await shot(ICON(192, false), 192, 192, 'assets/icons/icon-192.png', {});
  await shot(ICON(512, false), 512, 512, 'assets/icons/icon-512.png', {});
  fs.unlinkSync(TMP);
  await browser.close();
})();
