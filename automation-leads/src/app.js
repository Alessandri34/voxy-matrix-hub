const crypto = require('crypto');
const { answersFromFieldData, buildMessages } = require('./messages');
const { normalizePhone } = require('./phone');

const PHONE_FIELDS = ['phone_number', 'telephone', 'numero_de_telephone', 'phone'];

function createApp({ env, store, config, providers, log = console.log }) {
  const formFilter = (env.META_FORM_IDS || '').split(',').map((s) => s.trim()).filter(Boolean);

  function verifySignature(rawBody, header) {
    if (!env.META_APP_SECRET) return true;
    if (!header || !header.startsWith('sha256=')) return false;
    const expected = crypto.createHmac('sha256', env.META_APP_SECRET).update(rawBody).digest('hex');
    const given = header.slice(7);
    return given.length === expected.length && crypto.timingSafeEqual(Buffer.from(given), Buffer.from(expected));
  }

  async function smsFallback(leadId, phone, text, reason) {
    try {
      await providers.sendSms(env, phone, text);
      store.setLead(leadId, { status: 'sms_envoye', reason });
      log(`[lead ${leadId}] SMS envoye (${reason})`);
    } catch (e) {
      store.setLead(leadId, { status: 'echec_sms', error: e.message });
      log(`[lead ${leadId}] ECHEC SMS: ${e.message}`);
    }
  }

  async function processLead(leadgenId, formId) {
    if (store.hasLead(leadgenId)) return log(`[lead ${leadgenId}] deja traite, ignore`);
    if (formFilter.length && formId && !formFilter.includes(String(formId))) return;
    store.setLead(leadgenId, { status: 'recu', formId });

    const lead = await providers.fetchLead(env, leadgenId);
    const answers = answersFromFieldData(lead.field_data);
    const rawPhone = PHONE_FIELDS.map((f) => answers[f]).find(Boolean);
    const phone = normalizePhone(rawPhone, env.DEFAULT_COUNTRY_CODE || '33');
    if (!phone) {
      store.setLead(leadgenId, { status: 'telephone_invalide', rawPhone });
      return log(`[lead ${leadgenId}] telephone invalide: ${rawPhone}`);
    }

    const msg = buildMessages(config, answers);
    log(`[lead ${leadgenId}] regle "${msg.regle}" -> ${phone}`);

    if (env.SMS_ONLY === 'true') return smsFallback(leadgenId, phone, msg.sms, 'mode SMS seul');

    try {
      const wamid = await providers.sendWhatsAppTemplate(env, phone, msg.whatsappParams);
      store.setMessage(wamid, { leadId: leadgenId, phone, sms: msg.sms });
      store.setLead(leadgenId, { status: 'whatsapp_envoye', wamid, phone, regle: msg.regle });
      log(`[lead ${leadgenId}] WhatsApp envoye (${wamid})`);
    } catch (e) {
      log(`[lead ${leadgenId}] WhatsApp refuse: ${e.message}`);
      await smsFallback(leadgenId, phone, msg.sms, 'whatsapp refuse');
    }
  }

  async function processStatus(status) {
    if (status.status !== 'failed') return;
    const info = store.getMessage(status.id);
    if (!info || info.fallbackDone) return;
    store.setMessage(status.id, { ...info, fallbackDone: true });
    const code = status.errors?.[0]?.code;
    await smsFallback(info.leadId, info.phone, info.sms, `whatsapp echec code ${code}`);
  }

  async function handleEvent(payload) {
    for (const entry of payload.entry || []) {
      for (const change of entry.changes || []) {
        try {
          if (payload.object === 'page' && change.field === 'leadgen') {
            await processLead(change.value.leadgen_id, change.value.form_id);
          } else if (payload.object === 'whatsapp_business_account' && change.field === 'messages') {
            for (const s of change.value.statuses || []) await processStatus(s);
            for (const m of change.value.messages || []) {
              log(`[reponse] ${m.from}: ${m.text?.body ?? '(' + m.type + ')'}`);
            }
          }
        } catch (e) {
          log(`[erreur] ${e.message}`);
        }
      }
    }
  }

  function handler(req, res) {
    const url = new URL(req.url, 'http://x');
    if (url.pathname === '/health') return res.writeHead(200).end('ok');
    if (url.pathname !== '/webhook') return res.writeHead(404).end();

    if (req.method === 'GET') {
      const ok = url.searchParams.get('hub.mode') === 'subscribe' && url.searchParams.get('hub.verify_token') === env.META_VERIFY_TOKEN;
      return ok ? res.writeHead(200).end(url.searchParams.get('hub.challenge')) : res.writeHead(403).end();
    }
    if (req.method !== 'POST') return res.writeHead(405).end();

    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      const raw = Buffer.concat(chunks);
      if (!verifySignature(raw, req.headers['x-hub-signature-256'])) return res.writeHead(401).end();
      let payload;
      try {
        payload = JSON.parse(raw.toString('utf8'));
      } catch {
        return res.writeHead(400).end();
      }
      // Meta retries if it doesn't get a fast 200, so ack first and process after.
      res.writeHead(200).end('EVENT_RECEIVED');
      handleEvent(payload);
    });
  }

  return { handler, handleEvent, processLead, verifySignature };
}

module.exports = { createApp };
