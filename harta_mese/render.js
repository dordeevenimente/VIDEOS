// Exportă harta în PNG: feed 1080×1350 și story 1080×1920, la 2× (device scale).
// Rulare: node harta_mese/render.js   (Playwright + Chromium preinstalat)
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.join(__dirname, 'harta.html');
  const jobs = [
    { hash: '', w: 1080, h: 1350, out: 'harta_mese_planta_baja_1080x1350.png' },
    { hash: '#story', w: 1080, h: 1920, out: 'harta_mese_planta_baja_story_1080x1920.png' },
  ];
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 2 });
    await page.goto(url + j.hash);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(__dirname, 'out', j.out), clip: { x: 0, y: 0, width: j.w, height: j.h } });
    await page.close();
  }
  await browser.close();
})();
