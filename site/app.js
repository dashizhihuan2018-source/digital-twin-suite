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
const fpv = document.querySelector('#fpv-video');
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
