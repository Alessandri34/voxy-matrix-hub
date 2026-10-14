#!/usr/bin/env node
/**
 * Genere un site statique a vraies URL depuis site.html.
 * Chaque page obtient son titre, sa description, son canonical et son
 * balisage Schema.org. CSS et JS sont extraits en fichiers partages.
 */
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';

const RACINE = 'https://vformations.fr';
const SORTIE = 'dist';
const src = readFileSync('site.html', 'utf8');
const pages = JSON.parse(readFileSync('pages.json', 'utf8'));
const seo = JSON.parse(readFileSync('seo.json', 'utf8'));
// Jetons de verification de propriete : des meta-balises publiques, posees
// sur toutes les pages pour que la verification tienne quelle que soit
// l'URL que le moteur choisit de controler.
const verif = [
  seo.googleSiteVerification && `<meta name="google-site-verification" content="${seo.googleSiteVerification}">`,
  seo.bingSiteVerification && `<meta name="msvalidate.01" content="${seo.bingSiteVerification}">`,
].filter(Boolean).join('\n');
const parSlug = new Map(pages.map(p => [p[0], p]));
const urlDe = slug => {
  const p = parSlug.get(slug);
  return p ? '/' + p[1] : '/';
};

// ── Extraction des blocs communs ─────────────────────────────────────────
const prendre = (re, nom) => {
  const m = src.match(re);
  if (!m) { throw new Error('Bloc introuvable : ' + nom); }
  return m[1];
};
const css     = prendre(/<style>([\s\S]*?)<\/style>/, 'style');
const header  = prendre(/(<header class="header">[\s\S]*?<\/header>)/, 'header');
const footer  = prendre(/(<footer class="footer">[\s\S]*?<\/footer>)/, 'footer');
const cmp     = prendre(/(<div class="cmp" id="cmp"[\s\S]*?\n<\/div>)/, 'bandeau cookies');
let js        = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];

// Le routeur doit partir de la page declaree par le serveur, pas du fragment.
const routeurAvant = `    var h = (location.hash || '#accueil').replace('#','');
    if (PAGES.indexOf(h) === -1) h = 'accueil';`;
const routeurApres = `    var declaree = document.documentElement.getAttribute('data-page');
    var h = (location.hash || '').replace('#','');
    // Un lien deja partage sous la forme /#slug designe une page qui a
    // maintenant sa propre URL : on y renvoie plutot que d'afficher
    // l'accueil sans rien dire. replace() evite de polluer l'historique.
    if (h && URLS[h] && !document.querySelector('[data-page="' + h + '"]')) {
      location.replace(URLS[h]);
      return;
    }
    if (!h || PAGES.indexOf(h) === -1) h = declaree || 'accueil';
    if (!document.querySelector('[data-page="' + h + '"]')) return;`;
if (!js.includes(routeurAvant)) { throw new Error('Routeur : motif non trouve'); }
js = js.replace(routeurAvant, routeurApres);
// Un fragment interne ne doit plus declencher un changement de page.
js = js.replace("window.addEventListener('hashchange', route);",
  "window.addEventListener('hashchange', function(){ var h=(location.hash||'').replace('#',''); if (PAGES.indexOf(h)!==-1) route(); });");
// Table des URL reelles, lue par le routeur pour rediriger les anciens liens.
js = 'var URLS = ' + JSON.stringify(Object.fromEntries(pages.map(p => [p[0], '/' + p[1]]))) + ';\n' + js;

