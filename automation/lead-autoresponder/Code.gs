/**
 * VFormations — Réponse automatique aux prospects du formulaire instantané Meta
 *
 * Toutes les 5 minutes, ce script :
 *   1. va chercher les nouveaux prospects du formulaire Meta ;
 *   2. les range dans l'onglet « Prospects » de ce Google Sheet ;
 *   3. envoie au prospect un accusé de réception par e-mail ;
 *   4. prévient l'équipe qu'il faut le rappeler.
 *
 * Mode d'emploi pas à pas : README.md (même dossier).
 * Le jeton Meta ne s'écrit JAMAIS dans ce fichier. Il se colle dans
 * Paramètres du projet > Propriétés du script > META_TOKEN.
 */

var CONFIG = {
  PAGE_ID: '765749889955901',     // Page Facebook VFormations
  FORM_IDS: [],                   // vide = tous les formulaires actifs de la Page
  GRAPH_VERSION: 'v21.0',

  OWNER_EMAIL: '',                // reçoit les alertes techniques
  TEAM_EMAILS: [],                // reçoivent « nouveau prospect à rappeler »
  REPLY_TO: '',                   // adresse qui reçoit les réponses des prospects
  SENDER_NAME: 'VFormations',
  COMPANY_LEGAL: '',              // raison sociale + adresse, affichées en bas du mail
  BOOKING_URL: '',                // lien de prise de rendez-vous (facultatif)
  CALLBACK_PROMISE: 'dans un délai maximum de 2 jours ouvrés',

  DRY_RUN: true,                  // true = AUCUN mail n'est envoyé au prospect
  SHEET_PROSPECTS: 'Prospects',
  SHEET_OPTOUT: 'Désabonnés',
  OVERLAP_SECONDS: 120,
  MAX_PAGES: 10
};

var COLUMNS = [
  'lead_id', 'traite_le', 'cree_le_meta', 'formulaire', 'publicite',
  'nom', 'email', 'telephone', 'entreprise',
  'statut_juridique', 'anciennete', 'formation', 'objectif', 'autres_reponses',
  'reponse_auto', 'suivi', 'rappel_le', 'rdv_pris', 'notes'
];
var STATUS_COL = COLUMNS.indexOf('reponse_auto') + 1;

/* Expressions interdites dans tout message envoyé à un prospect.
   Même liste que dans les règles du projet : publicité, droit de la formation, Meta. */
var BANNED = [
  [/\bgratuit/, 'gratuit'],
  [/\b100\s*(%|pour\s*cent)/, '100 %'],
  [/sans\s+reste\s+a\s+charge/, 'sans reste à charge'],
  [/formation\s+offerte/, 'formation offerte'],
  [/\bgaranti/, 'garanti'],
  [/\bemploi/, 'emploi'],
  [/employabilite/, 'employabilité'],
  [/reconversion|se\s+reconvertir/, 'reconversion'],
  [/\bdiplome/, 'diplôme'],
  [/\brncp\b/, 'RNCP'],
  [/titre\s+certifiant/, 'titre certifiant'],
  [/\bcarriere/, 'carrière'],
  [/decrocher\s+un\s+poste/, 'décrocher un poste'],
  [/machine\s+a\s+cash/, 'machine à cash'],
  [/\bqualiopi/, 'Qualiopi (à retirer de cette liste une fois la certification obtenue)']
];

/* ------------------------------------------------------------------ */
/* Fonctions à lancer à la main, depuis l'éditeur Apps Script          */
/* ------------------------------------------------------------------ */

/** À lancer UNE fois. Prépare le Sheet, fixe le point de départ, installe le minuteur. */
function initialiser() {
  openSheets_();
  PropertiesService.getScriptProperties().setProperty('LAST_TS', String(nowSec_()));
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'pollLeads') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('pollLeads').timeBased().everyMinutes(5).create();
  Logger.log('Robot installé. Seuls les prospects arrivés à partir de maintenant recevront une réponse.');
}

