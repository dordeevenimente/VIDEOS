// Randează coperta: node video_bribon/thumb/shot.js  → coperta_1080x1920.png (+ previzualizare grilă 4:5)
const path = require('path'); const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'thumb.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, '..', 'out', 'coperta_1080x1920.png') }); await b.close();
})();
