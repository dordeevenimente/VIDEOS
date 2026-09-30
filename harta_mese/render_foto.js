// Exportă harta pe fotografia reală: landscape 1920×1280, feed 1080×1350, story 1080×1920.
// Rulare: node harta_mese/render_foto.js   (Playwright + Chromium preinstalat)
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const base = 'file://' + path.join(__dirname, '/');
  const jobs = [
    { file: 'lista.html', hash: '', w: 1080, h: 1350, scale: 2, out: 'lista_mese_1080x1350.png' },
    { file: 'lista.html', hash: '#story', w: 1080, h: 1920, scale: 2, out: 'lista_mese_story_1080x1920.png' },
    { file: 'tiktok.html', hash: '#harta', w: 1080, h: 1920, scale: 2, out: 'tiktok_1_harta_mese_1080x1920.png' },
    { file: 'tiktok.html', hash: '#lista', w: 1080, h: 1920, scale: 2, out: 'tiktok_2_lista_mese_1080x1920.png' },
    { hash: '', w: 1536, h: 1024, scale: 1.25, out: 'harta_foto_planta_baja_1920x1280.png' },
    { hash: '#vert', w: 1080, h: 1350, scale: 2, out: 'harta_foto_planta_baja_1080x1350.png' },
    { hash: '#vert,story', w: 1080, h: 1920, scale: 2, out: 'harta_foto_planta_baja_story_1080x1920.png' },
    { file: 'lista_es.html', hash: '', w: 1080, h: 1350, scale: 2, out: 'es_lista_mesas_1080x1350.png' },
    { file: 'lista_es.html', hash: '#story', w: 1080, h: 1920, scale: 2, out: 'es_lista_mesas_story_1080x1920.png' },
    { file: 'lista_es.html', hash: '#tiktok', w: 1080, h: 1920, scale: 2, out: 'es_tiktok_2_lista_mesas_1080x1920.png' },
    { file: 'harta_foto_es.html', hash: '#vert,tiktok', w: 1080, h: 1920, scale: 2, out: 'es_tiktok_1_mapa_mesas_1080x1920.png' },
    { file: 'harta_foto_es.html', hash: '', w: 1536, h: 1024, scale: 1.25, out: 'es_mapa_mesas_1920x1280.png' },
    { file: 'harta_foto_es.html', hash: '#vert', w: 1080, h: 1350, scale: 2, out: 'es_mapa_mesas_1080x1350.png' },
    { file: 'harta_foto_es.html', hash: '#vert,story', w: 1080, h: 1920, scale: 2, out: 'es_mapa_mesas_story_1080x1920.png' },
  ];
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale });
    await page.goto(base + (j.file || 'harta_foto.html') + j.hash);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(__dirname, 'out', j.out), clip: { x: 0, y: 0, width: j.w, height: j.h } });
    await page.close();
  }
  await browser.close();
})();
