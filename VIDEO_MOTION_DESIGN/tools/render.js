// Render frames: node render.js outDir fps start end [workerIdx workers]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, fpsS, aS, bS, wi='0', wn='1'] = process.argv.slice(2);
  const fps=+fpsS, a=+aS, b=+bS, W=+wn, I=+wi;
  const browser = await chromium.launch({args:['--force-color-profile=srgb','--disable-gpu-vsync']});
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errs=[]; page.on('pageerror', e => errs.push(e.message));
  await page.goto('file://' + path.resolve(__dirname, '../composition.html'));
  await page.evaluate(() => window.READY);
  const n0=Math.round(a*fps), n1=Math.round(b*fps);
  for (let f=n0; f<n1; f++) {
    if ((f % W) !== I) continue;
    await page.evaluate(t => window.seek(t), f/fps);
    await page.screenshot({ path: `${out}/${String(f).padStart(5,'0')}.jpg`, type:'jpeg', quality: 96 });
  }
  if (errs.length) console.error('ERRORS:', errs.slice(0,5).join('\n'));
  await browser.close();
})();
