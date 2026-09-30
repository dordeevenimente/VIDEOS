// Exportă harta pe fotografia reală: landscape 1920×1280, feed 1080×1350, story 1080×1920.
// Rulare: node harta_mese/render_foto.js   (Playwright + Chromium preinstalat)
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.join(__dirname, 'harta_foto.html');
  const jobs = [
    { hash: '', w: 1536, h: 1024, scale: 1.25, out: 'harta_foto_planta_baja_1920x1280.png' },
    { hash: '#vert', w: 1080, h: 1350, scale: 2, out: 'harta_foto_planta_baja_1080x1350.png' },
    { hash: '#vert,story', w: 1080, h: 1920, scale: 2, out: 'harta_foto_planta_baja_story_1080x1920.png' },
  ];
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale });
    await page.goto(url + j.hash);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(__dirname, 'out', j.out), clip: { x: 0, y: 0, width: j.w, height: j.h } });
    await page.close();
  }
  await browser.close();
})();
