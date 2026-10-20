// Renders catcape_lafabrica.html to a 1080x1350 PNG.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'catcape_lafabrica.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, '..', 'out', 'catcape_lafabrica_19dic_1080x1350.png') });
  const p2 = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await p2.goto('file://' + path.join(__dirname, 'catcape_lafabrica.html'));
  await p2.waitForSelector('body[data-ready="1"]');
  await p2.waitForTimeout(300);
  await p2.screenshot({ path: path.join(__dirname, '..', 'out', 'catcape_lafabrica_19dic_2160x2700.png') });
  await b.close();
})();
