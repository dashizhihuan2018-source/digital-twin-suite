import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.argv[2] || 'http://127.0.0.1:18867/';
const out = process.argv[3] || '.work/browser-qa';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: process.env.NO_PROXY_QA === '1' ? ['--no-proxy-server'] : [] });
const report = { base, humanOnlyPixelReview: false, screenshots: 'all HUMAN-ONLY media and video elements are masked before capture', viewports: [], links: [] };
try {
  const context = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await context.newPage();
  const browserGet = url => page.evaluate(async url => {
    const response = await fetch(url);
    return { status: response.status, bytes: (await response.arrayBuffer()).byteLength };
  }, url);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => Promise.race([document.fonts.ready, new Promise((_, reject) => setTimeout(() => reject(Error('font load timeout')), 45000))]));
  report.titleFontLoaded = await page.evaluate(() => document.fonts.check('700 40px "Twin Display"'));
  assert.ok(report.titleFontLoaded);

  report.publicCopy = await page.evaluate(() => {
    const node = document.querySelector('main').cloneNode(true);
    node.querySelectorAll('details,script,style').forEach(x => x.remove());
    const text = node.textContent;
    return { internalNotes: ['HUMAN-ONLY','当前记录','V3.5.5','本轮','未重新渲染','版本、哈希'].filter(x => text.includes(x)) };
  });
  assert.deepEqual(report.publicCopy.internalNotes, []);
  report.skillLinks = await page.locator('a[href^="skills/"][href$="/index.html"]').evaluateAll(nodes => nodes.map(n => n.getAttribute('href')));
  assert.equal(new Set(report.skillLinks).size, 9);
  assert.equal(report.skillLinks.filter(x => x.includes('product-launch-website')).length, 1);
  await page.waitForFunction(() => {
    const image = document.querySelector('.hero-poster img');
    const video = document.querySelector('#fpv-video');
    return image.complete && image.naturalWidth === 1600 && video.readyState >= 1 && video.dataset.bufferReady === 'true';
  }, null, { timeout: 60000 });
  report.poster = await page.locator('.hero-poster img').evaluate(image => ({ width: image.naturalWidth, height: image.naturalHeight }));
  assert.deepEqual(report.poster, { width: 1600, height: 2400 });
  report.video = await page.locator('#fpv-video').evaluate(async video => {
    video.muted = true;
    await video.play();
    return { width: video.videoWidth, height: video.videoHeight, duration: video.duration, startTime: video.currentTime, controls: video.controls };
  });
  await page.waitForFunction(start => document.querySelector('#fpv-video').currentTime > start + 0.5, report.video.startTime);
  report.video.afterTime = await page.locator('#fpv-video').evaluate(video => { video.pause(); video.currentTime = 20; return video.currentTime; });
  await page.waitForFunction(() => { const v = document.querySelector('#fpv-video'); return !v.seeking && v.readyState >= 2; });
  report.video.seekedTime = await page.locator('#fpv-video').evaluate(video => video.currentTime);
  report.mediaRange = await page.evaluate(async () => {
    const r = await fetch('assets/changfeng-r5-demo.mp4', { headers: { Range: 'bytes=0-1023' } });
    await r.arrayBuffer();
    return { status: r.status, contentRange: r.headers.get('content-range') };
  });
  report.video.buffer = await page.locator('#fpv-video').evaluate(v => ({ source: v.src.startsWith('blob:') ? 'verified-byte-buffer' : 'remote', sha256: v.dataset.verifiedSha256 }));
  assert.equal(report.video.buffer.sha256, '9dac1ef965277857d1496a6af21bae1d24e487268c0f9c2430cedaa351946f9c');
  assert.ok(Math.abs(report.video.seekedTime - 20) < 0.2, 'seek did not reach 20 seconds');
  report.video.seeked = true;
  assert.equal(report.video.width, 1920); assert.equal(report.video.height, 1080);
  assert.ok(Math.abs(report.video.duration - 30.733333) < 0.1);
  assert.ok(report.video.controls);
  report.video.playbackAdvanced = true;
  const product = page.locator('#product-video');
  await product.evaluate(video => { video.muted = true; video.load(); });
  await page.waitForFunction(() => document.querySelector('#product-video').readyState >= 1, null, { timeout: 90000 });
  report.productFilm = await product.evaluate(async video => {
    await video.play();
    return {width:video.videoWidth,height:video.videoHeight,duration:video.duration,controls:video.controls,startTime:video.currentTime,source:new URL(video.querySelector('source').src).pathname};
  });
  assert.equal(report.productFilm.width,3840); assert.equal(report.productFilm.height,2160);
  assert.ok(Math.abs(report.productFilm.duration-35.833334)<0.1);
  await page.waitForFunction(start => document.querySelector('#product-video').currentTime>start+0.5,report.productFilm.startTime);
  await product.evaluate(video => {video.pause();video.currentTime=24.5;});
  await page.waitForFunction(() => {const v=document.querySelector('#product-video');return !v.seeking && v.readyState>=2;},null,{timeout:60000});
  report.productFilm.seekedTime=await product.evaluate(v=>v.currentTime);
  assert.ok(Math.abs(report.productFilm.seekedTime-24.5)<0.2);
  report.productFilm.playbackAdvanced=true;
  // Inspect layout with exact approved media, but never send its pixels to AI.
  for (const width of [1440, 768, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.evaluate(() => window.scrollTo(0, 0));
    const geometry = await page.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth, h1: document.querySelector('h1').getBoundingClientRect().width }));
    assert.ok(geometry.page <= width, 'horizontal overflow at ' + width);
    if (width === 390) {
      await page.locator('.menu-toggle').click();
      assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'), 'true');
      await page.locator('#navigation a[href="#skills"]').click();
      assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'), 'false');
    }
    await page.locator('.skill details').first().locator('summary').click();
    assert.ok(await page.locator('.skill details').first().getAttribute('open') !== null);
    await page.locator('.skill details').first().locator('summary').click();
    const screenshot = out + '/layout-' + width + '-masked.png';
    await page.screenshot({ path: screenshot, fullPage: true, mask: [page.locator('[data-human-only]'), page.locator('video')], maskColor: '#a7b8c4' });
    report.viewports.push({ ...geometry, width, screenshot, overflow: false });
  }
  await page.locator('#copy-install').click();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  assert.equal(copied, 'python3 scripts/install.py\npython3 scripts/install.py --apply');
  report.clipboard = true;
  const localUrls = await page.locator('a[href],script[src],link[href],img[src],source[src]').evaluateAll(nodes => [...new Set(nodes.map(n => n.href || n.src).filter(Boolean))]);
  for (const value of localUrls) {
    const url = new URL(value, base);
    if (url.origin !== new URL(base).origin || (url.hash && url.pathname === new URL(base).pathname)) continue;
    const response = await browserGet(url.href);
    assert.equal(response.status, 200, url.href);
    report.links.push({ path: url.pathname, status: response.status });
  }
  for (const name of ['local-models', 'voice-reference', 'changfeng-case', 'final-selection', 'validation', 'creative-workflows']) {
    await page.goto(new URL('docs/' + name + '.html', base).href, { waitUntil: 'domcontentloaded' });
    assert.ok(await page.locator('article h1').count() === 1);
    const links = await page.locator('article a[href]').evaluateAll(nodes => nodes.map(n => n.href));
    for (const value of new Set(links)) {
      if (new URL(value).origin !== new URL(base).origin) continue;
      const response = await browserGet(value);
      assert.equal(response.status, 200, value);
    }
    report.links.push({ document: name, codeBlocks: await page.locator('pre').count() });
  }
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await page.locator('#voice-reference').evaluate(video => { video.muted = true; });
  await page.locator('#play-voice').click();
  try {
    await page.waitForFunction(() => { const v = document.querySelector('#voice-reference'); return v.currentTime > 10.7 && v.currentTime < 21.5 && !v.paused; }, null, { timeout: 25000 });
    report.voice = await page.locator('#voice-reference').evaluate(video => ({ duration: video.duration, startTime: video.currentTime, playing: !video.paused }));
    await page.waitForFunction(() => { const v = document.querySelector('#voice-reference'); return v.paused && v.currentTime >= 21.4 && v.currentTime < 21.9; }, null, { timeout: 20000 });
    report.voice.stopTime = await page.locator('#voice-reference').evaluate(video => video.currentTime);
    report.voice.intervalStopped = true;
  } catch {
    report.voice = { verified: false, status: await page.locator('#voice-status').textContent() };
  }
  report.pageErrors = errors;
  assert.deepEqual(errors, []);
  await context.close();
} finally {
  await browser.close();
  await writeFile(out + '/report.json', JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify(report));
