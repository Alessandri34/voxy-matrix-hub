const test = require('node:test');
const assert = require('node:assert');
const crypto = require('crypto');
const http = require('http');
const os = require('os');
const path = require('path');
const { createApp } = require('../src/app');
const { Store } = require('../src/store');
const { loadConfig } = require('../src/messages');
const { normalizePhone } = require('../src/phone');

const config = loadConfig(path.join(__dirname, '..', 'config', 'messages.json'));
const env = {
  META_VERIFY_TOKEN: 'verif',
  META_APP_SECRET: 'secret',
  META_PAGE_ACCESS_TOKEN: 'x',
  WA_TEMPLATE_NAME: 'lead_bienvenue',
};

function setup({ waFails = false } = {}) {
  const calls = { wa: [], sms: [] };
  const providers = {
    fetchLead: async () => ({
      field_data: [
        { name: 'full_name', values: ['Marie Dupont'] },
        { name: 'phone_number', values: ['06 12 34 56 78'] },
        { name: 'votre_niveau', values: ['Débutant complet'] },
      ],
    }),
    sendWhatsAppTemplate: async (_e, to, params) => {
      if (waFails) throw new Error('HTTP 400');
      calls.wa.push({ to, params });
      return 'wamid.1';
    },
    sendSms: async (_e, to, text) => calls.sms.push({ to, text }),
  };
  const store = new Store(path.join(os.tmpdir(), `leads-test-${Math.random()}.json`));
  return { app: createApp({ env, store, config, providers, log: () => {} }), calls };
}

const leadEvent = { object: 'page', entry: [{ changes: [{ field: 'leadgen', value: { leadgen_id: 'L1', form_id: 'F1' } }] }] };

test('normalise les numeros FR', () => {
  assert.strictEqual(normalizePhone('06 12 34 56 78'), '33612345678');
  assert.strictEqual(normalizePhone('+33 6 12 34 56 78'), '33612345678');
  assert.strictEqual(normalizePhone('0033612345678'), '33612345678');
  assert.strictEqual(normalizePhone('abc'), null);
});

test('lead -> WhatsApp personnalise selon la reponse, une seule fois', async () => {
  const { app, calls } = setup();
  await app.handleEvent(leadEvent);
  await app.handleEvent(leadEvent);
  assert.strictEqual(calls.wa.length, 1);
  assert.strictEqual(calls.wa[0].to, '33612345678');
  assert.strictEqual(calls.wa[0].params[0], 'Marie');
  assert.strictEqual(calls.wa[0].params[1], 'vos premiers pas');
  assert.strictEqual(calls.sms.length, 0);
});

test('WhatsApp en echec differe -> SMS de secours une seule fois', async () => {
  const { app, calls } = setup();
  await app.handleEvent(leadEvent);
  const failed = {
    object: 'whatsapp_business_account',
    entry: [{ changes: [{ field: 'messages', value: { statuses: [{ id: 'wamid.1', status: 'failed', errors: [{ code: 131026 }] }] } }] }],
  };
  await app.handleEvent(failed);
  await app.handleEvent(failed);
  assert.strictEqual(calls.sms.length, 1);
  assert.match(calls.sms[0].text, /^Bonjour Marie, merci pour vos premiers pas\. Bonne nouvelle/);
});

test('WhatsApp refuse immediatement -> SMS', async () => {
  const { app, calls } = setup({ waFails: true });
  await app.handleEvent(leadEvent);
  assert.strictEqual(calls.sms.length, 1);
});

test('webhook HTTP : verification Meta et signature', async () => {
  const { app } = setup();
  const server = http.createServer(app.handler).listen(0);
  const base = `http://127.0.0.1:${server.address().port}/webhook`;
  try {
    let r = await fetch(`${base}?hub.mode=subscribe&hub.verify_token=verif&hub.challenge=42`);
    assert.strictEqual(await r.text(), '42');
    r = await fetch(`${base}?hub.mode=subscribe&hub.verify_token=faux&hub.challenge=42`);
    assert.strictEqual(r.status, 403);

    const body = JSON.stringify({ object: 'page', entry: [] });
    r = await fetch(base, { method: 'POST', body, headers: { 'x-hub-signature-256': 'sha256=bad' } });
    assert.strictEqual(r.status, 401);
    const sig = 'sha256=' + crypto.createHmac('sha256', 'secret').update(body).digest('hex');
    r = await fetch(base, { method: 'POST', body, headers: { 'x-hub-signature-256': sig } });
    assert.strictEqual(r.status, 200);
  } finally {
    server.close();
  }
});
