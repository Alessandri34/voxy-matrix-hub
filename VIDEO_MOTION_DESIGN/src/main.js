/* VOXY Formation — timeline du film (GSAP, pilotée image par image)
   120 BPM : 1 temps = 0,5 s · 1 mesure = 2 s · toutes les coupes tombent sur une mesure. */
(() => {
  const DUR = 52;
  const RENDER = new URLSearchParams(location.search).has('render');
  if (RENDER) document.body.classList.add('render');

  gsap.defaults({ lazy: false, overwrite: false, ease: 'power3.out' });
  gsap.ticker.lagSmoothing(0);

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const tl = gsap.timeline({ paused: true });
  const procs = []; // animations procédurales : fonctions pures du temps

  /* ── Découpe des titres en mots (révélation mot à mot) ── */
  function split(node, cls) {
    [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(part => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
          const w = document.createElement('span'); w.className = 'w';
          const wi = document.createElement('span'); wi.className = 'wi' + (cls ? ' ' + cls : '');
          wi.textContent = part; w.appendChild(wi); frag.appendChild(w);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && n.tagName !== 'BR') {
        split(n, n.classList.contains('acc') ? ('accw ' + n.className.replace('acc', '')).trim() : cls);
      }
    });
  }
  $$('.h-xl,.h-xxl,.h-lg,.h-lg2,.h-md,.h-prog').forEach(h => split(h));

  /* ── Éléments générés ── */
  const pcols = [['#fecdd3', '#fb7185'], ['#fde68a', '#f59e0b'], ['#bae6fd', '#0284c7'], ['#ddd6fe', '#7c3aed'],
                 ['#bbf7d0', '#16a34a'], ['#fed7aa', '#ea580c'], ['#fbcfe8', '#db2777'], ['#e4e4e7', '#71717a']];
  const radii = ['50%', '14px', '50% 50% 12px 12px', '18px 18px 50% 50%', '14px', '50%', '50% 50% 12px 12px', '14px'];
  $('#s4-grid').innerHTML = pcols.map((c, i) =>
    `<div class="pcard"><div class="pimg" style="background:linear-gradient(150deg,${c[0]},${c[1]});--r:${radii[i]}"></div><u></u><u></u><span class="ptag">SEO ✓</span></div>`).join('');
  $('#s5-wave').innerHTML = '<i></i>'.repeat(23);
  $('#s6-sgrid').innerHTML = '<i></i>'.repeat(30);
  $('#s6-stars').innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 2.500l2.900 6.200 6.800.800-5 4.700 1.300 6.700L12 17.600l-6 3.300 1.300-6.700-5-4.700 6.800-.800z"/></svg>'.repeat(5);

  /* ── Aides ── */
  const nbsp = ' ';
  const fr = v => { const n = Math.round(v); return n >= 1000 ? Math.floor(n / 1000) + nbsp + String(n % 1000).padStart(3, '0') : String(n); };
  function reveal(sel, t, o = {}) {
    tl.fromTo($$('.wi', $(sel)), { yPercent: 55, opacity: 0, filter: 'blur(18px)' },
      { yPercent: 0, opacity: 1, filter: 'blur(0px)', duration: o.d || 0.9, stagger: o.s || 0.065 }, t);
  }
  function enter(sel, t, from = {}, o = {}) {
    tl.fromTo(sel, { opacity: 0, y: 36, filter: 'blur(12px)', ...from },
      { opacity: 1, x: 0, y: 0, scale: 1, filter: 'blur(0px)', duration: o.d || 0.8, stagger: o.s || 0, ease: o.ease || 'power3.out' }, t);
  }
  function count(sel, from, to, t, d, fmt, ease) {
    const el = $(sel), o = { v: from };
    el.innerHTML = fmt(from);
    tl.to(o, { v: to, duration: d, ease: ease || 'power2.inOut', onUpdate: () => { el.innerHTML = fmt(o.v); } }, t);
  }
  function scene(id, tin, tout, o = {}) {
    const out = o.out || 0.35;
    tl.set(id, { autoAlpha: 1 }, tin);
    tl.fromTo(id + ' > .cam', { scale: 1 }, { scale: o.push || 1.045, duration: tout - tin, ease: 'none' }, tin);
    if (!o.keep) {
      tl.to(id, { opacity: 0, scale: 1.06, filter: 'blur(22px)', duration: out, ease: 'power2.in' }, tout - out);
      tl.set(id, { autoAlpha: 0 }, tout);
    }
  }
  const ORBS = ['cool', 'red', 'amber', 'orange', 'rose', 'sky', 'green'];
  function orbs(t, map, d = 0.9) {
    ORBS.forEach(k => tl.to('.orb-' + k, { opacity: map[k] || 0, duration: d, ease: 'power2.inOut' }, t));
  }
  function flash(t, a = 0.5, d = 0.7) {
    tl.fromTo('#flash', { opacity: 0 }, { opacity: a, duration: 0.05, ease: 'none' }, t)
      .to('#flash', { opacity: 0, duration: d, ease: 'power2.out' }, t + 0.05);
  }
  function rings(sel, t, o = {}) {
    $$(sel).forEach((r, i) => tl.fromTo(r, { scale: o.from || 0.2, opacity: o.a || 0.7 },
      { scale: o.to || 2.4, opacity: 0, duration: o.d || 1.5, ease: 'power2.out', immediateRender: false }, t + i * 0.16));
  }

  gsap.set('.abs-pill,#s5-qual', { xPercent: -50 });

  /* ════════ S0 · HOOK (0 → 4) ════════ */
  orbs(0, { cool: 0.9 }, 0.01);
  scene('#s0', 0, 4);
  reveal('#s0-h1', 0.12, { s: 0.075 });
  tl.to('#s0-h1', { y: -235, scale: 0.56, opacity: 0.55, duration: 0.9, ease: 'power3.inOut' }, 1.7);
  enter('#s0-meter', 1.95, { y: 60, scale: 0.94 }, { d: 0.8 });
  tl.to('#s0-fill', { width: '0%', filter: 'hue-rotate(-42deg) saturate(1.5)', duration: 1.45, ease: 'power2.inOut' }, 2.3);
  count('#s0-pct', 100, 0, 2.3, 1.45, v => Math.round(v) + nbsp + '%');
  tl.to('#s0-pct', { color: '#ff5a5f', duration: 0.5 }, 3.2);
  orbs(2.6, { cool: 0.4, red: 0.7 }, 1.2);
  reveal('#s0-h2', 2.95, { s: 0.06, d: 0.7 });
  tl.to('#s0-meter', { borderColor: 'rgba(239,68,68,.55)', duration: 0.3 }, 3.7)
    .to('#s0-meter', { keyframes: { x: [0, -14, 12, -8, 5, 0] }, duration: 0.4, ease: 'none' }, 3.72);

  /* ════════ S1 · L'AGENCE (4 → 8) ════════ */
  orbs(4, { red: 0.85, cool: 0.25 });
  scene('#s1', 4, 8, { out: 0.3 });
  enter('#s1-eb', 4.1, { y: 20 });
  reveal('#s1-h', 4.18, { s: 0.09 });
  $$('#s1-list li').forEach((li, i) => {
    tl.fromTo(li, { opacity: 0, x: -40, filter: 'blur(8px)' }, { opacity: 1, x: 0, filter: 'blur(0px)', duration: 0.6 }, 5 + i * 0.5);
    tl.fromTo(li.querySelector('svg'), { scale: 0, rotation: -90 }, { scale: 1, rotation: 0, duration: 0.5, ease: 'back.out(2.5)' }, 5.05 + i * 0.5);
  });
  tl.fromTo('#s1-tilt', { rotationY: -40, rotationX: 16, rotationZ: 7, x: 280, y: 60, opacity: 0 },
    { rotationY: -17, rotationX: 8, rotationZ: 2, x: 0, y: 0, opacity: 1, duration: 1.4, ease: 'power3.out' }, 4.0);
  tl.fromTo('#s1-tilt', { rotationY: -17, rotationX: 8 }, { rotationY: -9, rotationX: 4, duration: 2.6, ease: 'sine.inOut', immediateRender: false }, 5.4);
  tl.fromTo('.inv-row', { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.5, stagger: 0.14 }, 4.7);
  count('#s1-total', 0, 5000, 5.0, 1.2, fr, 'power2.out');
  gsap.set('#s1-stamp', { rotation: -11, z: 60 });
  tl.fromTo('#s1-stamp', { scale: 3, opacity: 0, rotation: -28 }, { scale: 1, opacity: 1, rotation: -11, duration: 0.26, ease: 'power3.in' }, 6.24);
  tl.to('#s1-inv', { keyframes: { x: [0, -10, 8, -5, 0], y: [0, 8, -4, 2, 0] }, duration: 0.35, ease: 'none' }, 6.5);
  tl.to('#s1-tilt', { y: 120, rotationZ: 9, duration: 0.5, ease: 'power2.in' }, 7.5);

  /* ════════ S2 · RÉVÉLATION (8 → 12) ════════ */
  orbs(7.9, { amber: 1, orange: 0.45 }, 0.5);
  flash(8.0, 0.85, 0.9);
  scene('#s2', 8, 12);
  rings('#s2 .ring', 8.0);
  tl.fromTo('#s2-x', { scale: 1.55, opacity: 0, filter: 'blur(34px)' }, { scale: 1, opacity: 1, filter: 'blur(0px)', duration: 1.2, ease: 'expo.out' }, 8.0);
  tl.fromTo('#s2-x', { backgroundPosition: '100% 0' }, { backgroundPosition: '0% 0', duration: 1.7, ease: 'power2.inOut' }, 8.25);
  tl.fromTo('#s2-f', { opacity: 0, letterSpacing: '1.7em', filter: 'blur(10px)' }, { opacity: 1, letterSpacing: '0.92em', filter: 'blur(0px)', duration: 1.1 }, 8.4);
  tl.fromTo('#s2-pill', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.7 }, 8.85);
  tl.to('#s2-pill', { opacity: 0, y: -20, duration: 0.4, ease: 'power2.in' }, 9.55);
  tl.to('#s2-logo', { scale: 0.3, y: -165, duration: 0.95, ease: 'power3.inOut' }, 9.6);
  reveal('#s2-l1', 10.0, { s: 0.07 });
  reveal('#s2-l2', 10.75, { s: 0.045, d: 0.8 });

  /* ════════ S3 · 0 € (12 → 16) ════════ */
  orbs(12, { amber: 0.75, orange: 0.9 });
  scene('#s3', 12, 16);
  enter('#s3-eb', 12.1, { y: 20 });
  tl.fromTo('#s3-giant', { scale: 0.82, opacity: 0, filter: 'blur(30px)' }, { scale: 1, opacity: 1, filter: 'blur(0px)', duration: 0.7, ease: 'power3.out' }, 12.0);
  count('#s3-num', 5000, 0, 12.4, 1.1, v => fr(v).replace(nbsp, '<i class="sp"></i>'), 'power2.in');
  tl.fromTo('#s3-giant', { scale: 1.2 }, { scale: 1, duration: 0.9, ease: 'elastic.out(1,0.55)', immediateRender: false }, 13.5);
  flash(13.5, 0.55, 0.7);
  rings('#s3 .ring', 13.5, { a: 0.8, to: 2.6 });
  reveal('#s3-h', 13.95, { s: 0.05, d: 0.8 });
  tl.fromTo('#s3-chips .pill', { opacity: 0, y: 26, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.13, ease: 'back.out(1.6)' }, 14.45);
  tl.fromTo('#s3-fine', { opacity: 0 }, { opacity: 1, duration: 0.6 }, 14.9);

  /* ════════ Scènes programmes ════════ */
  function prog(id, t0) {
    scene(id, t0, t0 + 6);
    const q = s => id + ' ' + s;
    enter(q('.tagline'), t0 + 0.1, { y: 20 });
    reveal(q('.h-prog'), t0 + 0.18, { s: 0.1 });
    enter(q('.prog-sub'), t0 + 0.6, { y: 24 });
    $$(q('.bul li')).forEach((li, i) => {
      tl.fromTo(li, { opacity: 0, x: -40, filter: 'blur(8px)' }, { opacity: 1, x: 0, filter: 'blur(0px)', duration: 0.6 }, t0 + 1 + i * 0.5);
      tl.fromTo(li.querySelector('i'), { scale: 0 }, { scale: 1, duration: 0.5, ease: 'back.out(2.6)' }, t0 + 1.06 + i * 0.5);
    });
    tl.fromTo(q('.price'), { opacity: 0, y: 26, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'back.out(1.5)' }, t0 + 2.6);
    const tilt = q('.tilt');
    tl.fromTo(tilt, { rotationY: -38, rotationX: 14, x: 300, scale: 0.88, opacity: 0 },
      { rotationY: -21, rotationX: 8, x: 0, scale: 1, opacity: 1, duration: 1.4, ease: 'power3.out' }, t0);
    tl.fromTo(tilt, { rotationY: -21, rotationX: 8 }, { rotationY: -10, rotationX: 4, duration: 4.6, ease: 'sine.inOut', immediateRender: false }, t0 + 1.4);
  }
  const pop = (sel, t, from = {}, o = {}) => tl.fromTo(sel, { opacity: 0, scale: 0.82, y: 30, ...from },
    { opacity: 1, scale: 1, x: 0, y: 0, duration: o.d || 0.7, ease: o.ease || 'back.out(1.7)', stagger: o.s || 0 }, t);

  /* S4 · E-COM COMMANDO (16 → 22) */
  orbs(16, { rose: 1, amber: 0.15 });
  prog('#s4', 16);
  tl.fromTo('#s4 .pcard', { opacity: 0, y: 34, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.07 }, 16.55);
  tl.fromTo('#s4 .ptag', { scale: 0 }, { scale: 1, duration: 0.4, ease: 'back.out(3)', stagger: 0.14 }, 17.5);
  count('#s4-count', 0, 50, 17.5, 1.9, v => String(Math.round(v)).padStart(2, '0'), 'power1.inOut');
  pop('#s4-flow', 18.5, { y: -30 });
  pop('#s4-toast', 19.5, { x: -70, y: 0 });
  procs.push(t => { const p = ((t - 18.5) * 0.85) % 1; gsap.set('#s4-pulse', { x: (p < 0 ? 0 : p) * 322, opacity: Math.sin(Math.PI * Math.max(p, 0)) ** 0.4 }); });

  /* S5 · OUTBOUND HYBRIDE (22 → 28) */
  orbs(22, { sky: 1, amber: 0.3 });
  prog('#s5', 22);
  pop('#s5-pipe', 22.7, { x: -50, y: 0 });
  const bh = [0.3, 0.42, 0.36, 0.55, 0.66, 0.82, 1];
  $$('#s5-bars i').forEach((b, i) => tl.fromTo(b, { scaleY: 0 }, { scaleY: bh[i], duration: 0.7, ease: 'power3.out' }, 22.95 + i * 0.08));
  tl.fromTo('#s5-notif', { y: -110, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'back.out(1.5)' }, 22.5);
  tl.fromTo('#s5-timer', { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.5 }, 22.9);
  tl.fromTo('#s5-arc', { strokeDashoffset: 553 }, { strokeDashoffset: 0, duration: 1.2, ease: 'none' }, 23.1);
  count('#s5-sec', 0, 4, 23.1, 1.2, v => v.toFixed(1).replace('.', ','), 'none');
  tl.to('#s5-timer', { opacity: 0, scale: 1.15, filter: 'blur(10px)', duration: 0.3, ease: 'power2.in' }, 24.4);
  tl.fromTo('#s5-call', { opacity: 0, scale: 0.86, filter: 'blur(10px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.6 }, 24.6);
  tl.fromTo('#s5-qual', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(2.2)' }, 25.9);
  pop('#s5-rdv', 26.4, { x: 90, y: 0 });
  const wave = $$('#s5-wave i'), corb = $$('#s5 .call-orb i');
  procs.push(t => {
    const talk = 0.55 + 0.45 * Math.sin(t * 2.3) * Math.sin(t * 5.1 + 1);
    wave.forEach((b, i) => {
      const env = Math.sin(Math.PI * (i + 0.5) / wave.length) ** 0.8;
      const h = 12 + 74 * env * talk * Math.abs(Math.sin(t * 9.5 + i * 0.83) * Math.cos(t * 4.3 - i * 0.41));
      b.style.height = h.toFixed(1) + 'px';
    });
    corb.forEach((r, i) => { const p = ((t * 0.7 + i * 0.5) % 1); gsap.set(r, { scale: 1 + p * 0.8, opacity: 0.7 * (1 - p) }); });
  });

  /* S6 · DRIVE-TO-STORE (28 → 34) */
  orbs(28, { green: 1, amber: 0.25 });
  prog('#s6', 28);
  tl.fromTo('#s6-pl', { x: 0, rotationZ: 0, scale: 0.86, z: -160 }, { x: -205, rotationZ: -8, scale: 0.86, z: -160, duration: 1.1, ease: 'power3.out' }, 28.35);
  tl.fromTo('#s6-pr', { x: 0, rotationZ: 0, scale: 0.86, z: -160 }, { x: 205, rotationZ: 8, scale: 0.86, z: -160, duration: 1.1, ease: 'power3.out' }, 28.35);
  pop('#s6-shorts', 29.0, { x: -50, y: 0 });
  tl.fromTo('#s6-sgrid i', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(2.5)', stagger: 0.06 }, 29.3);
  count('#s6-count', 0, 30, 29.3, 1.8, v => String(Math.round(v)), 'none');
  pop('#s6-maps', 30.5, { x: 70, y: 0 });
  tl.fromTo('#s6-pin', { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'bounce.out' }, 31.0);
  tl.fromTo('#s6-pulse', { scale: 0.3, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 0.9, ease: 'power2.out', immediateRender: false }, 31.25);
  tl.fromTo('#s6-stars svg', { scale: 0, rotation: -70 }, { scale: 1, rotation: 0, duration: 0.4, ease: 'back.out(3)', stagger: 0.16 }, 31.5);
  pop('#s6-plan', 32.3, { y: 50 });
  tl.fromTo('#s6-planfill', { width: '0%' }, { width: '100%', duration: 1.0, ease: 'power2.inOut' }, 32.6);
  count('#s6-days', 0, 90, 32.6, 1.0, v => String(Math.round(v)), 'power2.inOut');
  const subs = $$('#s6-subs span');
  procs.push(t => {
    const k = Math.floor(Math.max(0, t - 28.6) * 3.2) % 4;
    subs.forEach((s, i) => s.classList.toggle('on', i === k));
    $('#s6-vp').style.width = Math.min(100, Math.max(0, (t - 28) / 6 * 100)) + '%';
  });

  /* ════════ S7 · PROCESSUS (34 → 40) ════════ */
  orbs(34, { amber: 0.7, cool: 0.5 });
  scene('#s7', 34, 40);
  enter('#s7-eb', 34.1, { y: 20 });
  reveal('#s7-h', 34.15, { s: 0.07 });
  tl.fromTo('#s7 .rail', { opacity: 0, scaleX: 0.6 }, { opacity: 1, scaleX: 1, duration: 0.7 }, 34.4);
  tl.fromTo('#s7-rail', { width: '0%' }, { width: '100%', duration: 3, ease: 'none' }, 35.0);
  $$('#s7 .node').forEach((n, i) => {
    tl.to(n, { backgroundColor: '#fbbf24', borderColor: '#fde68a', scale: 1.3, boxShadow: '0 0 0 8px rgba(251,191,36,.16), 0 0 30px #fbbf24', duration: 0.35, ease: 'back.out(3)' }, 35.0 + i);
  });
  $$('#s7 .step').forEach((s, i) => {
    tl.fromTo(s, { opacity: 0, y: 70, scale: 0.92, filter: 'blur(12px)' }, { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)', duration: 0.75, ease: 'power3.out' }, 34.98 + i);
    if (i < 3) tl.to(s, { opacity: 0.55, duration: 0.5 }, 35.9 + i);
  });
  tl.to('#s7 .step', { opacity: 1, duration: 0.5, stagger: 0.06 }, 38.9);

  /* ════════ S8 · PREUVES (40 → 44) ════════ */
  orbs(40, { amber: 0.9, orange: 0.7 });
  scene('#s8', 40, 44);
  enter('#s8-eb', 40.0, { y: 20 }, { d: 0.5 });
  $$('#s8 .stat').forEach((s, i) => {
    const t = 40 + i;
    tl.fromTo(s.querySelector('b'), { scale: 1.7, opacity: 0, filter: 'blur(26px)' }, { scale: 1, opacity: 1, filter: 'blur(0px)', duration: 0.6, ease: 'expo.out' }, t);
    tl.fromTo(s.querySelector('span'), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5 }, t + 0.22);
    flash(t, 0.32, 0.5);
  });
  tl.fromTo('#s8 .div', { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.6, stagger: 1 }, 40.6);
  tl.fromTo('#s8-fine', { opacity: 0 }, { opacity: 1, duration: 0.6 }, 42.5);

  /* ════════ S9 · APPEL À L'ACTION (44 → 52) ════════ */
  orbs(44, { amber: 1, orange: 0.8 });
  scene('#s9', 44, 52, { keep: true, push: 1.03 });
  tl.fromTo('#s9-pill', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6 }, 44.1);
  reveal('#s9-h', 44.2, { s: 0.11 });
  tl.fromTo('#s9-btn', { scale: 0.6, opacity: 0, y: 50 }, { scale: 1, opacity: 1, y: 0, duration: 0.85, ease: 'back.out(1.8)' }, 45.4);
  enter('#s9-sub', 45.95, { y: 20 });
  tl.to('#s9-btn', { scale: 1.035, duration: 0.6, ease: 'sine.inOut', yoyo: true, repeat: 1 }, 46.4);
  gsap.set('#cursor', { x: 1560, y: 1020, transformOrigin: '20% 10%' });
  tl.to('#cursor', { opacity: 1, duration: 0.25 }, 46.7);
  tl.to('#cursor', { x: 1110, y: 758, duration: 1.15, ease: 'power3.inOut' }, 46.7);
  // clic
  tl.to('#cursor', { scale: 0.8, duration: 0.09, ease: 'power2.in', yoyo: true, repeat: 1 }, 47.94);
  tl.to('#s9-btn', { scale: 0.94, duration: 0.1, ease: 'power2.in' }, 47.96)
    .to('#s9-btn', { scale: 1, duration: 0.7, ease: 'elastic.out(1,0.45)' }, 48.06);
  tl.fromTo('#s9-rip', { scale: 0, opacity: 0.8 }, { scale: 9, opacity: 0, duration: 0.8, ease: 'power2.out' }, 48.0);
  gsap.set('#s9 .ring', { y: 220 });
  rings('#s9 .ring', 48.0, { a: 0.8, to: 2.4 });
  flash(48.0, 0.45, 0.7);
  tl.to('#cursor', { opacity: 0, x: 1210, y: 880, duration: 0.6, ease: 'power2.in' }, 48.35);
  tl.to('#s9-pill', { opacity: 0, y: -20, duration: 0.4, ease: 'power2.in' }, 48.3);
  tl.to('#s9-group', { scale: 0.8, y: 78, duration: 1.0, ease: 'power3.inOut' }, 48.4);
  tl.fromTo('#s9-logo', { opacity: 0, y: -30, filter: 'blur(14px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9 }, 48.8);
  tl.fromTo('#fade', { opacity: 0 }, { opacity: 1, duration: 0.55, ease: 'power1.in' }, 51.42);
  tl.set({}, {}, DUR);

  /* ── Procédural global : dérive des halos, grille, grain ── */
  const orbEls = $$('.orb');
  procs.push(t => {
    orbEls.forEach((o, i) => gsap.set(o, { x: Math.sin(t * 0.33 + i * 1.7) * 90, y: Math.cos(t * 0.27 + i * 2.3) * 60 }));
    $('#grid').style.backgroundPosition = `0px ${(-t * 7).toFixed(2)}px`;
    const f = Math.round(t * 60), h = (f * 2654435761) >>> 0;
    $('#grain').style.transform = `translate(${(h % 173)}px,${((h >>> 8) % 151)}px)`;
  });

  window.__dur = DUR;
  window.__seek = t => { tl.seek(Math.min(Math.max(t, 0), DUR), false); procs.forEach(f => f(t)); };
  window.__ready = document.fonts.ready.then(() => { window.__seek(0); return true; });

  /* ── Aperçu temps réel dans le navigateur ── */
  if (!RENDER) {
    const fit = () => { const s = Math.min(innerWidth / 1920, innerHeight / 1080); const st = $('#stage');
      st.style.transform = `translate(${(innerWidth - 1920 * s) / 2}px,${(innerHeight - 1080 * s) / 2}px) scale(${s})`; };
    addEventListener('resize', fit); fit();
    const audio = new Audio('../out/voxy-soundtrack.m4a');
    let raf;
    $('#play').onclick = () => {
      cancelAnimationFrame(raf); audio.currentTime = 0; audio.play().catch(() => {});
      const t0 = performance.now();
      const loop = () => { const t = audio.paused ? (performance.now() - t0) / 1000 : audio.currentTime; window.__seek(t); if (t < DUR) raf = requestAnimationFrame(loop); };
      loop();
    };
    const q = new URLSearchParams(location.search).get('t');
    if (q) window.__ready.then(() => window.__seek(parseFloat(q)));
  }
})();
