// OpenClaw Control Dashboard - JavaScript

// ─── Config ────────────────────────────────────────────────────
const API_BASE = window.location.origin;
let SESSION_TOKEN = localStorage.getItem('oc_ctrl_session') || '';
let CURRENT_USER = JSON.parse(localStorage.getItem('oc_ctrl_user') || 'null');
let API_KEY_FALLBACK = localStorage.getItem('oc_ctrl_key') || ''; // 兼容旧版

// ─── Auth ──────────────────────────────────────────────────────
async function doLogin() {
  const rawKey = document.getElementById('modal-login-key').value.trim();
  if (!rawKey) { toast('请输入 API Key', 'error'); return; }
  try {
    const res = await fetch(API_BASE + '/api/v1/web-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: rawKey }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || '登录失败 HTTP ' + res.status);
    SESSION_TOKEN = data.token;
    CURRENT_USER = { name: data.key_name, level: data.level };
    localStorage.setItem('oc_ctrl_session', SESSION_TOKEN);
    localStorage.setItem('oc_ctrl_user', JSON.stringify(CURRENT_USER));
    localStorage.removeItem('oc_ctrl_key');
    closeModal('modal-login');
    updateUserBadge();
    toast('登录成功：' + data.key_name + ' (' + data.level + ')', 'success');
    refreshDashboard();
  } catch(e) { toast('登录失败: ' + e.message, 'error'); }
}

function doLogout() {
  if (!confirm('确认退出登录？')) return;
  const token = SESSION_TOKEN;
  SESSION_TOKEN = '';
  CURRENT_USER = null;
  localStorage.removeItem('oc_ctrl_session');
  localStorage.removeItem('oc_ctrl_user');
  if (token) {
    fetch(API_BASE + '/api/v1/web-logout?token=' + token, { method: 'POST' }).catch(() => {});
  }
  updateUserBadge();
  toast('已退出登录', 'info');
}

function updateUserBadge() {
  const el = document.getElementById('userBadge');
  if (el) {
    if (CURRENT_USER) {
      const lvlColor = { admin: 'var(--red)', execute: 'var(--yellow)', readonly: 'var(--green)' }[CURRENT_USER.level] || 'var(--text-dim)';
      el.innerHTML = '<span style="color:var(--text-dim);font-size:12px">' + esc(CURRENT_USER.name) + '</span> <span style="font-size:11px;padding:2px 7px;border-radius:10px;background:' + lvlColor + '22;color:' + lvlColor + '">' + esc(CURRENT_USER.level) + '</span> <button class="btn btn-sm" onclick="doLogout()" style="margin-left:6px">退出</button>';
    } else {
      el.innerHTML = '';
    }
  }
}

function requireLogin() {
  if (!SESSION_TOKEN && !API_KEY_FALLBACK) {
    openModal('modal-login');
    return false;
  }
  return true;
}

// ─── Utilities ────────────────────────────────────────────────
function esc(s) { if (!s) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtTime(ts) {
  if (!ts) return '-';
  try { return new Date(ts).toLocaleString('zh-CN', {hour12:false}); } catch { return ts; }
}

// ─── Toast ─────────────────────────────────────────────────────
function toast(msg, type='info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'show ' + (type === 'error' ? 'error' : 'success');
  setTimeout(() => t.className = '', 3000);
}

// ─── API ───────────────────────────────────────────────────────
async function api(path, opts={}) {
  if (!requireLogin()) throw new Error('需要登录');

  const authKey = SESSION_TOKEN || API_KEY_FALLBACK;
  if (!authKey) throw new Error('未登录');

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + authKey,
    ...(opts.headers||{})
  };

  try {
    const res = await fetch(API_BASE + path, { ...opts, headers });
    const data = await res.json().catch(() => ({}));

    // 401 → 清除 session，打开登录框
    if (res.status === 401) {
      SESSION_TOKEN = ''; API_KEY_FALLBACK = '';
      localStorage.removeItem('oc_ctrl_session');
      localStorage.removeItem('oc_ctrl_key');
      CURRENT_USER = null;
      openModal('modal-login');
      throw new Error(data.detail || '认证失败，请重新登录');
    }

    if (!res.ok) throw new Error(data.detail || 'HTTP ' + res.status);
    return data;
  } catch(e) {
    if (!e.message.includes('需要登录')) throw e;
    throw e;
  }
}

// ─── Navigation ────────────────────────────────────────────────
function switchPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.getElementById('page-' + page)?.classList.remove('hidden');
  document.querySelectorAll('nav a').forEach(a => a.classList.toggle('active', a.dataset.page === page));
  const loaders = {
    dashboard: refreshDashboard,
    tasks: loadTasks,
    scheduler: loadScheduler,
    notify: loadNotifyPage,
    keys: loadKeys,
    templates: loadTemplates,
    audit: loadAudit,
  };
  if (loaders[page]) loaders[page]();
}

document.querySelectorAll('nav a').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  switchPage(a.dataset.page);
}));

// ─── Tabs ──────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  const parent = t.closest('.tabs');
  parent.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  parent.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
  t.classList.add('active');
  document.getElementById('tab-' + t.dataset.tab)?.classList.add('active');
}));

// ─── Modal ─────────────────────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.add('show'); }
function closeModal(id) { document.getElementById(id).classList.remove('show'); }

