// Renders poster/poster.html to a 1080x1920 PNG.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, '../poster/poster.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.locator('.c').screenshot({ path: path.resolve(__dirname, '../out/dor_9oct_story_1080x1920.png') });
  await b.close();
})();
