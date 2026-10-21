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
// Identifiant du pixel Meta. Il n'est pas secret — il figure dans le code de
// n'importe quel site qui en porte un — mais il vaut mieux le tenir avec les
// autres reglages que perdu dans site.html. Le pixel ne se charge de toute
// facon qu'apres consentement publicitaire.
js = js.replace('__META_PIXEL_ID__', (seo.metaPixelId || '').replace(/[^0-9]/g, ''));

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
// Index de recherche : [url, titre, description, rubrique] pour chaque page.
// Les titres sont ceux de pages.json, sans le suffixe de marque.
// La rubrique affichee dans les suggestions vient d'abord des metadonnees de
// carte, sinon du premier segment d'URL — plus fiable que le type, qui range
// le catalogue et le Mag sous la meme etiquette « liste ».
const RUBRIQUE_SEGMENT = { '': 'Accueil', formations: 'Formations', mag: 'Le Mag',
  'formations-herault': 'Près de chez vous' };
const RUBRIQUE_TYPE = { contact: 'Contact', legal: 'Informations légales' };
const rubrique = ([slug, chemin, , , type, carte]) =>
  (carte && carte.tag) || RUBRIQUE_SEGMENT[chemin.split('/')[0]] || RUBRIQUE_TYPE[type] || 'Page';
js = 'var RECHERCHE = ' + JSON.stringify(pages.map(p =>
  ['/' + p[1], p[2], p[3], rubrique(p)])) + ';\n' + js;

// Table des URL reelles, lue par le routeur pour rediriger les anciens liens.
js = 'var URLS = ' + JSON.stringify(Object.fromEntries(pages.map(p => [p[0], '/' + p[1]]))) + ';\n' + js;

// Grilles d'articles. Elles etaient codees en dur dans site.html : chaque
// nouvel article obligeait a les modifier, et la grille de l'accueil avait
// fini par ne plus montrer que d'anciens articles. Elles sont desormais
// derivees de pages.json, ou l'ordre des articles fait foi.
const articles = pages.filter(p => p[4] === 'article');
function carteArticle([slug, chemin, titre, desc, type, c]) {
  const m = c || {};
  return `      <a class="ncard" href="#${slug}">` +
    `<img class="cover" src="img/${m.img || 'logo-vformations-blue.png'}" alt="${(m.carte || titre).replace(/"/g, '&quot;')}" loading="lazy">` +
    `<div class="nbody"><span class="ntag">${m.tag || 'Article'}</span>` +
    `<h3>${m.carte || titre}</h3></div></a>`;
}
const grilleCartes = liste => liste.map(carteArticle).join('\n');
function grilleArticles(combien) {
  return grilleCartes(combien ? articles.slice(0, combien) : articles);
}
// Rangees par rubrique, pour la page Le Mag. Trente-six articles dans une
// seule grille font une page qu'on parcourt au pouce sans jamais trouver :
// on les groupe par rubrique, chaque rubrique defilant horizontalement, et
// les puces du haut masquent les rubriques non retenues. Sans JavaScript,
// toutes les rubriques restent visibles : aucun article n'est perdu.
const CHEV_G = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg>';
const CHEV_D = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg>';
const cleRubrique = t => t.toLowerCase().normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function railsParRubrique() {
  const groupes = new Map();
  for (const a of articles) {
    const tag = (a[5] && a[5].tag) || 'Article';
    if (!groupes.has(tag)) { groupes.set(tag, []); }
    groupes.get(tag).push(a);
  }
  // Les rubriques les mieux fournies en premier : ce qu'on publie le plus
  // est ce qu'on sait le mieux faire, autant le montrer en haut.
  const ordre = [...groupes.entries()].sort((a, b) => b[1].length - a[1].length);

  const puces = '<div class="filters" id="magfilters">\n'
    + '        <button class="chip active" type="button" data-f="all">Tout voir</button>\n'
    + ordre.map(([t, l]) => `        <button class="chip" type="button" data-f="${cleRubrique(t)}">`
        + `${t}<span class="chip-n">${l.length}</span></button>`).join('\n')
    + '\n      </div>';

  const sections = ordre.map(([t, l]) => {
    const n = l.length;
    return `      <section class="magrub" data-rub="${cleRubrique(t)}">
        <div class="rub-head"><h2>${t}</h2><span class="rub-n">${n} article${n > 1 ? 's' : ''}</span></div>
        <div class="railwrap">
          <button class="railnav prev" type="button" aria-label="Articles précédents">${CHEV_G}</button>
          <div class="rail-h">
${grilleCartes(l)}
          </div>
          <button class="railnav next" type="button" aria-label="Articles suivants">${CHEV_D}</button>
        </div>
      </section>`;
  }).join('\n');

  return puces + '\n' + sections + '\n      <p class="magvide" hidden>Aucun article dans cette rubrique.</p>';
}