/** Facultatif. Range les prospects des 30 derniers jours dans le Sheet, SANS leur écrire. */
function importerHistorique() {
  var token = requireToken_();
  var pageToken = pageToken_(token);
  var ctx = openSheets_();
  var since = nowSec_() - 30 * 86400;
  var count = 0;
  formIds_(pageToken).forEach(function (fid) {
    fetchLeads_(fid, since, pageToken).forEach(function (raw) {
      if (ctx.known[raw.id]) return;
      var p = parseLead_(raw);
      appendProspect_(ctx, p, 'historique (aucun mail envoyé)', 'Historique — à qualifier');
      ctx.known[raw.id] = true;
      count++;
    });
  });
  Logger.log(count + ' prospects importés.');
}

/** Envoie à OWNER_EMAIL un exemple exact du mail que recevra un prospect. */
function envoyerTest() {
  var to = CONFIG.OWNER_EMAIL || Session.getEffectiveUser().getEmail();
  var r = renderReply_(sampleProspect_(), CONFIG);
  MailApp.sendEmail({ to: to, subject: '[TEST] ' + r.subject, body: r.text, htmlBody: r.html, name: CONFIG.SENDER_NAME });
  Logger.log('Mail de test envoyé à ' + to);
}

/** Lancé automatiquement toutes les 5 minutes. */
function pollLeads() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) return;
  try {
    run_();
  } catch (e) {
    alertOwner_('Le robot à prospects a rencontré une erreur', String((e && e.message) || e));
  } finally {
    lock.releaseLock();
  }
}

/* ------------------------------------------------------------------ */
/* Cœur du robot                                                       */
/* ------------------------------------------------------------------ */

function run_() {
  var props = PropertiesService.getScriptProperties();
  var token = requireToken_();
  var last = Number(props.getProperty('LAST_TS') || 0);
  if (!last) { // première exécution : on ne répond jamais aux anciens prospects
    props.setProperty('LAST_TS', String(nowSec_()));
    return;
  }

  var pageToken = pageToken_(token);
  var since = last - CONFIG.OVERLAP_SECONDS;
  var leads = [];
  formIds_(pageToken).forEach(function (fid) { leads = leads.concat(fetchLeads_(fid, since, pageToken)); });
  leads.sort(function (a, b) { return toSec_(a.created_time) - toSec_(b.created_time); });

  var ctx = openSheets_();
  var problems = templateProblems_();
  if (problems.length) {
    alertOwner_('Mail automatique bloqué : texte non conforme',
      'Ces expressions sont interdites dans le mail envoyé aux prospects : ' + problems.join(', ') +
      '. Aucun mail ne partira tant que ce n\'est pas corrigé (les prospects restent enregistrés).');
  }

  var maxTs = last, failTs = 0;
  leads.forEach(function (raw) {
    var ts = toSec_(raw.created_time);
    if (ctx.known[raw.id]) { if (ts > maxTs) maxTs = ts; return; }
    try {
      var p = parseLead_(raw);
      var rowIdx = appendProspect_(ctx, p, 'en cours', 'À rappeler');
      ctx.known[raw.id] = true;
      var status = replyStatus_(p, ctx, problems);
      ctx.sheet.getRange(rowIdx, STATUS_COL).setValue(status);
      notifyTeam_(p, status, ctx);
      if (ts > maxTs) maxTs = ts;
    } catch (e) {
      failTs = failTs ? Math.min(failTs, ts) : ts;
      Logger.log('Échec sur le prospect ' + raw.id + ' : ' + e.message);
    }
  });
  props.setProperty('LAST_TS', String(failTs ? Math.min(maxTs, failTs - 1) : maxTs));
}

