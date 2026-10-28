const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('open', open);
});
navigation?.addEventListener('click', event => {
  if (event.target.closest('a')) {
    menu.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
  }
});
const preview = document.querySelector('#case-preview');
if (preview) {
  const toggle = document.querySelector('#case-preview-toggle');
  const status = document.querySelector('#case-preview-status');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let visible = false, manual = null, failed = false;
  const wantsPlayback = () => manual ?? !reduced.matches;
  const syncPreview = () => {
    const wanted = wantsPlayback();
    toggle.textContent = wanted ? '暂停演示' : '播放演示';
    toggle.setAttribute('aria-pressed', String(!wanted));
    if (!wanted || !visible || document.hidden || failed) {
      preview.pause();
      return;
    }
    preview.play().catch(error => {
      if (error.name === 'AbortError' || !visible || document.hidden || failed) return;
      manual = false;
      status.textContent = '可点击播放演示，也可点击画面直接进入互动体验。';
      syncPreview();
    });
  };
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    manual = !wantsPlayback();
    status.textContent = '';
    syncPreview();
  });
  preview.addEventListener('error', () => {
    failed = true;
    toggle.hidden = true;
    status.textContent = '演示暂未加载，点击画面仍可进入长丰数字孪生。';
    syncPreview();
  }, true);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.18;
      syncPreview();
    }, { threshold: [0, 0.18] }).observe(preview);
  } else { visible = true; }
  reduced.addEventListener('change', syncPreview);
  document.addEventListener('visibilitychange', syncPreview);
  window.addEventListener('pagehide', () => preview.pause());
  window.addEventListener('pageshow', syncPreview);
  syncPreview();
}
const fpv = document.querySelector('#fpv-video');
// The static host ignores byte ranges. Buffer this exact small share file so
// native controls can seek without altering or re-encoding the approved media.
if (fpv) {
  const status = document.querySelector('#media-status');
  let objectUrl;
  status.textContent = '视频加载中…';
  (async () => {
    const response = await fetch(fpv.querySelector('source').src);
    if (!response.ok) throw new Error('media response');
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength !== 6818112) throw new Error('media length');
    const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
      .map(x => x.toString(16).padStart(2, '0')).join('');
    if (digest !== '9dac1ef965277857d1496a6af21bae1d24e487268c0f9c2430cedaa351946f9c') throw new Error('media integrity');
    const resume = !fpv.paused;
    objectUrl = URL.createObjectURL(new Blob([bytes], { type: 'video/mp4' }));
    fpv.src = objectUrl;
    fpv.load();
    fpv.dataset.bufferReady = 'true';
    fpv.dataset.verifiedSha256 = digest;
    status.textContent = '';
    if (resume) await fpv.play();
  })().catch(() => { status.textContent = '完整缓冲暂不可用，可下载同版视频观看。'; });
  window.addEventListener('pagehide', event => { if (!event.persisted && objectUrl) URL.revokeObjectURL(objectUrl); });
}
fpv?.addEventListener('error', () => {
  document.querySelector('#media-status').textContent = '视频加载失败，可下载同版文件或查看原媒体来源。';
});
const voice = document.querySelector('#voice-reference');
let audition = false;
document.querySelector('#play-voice')?.addEventListener('click', async () => {
  const status = document.querySelector('#voice-status');
  audition = true;
  voice.currentTime = 10.65;
  try { await voice.play(); status.textContent = '正在试听 10.65–21.45 秒公开参考。'; }
  catch { audition = false; status.textContent = '试听暂未加载，请在播放器重试，或打开声音来源页。'; }
});
voice?.addEventListener('timeupdate', () => {
  if (audition && voice.currentTime >= 21.45) {
    voice.pause(); audition = false;
    document.querySelector('#voice-status').textContent = '试听结束，点击按钮可再次播放。';
  }
});
document.querySelector('#copy-install')?.addEventListener('click', async () => {
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(document.querySelector('#install-command').textContent.trim());
    status.textContent = '安装命令已复制。请先在解压后的套件目录运行预览。';
  } catch { status.textContent = '复制不可用，请选中上方命令手动复制。'; }
});