// ── Reecriture des liens et des chemins ──────────────────────────────────
function reecrire(html) {
  return html
    .replace(/href="#([a-z0-9-]+)"/g, (m, slug) =>
      parSlug.has(slug) ? `href="${urlDe(slug)}"` : m)
    .replace(/src="img\//g, 'src="/img/')
    .replace(/href="img\//g, 'href="/img/');
}

// ── Schema.org ───────────────────────────────────────────────────────────
const ORGANISME = {
  '@type': 'EducationalOrganization',
  '@id': RACINE + '/#organisme',
  name: 'VFormations',
  legalName: 'VFORMATIONS',
  url: RACINE,
  logo: RACINE + '/img/logo-vformations-blue.png',
  email: 'contact@vformations.fr',
  telephone: '+33763678292',
  address: { '@type': 'PostalAddress', streetAddress: '47 rue Vivienne',
             postalCode: '75002', addressLocality: 'Paris', addressCountry: 'FR' },
  areaServed: { '@type': 'AdministrativeArea', name: 'Hérault' },
  identifier: [
    { '@type': 'PropertyValue', name: 'SIRET', value: '10394022700012' },
    { '@type': 'PropertyValue', name: 'Déclaration d’activité', value: '11757618175' },
    { '@type': 'PropertyValue', name: 'Qualiopi', value: 'VFO12912026001' }
  ]
};

function schema(slug, url, titre, desc, type) {
  const absolu = RACINE + url;
  const fil = [{ '@type': 'ListItem', position: 1, name: 'Accueil', item: RACINE + '/' }];
  const seg = url.replace(/^\/|\/$/g, '').split('/').filter(Boolean);
  seg.forEach((_, i) => {
    const bout = '/' + seg.slice(0, i + 1).join('/') + '/';
    const p = pages.find(x => '/' + x[1] === bout);
    fil.push({ '@type': 'ListItem', position: i + 2,
               name: p ? p[2] : seg[i], item: RACINE + bout });
  });

  const blocs = [];
  if (slug === 'accueil') {
    blocs.push(ORGANISME,
      { '@type': 'WebSite', '@id': RACINE + '/#site', url: RACINE,
        name: 'VFormations', inLanguage: 'fr-FR',
        publisher: { '@id': RACINE + '/#organisme' } });
  } else {
    blocs.push({ '@type': 'WebPage', '@id': absolu + '#page', url: absolu,
                 name: titre, description: desc, inLanguage: 'fr-FR',
                 isPartOf: { '@id': RACINE + '/#site' },
                 publisher: { '@id': RACINE + '/#organisme' } });
  }
  if (type === 'formation') {
    blocs.push({ '@type': 'Course', name: titre, description: desc, url: absolu,
      inLanguage: 'fr-FR',
      provider: { '@id': RACINE + '/#organisme' },
      hasCourseInstance: { '@type': 'CourseInstance',
        courseMode: 'onsite', courseWorkload: 'PT35H',
        location: { '@type': 'Place', address: {
          '@type': 'PostalAddress', addressRegion: 'Hérault', addressCountry: 'FR' } } } });
  }
  if (type === 'article') {
    blocs.push({ '@type': 'BlogPosting', headline: titre, description: desc,
      url: absolu, inLanguage: 'fr-FR',
      image: RACINE + '/img/logo-vformations-blue.png',
      author: { '@id': RACINE + '/#organisme' },
      publisher: { '@id': RACINE + '/#organisme' },
      mainEntityOfPage: { '@type': 'WebPage', '@id': absolu } });
  }
  if (type === 'contact') {
    blocs.push({ '@type': 'ContactPage', url: absolu,
                 mainEntity: { '@id': RACINE + '/#organisme' } });
  }
  blocs.push({ '@type': 'BreadcrumbList', itemListElement: fil });
  return JSON.stringify({ '@context': 'https://schema.org', '@graph': blocs });
}

// ── Generation ───────────────────────────────────────────────────────────
rmSync(SORTIE, { recursive: true, force: true });
mkdirSync(join(SORTIE, 'assets'), { recursive: true });
writeFileSync(join(SORTIE, 'assets/style.css'), css);
writeFileSync(join(SORTIE, 'assets/app.js'), js);

const headerR = reecrire(header), footerR = reecrire(footer), cmpR = reecrire(cmp);
let total = 0;

for (const [slug, chemin, titre, desc, type] of pages) {
  const re = new RegExp(`<section class="page" data-page="${slug}"[^>]*>([\\s\\S]*?)\\n</section>\\n`, 'm');
  const m = src.match(re);
  if (!m) { throw new Error('Section introuvable : ' + slug); }
  const corps = reecrire(`<section class="page" data-page="${slug}">${m[1]}\n</section>`);
  const url = '/' + chemin;
  const titreComplet = titre + ' | VFormations';

  const html = `<!DOCTYPE html>
<html lang="fr" data-page="${slug}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${titreComplet}</title>
<meta name="description" content="${desc}">
<link rel="canonical" href="${RACINE}${url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="${type === 'article' ? 'article' : 'website'}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="VFormations">
<meta property="og:title" content="${titreComplet}">
<meta property="og:description" content="${desc}">
<meta property="og:url" content="${RACINE}${url}">
<meta property="og:image" content="${RACINE}/img/logo-vformations-blue.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1A3C86">
${verif}
<link rel="icon" href="/img/logo-mark-blue.png">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">${schema(slug, url, titre, desc, type)}</script>
</head>
<body>
${headerR}
<main>
${corps}
</main>
${footerR}
${cmpR}
<script src="/assets/app.js" defer></script>
</body>
</html>`;

  const dest = join(SORTIE, chemin, 'index.html');
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, html);
  total++;
}

// ── Ressources ───────────────────────────────────────────────────────────
cpSync('img', join(SORTIE, 'img'), { recursive: true });
if (existsSync('api/contact.php')) { cpSync('api/contact.php', join(SORTIE, 'contact.php')); }

// Cle IndexNow : servie a la racine en text/plain, corps egal a la cle.
// C'est ce fichier qui prouve aux moteurs que les URL soumises sont bien
// les notres. Il est public par construction.
writeFileSync(join(SORTIE, seo.indexnowKey + '.txt'), seo.indexnowKey);

// ── sitemap.xml ──────────────────────────────────────────────────────────
const aujourdhui = new Date().toISOString().slice(0, 10);
const priorite = t => ({ accueil: '1.0', formation: '0.9', liste: '0.8',
                         local: '0.8', article: '0.7', contact: '0.7',
                         page: '0.6', legal: '0.3' }[t] || '0.5');
writeFileSync(join(SORTIE, 'sitemap.xml'),
`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(([s, c, , , t]) =>
`  <url>
    <loc>${RACINE}/${c}</loc>
    <lastmod>${aujourdhui}</lastmod>
    <changefreq>${t === 'article' || t === 'legal' ? 'monthly' : 'weekly'}</changefreq>
    <priority>${priorite(t)}</priority>
  </url>`).join('\n')}
</urlset>
`);

// ── robots.txt ───────────────────────────────────────────────────────────
writeFileSync(join(SORTIE, 'robots.txt'),
`User-agent: *
Allow: /
Disallow: /contact.php

Sitemap: ${RACINE}/sitemap.xml
`);

console.log(`${total} pages generees dans ${SORTIE}/`);
console.log(`  style.css ${(css.length / 1024).toFixed(0)} Ko · app.js ${(js.length / 1024).toFixed(0)} Ko`);
console.log('  sitemap.xml et robots.txt ecrits');