function replyStatus_(p, ctx, problems) {
  if (!isEmail_(p.email)) return 'pas d\'e-mail valide';
  if (ctx.optout[p.email.toLowerCase()]) return 'désabonné : aucun mail';
  if (problems.length) return 'bloqué : texte non conforme';
  if (CONFIG.DRY_RUN) return 'simulation (aucun mail envoyé)';
  if (MailApp.getRemainingDailyQuota() < 2) return 'quota Google atteint';
  try {
    var r = renderReply_(p, CONFIG);
    var opts = { to: p.email, subject: r.subject, body: r.text, htmlBody: r.html, name: CONFIG.SENDER_NAME };
    if (CONFIG.REPLY_TO) opts.replyTo = CONFIG.REPLY_TO;
    MailApp.sendEmail(opts);
    return 'envoyée';
  } catch (e) {
    return 'échec d\'envoi';
  }
}

function notifyTeam_(p, status, ctx) {
  var to = (CONFIG.TEAM_EMAILS.length ? CONFIG.TEAM_EMAILS : [CONFIG.OWNER_EMAIL]).filter(Boolean);
  if (!to.length) return;
  var lines = [
    'Nouveau prospect à rappeler', '',
    'Nom : ' + p.nom,
    'Entreprise : ' + p.entreprise,
    'Téléphone : ' + p.telephone,
    'E-mail : ' + p.email,
    'Statut juridique : ' + p.statut,
    'Ancienneté : ' + p.anciennete,
    'Formation qui l\'intéresse : ' + p.formation,
    'Objectif : ' + p.objectif,
    'Publicité d\'origine : ' + p.adName
  ];
  if (p.autres.length) lines.push('Autres réponses : ' + p.autres.join(' | '));
  lines.push('', 'Réponse automatique : ' + status, 'Tableau de suivi : ' + ctx.ss.getUrl());
  MailApp.sendEmail({
    to: to.join(','),
    subject: oneLine_('Nouveau prospect : ' + (p.entreprise || p.nom || 'sans nom'), 80),
    body: lines.join('\n'),
    name: CONFIG.SENDER_NAME
  });
}

/* ------------------------------------------------------------------ */
/* Meta                                                                */
/* ------------------------------------------------------------------ */

function requireToken_() {
  var token = PropertiesService.getScriptProperties().getProperty('META_TOKEN');
  if (!token) throw new Error('META_TOKEN est absent des propriétés du script.');
  return token;
}

function pageToken_(token) {
  var res = graph_(CONFIG.PAGE_ID, { fields: 'access_token' }, token);
  if (!res.access_token) throw new Error('Meta n\'a pas fourni de jeton de Page : la Page est-elle bien attribuée à l\'utilisateur système, avec le droit « Gérer les prospects » ?');
  return res.access_token;
}

function formIds_(pageToken) {
  if (CONFIG.FORM_IDS.length) return CONFIG.FORM_IDS;
  var res = graph_(CONFIG.PAGE_ID + '/leadgen_forms', { fields: 'id,status', limit: 50 }, pageToken);
  return (res.data || []).filter(function (f) { return f.status === 'ACTIVE'; }).map(function (f) { return f.id; });
}

function fetchLeads_(formId, sinceSec, pageToken) {
  var params = {
    fields: 'id,created_time,form_id,ad_id,ad_name,field_data',
    limit: 100,
    filtering: JSON.stringify([{ field: 'time_created', operator: 'GREATER_THAN', value: sinceSec }])
  };
  var res = graph_(formId + '/leads', params, pageToken);
  var out = res.data || [], pages = 1;
  while (res.paging && res.paging.next && pages < CONFIG.MAX_PAGES) {
    res = graphUrl_(stripToken_(res.paging.next), pageToken);
    out = out.concat(res.data || []);
    pages++;
  }
  return out;
}

function graph_(path, params, token) {
  var qs = Object.keys(params || {}).map(function (k) {
    return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
  }).join('&');
  return graphUrl_('https://graph.facebook.com/' + CONFIG.GRAPH_VERSION + '/' + path + (qs ? '?' + qs : ''), token);
}

