// Test du robot sans toucher à Google ni à Meta : tous les services sont simulés.
// Lancer :  node test.js
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const SRC = fs.readFileSync(__dirname + '/Code.gs', 'utf8');

const isoMeta = (ms) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, '+0000');

function makeSheet() {
  const rows = [];
  return {
    rows,
    getLastRow: () => rows.length,
    appendRow: (a) => { rows.push(a.slice()); },
    setFrozenRows() {},
    getRange(r, c, nr, nc) {
      return {
        getValues() { const o = []; for (let i = 0; i < (nr || 1); i++) { const row = rows[r - 1 + i] || []; const v = []; for (let j = 0; j < (nc || 1); j++) v.push(row[c - 1 + j] === undefined ? '' : row[c - 1 + j]); o.push(v); } return o; },
        setValue(v) { rows[r - 1] = rows[r - 1] || []; rows[r - 1][c - 1] = v; },
        setNumberFormat() {}
      };
    }
  };
}

function makeEnv() {
  const st = { props: {}, mails: [], sheets: {}, leads: [], calls: [], pageOk: true, error: null, triggers: [] };
  const sandbox = {
    console, Date, Math, JSON, Object, String, Number, encodeURIComponent,
    Logger: { log() {} },
    PropertiesService: { getScriptProperties: () => ({ getProperty: (k) => (k in st.props ? st.props[k] : null), setProperty: (k, v) => { st.props[k] = v; } }) },
    LockService: { getScriptLock: () => ({ tryLock: () => true, releaseLock() {} }) },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'patron@example.com' }) },
    MailApp: { sendEmail: (o) => st.mails.push(o), getRemainingDailyQuota: () => 100 },
    ScriptApp: {
      getProjectTriggers: () => st.triggers.map((h) => ({ getHandlerFunction: () => h })),
      deleteTrigger() {},
      newTrigger: (h) => ({ timeBased: () => ({ everyMinutes: () => ({ create: () => st.triggers.push(h) }) }) })
    },
    SpreadsheetApp: { getActiveSpreadsheet: () => ({
      getUrl: () => 'https://sheet.example/tableau',
      getSheetByName: (n) => st.sheets[n] || null,
      insertSheet: (n) => (st.sheets[n] = makeSheet())
    }) },
    UrlFetchApp: { fetch(url, opts) {
      st.calls.push({ url, auth: opts.headers.Authorization });
      let body;
      if (st.error) body = { error: st.error };
      else if (/\/765749889955901\?fields=access_token/.test(url)) body = st.pageOk ? { access_token: 'PAGE_TOKEN' } : {};
      else if (/\/765749889955901\/leadgen_forms/.test(url)) body = { data: [{ id: 'F1', status: 'ACTIVE' }, { id: 'F2', status: 'PAUSED' }] };
      else if (/\/F1\/leads/.test(url)) {
        const since = JSON.parse(decodeURIComponent(url.match(/filtering=([^&]*)/)[1]))[0].value;
        body = { data: st.leads.filter((l) => Math.floor(new Date(l.created_time.replace(/([+-]\d\d)(\d\d)$/, '$1:$2')).getTime() / 1000) > since) };
      } else body = { error: { code: 100, message: 'route inconnue ' + url } };
      return { getContentText: () => JSON.stringify(body) };
    } }
  };
  const ctx = vm.createContext(sandbox);
  vm.runInContext(SRC, ctx);
  st.props.META_TOKEN = 'SYS_TOKEN';
  return { ctx, st, run: (code) => vm.runInContext(code, ctx) };
}

const fakeLead = (id, ms, over = {}) => Object.assign({
  id, created_time: isoMeta(ms), form_id: 'F1', ad_name: 'ADS #3 Test',
  field_data: [
    { name: 'quel_est_le_statut_juridique_de_votre_entreprise_?', values: ['sasu'] },
    { name: 'depuis_combien_de_temps_votre_entreprise_est-elle_en_activité_?', values: ['plus_de_3_ans'] },
    { name: 'quelle_formation_vous_intéresse_le_plus_?', values: ["les_deux_m'intéressent"] },
    { name: 'quel_est_votre_objectif_principal_?', values: ['trouver_de_nouveaux_clients'] },
    { name: 'full_name', values: ['CAMILLE EXEMPLE'] },
    { name: 'email', values: ['camille@example.com'] },
    { name: 'phone_number', values: ['+33600000000'] },
    { name: 'company_name', values: ['Atelier Exemple'] }
  ]
}, over);

let n = 0;
const test = (name, fn) => { fn(); n++; console.log('  ok  ' + name); };

