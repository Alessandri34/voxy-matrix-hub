const fs = require('fs');

function loadConfig(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function normalize(s) {
  return String(s ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .trim();
}

function answersFromFieldData(fieldData = []) {
  const answers = {};
  for (const f of fieldData) answers[f.name] = (f.values || []).join(', ');
  return answers;
}

function firstName(answers) {
  if (answers.first_name) return answers.first_name.trim();
  const full = answers.full_name || answers.nom_complet || '';
  return full.trim().split(/\s+/)[0] || '';
}

function fill(text, vars) {
  return String(text).replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? '').toString());
}

// WhatsApp template parameters reject newlines, tabs and 4+ consecutive spaces.
function waSafe(text) {
  return String(text).replace(/[\n\r\t]+/g, ' ').replace(/ {4,}/g, ' ').trim();
}

function ruleMatches(rule, answers) {
  const value = normalize(answers[rule.champ]);
  if (rule.egal !== undefined) return value === normalize(rule.egal);
  if (rule.contient !== undefined) return value.includes(normalize(rule.contient));
  return false;
}

function buildMessages(config, answers) {
  const rule = (config.regles || []).find((r) => ruleMatches(r, answers)) || config.defaut;
  const prenom = firstName(answers) || config.prenom_par_defaut || '';
  const vars = { ...answers, prenom };
  const sujet = fill(rule.sujet, vars);
  const message = fill(rule.message, vars);
  const all = { ...vars, sujet, message };
  return {
    regle: rule.nom || 'defaut',
    whatsappParams: [prenom, sujet, message].map(waSafe),
    sms: fill(rule.sms || config.sms, all).trim(),
  };
}

module.exports = { loadConfig, answersFromFieldData, buildMessages, firstName, waSafe };