/** Le jeton voyage dans l'en-tête, jamais dans l'adresse : il ne peut pas finir dans un journal. */
function graphUrl_(url, token) {
  var res = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token }, muteHttpExceptions: true });
  var body = JSON.parse(res.getContentText() || '{}');
  if (body.error) throw new Error('Meta ' + body.error.code + ' : ' + body.error.message);
  return body;
}

function stripToken_(url) {
  return url.replace(/([?&])access_token=[^&]*&?/, '$1').replace(/[?&]$/, '');
}

/* ------------------------------------------------------------------ */
/* Lecture d'un prospect                                               */
/* ------------------------------------------------------------------ */

function parseLead_(lead) {
  var out = {
    id: lead.id, createdTime: lead.created_time || '', formId: lead.form_id || '', adName: lead.ad_name || '',
    nom: '', email: '', telephone: '', entreprise: '', statut: '', anciennete: '', formation: '', objectif: '', autres: []
  };
  (lead.field_data || []).forEach(function (f) {
    var key = normalizeKey_(f.name);
    var val = (f.values || []).join(', ').trim();
    if (!val) return;
    if (key === 'full_name' || key === 'nom_complet') out.nom = val;
    else if (key === 'email') out.email = val;
    else if (key === 'phone_number' || key === 'telephone') out.telephone = val;
    else if (key === 'company_name') out.entreprise = val;
    else if (key.indexOf('statut_juridique') >= 0) out.statut = humanize_(val);
    else if (key.indexOf('depuis_combien') >= 0) out.anciennete = humanize_(val);
    else if (key.indexOf('quelle_formation') >= 0) out.formation = humanize_(val);
    else if (key.indexOf('objectif') >= 0) out.objectif = humanize_(val);
    else out.autres.push(f.name + ' : ' + humanize_(val)); // toute nouvelle question est conservée
  });
  out.prenom = firstName_(out.nom);
  return out;
}

function normalizeKey_(s) {
  return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}

function humanize_(v) { return String(v || '').replace(/_/g, ' ').trim(); }

function firstName_(full) {
  var t = String(full || '').trim().split(/\s+/)[0] || '';
  if (!t) return '';
  if (t.length > 1 && t === t.toUpperCase()) t = t.toLowerCase();
  return t.charAt(0).toUpperCase() + t.slice(1);
}

function isEmail_(s) { return /^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]{2,}$/.test(String(s || '')); }

/* ------------------------------------------------------------------ */
/* Le mail envoyé au prospect                                          */
/* ------------------------------------------------------------------ */

function renderReply_(p, cfg) {
  var hello = p.prenom ? 'Bonjour ' + p.prenom + ',' : 'Bonjour,';
  var paras = [
    hello,
    'Merci d\'avoir rempli notre formulaire. Nous avons bien reçu votre demande.',
    'Prochaine étape : un membre de l\'équipe vous appelle ' + cfg.CALLBACK_PROMISE + ' pour comprendre votre activité et voir si nous pouvons vous aider.'
  ];
  if (cfg.BOOKING_URL) paras.push('Vous préférez choisir vous-même le moment ? Réservez ici : ' + cfg.BOOKING_URL);
  paras.push('Pendant cet échange, nous parlerons de votre activité, de la façon dont vos clients vous trouvent aujourd\'hui, et de ce qui peut être pris en charge selon votre statut. Le montant exact qui resterait à votre charge vous est toujours annoncé par écrit, sur le devis, avant tout engagement.');
  paras.push('À très vite,\n' + cfg.SENDER_NAME);
  var foot = 'Vous recevez ce message parce que vous avez rempli un formulaire sur Facebook ou Instagram. Pour ne plus être contacté, répondez simplement « STOP ».' + (cfg.COMPANY_LEGAL ? '\n' + cfg.COMPANY_LEGAL : '');

  var text = paras.join('\n\n') + '\n\n--\n' + foot;
  var html = '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.55;color:#1c2430">' +
    paras.map(function (x) { return '<p style="margin:0 0 14px">' + esc_(x).replace(/\n/g, '<br>') + '</p>'; }).join('') +
    '<p style="margin:22px 0 0;padding-top:12px;border-top:1px solid #d9dee6;font-size:12px;color:#6b7686">' + esc_(foot).replace(/\n/g, '<br>') + '</p></div>';
  return { subject: 'Votre demande a bien été reçue', text: text, html: html };
}

