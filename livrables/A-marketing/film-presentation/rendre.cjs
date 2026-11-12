/* Rend le film image par image, puis l'encode.

   node rendre.cjs                 film complet -> sortie/film-muet.mp4
   node rendre.cjs --apercu        images fixes a des instants choisis -> sortie/apercu/
   node rendre.cjs --apercu 3.4,12 instants a la demande
   node rendre.cjs --de 12 --a 16  un extrait seulement

   Pourquoi image par image : une capture d'ecran en temps reel saute des
   images des que la machine peine, et deux rendus ne donnent jamais le meme
   fichier. Ici le navigateur ne « joue » rien : on lui demande l'image de
   la seconde t, on l'attend, on la prend. Le resultat est le meme partout.

   Le rendu est decoupe en troncons confies a plusieurs onglets, chacun
   relie a son propre encodeur : les troncons sont ensuite recolles sans
   reencodage. Aucune image n'est ecrite sur le disque. */

const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }

const ICI = __dirname;
const SORTIE = path.join(ICI, "sortie");
const arg = (nom, defaut) => {
  const i = process.argv.indexOf("--" + nom);
  return i < 0 ? defaut : process.argv[i + 1];
};
// Deux formats, une composition : --format vertical rend en 1080 x 1920.
const FORMAT = arg("format", "paysage");
if (!["paysage", "vertical"].includes(FORMAT)) { console.error("format inconnu : " + FORMAT); process.exit(1); }
const VERTICAL = FORMAT === "vertical";
const TAILLE = VERTICAL ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
const SUFFIXE = VERTICAL ? "-vertical" : "";
const PAGE = "file://" + path.join(ICI, "film.html") + "?rendu" + (VERTICAL ? "&format=vertical" : "");

async function ouvrir(navigateur) {
  const contexte = await navigateur.newContext({ viewport: TAILLE, deviceScaleFactor: 1 });
  const page = await contexte.newPage();
  const erreurs = [];
  page.on("pageerror", (e) => erreurs.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") erreurs.push(m.text()); });
  await page.goto(PAGE, { waitUntil: "load" });
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode().catch(() => { throw new Error("image illisible : " + i.src); })));
  });
  if (erreurs.length) throw new Error("La composition a des erreurs :\n  " + erreurs.join("\n  "));
  // La police fait le style : si elle manque, le navigateur en met une autre sans rien dire.
  const police = await page.evaluate(() => document.fonts.check('600 100px "Inter Display"'));
  if (!police) throw new Error('La police « Inter Display » est absente de cette machine (https://rsms.me/inter/).');
  return page;
}

async function capturer(page, client, t, format = "png") {
  await page.evaluate((t) => window.FILM.aller(t), t);
  const { data } = await client.send("Page.captureScreenshot",
    format === "png" ? { format: "png", optimizeForSpeed: true } : { format: "jpeg", quality: 90 });
  return Buffer.from(data, "base64");
}