// Dans site.html, une grille s'ecrit <div class="news" data-auto="3"></div>
// (les 3 plus recents) ou data-auto="tous" ; data-rail="m" la fait defiler
// horizontalement sur mobile. <div data-auto="mag"></div> pose les rangees
// par rubrique de la page Le Mag.
function poserGrilles(html) {
  html = html.replace(/<div data-auto="mag"><\/div>/g, () => railsParRubrique());
  return html.replace(/<div class="news"([^>]*)><\/div>/g, (bloc, attrs) => {
    const auto = /data-auto="([^"]+)"/.exec(attrs);
    if (!auto) { return bloc; }
    const n = auto[1] === 'tous' ? 0 : parseInt(auto[1], 10);
    const rail = /data-rail="m"/.test(attrs) ? ' rail-h rail-m' : '';
    return `<div class="news${rail}">\n${grilleArticles(n)}\n      </div>`;
  });
}

js += '\n/* ── Recherche ──────────────────────────────────────────────────────────\n   Les deux formulaires (en-tete et hero) ignoraient la saisie et renvoyaient\n   au catalogue quoi qu\'on tape. Ils interrogent maintenant un index des\n   pages du site, construit au moment de la generation.\n   Sans JavaScript, le formulaire renvoie au catalogue : le comportement\n   d\'avant, qui reste un repli acceptable.                                */\n(function () {\n  if (typeof RECHERCHE === \'undefined\') { return; }\n\n  // Le francais impose de comparer sans accents : « video » doit trouver\n  // « vidéo », « herault » doit trouver « Hérault ».\n  function plat(t) {\n    return (t || \'\').toLowerCase().normalize(\'NFD\').replace(/[̀-ͯ]/g, \'\');\n  }\n\n  var index = RECHERCHE.map(function (p) {\n    return { url: p[0], titre: p[1], desc: p[2], tag: p[3],\n             cle: plat(p[1] + \' \' + p[2] + \' \' + p[3]) };\n  });\n\n  function chercher(q) {\n    var mots = plat(q).split(/\\s+/).filter(Boolean);\n    if (!mots.length) { return []; }\n    var out = [];\n    for (var i = 0; i < index.length; i++) {\n      var p = index[i], t = plat(p.titre), score = 0, tous = true;\n      for (var m = 0; m < mots.length; m++) {\n        if (p.cle.indexOf(mots[m]) === -1) { tous = false; break; }\n        // un mot en tete de titre pese plus qu\'un mot perdu dans la description\n        if (t.indexOf(mots[m]) === 0) { score += 4; }\n        else if (t.indexOf(mots[m]) !== -1) { score += 2; }\n        else { score += 1; }\n      }\n      if (tous) { out.push({ p: p, score: score }); }\n    }\n    out.sort(function (a, b) { return b.score - a.score; });\n    return out.slice(0, 6).map(function (r) { return r.p; });\n  }\n\n  function surligner(texte, q) {\n    var mots = plat(q).split(/\\s+/).filter(Boolean), tp = plat(texte), marques = [];\n    mots.forEach(function (m) {\n      var i = tp.indexOf(m);\n      while (i !== -1) { marques.push([i, i + m.length]); i = tp.indexOf(m, i + m.length); }\n    });\n    if (!marques.length) { return document.createTextNode(texte); }\n    marques.sort(function (a, b) { return a[0] - b[0]; });\n    var frag = document.createDocumentFragment(), pos = 0;\n    marques.forEach(function (z) {\n      if (z[0] < pos) { return; }\n      frag.appendChild(document.createTextNode(texte.slice(pos, z[0])));\n      var b = document.createElement(\'b\');\n      b.textContent = texte.slice(z[0], z[1]);\n      frag.appendChild(b);\n      pos = z[1];\n    });\n    frag.appendChild(document.createTextNode(texte.slice(pos)));\n    return frag;\n  }\n\n  document.querySelectorAll(\'form[data-recherche]\').forEach(function (form, n) {\n    var champ = form.querySelector(\'input[type="text"]\');\n    if (!champ) { return; }\n\n    var panneau = document.createElement(\'div\');\n    panneau.className = \'rsug\';\n    panneau.id = \'rsug-\' + n;\n    panneau.setAttribute(\'role\', \'listbox\');\n    panneau.hidden = true;\n    form.appendChild(panneau);\n\n    champ.setAttribute(\'role\', \'combobox\');\n    champ.setAttribute(\'aria-autocomplete\', \'list\');\n    champ.setAttribute(\'aria-expanded\', \'false\');\n    champ.setAttribute(\'aria-controls\', panneau.id);\n\n    var resultats = [], actif = -1;\n\n    function fermer() {\n      panneau.hidden = true;\n      champ.setAttribute(\'aria-expanded\', \'false\');\n      actif = -1;\n    }\n\n    function marquerActif() {\n      [].forEach.call(panneau.children, function (el, i) {\n        var on = i === actif;\n        el.classList.toggle(\'on\', on);\n        el.setAttribute(\'aria-selected\', on ? \'true\' : \'false\');\n      });\n      if (actif >= 0 && panneau.children[actif]) {\n        panneau.children[actif].scrollIntoView({ block: \'nearest\' });\n      }\n    }\n\n    function afficher(q) {\n      resultats = chercher(q);\n      panneau.textContent = \'\';\n      actif = -1;\n\n      if (!q.trim()) { fermer(); return; }\n\n      if (!resultats.length) {\n        var vide = document.createElement(\'div\');\n        vide.className = \'rsug-vide\';\n        vide.textContent = \'Aucun résultat pour « \' + q.trim() + \' »\';\n        var lien = document.createElement(\'a\');\n        lien.href = \'/formations/\';\n        lien.textContent = \'Voir toutes les formations\';\n        vide.appendChild(document.createElement(\'br\'));\n        vide.appendChild(lien);\n        panneau.appendChild(vide);\n      } else {\n        resultats.forEach(function (p, i) {\n          var a = document.createElement(\'a\');\n          a.href = p.url;\n          a.className = \'rsug-item\';\n          a.setAttribute(\'role\', \'option\');\n          a.setAttribute(\'aria-selected\', \'false\');\n          var tag = document.createElement(\'span\');\n          tag.className = \'rsug-tag\';\n          tag.textContent = p.tag;\n          var ti = document.createElement(\'span\');\n          ti.className = \'rsug-titre\';\n          ti.appendChild(surligner(p.titre, q));\n          a.appendChild(tag);\n          a.appendChild(ti);\n          a.addEventListener(\'mouseenter\', function () { actif = i; marquerActif(); });\n          panneau.appendChild(a);\n        });\n      }\n      panneau.hidden = false;\n      champ.setAttribute(\'aria-expanded\', \'true\');\n    }\n\n    champ.addEventListener(\'input\', function () { afficher(champ.value); });\n    champ.addEventListener(\'focus\', function () { if (champ.value.trim()) { afficher(champ.value); } });\n\n    champ.addEventListener(\'keydown\', function (e) {\n      if (panneau.hidden || !resultats.length) { return; }\n      if (e.key === \'ArrowDown\') { e.preventDefault(); actif = (actif + 1) % resultats.length; marquerActif(); }\n      else if (e.key === \'ArrowUp\') { e.preventDefault(); actif = (actif - 1 + resultats.length) % resultats.length; marquerActif(); }\n      else if (e.key === \'Escape\') { fermer(); }\n    });\n\n    form.addEventListener(\'submit\', function (e) {\n      // Un resultat existe : on y va. Sinon on laisse le repli vers le catalogue.\n      var cible = actif >= 0 ? resultats[actif] : resultats[0];\n      if (cible) { e.preventDefault(); fermer(); location.href = cible.url; }\n    });\n\n    document.addEventListener(\'click\', function (e) {\n      if (!form.contains(e.target)) { fermer(); }\n    });\n  });\n})();\n';

