// Randează harta 3D a etajului: node harta_mese/3d/render.js
// Pornește un server HTTP local (modulele ES nu se încarcă din file://), apoi face screenshot cu Chromium (WebGL/SwiftShader).
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const root = path.join(__dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.woff2': 'font/woff2', '.webp': 'image/webp' };

const srv = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0, async () => {
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1440 }, deviceScaleFactor: 1.5 });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto(`http://localhost:${port}/3d/etaj.html` + (process.env.HASH || ''));
  await page.waitForFunction(() => document.body.dataset.ready === '1', null, { timeout: 180000 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.screenshot({ path: process.env.OUT || path.join(root, 'out', 'harta_3d_planta_alta_2880x2160.png') });
  await browser.close(); srv.close();
});
