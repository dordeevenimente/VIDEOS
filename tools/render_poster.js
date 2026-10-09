// Randează grafica statică „Primul DOR” în PNG, în două formate.
// Utilizare: node tools/render_poster.js
const path = require('path');
const { chromium } = require('playwright');

const formats = { story: [1080, 1920], feed: [1080, 1350] };

(async () => {
  const browser = await chromium.launch();
  for (const [f, [w, h]] of Object.entries(formats)) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.resolve(__dirname, 'poster.html') + '?f=' + f);
    await page.evaluate(() => document.fonts.ready);
    const out = path.resolve(__dirname, '..', 'out', `primul_dor_bogdan_dlp_${w}x${h}.png`);
    await page.locator('#poster').screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
