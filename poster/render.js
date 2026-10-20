// Renders catcape_lafabrica.html for Meta feed ads: 1080x1350 PNG + JPG, a 2x PNG,
// and a safe-area check image in the scratchpad.
const { chromium } = require('playwright');
const path = require('path');
const src = 'file://' + path.join(__dirname, 'catcape_lafabrica.html');
const out = (f) => path.join(__dirname, '..', 'out', f);
async function shot(b, scale, hash, opts) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
  await p.goto(src + hash);
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(300);
  await p.screenshot(opts);
  await p.close();
}
(async () => {
  const b = await chromium.launch();
  await shot(b, 1, '', { path: out('catcape_lafabrica_19dic_1080x1350.png') });
  await shot(b, 1, '', { path: out('catcape_lafabrica_19dic_1080x1350.jpg'), type: 'jpeg', quality: 95 });
  await shot(b, 2, '', { path: out('catcape_lafabrica_19dic_2160x2700.png') });
  if (process.env.GUIDES) await shot(b, 1, '#guides', { path: process.env.GUIDES });
  await b.close();
})();
