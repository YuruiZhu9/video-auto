/**
 * clawctl Web Admin Dashboard JS
 * 移动端优先 / 实时 SSE / 任务管理 / 统计图表
 */

(function () {
  'use strict';

  const API_BASE = window.API_BASE || '/api/v1';
  let apiKey = localStorage.getItem('clawctl_api_key') || '';
  let sseConnected = false;
  let currentPage = 'dashboard';
  let taskHistory = [];
  let stats = {};

  // ── 工具函数 ─────────────────────────────────────────────────────────────

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  function authHeaders() {
    return { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' };
  }

  async function apiFetch(path, opts = {}) {
    const r = await fetch(`${API_BASE}${path}`, {
      ...opts,
      headers: { ...authHeaders(), ...(opts.headers || {}) },
    });
    if (r.status === 401 || r.status === 403) {
      showToast('认证失败，请检查 API Key', 'error');
      return null;
    }
    return r.json();
  }

  function showToast(msg, type = 'info') {
    const el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.className = `toast toast--${type} toast--show`;
    setTimeout(() => el.classList.remove('toast--show'), 3500);
  }

  function badgeHTML(status) {
    const map = {
      success: '✅ 成功',
      failed:  '❌ 失败',
      running: '🔄 运行中',
      pending:  '⏳ 等待',
      queued:  '📋 排队',
      cancelled:'⚠️ 已取消',
    };
    return `<span class="badge badge--${status}">${map[status] || status}</span>`;
  }

  function timeAgo(isoStr) {
    if (!isoStr) return '-';
    const diff = Date.now() - new Date(isoStr).getTime();
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
    return `${Math.floor(diff / 86400000)} 天前`;
  }

  function initSSE() {
    if (!apiKey) return;
    const es = new EventSource(`${API_BASE}/events?token=${encodeURIComponent(apiKey)}`);

    es.addEventListener('open', () => {
      sseConnected = true;
      updateSseIndicator(true);
    });

    es.addEventListener('task_update', (e) => {
      const data = JSON.parse(e.data);
      showToast(`📡 任务 [${data.name || data.task_id}] 状态: ${data.status}`, 'info');
      // 刷新任务列表
      if (currentPage === 'history') loadHistory();
      if (currentPage === 'dashboard') loadDashboard();
    });

    es.addEventListener('task_result', (e) => {
      const data = JSON.parse(e.data);
      if (data.status === 'success') {
        showToast(`✅ 任务完成: ${data.name}`, 'success');
      } else if (data.status === 'failed') {
        showToast(`❌ 任务失败: ${data.name}`, 'error');
      }
    });

    es.addEventListener('system_alert', (e) => {
      const data = JSON.parse(e.data);
      showToast(`⚠️ 系统: ${data.message}`, 'warn');
    });

    es.addEventListener('heartbeat', () => {
      sseConnected = true;
      updateSseIndicator(true);
    });

    es.addEventListener('error', () => {
      sseConnected = false;
      updateSseIndicator(false);
      setTimeout(initSSE, 5000);
    });
  }

  function updateSseIndicator(connected) {
    const el = $('#sse-indicator');
    if (!el) return;
    el.className = connected ? 'sse-dot sse-dot--live' : 'sse-dot sse-dot--offline';
    el.title = connected ? '实时推送已连接' : '实时推送断线重连中...';
  }

  // ── 页面渲染 ─────────────────────────────────────────────────────────────

  function renderShell(content) {
    $('#app').innerHTML = `
      <header class="top-bar">
        <div class="top-bar__left">
          <span class="logo">🤖 clawctl</span>
          <span id="sse-indicator" class="sse-dot sse-dot--offline" title="实时推送状态"></span>
        </div>
        <nav class="bottom-nav">
          <button class="nav-btn ${currentPage==='dashboard'?'active':''}" data-page="dashboard">📊</button>
          <button class="nav-btn ${currentPage==='history'?'active':''}" data-page="history">📋</button>
          <button class="nav-btn ${currentPage==='quick'?'active':''}" data-page="quick">⚡</button>
          <button class="nav-btn ${currentPage==='stats'?'active':''}" data-page="stats">📈</button>
          <button class="nav-btn ${currentPage==='settings'?'active':''}" data-page="settings">⚙️</button>
        </nav>
      </header>
      <main class="page" id="page-content">${content}</main>
      <div id="toast" class="toast"></div>
    `;
    bindNavEvents();
  }

  function bindNavEvents() {
    $$('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        currentPage = btn.dataset.page;
        if (currentPage === 'dashboard') loadDashboard();
        else if (currentPage === 'history') loadHistory();
        else if (currentPage === 'quick') loadQuickPage();
        else if (currentPage === 'stats') loadStatsPage();
        else if (currentPage === 'settings') loadSettingsPage();
      });
    });
  }

  // ── 仪表盘 ─────────────────────────────────────────────────────────────

  async function loadDashboard() {
    renderShell('<div class="loading">加载中...</div>');
    const data = await apiFetch('/status');
    if (!data) { renderShell('<p class="error">加载失败，请检查 API Key</p>'); return; }

    const quickBtns = [
      { name: 'AI 早报', icon: '📰', template: 'quick-report' },
      { name: '技术分析', icon: '🔬', template: 'tech-analyst' },
      { name: '商业洞察', icon: '💡', template: 'market-insight' },
      { name: '全量扫描', icon: '🔍', template: 'full-scan' },
    ];

    const running = data.tasks?.running || 0;
    const success = data.tasks?.success || 0;
    const failed = data.tasks?.failed || 0;

    renderShell(`
      <div class="page-header"><h1>📊 控制台</h1></div>

      <div class="card-grid">
        <div class="stat-card stat-card--blue">
          <div class="stat-card__value">${running}</div>
          <div class="stat-card__label">运行中</div>
        </div>
        <div class="stat-card stat-card--green">
          <div class="stat-card__value">${success}</div>
          <div class="stat-card__label">成功</div>
        </div>
        <div class="stat-card stat-card--red">
          <div class="stat-card__value">${failed}</div>
          <div class="stat-card__label">失败</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">${data.tasks?.total || 0}</div>
          <div class="stat-card__label">总计</div>
        </div>
      </div>

      <div class="section-title">⚡ 快捷操作</div>
      <div class="quick-grid">
        ${quickBtns.map(b => `
          <button class="quick-btn" data-template="${b.template}">
            <span class="quick-btn__icon">${b.icon}</span>
            <span class="quick-btn__label">${b.name}</span>
          </button>
        `).join('')}
      </div>

      <div class="section-title">🔗 OpenClaw 状态</div>
      <div class="card">
        <div class="status-row">
          <span>OpenClaw 连接</span>
          <span class="${data.openclaw_connected ? 'text-green' : 'text-red'}">
            ${data.openclaw_connected ? '✅ 已连接' : '❌ 断开'}
          </span>
        </div>
        <div class="status-row">
          <span>clawctl 版本</span><span>v1.4.1</span>
        </div>
        <div class="status-row">
          <span>实时推送</span>
          <span id="sse-status">${sseConnected ? '✅ 已连接' : '⚡ 连接中...'}</span>
        </div>
      </div>
    `);

    $$('.quick-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const tmpl = btn.dataset.template;
        btn.disabled = true;
        btn.textContent = '⏳ 执行中...';
        const r = await apiFetch(`/templates/${tmpl}/execute`, { method: 'POST', body: JSON.stringify({}) });
        btn.disabled = false;
        btn.querySelector('.quick-btn__label').textContent = quickBtns.find(b => b.template === tmpl).name;
        if (r && r.id) showToast(`🚀 任务已提交: ${r.id}`, 'success');
        else showToast('❌ 提交失败', 'error');
      });
    });
  }

  // ── 历史记录 ────────────────────────────────────────────────────────────

  async function loadHistory() {
    renderShell('<div class="loading">加载历史...</div>');
    const data = await apiFetch('/history?limit=30');
    taskHistory = data?.tasks || [];

    const rows = taskHistory.map(t => `
      <tr class="task-row" data-id="${t.id}">
        <td class="task-name" title="${t.name}">${t.name}</td>
        <td>${badgeHTML(t.status)}</td>
        <td class="task-time">${timeAgo(t.created_at)}</td>
        <td class="task-dur">${t.duration_ms ? (t.duration_ms/1000).toFixed(1)+'s' : '-'}</td>
      </tr>
    `).join('');

    renderShell(`
      <div class="page-header"><h1>📋 任务历史</h1><button id="refresh-btn" class="btn btn--sm">🔄</button></div>
      ${taskHistory.length === 0 ? '<p class="empty">暂无历史任务</p>' : `
      <div class="table-wrap">
        <table class="task-table">
          <thead><tr><th>任务</th><th>状态</th><th>时间</th><th>耗时</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`}
    `);

    $('#refresh-btn')?.addEventListener('click', loadHistory);
    $$('.task-row').forEach(row => {
      row.addEventListener('click', () => showTaskDetail(row.dataset.id));
    });
  }

  async function showTaskDetail(taskId) {
    const data = await apiFetch(`/history/${taskId}`);
    if (!data) return;
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal">
        <div class="modal__header">
          <h3>${data.name}</h3>
          <button class="modal__close" data-close>✕</button>
        </div>
        <div class="modal__body">
          <div class="detail-grid">
            <span class="detail-label">任务ID</span><code class="detail-val">${data.id}</code>
            <span class="detail-label">状态</span>${badgeHTML(data.status)}
            <span class="detail-label">耗时</span><span>${data.duration_ms ? (data.duration_ms/1000).toFixed(1)+'s' : '-'}</span>
            <span class="detail-label">创建时间</span><span>${data.created_at || '-'}</span>
            <span class="detail-label">完成时间</span><span>${data.completed_at || '-'}</span>
            <span class="detail-label">动作</span><span>${data.action}</span>
          </div>
          ${data.params ? `<details class="detail-section"><summary>📦 参数</summary><pre class="json-pre">${JSON.stringify(JSON.parse(data.params||'{}'), null, 2)}</pre></details>` : ''}
          ${data.result ? `<details class="detail-section"><summary>📤 结果</summary><pre class="json-pre">${JSON.stringify(JSON.parse(data.result||'{}'), null, 2)}</pre></details>` : ''}
          ${data.error ? `<details class="detail-section"><summary>❌ 错误</summary><pre class="json-pre error-text">${data.error}</pre></details>` : ''}
        </div>
      </div>`;
    document.body.appendChild(modal);
    modal.querySelector('[data-close]').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
  }

  // ── 快捷操作页 ─────────────────────────────────────────────────────────

  async function loadQuickPage() {
    renderShell('<div class="loading">加载模板...</div>');
    const data = await apiFetch('/templates');

    const shortcuts = [
      { name: 'AI 早报', desc: '生成今日 AI 资讯简报', template: 'quick-report', icon: '📰' },
      { name: '技术分析', desc: '分析技术前沿动态', template: 'tech-analyst', icon: '🔬' },
      { name: '商业洞察', desc: '发现 AI 商业机会', template: 'market-insight', icon: '💡' },
      { name: '全量扫描', desc: '抓取全量信息', template: 'full-scan', icon: '🔍' },
      { name: 'GitHub 趋势', desc: '查看 GitHub Trending', template: 'github-trending', icon: '🐙' },
      { name: '市场周报', desc: '生成商业市场周报', template: 'market-weekly', icon: '📊' },
    ];

    renderShell(`
      <div class="page-header"><h1>⚡ 快捷操作</h1></div>
      <div class="card-grid-2">
        ${shortcuts.map(s => `
          <div class="quick-card">
            <div class="quick-card__icon">${s.icon}</div>
            <div class="quick-card__body">
              <div class="quick-card__name">${s.name}</div>
              <div class="quick-card__desc">${s.desc}</div>
            </div>
            <button class="btn btn--run" data-template="${s.template}">▶ 执行</button>
          </div>`).join('')}
      </div>

      <div class="section-title">💬 发送消息</div>
      <div class="card">
        <textarea id="msg-input" class="input" rows="3" placeholder="输入要发送的消息..."></textarea>
        <button id="send-btn" class="btn btn--primary" style="margin-top:8px">发送</button>
      </div>

      <div class="section-title">🔗 URL Scheme</div>
      <div class="card">
        <p class="scheme-label">iOS 快捷指令 / Android Tasker</p>
        <div class="scheme-box">
          <code id="scheme-url">clawctl://run?name=quick-report</code>
          <button id="copy-scheme" class="btn btn--sm">📋 复制</button>
        </div>
      </div>
    `);

    $$('.btn--run').forEach(btn => {
      btn.addEventListener('click', async () => {
        const tmpl = btn.dataset.template;
        btn.textContent = '⏳...'; btn.disabled = true;
        const r = await apiFetch(`/templates/${tmpl}/execute`, { method: 'POST' });
        btn.textContent = '▶ 执行'; btn.disabled = false;
        if (r && r.id) { showToast(`✅ 任务已提交: ${r.name || tmpl}`, 'success'); }
        else showToast('❌ 提交失败', 'error');
      });
    });

    $('#send-btn')?.addEventListener('click', async () => {
      const msg = $('#msg-input')?.value?.trim();
      if (!msg) return;
      $('#send-btn').disabled = true;
      const r = await apiFetch('/send', { method: 'POST', body: JSON.stringify({ message: msg }) });
      $('#send-btn').disabled = false;
      if (r?.success) { showToast('✅ 消息已发送', 'success'); $('#msg-input').value = ''; }
      else showToast('❌ 发送失败', 'error');
    });

    $('#copy-scheme')?.addEventListener('click', () => {
      const url = $('#scheme-url')?.textContent;
      if (url) { navigator.clipboard.writeText(url); showToast('📋 URL Scheme 已复制', 'success'); }
    });
  }

  // ── 统计页 ─────────────────────────────────────────────────────────────

  async function loadStatsPage() {
    renderShell('<div class="loading">加载统计...</div>');
    const data = await apiFetch('/stats?days=7');
    stats = data || {};

    const byStatus = stats.by_status || {};
    const total = stats.total || 0;
    const success = byStatus.success || 0;
    const failed = byStatus.failed || 0;
    const rate = stats.success_rate || 0;
    const avgDur = stats.avg_duration_ms ? (stats.avg_duration_ms / 1000).toFixed(1) + 's' : '-';
    const daily = stats.daily || [];

    const maxCount = Math.max(...daily.map(d => d.count), 1);
    const bars = daily.map(d => {
      const pct = Math.round((d.count / maxCount) * 100);
      return `<div class="bar-item"><div class="bar-label">${d.date.slice(5)}</div><div class="bar-wrap"><div class="bar-fill" style="width:${pct}%">${d.count}</div></div></div>`;
    }).join('');

    renderShell(`
      <div class="page-header"><h1>📈 统计报表</h1><button id="refresh-stats" class="btn btn--sm">🔄</button></div>

      <div class="card-grid">
        <div class="stat-card stat-card--green">
          <div class="stat-card__value">${total}</div>
          <div class="stat-card__label">近7天任务</div>
        </div>
        <div class="stat-card stat-card--blue">
          <div class="stat-card__value">${rate}%</div>
          <div class="stat-card__label">成功率</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">${success}</div>
          <div class="stat-card__label">成功</div>
        </div>
        <div class="stat-card stat-card--red">
          <div class="stat-card__value">${failed}</div>
          <div class="stat-card__label">失败</div>
        </div>
      </div>

      <div class="section-title">⏱ 平均耗时: ${avgDur}</div>

      <div class="section-title">📅 每日趋势（近7天）</div>
      <div class="card">${bars}</div>
    `);

    $('#refresh-stats')?.addEventListener('click', loadStatsPage);
  }

  // ── 设置页 ─────────────────────────────────────────────────────────────

  function loadSettingsPage() {
    renderShell(`
      <div class="page-header"><h1>⚙️ 设置</h1></div>

      <div class="section-title">🔑 API Key</div>
      <div class="card">
        <input id="api-key-input" class="input" type="password" value="${apiKey}" placeholder="输入 API Key (sk-...)" />
        <button id="save-key-btn" class="btn btn--primary" style="margin-top:8px">保存</button>
      </div>

      <div class="section-title">📡 实时推送</div>
      <div class="card">
        <div class="status-row">
          <span>SSE 连接</span>
          <span id="sse-status-settings">${sseConnected ? '✅ 已连接' : '⚡ 未连接'}</span>
        </div>
        <button id="reconnect-sse" class="btn btn--sm" style="margin-top:8px">重新连接</button>
      </div>

      <div class="section-title">🗑 数据管理</div>
      <div class="card">
        <p>清理30天前的历史记录</p>
        <button id="cleanup-btn" class="btn btn--danger" style="margin-top:8px">清理历史</button>
      </div>

      <div class="section-title">📤 导出</div>
      <div class="card">
        <p>导出所有历史任务（JSON）</p>
        <button id="export-btn" class="btn btn--sm" style="margin-top:8px">导出数据</button>
      </div>

      <div class="section-title">ℹ️ 关于</div>
      <div class="card">
        <div class="status-row"><span>版本</span><span>clawctl v1.4.1</span></div>
        <div class="status-row"><span>SSE</span><span>Server-Sent Events 实时推送</span></div>
        <div class="status-row"><span>存储</span><span>SQLite 本地持久化</span></div>
      </div>
    `);

    $('#save-key-btn')?.addEventListener('click', () => {
      const key = $('#api-key-input')?.value?.trim();
      if (!key) return;
      apiKey = key;
      localStorage.setItem('clawctl_api_key', key);
      showToast('✅ API Key 已保存', 'success');
    });

    $('#reconnect-sse')?.addEventListener('click', () => {
      if (!apiKey) { showToast('请先保存 API Key', 'error'); return; }
      showToast('重新连接 SSE...', 'info');
    });

    $('#cleanup-btn')?.addEventListener('click', async () => {
      if (!confirm('确认清理30天前的历史任务？')) return;
      const r = await apiFetch('/history/cleanup?days=30', { method: 'DELETE' });
      if (r?.ok) { showToast(`✅ 已清理 ${r.deleted} 条记录`, 'success'); loadStatsPage(); }
      else showToast('❌ 清理失败', 'error');
    });

    $('#export-btn')?.addEventListener('click', async () => {
      const r = await apiFetch('/history/export');
      if (!r) return;
      const blob = new Blob([JSON.stringify(r, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url;
      a.download = `clawctl-export-${new Date().toISOString().slice(0,10)}.json`;
      a.click(); URL.revokeObjectURL(url);
      showToast(`✅ 已导出 ${r.count} 条记录`, 'success');
    });
  }

  // ── 入口 ────────────────────────────────────────────────────────────────

  function init() {
    if (apiKey) {
      initSSE();
      loadDashboard();
    } else {
      renderShell(`
        <div class="page-header"><h1>🤖 clawctl</h1></div>
        <div class="card">
          <p class="form-label">请输入 API Key 以继续</p>
          <input id="init-key" class="input" type="password" placeholder="sk-...-EXECUTE" />
          <button id="init-go" class="btn btn--primary" style="margin-top:12px">进入控制台 →</button>
        </div>
      `);
      $('#init-go')?.addEventListener('click', () => {
        const key = $('#init-key')?.value?.trim();
        if (!key) return;
        apiKey = key;
        localStorage.setItem('clawctl_api_key', key);
        initSSE();
        loadDashboard();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
