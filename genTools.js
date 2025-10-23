function $(id){ return document.getElementById(id); }
function escapeHtml(s){
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
}

// delete characters
const delBtn = $('del_btn');
if (delBtn) delBtn.addEventListener('click', () => {
  const text = $('del_in').value || '';
  const chars = $('del_chars').value || '';
  const space = $('del_spaces').checked;
  const set = new Set(chars.split(''));
  if (space) set.add(' ');
  const out = Array.from(text).filter(ch => !set.has(ch)).join('');
  $('del_out').textContent = out;
});

// highlight strings
const hlBtn = $('hl_btn');
if (hlBtn) hlBtn.addEventListener('click', () => {
  const text = $('hl_in').value || '';
  const raw = $('hl_terms').value || '';
  const terms = raw.split(',').map(s => s.trim()).filter(Boolean);
  const caseSensitive = $('hl_case').checked;
  if (!terms.length){ $('hl_out').textContent = text; return; }
  const flags = caseSensitive ? 'g' : 'gi';
  const parts = [];
  let lastIndex = 0;
  // Build combined regex
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, r => '\\' + r);
  const re = new RegExp(terms.map(esc).join('|'), flags);
  let m;
  while ((m = re.exec(text))){
    parts.push(escapeHtml(text.slice(lastIndex, m.index)));
    parts.push('<span class="hl">' + escapeHtml(m[0]) + '</span>');
    lastIndex = re.lastIndex;
    if (m[0].length === 0) { re.lastIndex++; }
  }
  parts.push(escapeHtml(text.slice(lastIndex)));
  $('hl_out').innerHTML = parts.join('');
});

// compare two strings (character-by-character)
const cmpBtn = $('cmp_btn');
if (cmpBtn) cmpBtn.addEventListener('click', () => {
  const a = $('cmp_a').value || '';
  const b = $('cmp_b').value || '';
  const n = Math.max(a.length, b.length);
  const lineA = [];
  const lineB = [];
  for (let i=0;i<n;i++){
    const ca = a[i] ?? '';
    const cb = b[i] ?? '';
    if (ca === cb){
      const ch = escapeHtml(ca || '');
      lineA.push('<span class="ok">' + ch + '</span>');
      lineB.push('<span class="ok">' + escapeHtml(cb || '') + '</span>');
    } else {
      lineA.push('<span class="bad">' + escapeHtml(ca || '') + '</span>');
      lineB.push('<span class="bad2">' + escapeHtml(cb || '') + '</span>');
    }
  }
  const html = [
    '<div><span class="tag">A</span> ' + lineA.join('') + '</div>',
    '<div><span class="tag">B</span> ' + lineB.join('') + '</div>'
  ].join('\n');
  $('cmp_out').innerHTML = html;
});

