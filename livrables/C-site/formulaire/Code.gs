/**
 * VFormations — réception des formulaires du site (contact + diagnostic).
 * Chaque envoi : 1) ajoute une ligne dans le Google Sheet, 2) envoie un
 * e-mail de notification à contact@vformations.fr.
 *
 * Déploiement : voir GUIDE_BRANCHEMENT.md (même dossier).
 * Aucune clé secrète ici — ce code s'exécute dans TON compte Google.
 */

// ───────────────────────── Paramètres ─────────────────────────
var NOTIFY_EMAIL = 'contact@vformations.fr'; // destinataire des notifications
var SHEET_NAME   = 'Demandes';               // onglet où écrire les lignes
var SHEET_ID     = '';                        // laisser vide si le script est lié au Sheet
// ───────────────────────────────────────────────────────────────

// Ordre et libellés des colonnes du Sheet.
var COLUMNS = [
  ['_date',    'Date'],
  ['_form',    'Formulaire'],
  ['nom',      'Nom & prénom'],
  ['email',    'E-mail'],
  ['tel',      'Téléphone'],
  ['activite', 'Activité'],
  ['sujet',    'Sujet'],
  ['besoin',   'Besoin'],
  ['financeur','Financeur'],
  ['message',  'Message'],
  ['_page',    'Page']
];

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};

    // Pot de miel anti-spam : si rempli, on ignore sans rien écrire.
    if (p._gotcha) { return json_({ ok: true, skipped: 'spam' }); }

    var sheet = getSheet_();
    ensureHeaders_(sheet);

    var now = p._date ? new Date(p._date) : new Date();
    var row = COLUMNS.map(function (c) {
      var key = c[0];
      if (key === '_date') { return formatDate_(now); }
      return p[key] || '';
    });
    sheet.appendRow(row);

    sendNotification_(p, now);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

// Permet de tester que le déploiement répond (ouvrir l'URL dans le navigateur).
function doGet() {
  return json_({ ok: true, service: 'VFormations form endpoint' });
}

function getSheet_() {
  var ss = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    throw new Error('Aucun Google Sheet lié. Renseigne SHEET_ID ou crée le script depuis Extensions > Apps Script du Sheet.');
  }
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) { sheet = ss.insertSheet(SHEET_NAME); }
  return sheet;
}

function ensureHeaders_(sheet) {
  if (sheet.getLastRow() > 0) { return; }
  var headers = COLUMNS.map(function (c) { return c[1]; });
  sheet.appendRow(headers);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.setFrozenRows(1);
}

function sendNotification_(p, now) {
  var formLabel = (p._form === 'diagnostic') ? 'Demande de diagnostic' : 'Message de contact';
  var subject = '[VFormations] ' + formLabel + (p.nom ? ' — ' + p.nom : '');

  var lines = [];
  lines.push(formLabel + ' reçu le ' + formatDate_(now));
  lines.push('');
  COLUMNS.forEach(function (c) {
    var key = c[0];
    if (key === '_date' || key === '_form') { return; }
    if (p[key]) { lines.push(c[1] + ' : ' + p[key]); }
  });
  lines.push('');
  lines.push('— Notification automatique du site vformations.fr');

  var options = {
    name: 'Site VFormations',
    noReply: true
  };
  // Répondre directement au visiteur depuis l'e-mail de notification.
  if (p.email && /\S+@\S+\.\S+/.test(p.email)) {
    options.replyTo = p.email;
    delete options.noReply;
  }
  MailApp.sendEmail(NOTIFY_EMAIL, subject, lines.join('\n'), options);
}

function formatDate_(d) {
  return Utilities.formatDate(d, Session.getScriptTimeZone(), 'dd/MM/yyyy HH:mm');
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