// ── Reecriture des liens et des chemins ──────────────────────────────────
function reecrire(html) {
  return html
    .replace(/href="#([a-z0-9-]+)"/g, (m, slug) =>
      parSlug.has(slug) ? `href="${urlDe(slug)}"` : m)
    .replace(/src="img\//g, 'src="/img/')
    .replace(/href="img\//g, 'href="/img/');
}

// ── Schema.org ───────────────────────────────────────────────────────────
// Le siege social est a Paris : c'est une domiciliation, personne n'y est
// jamais forme. Le declarer comme adresse de l'organisme disait a Google
// « entreprise parisienne » alors que toute l'activite est heraultaise, et
// contredisait la fiche d'etablissement, qui est l'autre moitie du signal.
// On ne declare donc que ce qui est vrai du lieu d'exercice : la region,
// et la commune si elle est renseignee dans seo.json. Le siege reste
// integralement publie aux mentions legales, la ou la loi l'exige.
const ADRESSE = { '@type': 'PostalAddress',
  ...(seo.villeBase ? { addressLocality: seo.villeBase } : {}),
  ...(seo.codePostalBase ? { postalCode: seo.codePostalBase } : {}),
  addressRegion: 'Hérault', addressCountry: 'FR' };

// Le second type ouvre les traitements locaux de Google. Il n'est pose que
// si une commune est connue : annoncer un etablissement local sans savoir
// ou il se trouve serait une declaration a moitie vraie.
const TYPES = seo.villeBase
  ? ['EducationalOrganization', 'LocalBusiness']
  : ['EducationalOrganization'];

const HORAIRES = (seo.horairesJours || []).length && seo.horairesDebut && seo.horairesFin
  ? [{ '@type': 'OpeningHoursSpecification', dayOfWeek: seo.horairesJours,
       opens: seo.horairesDebut, closes: seo.horairesFin }]
  : null;

// Toutes les fiches ou l'organisme est reellement inscrit. C'est ce
// recoupement qui permet a Google de tenir les differentes mentions du
// site pour une seule et meme entite.
const MEMES = [seo.ficheGoogle, ...(seo.profilsExternes || [])].filter(Boolean);

const ORGANISME = {
  '@type': TYPES,
  '@id': RACINE + '/#organisme',
  name: 'VFormations',
  legalName: 'VFORMATIONS',
  url: RACINE,
  logo: RACINE + '/img/logo-vformations-blue.png',
  image: RACINE + '/img/logo-vformations-blue.png',
  email: 'contact@vformations.fr',
  telephone: '+33763678292',
  address: ADRESSE,
  ...(HORAIRES ? { openingHoursSpecification: HORAIRES } : {}),
  areaServed: [{ '@type': 'AdministrativeArea', name: 'Hérault' },
               { '@type': 'AdministrativeArea', name: 'Occitanie' }],
  // Rayon d'intervention reel, centre sur Montpellier : il couvre Beziers,
  // Sete, Lunel et Lodeve, soit la zone annoncee aux mentions legales.
  serviceArea: { '@type': 'GeoCircle',
    geoMidpoint: { '@type': 'GeoCoordinates', latitude: 43.6109, longitude: 3.8772 },
    geoRadius: '80000' },
  contactPoint: { '@type': 'ContactPoint', contactType: 'sales',
    telephone: '+33763678292', email: 'contact@vformations.fr',
    areaServed: 'FR-34', availableLanguage: ['fr'] },
  // Relie le site a la fiche d'etablissement Google : c'est ce qui permet
  // a Google de rattacher les deux entites l'une a l'autre. URL par CID,
  // stable et sans parametres de suivi.
  ...(MEMES.length ? { sameAs: MEMES } : {}),
  ...(seo.ficheGoogle ? { hasMap: seo.ficheGoogle } : {}),
  identifier: [
    { '@type': 'PropertyValue', name: 'SIRET', value: '10394022700012' },
    { '@type': 'PropertyValue', name: 'Déclaration d’activité', value: '11757618175' },
    { '@type': 'PropertyValue', name: 'Qualiopi', value: 'VFO12912026001' }
  ]
};

function schema(slug, url, titre, desc, type, carte) {
  const absolu = RACINE + url;
  const fil = [{ '@type': 'ListItem', position: 1, name: 'Accueil', item: RACINE + '/' }];
  const seg = url.replace(/^\/|\/$/g, '').split('/').filter(Boolean);
  seg.forEach((_, i) => {
    const bout = '/' + seg.slice(0, i + 1).join('/') + '/';
    const p = pages.find(x => '/' + x[1] === bout);
    fil.push({ '@type': 'ListItem', position: i + 2,
               name: p ? p[2] : seg[i], item: RACINE + bout });
  });

  // L'organisme et le site sont declares sur CHAQUE page. Google traite
  // chaque URL separement : un renvoi @id vers un noeud defini sur une
  // autre page ne se resout pas. « publisher » et « author » pointaient
  // donc dans le vide sur 45 des 46 pages, et l'entite n'etait rattachee
  // a la fiche d'etablissement que depuis l'accueil.
  const blocs = [ORGANISME,
    { '@type': 'WebSite', '@id': RACINE + '/#site', url: RACINE,
      name: 'VFormations', inLanguage: 'fr-FR',
      publisher: { '@id': RACINE + '/#organisme' } }];
  if (slug !== 'accueil') {
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
      // Google se sert de cette image pour les resultats enrichis : il lui
      // faut la photo de l'article, pas le logo de l'organisme.
      image: RACINE + '/img/' + ((carte && carte.img) || 'logo-vformations-blue.png'),
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

// Le corps d'une page vient de site.html, ou bien de son propre fichier
// dans contenu/. A pres de 9 Ko par article, tout entasser dans la source
// unique la rendrait impossible a relire et chaque retouche ferait courir
// un risque au site entier. Un fichier de contenu ne porte que l'interieur
// de la section : le slug reste declare une seule fois, dans pages.json.
function corpsDe(slug) {
  const m = src.match(new RegExp(
    `<section class="page" data-page="${slug}"[^>]*>([\\s\\S]*?)\\n</section>\\n`, 'm'));
  if (m) { return m[1]; }
  const f = join('contenu', slug + '.html');
  if (existsSync(f)) { return '\n' + readFileSync(f, 'utf8').trim(); }
  throw new Error(`Corps introuvable pour « ${slug} » : absent de site.html et de ${f}`);
}

// ── « Dans la meme rubrique » ────────────────────────────────────────────
// Le maillage ecrit a la main en fin d'article cree des liens choisis, mais
// il laisse fatalement des trous : un article ajoute apres les autres ne
// recoit aucun lien entrant, et reste donc difficile a decouvrir — pour un
// lecteur comme pour un moteur. Ce bloc comble le manque mecaniquement.
// Chaque article pointe vers les trois suivants de sa rubrique, en boucle :
// chacun recoit ainsi exactement trois liens entrants, et aucun n'est
// oublie le jour ou l'on en ajoute quinze d'un coup.
function rubriqueDe(slug) {
  const a = articles.find(x => x[0] === slug);
  return ((a && a[5]) || {}).tag || '';
}

// La description sert de sous-titre de carte : on garde la premiere
// proposition, qui porte l'essentiel, plutot que de couper au caractere.
function sousTitre(desc) {
  const t = (desc || '').split(/[.,:]/)[0].trim();
  return t.length > 54 ? t.slice(0, 51).trimEnd() + '…' : t;
}

function memeRubrique(slug) {
  const tag = rubriqueDe(slug);
  let famille = articles.filter(a => rubriqueDe(a[0]) === tag);
  // Une rubrique de deux ou trois articles ne peut pas remplir trois
  // cartes : on complete avec le reste du Mag plutot que d'afficher un
  // bloc incomplet ou de se repeter.
  if (famille.length < 4) {
    famille = famille.concat(articles.filter(a => rubriqueDe(a[0]) !== tag));
  }
  const i = famille.findIndex(a => a[0] === slug);
  const choix = [];
  for (let n = 1; choix.length < 3 && n < famille.length; n++) {
    choix.push(famille[(i + n) % famille.length]);
  }
  if (!choix.length) { return ''; }
  const cartes = choix.map(([s, c, t, d, ty, m]) => {
    const meta = m || {};
    return `        <a class="card-blank" href="#${s}">` +
      `<span class="k">${meta.tag || 'Article'}</span>` +
      `<h4>${meta.carte || t}</h4>` +
      `<span class="m">${sousTitre(d)}</span></a>`;
  }).join('\n');
  return `
    <div class="maillage"><div class="k">Dans la même rubrique</div>
      <div class="grid3">
${cartes}
      </div>
    </div>`;
}

// ── Conversion en fin d'article ──────────────────────────────────────────
// Les articles sont la porte d'entree depuis Google : ce sont eux qui
// repondent aux requetes precises. Jusqu'ici ils se terminaient sur un lien
// vers le diagnostic, ce qui impose une page de plus avant le premier champ
// a remplir. Le formulaire est donc pose directement en fin d'article.
// Le slug voyage avec la demande (data-lead) : sans lui, on saurait qu'une
// demande est arrivee sans savoir quel article l'a produite.
function blocConversion(slug) {
  const id = 'lead-' + slug;
  const champ = (suffixe, nom, libelle, attrs) =>
    `<div class="field"><label for="${id}-${suffixe}">${libelle}</label>` +
    `<input id="${id}-${suffixe}" name="${nom}" ${attrs}></div>`;
  return `
    <div class="artcta">
      <div class="k">Votre situation en particulier</div>
      <h2>Savoir ce qui est mobilisable dans votre cas</h2>
      <p>Un échange court, sans engagement : on identifie votre fonds, le volume d'heures mobilisable cette année et ce qui reste à votre charge. Vous repartez avec un chiffre écrit.</p>
      <form data-lead="${slug}" data-ok="${id}-ok" novalidate>
        <div class="form">
          ${champ('nom', 'nom', 'Nom &amp; prénom *', 'autocomplete="name" required')}
          ${champ('act', 'activite', 'Votre activité *', 'placeholder="Ex. restaurant, plombier, salon…" required')}
          ${champ('mail', 'email', 'E-mail *', 'type="email" autocomplete="email" required')}
          ${champ('tel', 'tel', 'Téléphone', 'type="tel" autocomplete="tel"')}
          <div class="field full"><label for="${id}-msg">Votre question</label><textarea id="${id}-msg" name="message" placeholder="Ce que vous cherchez à savoir, en quelques mots…"></textarea></div>
          <div class="field full">
            <label style="display:flex;gap:.6rem;align-items:flex-start;font-weight:400;"><input type="checkbox" id="${id}-rgpd" name="consentement" value="oui" style="width:auto;margin-top:.2rem;" required> <span class="form-note">J'accepte que mes informations soient utilisées pour être recontacté au sujet de ma demande. Elles ne sont ni revendues ni transmises à des tiers. *</span></label>
          </div>
          <div class="field full" style="position:absolute;left:-9999px;" aria-hidden="true"><label>Ne pas remplir<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
          <div class="field full"><button type="submit" class="btn btn-wine">Envoyer ma demande</button></div>
        </div>
      </form>
      <div id="${id}-ok" class="form-ok" hidden>✓ Merci, votre demande a bien été envoyée. Nous vous recontactons sous 48 h ouvrées.</div>
      <div id="${id}-okErr" class="form-err" hidden>L'envoi n'a pas abouti. Écrivez-nous à <a href="mailto:contact@vformations.fr">contact@vformations.fr</a> ou appelez le 07 63 67 82 92.</div>
      <p class="artcta-aide">Vous préférez lire d'abord ? La page <a href="#financements">Financements</a> détaille les dispositifs, et <a href="#methode">la méthode</a> explique comment se déroule un parcours.</p>
    </div>`;
}

for (const [slug, chemin, titre, desc, type, carte] of pages) {
  let interieur = corpsDe(slug);
  if (type === 'article') {
    // Le formulaire se glisse juste apres le corps redactionnel, donc avant
    // le bloc « Pour aller plus loin » : on demande au moment ou l'interet
    // est le plus haut, pas apres trois listes de liens.
    let i = interieur.indexOf('<div class="maillage">');
    if (i === -1) { i = interieur.lastIndexOf('</article>'); }
    if (i === -1) { throw new Error(`fin d'article introuvable dans « ${slug} »`); }
    interieur = interieur.slice(0, i) + blocConversion(slug).trim() + '\n\n    ' + interieur.slice(i);
    // Le bloc de rubrique ferme la page, pour qui ne remplit pas le formulaire.
    const j = interieur.lastIndexOf('</article>');
    interieur = interieur.slice(0, j) + memeRubrique(slug) + '\n  ' + interieur.slice(j);
  }
  const corps = reecrire(poserGrilles(`<section class="page" data-page="${slug}">${interieur}\n</section>`));
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
<script type="application/ld+json">${schema(slug, url, titre, desc, type, carte)}</script>
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
