// Renders the poster HTML files to PNG.
const { chromium } = require('playwright');
const path = require('path');
const jobs = [
  ['poster/poster.html', 'out/dor_9oct_story_1080x1920.png', 1080, 1920],
  ['poster/feed.html', 'out/dor_9oct_feed_1080x1350.png', 1080, 1350],
];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files'] });
  for (const [src, dst, width, height] of jobs) {
    const p = await b.newPage({ viewport: { width, height } });
    await p.goto('file://' + path.resolve(__dirname, '..', src));
    await p.evaluate(() => document.fonts.ready);
    await p.locator('.c').screenshot({ path: path.resolve(__dirname, '..', dst) });
    await p.close();
  }
  await b.close();
})();
