const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + __dirname + '/poster.html');
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: __dirname + '/catcape_lafabrica_19dic_1080x1350.png' });
  await b.close();
})();