function sampleProspect_() { return { prenom: 'Camille', nom: 'Camille Exemple' }; }

/** Vérifie le texte du mail avec un prénom neutre : seuls NOS mots comptent, pas ceux du prospect. */
function templateProblems_() {
  var r = renderReply_(sampleProspect_(), CONFIG);
  return checkCompliance_(r.subject + '\n' + r.text);
}

function checkCompliance_(text) {
  var t = normalizeText_(text), found = [];
  BANNED.forEach(function (b) { if (b[0].test(t)) found.push(b[1]); });
  return found;
}

function normalizeText_(s) {
  return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

/* ------------------------------------------------------------------ */
/* Sheet                                                               */
/* ------------------------------------------------------------------ */

function openSheets_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.SHEET_PROSPECTS) || ss.insertSheet(CONFIG.SHEET_PROSPECTS);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(COLUMNS);
    sheet.setFrozenRows(1);
    // Les identifiants Meta ont 16 chiffres : en format nombre, Sheets les arrondirait.
    sheet.getRange(1, 1, 5000, 1).setNumberFormat('@');
    sheet.getRange(1, COLUMNS.indexOf('telephone') + 1, 5000, 1).setNumberFormat('@');
  }
  var opt = ss.getSheetByName(CONFIG.SHEET_OPTOUT) || ss.insertSheet(CONFIG.SHEET_OPTOUT);
  if (opt.getLastRow() === 0) opt.appendRow(['email']);

  var known = {}, optout = {};
  if (sheet.getLastRow() > 1) {
    sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues().forEach(function (r) { if (r[0]) known[String(r[0])] = true; });
  }
  if (opt.getLastRow() > 1) {
    opt.getRange(2, 1, opt.getLastRow() - 1, 1).getValues().forEach(function (r) { if (r[0]) optout[String(r[0]).trim().toLowerCase()] = true; });
  }
  return { ss: ss, sheet: sheet, known: known, optout: optout };
}

function appendProspect_(ctx, p, status, suivi) {
  var row = [
    p.id, new Date().toISOString(), p.createdTime, p.formId, p.adName,
    p.nom, p.email, p.telephone, p.entreprise,
    p.statut, p.anciennete, p.formation, p.objectif, p.autres.join(' | '),
    status, suivi, '', '', ''
  ].map(safeCell_);
  ctx.sheet.appendRow(row);
  return ctx.sheet.getLastRow();
}

/** Ce que tape un inconnu dans un formulaire ne doit jamais être exécuté comme une formule. */
function safeCell_(v) {
  var s = String(v === undefined || v === null ? '' : v);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

/* ------------------------------------------------------------------ */
/* Divers                                                              */
/* ------------------------------------------------------------------ */

function alertOwner_(subject, message) {
  var props = PropertiesService.getScriptProperties();
  var now = nowSec_();
  if (now - Number(props.getProperty('LAST_ALERT_TS') || 0) < 6 * 3600) return; // pas plus d'une alerte toutes les 6 h
  props.setProperty('LAST_ALERT_TS', String(now));
  var to = CONFIG.OWNER_EMAIL || Session.getEffectiveUser().getEmail();
  MailApp.sendEmail({ to: to, subject: '[Robot prospects] ' + subject, body: message, name: CONFIG.SENDER_NAME });
}

function nowSec_() { return Math.floor(Date.now() / 1000); }

function toSec_(iso) {
  return Math.floor(new Date(String(iso).replace(/([+-]\d\d)(\d\d)$/, '$1:$2')).getTime() / 1000);
}

function esc_(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function oneLine_(s, max) { return String(s).replace(/[\r\n]+/g, ' ').slice(0, max); }
