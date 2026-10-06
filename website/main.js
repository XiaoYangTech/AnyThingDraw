// 亿方万能画笔官网脚本
// 从亿方智云接口获取最新版本、更新日志与各架构安装包直链；
// 接口不可用时自动降级为指向 GitHub Releases 页面，保证页面始终可用。

const API = 'https://api.yfyw.top/apps/atdraw/api.php';
const RELEASES_URL = 'https://github.com/XiaoYangTech/AnyThingDraw/releases';

async function api(route, extra = '') {
  const res = await fetch(`${API}?route=${route}${extra}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const json = await res.json();
  if (!json.ok) throw new Error(json.error ? json.error.message : 'API error');
  return json.data || {};
}

function fmtSize(bytes) {
  if (!bytes || bytes <= 0) return '';
  const mb = bytes / 1048576;
  return mb >= 1 ? mb.toFixed(1) + ' MB' : (bytes / 1024).toFixed(0) + ' KB';
}

(async () => {
  const verBadge = document.getElementById('ver-badge');
  const verInfo = document.getElementById('ver-info');
  const mainBtn = document.getElementById('main-download');
  const changelogBox = document.getElementById('changelog-box');
  const changelogText = document.getElementById('changelog-text');

  // ---------- 版本信息 ----------
  try {
    const d = await api('app_info');
    const ver = (d.latest_version || '').replace(/^v/i, '');
    if (ver) {
      verBadge.textContent = ' v' + ver;
      verInfo.textContent = '最新版本 v' + ver + (d.latest_release_date ? ' · ' + d.latest_release_date : '') + ' · 支持 Windows 7 及以上';
    } else {
      verInfo.textContent = '暂无版本信息，可前往 Release 页面下载';
    }
    if (d.latest_download_url) mainBtn.href = d.latest_download_url;
    if (d.latest_changelog && changelogText) changelogText.textContent = d.latest_changelog;
    else if (changelogText) changelogText.textContent = '本版本暂无更新说明。';
  } catch (e) {
    verInfo.textContent = '暂时无法获取版本信息，请前往 GitHub Releases 下载';
    mainBtn.href = RELEASES_URL;
    if (changelogText) changelogText.textContent = '（获取更新内容失败，请前往 Releases 页面查看）';
  }

  // ---------- 各架构安装包直链 ----------
  const arches = ['x64', 'ia32', 'arm64'];
  await Promise.all(arches.map(async (arch) => {
    const btn = document.getElementById('dl-' + arch);
    const sizeEl = document.getElementById('size-' + arch);
    if (!btn) return;
    try {
      const d = await api('app_update', `&os=win32&arch=${arch}`);
      if (d.download_url) {
        btn.href = d.download_url;
        const size = d.matched && d.matched.size_bytes;
        const ver = (d.latest_version || '').replace(/^v/i, '');
        sizeEl.textContent = [ver && ('v' + ver), fmtSize(size)].filter(Boolean).join(' · ');
      } else {
        btn.href = RELEASES_URL;
        sizeEl.textContent = '该架构暂无直链安装包，前往 Release 选择';
      }
    } catch (e) {
      btn.href = RELEASES_URL;
      sizeEl.textContent = '获取失败，前往 Release 页面';
    }
  }));
})();
