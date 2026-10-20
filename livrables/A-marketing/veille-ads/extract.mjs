import pw from '/opt/node-tools/node_modules/playwright/index.js';
import fs from 'fs';
const { chromium } = pw;
const d = '/tmp/claude-0/-home-user-voxy-matrix-hub/b4f24b7f-2364-5f62-b5c3-7e02e8dca431/scratchpad/ads';
const CIBLES = [
  ['122097448364017483', 'Youdji'],
  ['1146053731933464', "L'agence Paid"],
  ['513744841823424', "L'agence Short"],
];

const b = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--disable-blink-features=AutomationControlled','--no-sandbox']
});
const ctx = await b.newContext({
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  locale: 'fr-FR', timezoneId: 'Europe/Paris', viewport: { width: 1440, height: 1000 }
});
await ctx.addInitScript(() => {
  Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
  Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});
});

const tout = {};
for (const [id, nom] of CIBLES) {
  const p = await ctx.newPage();
  await p.goto(`https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&media_type=all&search_type=page&view_all_page_id=${id}`,
    { waitUntil:'domcontentloaded', timeout:60000 });
  await p.waitForTimeout(11000);

  // Charger toute la liste : la bibliotheque pagine au defilement.
  let avant = 0;
  for (let i = 0; i < 14; i++) {
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await p.waitForTimeout(2200);
    const n = await p.evaluate(() =>
      (document.body.innerText.match(/ID dans la bibliothèque/g) || []).length);
    if (n === avant && i > 2) break;
    avant = n;
  }

  // On repart du texte de la page : le DOM de Meta est obfusque, mais le
  // texte rendu porte toute l'information publique de chaque annonce.
  const brut = await p.evaluate(() => document.body.innerText);
  fs.writeFileSync(`${d}/texte-${id}.txt`, brut);
  // Les liens de destination ne sont pas dans le texte : on les prend du DOM.
  const liens = await p.evaluate(() => [...new Set(
    [...document.querySelectorAll('a[href*="l.facebook.com"], a[href^="http"]')]
      .map(a => a.href)
      .filter(h => !/facebook\.com\/(ads|business|help|policies|privacy|legal)/.test(h))
      .filter(h => !/^https:\/\/(www\.)?facebook\.com\/?$/.test(h))
  )].slice(0, 60));
  fs.writeFileSync(`${d}/liens-${id}.json`, JSON.stringify(liens, null, 1));

  const n = (brut.match(/ID dans la bibliothèque/g) || []).length;
  const annonce = (brut.match(/(\d+)\s+résultats?/) || [])[1];
  console.log(`${nom.padEnd(16)} annoncé ${annonce} · extrait ${n} · ${brut.length} o · ${liens.length} liens`);
  tout[nom] = { id, annonce: Number(annonce), extrait: n };
  await p.close();
}
fs.writeFileSync(`${d}/resume.json`, JSON.stringify(tout, null, 1));
await b.close();
