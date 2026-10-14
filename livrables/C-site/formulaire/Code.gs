var NOTIFY_EMAIL = 'contact@vformations.fr';
var SHEET_ID = '1Iij8fCiqW4Wv2R_Vn_jlHJd8jm_UEIof3pOGg8c7QSQ';
var SHEET_NAME = 'Demandes';
var COLS = [['_date','Date'],['_form','Formulaire'],['nom','Nom et prenom'],
  ['email','E-mail'],['tel','Telephone'],['activite','Activite'],['sujet','Sujet'],
  ['besoin','Besoin'],['financeur','Financeur'],['message','Message'],
  ['consentement','Consentement RGPD'],['_page','Page']];

function doGet() {
  return json_({ ok: true, service: 'VFormations form endpoint' });
}

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    if (p._gotcha) { return json_({ ok: true, skipped: 'spam' }); }

    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) {
      sh.appendRow(COLS.map(function (c) { return c[1]; }));
      sh.getRange(1, 1, 1, COLS.length).setFontWeight('bold');
      sh.setFrozenRows(1);
    }

    var now = p._date ? new Date(p._date) : new Date();
    var d = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd/MM/yyyy HH:mm');
    sh.appendRow(COLS.map(function (c) {
      return c[0] === '_date' ? d : (p[c[0]] || '');
    }));

    var lignes = [];
    COLS.forEach(function (c) {
      if (c[0] !== '_date' && p[c[0]]) { lignes.push(c[1] + ' : ' + p[c[0]]); }
    });
    var opt = { name: 'Site VFormations' };
    if (p.email && /\S+@\S+\.\S+/.test(p.email)) { opt.replyTo = p.email; }
    MailApp.sendEmail(NOTIFY_EMAIL,
      '[VFormations] ' + (p._form === 'diagnostic' ? 'Diagnostic' : 'Contact') +
        (p.nom ? ' - ' + p.nom : ''),
      'Recu le ' + d + '\n\n' + lignes.join('\n'), opt);

    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}
