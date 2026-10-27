async function request(url, options) {
  const res = await fetch(url, options);
  const text = await res.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = text;
  }
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status} ${url.split('?')[0]}: ${typeof body === 'string' ? body : JSON.stringify(body)}`);
    err.body = body;
    throw err;
  }
  return body;
}

function graphUrl(env, p) {
  return `https://graph.facebook.com/${env.META_GRAPH_VERSION || 'v21.0'}/${p}`;
}

async function fetchLead(env, leadgenId) {
  const url = graphUrl(env, `${leadgenId}?fields=field_data,form_id,created_time`);
  return request(url, { headers: { Authorization: `Bearer ${env.META_PAGE_ACCESS_TOKEN}` } });
}

async function sendWhatsAppTemplate(env, to, params) {
  const body = {
    messaging_product: 'whatsapp',
    to,
    type: 'template',
    template: {
      name: env.WA_TEMPLATE_NAME,
      language: { code: env.WA_TEMPLATE_LANG || 'fr' },
      components: [{ type: 'body', parameters: params.map((text) => ({ type: 'text', text })) }],
    },
  };
  const res = await request(graphUrl(env, `${env.WA_PHONE_NUMBER_ID}/messages`), {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.WA_ACCESS_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.messages?.[0]?.id;
}

async function sendSms(env, to, text) {
  const provider = (env.SMS_PROVIDER || 'twilio').toLowerCase();
  if (provider === 'httpsms') {
    return request('https://api.httpsms.com/v1/messages/send', {
      method: 'POST',
      headers: { 'x-api-key': env.HTTPSMS_API_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: '+' + env.HTTPSMS_FROM.replace(/^\+/, ''), to: '+' + to, content: text }),
    });
  }
  if (provider === 'twilio') {
    const form = new URLSearchParams({ To: '+' + to, Body: text });
    if (env.TWILIO_MESSAGING_SERVICE_SID) form.set('MessagingServiceSid', env.TWILIO_MESSAGING_SERVICE_SID);
    else form.set('From', env.TWILIO_FROM);
    const auth = Buffer.from(`${env.TWILIO_ACCOUNT_SID}:${env.TWILIO_AUTH_TOKEN}`).toString('base64');
    return request(`https://api.twilio.com/2010-04-01/Accounts/${env.TWILIO_ACCOUNT_SID}/Messages.json`, {
      method: 'POST',
      headers: { Authorization: `Basic ${auth}`, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    });
  }
  throw new Error(`SMS_PROVIDER inconnu: ${provider}`);
}

module.exports = { fetchLead, sendWhatsAppTemplate, sendSms };
