// Deterministic frame capture: seek(t) -> screenshot. No wall-clock animation.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = __dirname;
const MIME = { '.html':'text/html', '.woff2':'font/woff2', '.css':'text/css', '.js':'text/javascript' };

function serve(port) {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
      r.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream', 'cache-control':'no-store' });
      fs.createReadStream(f).pipe(r);
    }).listen(port, () => res(s));
  });
}

(async () => {
  const mode = process.argv[2] || 'probe';
  const PORT = Number(process.env.PORT || 8123);
  const srv = await serve(PORT);
  const browser = await chromium.launch({ args: ['--force-device-scale-factor=2', '--font-render-hinting=none'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const tlq = process.env.TL ? `?tl=${encodeURIComponent(process.env.TL)}` : '';
  await page.goto(`http://127.0.0.1:${PORT}/scenes.html${tlq}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__ready === true);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(600);

  const shoot = async (t, file) => {
    await page.evaluate(x => window.seek(x), t);
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.screenshot({ path: file, scale: 'css', animations: 'disabled' });
  };

  if (mode === 'probe') {
    const times = process.argv.slice(3).map(Number);
    fs.mkdirSync(path.join(ROOT, 'probe'), { recursive: true });
    for (const t of times) {
      await shoot(t, path.join(ROOT, 'probe', `t${String(t).replace('.', '_')}.png`));
      console.log('probe', t);
    }
  } else {
    const FPS = 30;
    const TL = process.env.TL || 'timeline.json';
    const DUR = JSON.parse(fs.readFileSync(path.join(ROOT, TL), 'utf8')).duration;
    const N = Math.round(FPS * DUR);
    const OUT = path.join(ROOT, process.env.FRAMES || 'frames');
    // RESUME=1 keeps already-rendered frames. The container can be recycled mid-run, and
    // a 24k-frame render is too expensive to restart from zero because of a restart.
    const RESUME = process.env.RESUME === '1';
    if (!RESUME) fs.rmSync(OUT, { recursive: true, force: true });
    fs.mkdirSync(OUT, { recursive: true });
    const have = RESUME ? new Set(fs.readdirSync(OUT)) : new Set();
    if (RESUME && have.size) console.log(`resuming: ${have.size} frames already on disk`);
    const t0 = Date.now();
    for (let i = 0; i < N; i++) {
      const name = String(i).padStart(5, '0') + '.png';
      if (have.has(name)) continue;
      await shoot(i / FPS, path.join(OUT, name));
      if (i % 150 === 0) {
        const el = (Date.now() - t0) / 1000;
        console.log(`${i}/${N}  ${el.toFixed(0)}s elapsed  eta ${(el / (i + 1) * (N - i) / 60).toFixed(1)}min`);
      }
    }
    console.log('done', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  await browser.close(); srv.close();
})();