(async () => {
  fs.mkdirSync(SORTIE, { recursive: true });
  const navigateur = await chromium.launch({
    // Sans indication de trame, le texte se place au sous-pixel : un titre
    // qui glisse lentement ne tremble plus d'une image a l'autre.
    args: ["--font-render-hinting=none", "--disable-lcd-text", "--force-color-profile=srgb", "--hide-scrollbars"],
  });
  const premiere = await ouvrir(navigateur);
  const { duree, ips, reperes } = await premiere.evaluate(() => ({ duree: FILM.duree, ips: FILM.ips, reperes: FILM.reperes }));
  // Les reperes sonores sortent de la composition : le son se cale sur l'image, jamais l'inverse.
  const contenu = JSON.stringify({ duree, cadence: 120, reperes: reperes.sort((a, b) => a.t - b.t) }, null, 1) + "\n";
  const chemin = path.join(ICI, "reperes.json");
  if (VERTICAL) {
    // Le son est commun aux deux formats : le vertical ne doit pas deplacer un seul repere.
    if (fs.existsSync(chemin) && fs.readFileSync(chemin, "utf8") !== contenu)
      throw new Error("Le format vertical produit des reperes sonores differents du paysage : les deux films ne partageraient plus le meme son.");
  } else fs.writeFileSync(chemin, contenu);

  if (process.argv.includes("--apercu")) {
    const dossier = path.join(SORTIE, "apercu" + SUFFIXE);
    fs.rmSync(dossier, { recursive: true, force: true });
    fs.mkdirSync(dossier, { recursive: true });
    const demande = arg("apercu", "");
    const instants = /^[\d.,]+$/.test(demande || "")
      ? demande.split(",").map(Number)
      : [1.3, 2.4, 3.8, 5.6, 6.9, 8.4, 9.5, 10.5, 11.5, 12.4, 13.9, 15.2, 17.6, 19.4, 21.8, 23.4, 26.2, 27.6, 30.2, 31.4, 33.6, 36.4, 39.2, 41.2, 43.4, 45.4, 47.2, 49.2, 50.6, 52.6];
    const client = await premiere.context().newCDPSession(premiere);
    for (const t of instants) {
      fs.writeFileSync(path.join(dossier, `t${t.toFixed(2).padStart(5, "0")}.jpg`), await capturer(premiere, client, t, "jpeg"));
    }
    console.log(`${instants.length} images dans ${dossier}`);
    await navigateur.close();
    return;
  }

  const de = Math.round(+arg("de", 0) * ips), a = Math.round(+arg("a", duree) * ips);
  const total = a - de;
  const ouvriers = Math.max(1, Math.min(+arg("ouvriers", os.cpus().length), 6));
  const part = Math.ceil(total / ouvriers);
  const qualite = arg("crf", "16");
  const debut = Date.now();
  let faites = 0;

  const troncons = await Promise.all(Array.from({ length: ouvriers }, async (_, n) => {
    const i0 = de + n * part, i1 = Math.min(a, i0 + part);
    if (i0 >= i1) return null;
    const fichier = path.join(SORTIE, `troncon${SUFFIXE}-${n}.mp4`);
    const encodeur = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-c:v", "png", "-framerate", String(ips), "-i", "-",
      "-c:v", "libx264", "-preset", "slow", "-crf", qualite, "-pix_fmt", "yuv420p", "-profile:v", "high",
      "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
      "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709", "-g", String(ips * 2), "-r", String(ips), fichier], { stdio: ["pipe", "inherit", "inherit"] });
    const fini = new Promise((ok, ko) => encodeur.on("close", (c) => (c === 0 ? ok() : ko(new Error("ffmpeg a echoue sur le troncon " + n)))));
    const page = n === 0 ? premiere : await ouvrir(navigateur);
    const client = await page.context().newCDPSession(page);
    for (let i = i0; i < i1; i++) {
      const image = await capturer(page, client, i / ips);
      if (!encodeur.stdin.write(image)) await new Promise((r) => encodeur.stdin.once("drain", r));
      if (++faites % 240 === 0) {
        const s = (Date.now() - debut) / 1000;
        console.log(`  ${faites}/${total} images · ${(faites / s).toFixed(1)} images/s · reste ${Math.round((total - faites) / (faites / s))} s`);
      }
    }
    encodeur.stdin.end();
    await fini;
    return fichier;
  }));
  await navigateur.close();

  const liste = path.join(SORTIE, `troncons${SUFFIXE}.txt`);
  const presents = troncons.filter(Boolean);
  fs.writeFileSync(liste, presents.map((f) => `file '${f}'`).join("\n") + "\n");
  const muet = path.join(SORTIE, `film-muet${SUFFIXE}.mp4`);
  const colle = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", liste, "-c", "copy", "-movflags", "+faststart", muet], { stdio: "inherit" });
  if (colle.status !== 0) throw new Error("le recollage des troncons a echoue");
  for (const f of [...presents, liste]) fs.rmSync(f);
  console.log(`${total} images en ${Math.round((Date.now() - debut) / 1000)} s -> ${muet}`);
})().catch((e) => { console.error(e.message || e); process.exit(1); });
