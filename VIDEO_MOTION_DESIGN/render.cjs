#!/usr/bin/env node
/* Rendu image par image de la composition (src/index.html) avec Chromium/Playwright.
   node render.cjs                     → toutes les images (60 i/s) dans build/frames
   node render.cjs --stills 1.5,8.4    → images fixes de contrôle dans build/stills
   Options : --fps 60 --workers 4 --scale 1 --out <dossier> */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > -1 ? process.argv[i + 1] : d; };
const FPS = +arg('fps', 60), WORKERS = +arg('workers', 4), SCALE = +arg('scale', 1);
const STILLS = arg('stills', null);
const OUT = path.resolve(arg('out', path.join(__dirname, 'build', STILLS ? 'stills' : 'frames')));
const URL = 'file://' + path.join(__dirname, 'src', 'index.html') + '?render';

async function openPage(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: SCALE });
  const page = await ctx.newPage();
  page.on('pageerror', e => { console.error('ERREUR PAGE:', e.message); process.exitCode = 1; });
  await page.goto(URL);
  await page.evaluate(() => window.__ready);
  return page;
}
const shot = async (page, t, file) => {
  await page.evaluate(t => new Promise(r => { window.__seek(t); requestAnimationFrame(() => requestAnimationFrame(r)); }), t);
  await page.screenshot({ path: file, type: STILLS ? 'jpeg' : 'png', quality: STILLS ? 88 : undefined });
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  if (STILLS) {
    const page = await openPage(browser);
    for (const s of STILLS.split(',')) {
      const t = parseFloat(s);
      await shot(page, t, path.join(OUT, `t${t.toFixed(2).padStart(5, '0')}.jpg`));
    }
  } else {
    const dur = await (await openPage(browser)).evaluate(() => window.__dur);
    const total = Math.round(dur * FPS);
    let next = 0, done = 0; const t0 = Date.now();
    await Promise.all(Array.from({ length: WORKERS }, async () => {
      const page = await openPage(browser);
      for (;;) {
        const i = next++; if (i >= total) break;
        await shot(page, i / FPS, path.join(OUT, String(i).padStart(5, '0') + '.png'));
        if (++done % 200 === 0) console.log(`${done}/${total} images · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
      }
    }));
    console.log(`${total} images rendues en ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  await browser.close();
})();
