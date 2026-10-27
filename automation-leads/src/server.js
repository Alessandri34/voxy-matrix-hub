const http = require('http');
const path = require('path');
const { createApp } = require('./app');
const { Store } = require('./store');
const { loadConfig } = require('./messages');
const providers = require('./providers');

const env = process.env;
const required = ['META_VERIFY_TOKEN', 'META_APP_SECRET', 'META_PAGE_ACCESS_TOKEN'];
if (env.SMS_ONLY !== 'true') required.push('WA_ACCESS_TOKEN', 'WA_PHONE_NUMBER_ID', 'WA_TEMPLATE_NAME');
const missing = required.filter((k) => !env[k]);
if (missing.length) {
  console.error(`Variables manquantes dans .env: ${missing.join(', ')}`);
  process.exit(1);
}

const root = path.join(__dirname, '..');
const store = new Store(env.STATE_FILE || path.join(root, 'data', 'state.json'));
const config = loadConfig(env.MESSAGES_FILE || path.join(root, 'config', 'messages.json'));
const app = createApp({ env, store, config, providers, log: (m) => console.log(new Date().toISOString(), m) });

const port = Number(env.PORT || 3000);
http.createServer(app.handler).listen(port, () => console.log(`Webhook leads pret sur :${port}/webhook`));
