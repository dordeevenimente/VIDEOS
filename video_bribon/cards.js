// Randează straturile de text (PNG transparent 1080×1920): node video_bribon/cards.js
const path = require('path');
const { chromium } = require('playwright');
const IDS = ['hook', 'venue', 'gold', 'plat', 'vip', 'prive', 'bal', 'end'];

(async () => {
  const browser = await chromium.launch();
  for (const id of IDS) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await page.goto('file://' + path.join(__dirname, 'cards.html') + '#' + id);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(__dirname, 'cards', id + '.png'), omitBackground: true });
    await page.close();
  }
  await browser.close();
})();