// ─── Dashboard ──────────────────────────────────────────────────
async function refreshDashboard() {
  // v1.3: 初始化 ECharts（仅首次）
  if (!chartStatus) initCharts();
  try {
    const [tasks, jobs, status] = await Promise.all([
      api('/api/v1/tasks').catch(() => ({ tasks: [], total: 0 })),
      api('/api/v1/scheduler/jobs').catch(() => []),
      api('/api/v1/status').catch(() => ({})),
    ]);
    const all = tasks.tasks || [];
    const running = all.filter(t => t.status === 'running' || t.status === 'pending');
    const completed = all.filter(t => t.status === 'completed');
    const failed = all.filter(t => t.status === 'failed');

    document.getElementById('stat-completed').textContent = completed.length;
    document.getElementById('stat-running').textContent = running.length;
    document.getElementById('stat-jobs').textContent = Array.isArray(jobs) ? jobs.length : 0;
    document.getElementById('stat-failed').textContent = failed.length;

    const recent = all.slice(0, 8);
    document.getElementById('recentTasks').innerHTML = recent.length ? recent.map(t => '<tr>' +
      '<td><code>' + esc((t.id||'').slice(0,8)) + '</code></td>' +
      '<td>' + esc(t.name) + '</td>' +
      '<td style="color:var(--text-dim)">' + esc(t.action||'') + '</td>' +
      '<td><span class="badge ' + esc(t.status) + '">' + esc(t.status) + '</span></td>' +
      '<td style="font-size:12px;color:var(--text-dim)">' + fmtTime(t.created_at) + '</td>' +
      '<td>' + (t.duration_seconds ? t.duration_seconds.toFixed(1)+'s' : '-') + '</td>' +
      '<td><button class="btn btn-sm" onclick="viewTask(\''+esc(t.id||'')+'\')">详情</button></td>' +
    '</tr>').join('') : '<tr><td colspan="6" class="empty">暂无任务记录</td></tr>';

    document.getElementById('agentStats').innerHTML = '<div class="grid-4">' +
      '<div class="stat-card blue"><div class="stat-label">总任务数</div><div class="stat-value">' + (tasks.total||0) + '</div></div>' +
      '<div class="stat-card green"><div class="stat-label">成功</div><div class="stat-value">' + completed.length + '</div></div>' +
      '<div class="stat-card orange"><div class="stat-label">进行中</div><div class="stat-value">' + running.length + '</div></div>' +
      '<div class="stat-card red"><div class="stat-label">失败</div><div class="stat-value">' + failed.length + '</div></div>' +
    '</div><div style="margin-top:12px;font-size:12px;color:var(--text-dim)">' +
      'Gateway: ' + (status.gateway_connected?'<span style="color:var(--green)">&#10004; 已连接</span>':'<span style="color:var(--red)">&#10006; 未连接</span>') + ' | ' +
      '活跃会话: ' + (status.active_sessions||0) + ' | ' +
      '队列: ' + (status.queue_size||0) +
    '</div>';

    document.getElementById('apiStatus').textContent = '&#10004; 已连接';
    document.getElementById('apiStatus').className = 'api-status ok';

    // v1.3: 刷新 ECharts 图表
    refreshCharts(all);
  } catch(e) {
    document.getElementById('apiStatus').textContent = '&#10006; 未连接';
    document.getElementById('apiStatus').className = 'api-status err';
    document.getElementById('recentTasks').innerHTML = '<tr><td colspan="6" class="empty">&#9888; API 未连接，请检查服务是否启动</td></tr>';
    document.getElementById('agentStats').innerHTML = '<div class="empty">&#9888; 无法加载状态，请确认服务器地址和 API Key 正确</div>';
  }
}