test('lecture d\'un prospect avec les vraies clés du formulaire', () => {
  const { run, ctx } = makeEnv();
  ctx.L = fakeLead('123', Date.now());
  const p = run('parseLead_(L)');
  assert.strictEqual(p.prenom, 'Camille');
  assert.strictEqual(p.email, 'camille@example.com');
  assert.strictEqual(p.entreprise, 'Atelier Exemple');
  assert.strictEqual(p.statut, 'sasu');
  assert.strictEqual(p.anciennete, 'plus de 3 ans');
  assert.strictEqual(p.formation, "les deux m'intéressent");
  assert.strictEqual(p.objectif, 'trouver de nouveaux clients');
  assert.deepStrictEqual(Array.from(p.autres), []);
});

test('une nouvelle question du formulaire est conservée, pas perdue', () => {
  const { run, ctx } = makeEnv();
  ctx.L = fakeLead('1', Date.now(), { field_data: [{ name: 'êtes-vous_gérant_non_salarié_?', values: ['oui'] }, { name: 'email', values: ['a@example.com'] }] });
  const p = run('parseLead_(L)');
  assert.strictEqual(p.autres[0], 'êtes-vous_gérant_non_salarié_? : oui');
});

test('le texte du mail actuel passe le contrôle de conformité', () => {
  const { run } = makeEnv();
  assert.deepStrictEqual(Array.from(run('templateProblems_()')), []);
});

test('le contrôle attrape les formulations interdites, dont celle du formulaire en ligne', () => {
  const { run, ctx } = makeEnv();
  for (const bad of ['une formation à 3 000€, potentiellement financée à 100% selon votre statut', 'Formation GRATUITE', 'vos débouchés et votre reconversion', 'un diplôme reconnu', 'sans reste à charge', 'organisme certifié Qualiopi']) {
    ctx.T = bad;
    assert.ok(run('checkCompliance_(T)').length > 0, 'devrait refuser : ' + bad);
  }
  ctx.T = 'Merci pour votre demande, nous vous rappelons.';
  assert.strictEqual(run('checkCompliance_(T)').length, 0);
});

test('un champ de contrôle modifié par erreur bloque l\'envoi', () => {
  const { run } = makeEnv();
  run("CONFIG.CALLBACK_PROMISE = 'tout de suite, et c\\'est gratuit'");
  assert.deepStrictEqual(Array.from(run('templateProblems_()')), ['gratuit']);
});

test('une saisie qui ressemble à une formule est neutralisée', () => {
  const { run, ctx } = makeEnv();
  ctx.V = '=HYPERLINK("http://mal.example","clic")';
  assert.strictEqual(run('safeCell_(V)'), "'=HYPERLINK(\"http://mal.example\",\"clic\")");
  ctx.V = '+33600000000';
  assert.strictEqual(run('safeCell_(V)'), "'+33600000000");
  ctx.V = 'Atelier Exemple';
  assert.strictEqual(run('safeCell_(V)'), 'Atelier Exemple');
});

test('le HTML du mail échappe ce que le prospect a tapé', () => {
  const { run, ctx } = makeEnv();
  ctx.P = { prenom: '<script>alert(1)</script>' };
  const r = run('renderReply_(P, CONFIG)');
  assert.ok(!r.html.includes('<script>'));
  assert.ok(r.html.includes('&lt;script&gt;'));
});

test('première exécution : on fixe le point de départ et on n\'écrit à personne', () => {
  const { run, st } = makeEnv();
  st.leads = [fakeLead('OLD', Date.now() - 86400000)];
  run('CONFIG.DRY_RUN = false; pollLeads()');
  assert.ok(Number(st.props.LAST_TS) > 0);
  assert.strictEqual(st.mails.length, 0);
  assert.ok(!st.sheets.Prospects);
});

test('simulation : le prospect est rangé et l\'équipe prévenue, mais aucun mail ne lui part', () => {
  const { run, st } = makeEnv();
  run("CONFIG.TEAM_EMAILS = ['equipe@example.com']; initialiser()");
  st.leads = [fakeLead('2777818899300843', Date.now() + 30000)];
  run('pollLeads()');
  const rows = st.sheets.Prospects.rows;
  assert.strictEqual(rows.length, 2);
  assert.strictEqual(rows[1][0], '2777818899300843');
  assert.strictEqual(rows[1][STATUS()], 'simulation (aucun mail envoyé)');
  assert.deepStrictEqual(st.mails.map((m) => m.to), ['equipe@example.com']);
});

