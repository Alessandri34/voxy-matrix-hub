function normalizePhone(raw, defaultCountryCode = '33') {
  if (!raw) return null;
  let p = String(raw).trim().replace(/[\s.\-()]/g, '');
  if (p.startsWith('00')) p = '+' + p.slice(2);
  if (p.startsWith('+')) p = p.slice(1);
  else if (p.startsWith('0')) p = defaultCountryCode + p.slice(1);
  if (!/^\d{8,15}$/.test(p)) return null;
  return p;
}

module.exports = { normalizePhone };
