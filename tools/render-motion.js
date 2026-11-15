// Render fail HTML beranimasi (window.seek(t), window.DURATION) ke jujukan PNG.
// Guna: node tools/render-motion.js motion/cta-outro.html out_dir [fps] [--alpha]
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const [src, outDir, fpsArg] = process.argv.slice(2);
  const alpha = process.argv.includes('--alpha');
  const fps = Number(fpsArg) || 30;
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(src));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const dur = await p.evaluate(() => window.DURATION);
  const n = Math.round(dur * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate((t) => window.seek(t), i / fps);
    await p.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, '0')}.png`), omitBackground: alpha });
  }
  await b.close();
  console.log(`rendered ${n} frames`);
})();