// ─── Tasks ─────────────────────────────────────────────────────
async function loadTasks() {
  const TID = { 'id':0,'name':1,'action':2,'status':3,'created':4,'duration':5,'result':6,'ops':7 };
  const cols = (names) => names.map(n => TID[n]);
  const render = (list, fields) => {
    if (!list.length) return '<tr><td colspan="'+fields.length+'" class="empty">暂无任务</td></tr>';
    return list.map(t => {
      const td = (v, extra) => '<td' + (extra||'') + '>' + v + '</td>';
      let row = '';
      const rowClick = "openTaskDetail(" + JSON.stringify(t).replace(/"/g, '&quot;') + ")";
      if (fields.includes('id')) row += td('<code>'+esc((t.id||'').slice(0,8))+'</code>');
      if (fields.includes('name')) row += td('<span style="cursor:pointer;color:var(--accent)" title="点击查看详情" onclick="'+rowClick+'">'+esc(t.name)+'</span>');
      if (fields.includes('action')) row += td('<span style="color:var(--text-dim)">'+esc(t.action||'')+'</span>');
      if (fields.includes('status')) row += td('<span class="badge '+esc(t.status)+'">'+esc(t.status)+'</span>');
      if (fields.includes('created')) row += td('<span style="font-size:12px;color:var(--text-dim)">'+fmtTime(t.created_at)+'</span>');
      if (fields.includes('duration')) row += td(t.duration_seconds ? t.duration_seconds.toFixed(1)+'s' : '-');
      if (fields.includes('result')) row += td('<span style="font-size:12px;color:var(--text-dim);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+esc(JSON.stringify(t.result||t.error||''))+'">'+esc(JSON.stringify(t.result||t.error||'')).slice(0,40)+'</span>');
      if (fields.includes('ops')) row += td('<button class="btn btn-sm" onclick="viewTask(\''+esc(t.id||'')+'\')">查看</button>');
      return '<tr style="cursor:pointer" onclick="'+rowClick+'">' + row + '</tr>';
    }).join('');
  };

  try {
    const data = await api('/api/v1/tasks');
    const tasks = data.tasks || [];
    document.getElementById('tasks-active').innerHTML = render(tasks.filter(t=>t.status==='running'||t.status==='pending'), ['id','name','action','created']);
    document.getElementById('tasks-completed').innerHTML = render(tasks.filter(t=>t.status==='completed'), ['id','name','duration','created','result']);
    document.getElementById('tasks-failed').innerHTML = render(tasks.filter(t=>t.status==='failed'), ['id','name','result','created']);
    document.getElementById('tasks-all').innerHTML = render(tasks, ['id','name','action','status','created','ops']);
  } catch(e) {
    ['tasks-active','tasks-completed','tasks-failed','tasks-all'].forEach(id => {
      document.getElementById(id).innerHTML = '<tr><td colspan="8" class="empty">加载失败: '+esc(e.message)+'</td></tr>';
    });
  }
}

async function createNewTask() {
  const template = document.getElementById('newTaskTemplate').value;
  const name = document.getElementById('newTaskName').value || (document.getElementById('newTaskTemplate').selectedOptions[0] && document.getElementById('newTaskTemplate').selectedOptions[0].text) || '自定义任务';
  let params = {};
  try { params = JSON.parse(document.getElementById('newTaskParams').value || '{}'); } catch(e) {}
  try {
    await api('/api/v1/tasks', { method: 'POST', body: JSON.stringify({ name, action: 'spawn', params, template }) });
    toast('&#10004; 任务已创建', 'success');
    document.getElementById('newTaskName').value = '';
    document.getElementById('newTaskParams').value = '';
    loadTasks();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function spawnTask(templateId) {
  const names = { status_check:'状态检查', quick_fetch:'快速抓取', tech_brief:'技术简报', biz_brief:'商业简报' };
  try {
    await api('/api/v1/tasks', { method: 'POST', body: JSON.stringify({ name: names[templateId]||templateId, action: 'spawn', template: templateId, params: {} }) });
    toast('&#10004; '+(names[templateId]||templateId)+' 已启动', 'success');
    loadTasks();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

// ─── Scheduler ─────────────────────────────────────────────────
async function loadScheduler() {
  try {
    const data = await api('/api/v1/scheduler/jobs');
    const jobs = Array.isArray(data) ? data : (data.jobs||[]);
    document.getElementById('scheduledJobs').innerHTML = jobs.length ? jobs.map(j => '<tr>' +
      '<td>'+esc(j.name)+'</td>' +
      '<td><code>'+esc(j.template_id||'')+'</code></td>' +
      '<td><span style="font-size:12px;font-family:monospace;color:var(--accent)">'+esc(j.cron_expr||(j.interval_seconds+'s'))+'</span></td>' +
      '<td style="font-size:12px;color:var(--text-dim)">'+fmtTime(j.next_run)+'</td>' +
      '<td style="font-size:12px;color:var(--text-dim)">'+fmtTime(j.last_run)+'</td>' +
      '<td><span class="badge '+(j.enabled?'active':'pending')+'">'+(j.enabled?'&#10004; 启用':'&#10006; 暂停')+'</span></td>' +
      '<td><div class="actions">' +
        '<button class="btn btn-sm" onclick="toggleJob(\''+esc(j.job_id)+'\','+!j.enabled+')">'+(j.enabled?'&#10006; 暂停':'&#10004; 启用')+'</button>' +
        '<button class="btn btn-sm danger" onclick="deleteJob(\''+esc(j.job_id)+'\')">&#128465;</button>' +
      '</div></td>' +
    '</tr>').join('') : '<tr><td colspan="7" class="empty">暂无定时任务，点击「新建」添加</td></tr>';

    const presets = [
      { name:'晨报（每天 8:00）', template:'quick_fetch', cron:'0 8 * * *', desc:'抓取AI资讯+生成简报' },
      { name:'技术日报（工作日 18:00）', template:'tech_brief', cron:'0 18 * * 1-5', desc:'生成技术前沿报告' },
      { name:'商业洞察（工作日 9:30）', template:'biz_brief', cron:'0 9 * * 1-5', desc:'生成商业需求洞察' },
      { name:'状态巡检（每60分钟）', template:'status_check', cron:'*/60 * * * *', desc:'每小时检查系统状态' },
    ];
    document.getElementById('jobPresets').innerHTML = presets.map(p => '<div class="preset-card">' +
      '<div><div class="preset-name">'+esc(p.name)+'</div><div class="preset-desc">'+esc(p.desc)+'</div><div class="preset-cron">'+esc(p.cron)+'</div></div>' +
      '<button class="btn btn-sm primary" onclick="addPreset(\''+esc(p.name)+'\',\''+esc(p.template)+'\',\''+esc(p.cron)+'\')">&#43; 添加</button>' +
    '</div>').join('');
  } catch(e) {
    document.getElementById('scheduledJobs').innerHTML = '<tr><td colspan="7" class="empty">加载失败: '+esc(e.message)+'</td></tr>';
  }
}

function toggleJobCronInterval() {
  const type = document.getElementById('modal-job-type').value;
  document.getElementById('modal-job-cron-group').classList.toggle('hidden', type !== 'cron');
  document.getElementById('modal-job-interval-group').classList.toggle('hidden', type !== 'interval');
}

async function createJob() {
  const name = document.getElementById('modal-job-name').value;
  const template = document.getElementById('modal-job-template').value;
  const type = document.getElementById('modal-job-type').value;
  if (!name) { toast('&#9888; 请输入任务名称', 'error'); return; }
  const body = { name, template_id: template };
  if (type === 'cron') body.cron_expr = document.getElementById('modal-job-cron').value;
  else body.interval_seconds = parseInt(document.getElementById('modal-job-interval').value) || 3600;
  try {
    await api('/api/v1/scheduler/jobs', { method: 'POST', body: JSON.stringify(body) });
    closeModal('modal-new-job');
    toast('&#10004; 定时任务已创建', 'success');
    loadScheduler();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function addPreset(name, template, cron) {
  try {
    await api('/api/v1/scheduler/jobs', { method: 'POST', body: JSON.stringify({ name, template_id: template, cron_expr: cron }) });
    toast('&#10004; 预设任务已添加', 'success');
    loadScheduler();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function toggleJob(jobId, enable) {
  try {
    await api('/api/v1/scheduler/jobs/'+esc(jobId)+'/toggle?enabled='+enable, { method: 'POST' });
    toast('&#10004; 已'+(enable?'启用':'暂停'), 'success');
    loadScheduler();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function deleteJob(jobId) {
  if (!confirm('确认删除此定时任务？')) return;
  try {
    await api('/api/v1/scheduler/jobs/'+esc(jobId), { method: 'DELETE' });
    toast('&#10004; 已删除', 'success');
    loadScheduler();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

// ─── Notify ────────────────────────────────────────────────────
function loadNotifyPage() {
  const templates = [
    { id:'task_start', name:'&#63720; 任务开始', icon:'&#127881;', desc:'任务启动时发送通知' },
    { id:'task_complete', name:'&#9989; 任务完成', icon:'&#9989;', desc:'任务成功完成时发送' },
    { id:'task_failed', name:'&#10060; 任务失败', icon:'&#10060;', desc:'任务执行失败时发送告警' },
    { id:'alert', name:'&#9888; 系统告警', icon:'&#9888;', desc:'OpenClaw 系统异常告警' },
    { id:'status_report', name:'&#128200; 状态报告', icon:'&#128200;', desc:'定期发送系统状态汇总' },
    { id:'daily_brief', name:'&#128240; 今日简报', icon:'&#128240;', desc:'整合资讯和洞察的日报' },
  ];
  document.getElementById('templateList').innerHTML = templates.map(t => '<div class="preset-card">' +
    '<div><div class="preset-name">'+t.icon+' '+t.name+'</div><div class="preset-desc">'+t.desc+'</div></div>' +
    '<button class="btn btn-sm" onclick="useTemplate(\''+t.id+'\')">&#128221; 使用</button>' +
  '</div>').join('');
}

function useTemplate(templateId) {
  document.getElementById('notifyType').value = templateId;
  switchPage('notify');
  document.querySelector('#page-notify .tab[data-tab="send"]').click();
}

async function sendNotify() {
  const channel = document.getElementById('notifyChannel').value;
  const type = document.getElementById('notifyType').value;
  const content = document.getElementById('notifyContent').value;
  if (!content && type !== 'text') { toast('&#9888; 请输入消息内容', 'error'); return; }
  try {
    const body = type === 'text'
      ? { channel, message: content }
      : { channel, template: type, task_name:'测试任务', duration: 2.5, result_summary: content||'测试消息', timestamp: new Date().toLocaleString('zh-CN') };
    await api('/api/v1/notify', { method: 'POST', body: JSON.stringify(body) });
    toast('&#10004; 消息已发送', 'success');
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function testChannel(channel) {
  if (channel === 'wecom') {
    // WeCom 专用接口
    const msg = '&#128236; OpenClaw 控制台测试消息 - ' + new Date().toLocaleString('zh-CN');
    try {
      await api('/api/v1/notify/wecom', {
        method: 'POST',
        body: JSON.stringify({ msgtype: 'markdown', content: '**OpenClaw 控制台**\n\n这是一条来自 OpenClaw 控制台的企业微信测试消息\n\n时间：' + new Date().toLocaleString('zh-CN') + '\n\n状态：&#10004; 发送成功' })
      });
      toast('&#10004; 企业微信测试消息已发送', 'success');
    } catch(e) { toast('&#10006; 企业微信：'+e.message, 'error'); }
    return;
  }
  try {
    await api('/api/v1/notify', { method: 'POST', body: JSON.stringify({ channel, message: '&#128236; OpenClaw 控制台测试消息 - '+new Date().toLocaleString('zh-CN') }) });
    toast('&#10004; 测试消息已发送', 'success');
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

// ─── Keys ───────────────────────────────────────────────────────

// ─── Task Detail ─────────────────────────────────────────────────
async function viewTask(taskId) {
  try {
    const data = await api('/api/v1/tasks/' + esc(taskId));
    const t = data.task || data;
    const statusColor = { completed: 'var(--green)', running: 'var(--yellow)', failed: 'var(--red)', pending: 'var(--text-dim)' };
    const status = t.status || 'unknown';
    const dur = t.duration_seconds ? t.duration_seconds.toFixed(2) + ' 秒' : '-';
    const result = t.result || t.error || {};
    const resultText = typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result);
    const params = t.params || {};
    const paramsText = typeof params === 'object' ? JSON.stringify(params, null, 2) : String(params);

    const html = \`
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">任务ID</div><code style="font-size:12px">\${esc(t.id||'')}</code></div>
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">状态</div><span class="badge \${esc(status)}" style="font-size:13px">\${esc(status)}</span></div>
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">任务名</div><b>\${esc(t.name||'')}</b></div>
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">动作</div><span style="color:var(--text-dim)">\${esc(t.action||'')}</span></div>
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">创建时间</div>\${fmtTime(t.created_at)}</div>
        <div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">耗时</div>\${dur}</div>
        \${t.started_at ? '<div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">开始时间</div>'+fmtTime(t.started_at)+'</div>' : ''}
        \${t.completed_at ? '<div><div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">完成时间</div>'+fmtTime(t.completed_at)+'</div>' : ''}
      </div>
      <div style="margin-bottom:12px">
        <div style="font-size:11px;color:var(--text-dim);margin-bottom:4px">参数</div>
        <div class="code-block" style="margin:0;font-size:11px;max-height:120px;overflow:auto">\${paramsText ? esc(paramsText) : '(无)'}</div>
      </div>
      \${resultText ? '<div>' :
        '<div style="font-size:11px;color:var(--text-dim);margin-bottom:4px">结果 / 错误</div>' :
        '<div class="code-block" style="margin:0;font-size:11px;max-height:200px;overflow:auto">' + esc(resultText) + '</div>'}
    \`;
    document.getElementById('task-detail-content').innerHTML = html;
    openModal('modal-task-detail');
  } catch(e) {
    document.getElementById('task-detail-content').innerHTML = '<div style="color:var(--red)">加载失败: ' + esc(e.message) + '</div>';
    openModal('modal-task-detail');
  }
}

// ─── Task Detail Modal (v1.4.0) ───────────────────────────────
let _currentTaskResult = '';

function openTaskDetail(t) {
  _currentTaskResult = '';
  const status = t.status || 'unknown';
  const badge = document.getElementById('modal-task-status-badge');
  badge.textContent = status;
  badge.className = status;

  document.getElementById('modal-task-title').textContent = t.name || t.id || '任务详情';
  document.getElementById('m-task-id').textContent = t.id || '-';
  document.getElementById('m-task-duration').textContent = t.duration_seconds ? t.duration_seconds.toFixed(2) + ' 秒' : '-';
  document.getElementById('m-task-created').textContent = fmtTime(t.created_at) || '-';
  document.getElementById('m-task-completed').textContent = fmtTime(t.completed_at) || '-';
  document.getElementById('m-task-action').textContent = t.action || '-';

  const result = t.result || t.error || {};
  const resultText = typeof result === 'object' ? JSON.stringify(result, null, 2) : (result || '-');
  document.getElementById('m-task-result').textContent = resultText;
  _currentTaskResult = resultText;

  // Build new detail layout
  const params = t.params || {};
  const paramsText = typeof params === 'object' ? JSON.stringify(params, null, 2) : (params || '');
  const html = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
      <h3 style="margin:0;font-size:15px;">${esc(t.name || '任务详情')}</h3>
      <span style="font-size:12px;padding:2px 8px;border-radius:12px;" class="${esc(status)}">${esc(status)}</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
      <div><span style="color:var(--text-dim);font-size:12px;">任务ID</span><div style="font-family:monospace;font-size:12px;word-break:break-all;">${esc(t.id||'-')}</div></div>
      <div><span style="color:var(--text-dim);font-size:12px;">耗时</span><div style="font-size:13px;">${t.duration_seconds ? t.duration_seconds.toFixed(2)+' 秒' : '-'}</div></div>
      <div><span style="color:var(--text-dim);font-size:12px;">创建时间</span><div style="font-size:13px;">${fmtTime(t.created_at)||'-'}</div></div>
      <div><span style="color:var(--text-dim);font-size:12px;">完成时间</span><div style="font-size:13px;">${fmtTime(t.completed_at)||'-'}</div></div>
    </div>
    <div style="margin-bottom:10px;"><span style="color:var(--text-dim);font-size:12px;">操作类型</span><div style="font-size:13px;">${esc(t.action||'-')}</div></div>
    ${paramsText ? `<div style="margin-bottom:10px;"><span style="color:var(--text-dim);font-size:12px;">参数</span><pre style="background:var(--bg-deep);border:1px solid var(--border);border-radius:6px;padding:8px;font-size:11px;max-height:100px;overflow:auto;margin:4px 0 0">${esc(paramsText)}</pre></div>` : ''}
    <div style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="color:var(--text-dim);font-size:12px;">${t.error ? '错误信息' : '执行结果'}</span>
        <button class="btn btn-sm" onclick="copyTaskResult()" style="font-size:11px;padding:2px 8px;">&#128203; 复制</button>
      </div>
      <pre id="m-task-result" style="background:var(--bg-deep);border:1px solid var(--border);border-radius:8px;padding:12px;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;word-break:break-all;margin:0;">${esc(resultText)}</pre>
    </div>
    <div class="modal-footer">
      <button class="btn" onclick="closeModal('modal-task-detail')">关闭</button>
    </div>`;

  document.getElementById('task-detail-new').innerHTML = html;
  document.getElementById('task-detail-content').style.display = 'none';
  document.getElementById('task-detail-new').style.display = 'block';
  openModal('modal-task-detail');
}

function copyTaskResult() {
  const text = document.getElementById('m-task-result')?.textContent || _currentTaskResult;
  if (!text || text === '-') { toast('&#9888; 无内容可复制', 'warn'); return; }
  navigator.clipboard.writeText(text).then(() => toast('&#10004; 已复制到剪贴板', 'success')).catch(() => toast('&#10006; 复制失败，请手动选择', 'error'));
}

async function loadKeys() {
  try {
    const data = await api('/api/v1/keys');
    const keys = data.keys || [];
    document.getElementById('keysList').innerHTML = keys.length ? keys.map(k => '<tr>' +
      '<td>'+esc(k.name)+'</td>' +
      '<td><span class="badge '+(k.level==='admin'?'failed':k.level==='execute'?'running':'pending')+'">'+esc(k.level)+'</span></td>' +
      '<td style="font-size:12px">'+fmtTime(k.created_at)+'</td>' +
      '<td style="font-size:12px;color:var(--text-dim)">'+(k.expires_at?fmtTime(k.expires_at):'永不过期')+'</td>' +
      '<td><code style="font-size:10px">'+esc((k.key||k.key_id||'').slice(0,20))+'...</code></td>' +
      '<td><button class="btn btn-sm danger" onclick="revokeKey(\''+esc(k.key_id||'')+'\')">&#128465; 撤销</button></td>' +
    '</tr>').join('') : '<tr><td colspan="6" class="empty">暂无 Key</td></tr>';
  } catch(e) { document.getElementById('keysList').innerHTML = '<tr><td colspan="6" class="empty">加载失败: '+esc(e.message)+'</td></tr>'; }
}

async function createKey() {
  const name = document.getElementById('modal-key-name').value;
  const level = document.getElementById('modal-key-level').value;
  const expires = document.getElementById('modal-key-expires').value;
  if (!name) { toast('&#9888; 请输入 Key 名称', 'error'); return; }
  try {
    const data = await api('/api/v1/keys', { method: 'POST', body: JSON.stringify({ name, level, expires_days: expires||null }) });
    closeModal('modal-new-key');
    const newKey = data.key || data.api_key || data.key_value;
    if (newKey) {
      const confirmed = confirm('&#9888; API Key 已生成（仅此一次显示）：\n\n' + newKey + '\n\n请妥善保管！');
      if (confirmed) { try { navigator.clipboard.writeText(newKey); } catch(e) {} toast('&#10004; 已复制到剪贴板', 'success'); }
    } else { toast('&#10004; Key 已生成，请在列表中查看', 'success'); }
    loadKeys();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function revokeKey(keyId) {
  if (!keyId || !confirm('确认撤销此 Key？')) return;
  try { await api('/api/v1/keys/'+esc(keyId), { method: 'DELETE' }); toast('&#10004; 已撤销', 'success'); loadKeys(); } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

// ─── Audit ─────────────────────────────────────────────────────
async function loadAudit() {
  try {
    const data = await api('/api/v1/audit?limit=100');
    const logs = data.logs || [];
    document.getElementById('auditLogs').innerHTML = logs.length ? logs.map(l => '<tr>' +
      '<td style="font-size:11px;white-space:nowrap">'+fmtTime(l.timestamp)+'</td>' +
      '<td><span class="badge '+(l.action==='admin'?'failed':l.action==='execute'?'running':'pending')+'">'+esc(l.action)+'</span></td>' +
      '<td><code style="font-size:10px">'+esc(l.key_name||'')+'</code></td>' +
      '<td style="font-size:11px">'+esc(l.ip||'')+'</td>' +
      '<td style="font-size:11px;font-family:monospace">'+esc(l.path||'')+'</td>' +
      '<td style="font-size:11px">'+esc(l.method||'')+'</td>' +
      '<td><span class="badge '+((l.status_code||0)<400?'success':'failed')+'">'+esc(String(l.status_code||'-'))+'</span></td>' +
      '<td style="font-size:11px;color:var(--text-dim);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+esc(l.detail||'')+'">'+esc(l.detail||'').slice(0,50)+'</td>' +
    '</tr>').join('') : '<tr><td colspan="8" class="empty">暂无审计日志</td></tr>';
  } catch(e) { document.getElementById('auditLogs').innerHTML = '<tr><td colspan="8" class="empty">加载失败: '+esc(e.message)+'</td></tr>'; }
}

// ─── Send Custom Msg ────────────────────────────────────────────
function sendCustomMsg() { openModal('modal-send-msg'); }

async function doSendCustomMsg() {
  const content = document.getElementById('modal-msg-content').value;
  if (!content) { toast('&#9888; 请输入消息内容', 'error'); return; }
  try {
    await api('/api/v1/gateway/message', { method: 'POST', body: JSON.stringify({ channel:'dingtalk', message: content }) });
    closeModal('modal-send-msg');
    toast('&#10004; 消息已发送', 'success');
    document.getElementById('modal-msg-content').value = '';
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

// ─── Clock ──────────────────────────────────────────────────────
function updateClock() {
  const el = document.getElementById('serverTime');
  if (el) el.textContent = new Date().toLocaleString('zh-CN', {hour12:false});
}
setInterval(updateClock, 1000);

// ─── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateUserBadge();
  if (!SESSION_TOKEN && !API_KEY_FALLBACK) { openModal('modal-login'); return; }
  updateClock();
  refreshDashboard();
});

// ═══════════════════════════════════════════════════════════════════
//  v1.3 新增：ECharts 可视化
// ═══════════════════════════════════════════════════════════════════
let chartStatus = null;
let chartTrend = null;

function initCharts() {
  const theme = {
    bg: '#1a1d27', text: '#8b8fa8', accent: '#5b8def',
    green: '#4ade80', orange: '#fb923c', red: '#f87171', yellow: '#fbbf24',
  };
  chartStatus = echarts.init(document.getElementById('chart-task-status'));
  chartTrend  = echarts.init(document.getElementById('chart-task-trend'));

  chartStatus.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: theme.bg, borderColor: '#2a2d3e', textStyle: { color: theme.text } },
    legend: { bottom: 0, textStyle: { color: theme.text, fontSize: 12 } },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: theme.bg, borderWidth: 2 },
      label: { show: true, color: theme.text, fontSize: 12, formatter: '{b}: {c} ({d}%)' },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: 0, name: '已完成', itemStyle: { color: theme.green } },
        { value: 0, name: '进行中',  itemStyle: { color: theme.yellow } },
        { value: 0, name: '失败',    itemStyle: { color: theme.red } },
      ],
    }],
  });

  // 近7天趋势折线图（占位初始化）
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    days.push((d.getMonth()+1) + '/' + d.getDate());
  }
  chartTrend.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: theme.bg, borderColor: '#2a2d3e', textStyle: { color: theme.text },
      formatter: (p) => p[0].name + '<br>' + p.map(v => v.marker + ' ' + v.seriesName + ': <b>' + v.value + '</b>').join('<br>') },
    legend: { bottom: 0, textStyle: { color: theme.text, fontSize: 12 } },
    grid: { left: 40, right: 16, top: 16, bottom: 40 },
    xAxis: { type: 'category', data: days, axisLine: { lineStyle: { color: '#2a2d3e' } }, axisLabel: { color: theme.text, fontSize: 11 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisLabel: { color: theme.text, fontSize: 11 }, splitLine: { lineStyle: { color: '#2a2d3e', type: 'dashed' } } },
    series: [
      { name: '任务数', type: 'bar', smooth: true, data: [0,0,0,0,0,0,0], itemStyle: { color: theme.accent, borderRadius: [4,4,0,0] } },
      { name: '成功数', type: 'line', smooth: true, data: [0,0,0,0,0,0,0], itemStyle: { color: theme.green }, lineStyle: { width: 2 }, symbol: 'circle' },
    ],
  });

  window.addEventListener('resize', () => { chartStatus && chartStatus.resize(); chartTrend && chartTrend.resize(); });
}

function refreshCharts(tasks) {
  if (!chartStatus || !chartTrend) return;
  const all = tasks || [];
  const completed = all.filter(t => t.status === 'completed').length;
  const running    = all.filter(t => t.status === 'running' || t.status === 'pending').length;
  const failed     = all.filter(t => t.status === 'failed').length;

  chartStatus.setOption({
    series: [{ data: [
      { value: completed, name: '已完成', itemStyle: { color: '#4ade80' } },
      { value: running,    name: '进行中',  itemStyle: { color: '#fbbf24' } },
      { value: failed,     name: '失败',    itemStyle: { color: '#f87171' } },
    ]}],
  });

  // 近7天趋势
  const now = Date.now();
  const dayMs = 86400000;
  const days = [];
  for (let i = 6; i >= 0; i--) days.push(new Date(now - i * dayMs));

  const counts = days.map(d => {
    const s = new Date(d); s.setHours(0,0,0,0);
    const e = new Date(d); e.setHours(23,59,59,999);
    return all.filter(t => { const ct = new Date(t.created_at); return ct >= s && ct <= e; }).length;
  });
  const successes = days.map(d => {
    const s = new Date(d); s.setHours(0,0,0,0);
    const e = new Date(d); e.setHours(23,59,59,999);
    return all.filter(t => t.status === 'completed' && new Date(t.completed_at||t.updated_at||0) >= s && new Date(t.completed_at||t.updated_at||0) <= e).length;
  });

  chartTrend.setOption({
    xAxis: { data: days.map(d => (d.getMonth()+1)+'/'+d.getDate()) },
    series: [
      { data: counts },
      { data: successes },
    ],
  });
}

// ═══════════════════════════════════════════════════════════════════
//  v1.3 新增：模板管理器
// ═══════════════════════════════════════════════════════════════════

// 内置/默认模板（API 返回前显示占位）
const BUILTIN_TEMPLATES = [
  { id: 'status_check', name: '状态检查', agent: 'system', description: '检查 OpenClaw Gateway 运行状态和活跃会话', params: {}, created_at: null },
  { id: 'quick_fetch',  name: '快速抓取',  agent: 'info-fetcher', description: '快速抓取当日 AI 资讯热点', params: { scope: 'brief' }, created_at: null },
  { id: 'tech_brief',   name: '技术简报',  agent: 'tech-analyst', description: '生成推荐系统+大模型技术前沿简报', params: { scope: 'brief', agents: ['tech-analyst'] }, created_at: null },
  { id: 'biz_brief',    name: '商业简报',  agent: 'biz-analyst',  description: '生成商业需求洞察报告', params: { scope: 'brief', agents: ['biz-analyst'] }, created_at: null },
];

function renderTemplates(templates) {
  // 缓存所有模板（用于编辑表单预填充）
  window._templateCache = {};
  const all = [...BUILTIN_TEMPLATES];
  if (templates && templates.length) {
    templates.forEach(t => {
      window._templateCache[t.id] = t;  // 写入缓存
      const existing = all.findIndex(b => b.id === t.id);
      if (existing >= 0) all[existing] = t;
      else all.push(t);
    });
  }
  const builtins = all.filter(t => !t.created_at || BUILTIN_TEMPLATES.find(b => b.id === t.id));
  const custom   = all.filter(t => t.created_at && !BUILTIN_TEMPLATES.find(b => b.id === t.id));

  function row(t, isBuiltin) {
    const params = t.params ? JSON.stringify(t.params).slice(0,40) : '';
    let ops;
    if (isBuiltin) {
      ops = '<span style="font-size:12px;color:var(--text-dim)">内置模板</span>';
    } else {
      ops = '<button class="btn btn-sm" onclick="openEditTemplate(\''+esc(t.id)+'\')" style="margin-right:4px">&#9998; 编辑</button>' +
            '<button class="btn btn-sm danger" onclick="deleteTemplate(\''+esc(t.id)+'\')">&#128465; 删除</button>';
    }
    return '<tr>' +
      '<td><code>'+esc(t.id)+'</code></td>' +
      '<td><b>'+esc(t.name||t.id)+'</b></td>' +
      '<td>'+esc(t.agent||'-')+'</td>' +
      '<td style="font-size:12px;color:var(--text-dim)">'+esc(t.description||'-')+'</td>' +
      '<td><code style="font-size:11px">'+esc(params||'-')+'</code></td>' +
      '<td style="font-size:12px;color:var(--text-dim)">'+(t.created_at ? fmtTime(t.created_at) : '<span style="color:var(--accent)">内置</span>')+'</td>' +
      '<td style="white-space:nowrap">'+ops+'</td>' +
    '</tr>';
  }

  let html = '';
  if (builtins.length) {
    html += '<tr><td colspan="7" style="font-size:11px;color:var(--text-dim);background:rgba(0,0,0,0.2);padding:8px 16px">&#9881; 内置模板（来自 templates.yaml）</td></tr>';
    builtins.forEach(t => { html += row(t, true); });
  }
  if (custom.length) {
    html += '<tr><td colspan="7" style="font-size:11px;color:var(--text-dim);background:rgba(0,0,0,0.2);padding:8px 16px">&#128196; 自定义模板</td></tr>';
    custom.forEach(t => { html += row(t, false); });
  }
  if (!all.length) html = '<tr><td colspan="7" class="empty">暂无模板</td></tr>';
  document.getElementById('templatesList').innerHTML = html;
}

async function loadTemplates() {
  try {
    const data = await api('/api/v1/templates').catch(() => ({}));
    renderTemplates(data.templates || []);
  } catch(e) {
    renderTemplates([]);
    toast('&#9888; 模板加载失败: '+e.message, 'error');
  }
}

function openNewTemplate() {
  document.getElementById('modal-template-title').textContent = '&#128196; 新建任务模板';
  document.getElementById('modal-tpl-id').value = '';
  document.getElementById('modal-tpl-id').disabled = false;
  document.getElementById('modal-tpl-name').value = '';
  document.getElementById('modal-tpl-agent').value = 'info-fetcher';
  document.getElementById('modal-tpl-desc').value = '';
  document.getElementById('modal-tpl-params').value = '{}';
  document.getElementById('modal-tpl-action').value = 'spawn';
  document.getElementById('modal-tpl-editing').value = '';  // 新建模式
  openModal('modal-new-template');
}

// ── 模板编辑 ─────────────────────────────────────────────────────
window._templateCache = {};  // 缓存已加载的模板列表

function openEditTemplate(templateId) {
  const t = window._templateCache[templateId];
  if (!t) { toast('&#9888; 模板数据未加载，请刷新后重试', 'error'); return; }
  document.getElementById('modal-template-title').textContent = '&#9998; 编辑任务模板';
  document.getElementById('modal-tpl-id').value = t.id || templateId;
  document.getElementById('modal-tpl-id').disabled = true;   // ID 不可改
  document.getElementById('modal-tpl-name').value = t.name || '';
  document.getElementById('modal-tpl-agent').value = t.agent || 'info-fetcher';
  document.getElementById('modal-tpl-desc').value = t.description || '';
  document.getElementById('modal-tpl-params').value = t.params ? JSON.stringify(t.params, null, 2) : '{}';
  document.getElementById('modal-tpl-action').value = t.action || 'spawn';
  document.getElementById('modal-tpl-editing').value = templateId;  // 编辑模式
  openModal('modal-new-template');
}

async function submitTemplate() {
  const id        = document.getElementById('modal-tpl-id').value.trim();
  const name      = document.getElementById('modal-tpl-name').value.trim();
  const agent     = document.getElementById('modal-tpl-agent').value;
  const desc      = document.getElementById('modal-tpl-desc').value.trim();
  const paramsStr = document.getElementById('modal-tpl-params').value.trim() || '{}';
  const action     = document.getElementById('modal-tpl-action').value;
  const editingId = document.getElementById('modal-tpl-editing').value;  // 空=新建，有值=编辑

  if (!id)   { toast('&#9888; 请输入模板 ID', 'error'); return; }
  if (!name) { toast('&#9888; 请输入模板名称', 'error'); return; }
  let params = {};
  try { params = JSON.parse(paramsStr); } catch(e) { toast('&#9888; 默认参数 JSON 格式错误: '+e.message, 'error'); return; }

  try {
    const payload = { name, agent, description: desc, params, action };
    if (editingId) {
      // 编辑模式：PUT /api/v1/templates/{id}
      await api('/api/v1/templates/'+encodeURIComponent(editingId), {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      toast('&#10004; 模板「'+name+'」已更新', 'success');
    } else {
      // 新建模式：POST /api/v1/templates
      await api('/api/v1/templates', {
        method: 'POST',
        body: JSON.stringify({ id, ...payload }),
      });
      toast('&#10004; 模板「'+name+'」已创建', 'success');
    }
    closeModal('modal-new-template');
    loadTemplates();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}

async function deleteTemplate(id) {
  if (!confirm('确认删除模板「'+id+'」？此操作不可撤销。')) return;
  try {
    await api('/api/v1/templates/'+encodeURIComponent(id), { method: 'DELETE' });
    toast('&#10004; 模板已删除', 'success');
    loadTemplates();
  } catch(e) { toast('&#10006; '+e.message, 'error'); }
}
