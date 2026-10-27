const fs = require('fs');
const path = require('path');

const MAX_ENTRIES = 5000;

class Store {
  constructor(file) {
    this.file = file;
    this.data = { leads: {}, messages: {} };
    try {
      this.data = JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch {}
  }

  save() {
    for (const key of ['leads', 'messages']) {
      const ids = Object.keys(this.data[key]);
      if (ids.length > MAX_ENTRIES) {
        for (const id of ids.slice(0, ids.length - MAX_ENTRIES)) delete this.data[key][id];
      }
    }
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    const tmp = this.file + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(this.data));
    fs.renameSync(tmp, this.file);
  }

  hasLead(id) {
    return Boolean(this.data.leads[id]);
  }

  setLead(id, info) {
    this.data.leads[id] = { ...this.data.leads[id], ...info, at: new Date().toISOString() };
    this.save();
  }

  setMessage(wamid, info) {
    this.data.messages[wamid] = info;
    this.save();
  }

  getMessage(wamid) {
    return this.data.messages[wamid];
  }
}

module.exports = { Store };