// frequency analysis
const EN_FREQ = {
  A:8.17,B:1.49,C:2.78,D:4.25,E:12.70,F:2.23,G:2.02,H:6.09,I:6.97,J:0.15,K:0.77,L:4.03,
  M:2.41,N:6.75,O:7.51,P:1.93,Q:0.10,R:5.99,S:6.33,T:9.06,U:2.76,V:0.98,W:2.36,X:0.15,Y:1.97,Z:0.07
};
function letterCounts(text){
  const c = Array(26).fill(0);
  for (const ch of text.toUpperCase()){
    const k = ch.charCodeAt(0) - 65;
    if (k>=0 && k<26) c[k]++;
  }
  const total = c.reduce((a,b)=>a+b,0) || 1;
  const pct = c.map(x => x*100/total);
  return {counts:c, pct};
}
function sizeCanvas(canvas){
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const rect = canvas.getBoundingClientRect();
  const cw = Math.max(200, Math.floor(rect.width));
  const ch = Math.max(120, Math.floor(rect.height));
  if (canvas.width !== cw * dpr || canvas.height !== ch * dpr){
    canvas.width = cw * dpr;
    canvas.height = ch * dpr;
  }
  const ctx = canvas.getContext('2d');
  ctx.setTransform(1,0,0,1,0,0);
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.scale(dpr, dpr);
  return { ctx, W: cw, H: ch };
}
function drawChart(canvas, pct){
  const { ctx, W, H } = sizeCanvas(canvas);
  const cs = getComputedStyle(document.documentElement);
  const COL = {
    axis: cs.getPropertyValue('--axis').trim() || '#444',
    en: cs.getPropertyValue('--bar-en').trim() || '#999',
    me: cs.getPropertyValue('--bar-sample').trim() || '#4aa3ff',
    text: cs.getPropertyValue('--panel-text').trim() || '#ddd',
  };
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  const maxY = 14; // keeps scale stable and readable
  const m = { l: 44, r: 14, t: 18, b: 36 };

  // axes and grid
  ctx.strokeStyle = COL.axis;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(m.l, m.t); ctx.lineTo(m.l, H-m.b); ctx.lineTo(W-m.r, H-m.b);
  ctx.stroke();
  ctx.globalAlpha = 0.45;
  for (let y=2; y<=maxY; y+=2){
    const yy = H-m.b - (H-m.b-m.t) * (y/maxY);
    ctx.beginPath(); ctx.moveTo(m.l, yy); ctx.lineTo(W-m.r, yy); ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // y-axis ticks + labels
  ctx.fillStyle = COL.text;
  ctx.font = '11px system-ui, sans-serif';
  for (let y=0; y<=maxY; y+=2){
    const yy = H-m.b - (H-m.b-m.t) * (y/maxY);
    ctx.beginPath(); ctx.moveTo(m.l-4, yy); ctx.lineTo(m.l, yy); ctx.strokeStyle = COL.axis; ctx.stroke();
    ctx.fillText(String(y), 6, yy+3);
  }

  // bars
  const innerW = W - m.l - m.r;
  const innerH = H - m.t - m.b;
  const group = innerW / 26;
  const gap = Math.min(6, Math.max(3, group*0.2));
  const barW = Math.max(2, (group - gap) / 2);

  for (let i=0;i<26;i++){
    const x0 = m.l + i*group + 1;
    const en = EN_FREQ[letters[i]];
    const me = pct[i];
    const hEn = innerH * (en/maxY);
    const hMe = innerH * (me/maxY);
    // baseline (english)
    ctx.fillStyle = COL.en;
    ctx.fillRect(x0, H-m.b - hEn, barW, hEn);
    // sample
    ctx.fillStyle = COL.me;
    ctx.fillRect(x0+barW+gap/2, H-m.b - hMe, barW, hMe);
    // letter label (x ticks)
    ctx.fillStyle = COL.text;
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillText(letters[i], x0+1, H-14);
  }

  // legend
  ctx.fillStyle = COL.text;
  ctx.font = '12px system-ui, sans-serif';
  const legendY = m.t - 4;
  let lx = m.l + 4;
  ctx.fillStyle = COL.en; ctx.fillRect(lx, legendY-8, 10, 10); lx += 14;
  ctx.fillStyle = COL.text; ctx.fillText('english', lx, legendY);
  lx += 54;
  ctx.fillStyle = COL.me; ctx.fillRect(lx, legendY-8, 10, 10); lx += 14;
  ctx.fillStyle = COL.text; ctx.fillText('input', lx, legendY);

  // axis labels
  ctx.fillStyle = COL.text;
  ctx.font = '12px system-ui, sans-serif';
  ctx.save();
  ctx.translate(14, (H - m.b + m.t) / 2);
  ctx.rotate(-Math.PI/2);
  ctx.textAlign = 'center';
  ctx.fillText('Frequency (%)', 0, 0);
  ctx.restore();
  ctx.textAlign = 'center';
  ctx.fillText('Letters', (W - m.r + m.l) / 2, H - 6);
}
let lastPct = null;
const fqBtn = $('fq_btn');
if (fqBtn) fqBtn.addEventListener('click', () => {
  const t = $('fq_in').value || '';
  $('fq_status').textContent = 'working...';
  const {pct} = letterCounts(t);
  lastPct = pct;
  drawChart($('fq_canvas'), pct);
  const lines = [];
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  for (let i=0;i<26;i++){
    lines.push(letters[i]+': '+pct[i].toFixed(2)+'%  (en '+EN_FREQ[letters[i]].toFixed(2)+'%)');
  }
  $('fq_out').textContent = lines.join('  |  ');
  $('fq_status').textContent = 'done';
});
window.addEventListener('resize', () => { if (lastPct) drawChart($('fq_canvas'), lastPct); });

// reverse
const rvBtn = $('rv_btn');
if (rvBtn) rvBtn.addEventListener('click', () => {
  const t = $('rv_in').value || '';
  $('rv_out').textContent = Array.from(t).reverse().join('');
});
