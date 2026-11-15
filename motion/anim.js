// Pembantu animasi deterministik: setiap frame dikira daripada masa t (saat).
const $ = (id) => document.getElementById(id);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const easeOut = (k) => 1 - Math.pow(1 - k, 3);
const easeInOut = (k) => k < .5 ? 4*k*k*k : 1 - Math.pow(-2*k + 2, 3) / 2;
const easeOutBack = (k) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3*Math.pow(k-1,3) + c1*Math.pow(k-1,2); };
const range = (t, a, b, ease = (k) => k) => ease(clamp((t - a) / (b - a)));
function makeParticles(host, n, seed) {
  let s = seed; const rnd = () => (s = (s * 9301 + 49297) % 233280) / 233280;
  const ps = [];
  for (let i = 0; i < n; i++) {
    const el = document.createElement('i'); const size = 2 + rnd()*5;
    el.style.width = el.style.height = size + 'px'; host.appendChild(el);
    ps.push({ el, x: rnd()*1080, y: rnd()*1920, vy: 8 + rnd()*22, ph: rnd()*6.28, a: .25 + rnd()*.6 });
  }
  return { update(t, k = 1) { for (const p of ps) {
    const y = (p.y - p.vy*t + 1920*4) % 1920, x = p.x + Math.sin(t*.6 + p.ph)*18;
    p.el.style.transform = `translate(${x}px, ${y}px)`; p.el.style.opacity = p.a * k * (.6 + .4*Math.sin(t*2 + p.ph)); } } };
}
