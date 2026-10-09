// Render poster.html to PNG: node poster/render.js
const path = require('path');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const [f, h] of [['feed', 1350], ['story', 1920]]) {
    await p.setViewportSize({ width: 1080, height: h });
    await p.goto('file://' + path.join(__dirname, 'poster.html') + '?f=' + f);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('#poster').screenshot({ path: path.join(__dirname, '..', 'out', `primul_dor_bogdan_dlp_${f}.png`) });
  }
  await b.close();
})();
