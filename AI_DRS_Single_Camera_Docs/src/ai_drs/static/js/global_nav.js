// Global Unified Navbar Component for AI DRS & PitchVision Platform

function renderGlobalHeader() {
  const currentPath = window.location.pathname;

  const header = document.createElement('header');
  header.className = 'global-header';

  header.innerHTML = `
    <a class="global-logo" href="/">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polygon points="12 2 2 7 12 12 22 7 12 2"/>
        <polyline points="2 17 12 22 22 17"/>
        <polyline points="2 12 12 17 22 12"/>
      </svg>
      AI<span>DRS</span>
      <span class="logo-badge">PRO v3.0</span>
    </a>
    <ul class="global-nav">
      <li><a href="/" class="${currentPath === '/' ? 'active' : ''}">⚡ Home</a></li>
      <li><a href="/setup" class="${currentPath.startsWith('/setup') ? 'active' : ''}">⚙️ Setup</a></li>
      <li><a href="/live" class="${currentPath.startsWith('/live') ? 'active' : ''}">📹 Live Operator</a></li>
      <li><a href="/analytics" class="${currentPath.startsWith('/analytics') ? 'active' : ''}">📊 Analytics</a></li>
      <li><a href="/scoreboard" class="${currentPath.startsWith('/scoreboard') ? 'active' : ''}">🏟️ Scoreboard</a></li>
      <li><a href="/docs" target="_blank">📖 API Docs</a></li>
    </ul>
    <div class="global-cta">
      <span class="badge-connected" id="nav-hardware-status">● HARDWARE ONLINE</span>
      <a href="/live" class="btn-theme btn-primary">▶ CONNECT FEED</a>
    </div>
  `;

  const existing = document.querySelector('.global-header');
  if (existing) {
    existing.replaceWith(header);
  } else {
    document.body.prepend(header);
  }

  // Probe hardware router status silently
  fetch('/api/v1/hardware/devices')
    .then(r => r.json())
    .then(d => {
      const badge = document.getElementById('nav-hardware-status');
      if (badge && d.detected_cameras && d.detected_cameras.length > 0) {
        badge.innerHTML = `🎥 ${d.detected_cameras.length} CAMERAS DISCOVERED`;
      }
    })
    .catch(() => {});
}

document.addEventListener('DOMContentLoaded', () => {
  renderGlobalHeader();
});