test('en production : un mail au prospect, une alerte à l\'équipe, et jamais deux fois', () => {
  const { run, st } = makeEnv();
  run("CONFIG.DRY_RUN = false; CONFIG.TEAM_EMAILS = ['equipe@example.com']; initialiser()");
  st.leads = [fakeLead('L1', Date.now() + 30000)];
  run('pollLeads()'); run('pollLeads()'); run('pollLeads()');
  assert.strictEqual(st.sheets.Prospects.rows.length, 2);
  assert.strictEqual(st.mails.filter((m) => m.to === 'camille@example.com').length, 1);
  assert.strictEqual(st.mails.filter((m) => m.to === 'equipe@example.com').length, 1);
  assert.strictEqual(st.sheets.Prospects.rows[1][STATUS()], 'envoyée');
});

test('un prospect désabonné est rangé mais ne reçoit rien', () => {
  const { run, st } = makeEnv();
  run("CONFIG.DRY_RUN = false; initialiser()");
  st.sheets['Désabonnés'].appendRow(['CAMILLE@example.com']);
  st.leads = [fakeLead('L2', Date.now() + 30000)];
  run('pollLeads()');
  assert.strictEqual(st.mails.filter((m) => m.to === 'camille@example.com').length, 0);
  assert.strictEqual(st.sheets.Prospects.rows[1][STATUS()], 'désabonné : aucun mail');
});

test('sans e-mail valide : rangé, signalé, aucun envoi', () => {
  const { run, st } = makeEnv();
  run("CONFIG.DRY_RUN = false; initialiser()");
  st.leads = [fakeLead('L3', Date.now() + 30000, { field_data: [{ name: 'full_name', values: ['Sans Mail'] }, { name: 'email', values: ['pas-un-mail'] }] })];
  run('pollLeads()');
  assert.strictEqual(st.sheets.Prospects.rows[1][STATUS()], "pas d'e-mail valide");
  assert.strictEqual(st.mails.filter((m) => m.to === 'pas-un-mail').length, 0);
});

test('le jeton ne figure jamais dans une adresse, seulement dans l\'en-tête', () => {
  const { run, st } = makeEnv();
  run('initialiser()');
  st.leads = [fakeLead('L4', Date.now() + 30000)];
  run('pollLeads()');
  assert.ok(st.calls.length >= 3);
  st.calls.forEach((c) => { assert.ok(!/access_token=/.test(c.url), c.url); assert.ok(/^Bearer /.test(c.auth)); });
  assert.strictEqual(st.calls[0].auth, 'Bearer SYS_TOKEN');
  assert.strictEqual(st.calls[1].auth, 'Bearer PAGE_TOKEN');
});

test('le lien de page suivante est nettoyé de tout jeton', () => {
  const { run, ctx } = makeEnv();
  ctx.U = 'https://graph.facebook.com/v21.0/F1/leads?access_token=SECRET&limit=100&after=abc';
  assert.strictEqual(run('stripToken_(U)'), 'https://graph.facebook.com/v21.0/F1/leads?limit=100&after=abc');
  ctx.U = 'https://graph.facebook.com/v21.0/F1/leads?limit=100&access_token=SECRET';
  assert.strictEqual(run('stripToken_(U)'), 'https://graph.facebook.com/v21.0/F1/leads?limit=100');
});

test('jeton refusé par Meta : une seule alerte au patron, pas de plantage, rien n\'est perdu', () => {
  const { run, st } = makeEnv();
  run('initialiser()');
  st.error = { code: 190, message: 'Invalid OAuth access token' };
  run('pollLeads()'); run('pollLeads()'); run('pollLeads()');
  assert.strictEqual(st.mails.length, 1);
  assert.strictEqual(st.mails[0].to, 'patron@example.com');
  assert.ok(/190/.test(st.mails[0].body));
  assert.ok(!st.mails[0].body.includes('SYS_TOKEN'));
});

test('Page non attribuée : message qui dit quoi faire', () => {
  const { run, st } = makeEnv();
  run('initialiser()'); st.pageOk = false;
  run('pollLeads()');
  assert.ok(/Gérer les prospects/.test(st.mails[0].body));
});

test('un prospect arrivé pendant une panne est récupéré ensuite', () => {
  const { run, st } = makeEnv();
  run("CONFIG.DRY_RUN = false; initialiser()");
  st.leads = [fakeLead('L5', Date.now() + 30000)];
  st.error = { code: 2, message: 'Service temporarily unavailable' };
  run('pollLeads()');
  assert.ok(!st.sheets.Prospects || st.sheets.Prospects.rows.length === 1);
  st.error = null;
  run('pollLeads()');
  assert.strictEqual(st.sheets.Prospects.rows.length, 2);
});

function STATUS() { return 14; } // colonne « reponse_auto », comptée depuis 0

console.log('\n' + n + ' tests réussis');
