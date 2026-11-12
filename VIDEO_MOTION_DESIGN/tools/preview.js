// Usage: node preview.js out_dir t1 t2 ...
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, ...ts] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs=[]; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  await page.goto('file://' + path.resolve(__dirname, '../composition.html'));
  await page.evaluate(() => window.READY);
  for (const t of ts) {
    await page.evaluate(t => window.seek(t), parseFloat(t));
    await page.screenshot({ path: `${out}/f_${String(t).padStart(5,'0')}.png` });
  }
  if (errs.length) console.log('ERRORS:', errs.join('\n'));
  await browser.close();
})();
