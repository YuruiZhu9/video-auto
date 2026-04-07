/* ClawCtl Web Admin v3 — Application Logic */
const API_BASE = '/api/v1';
let _apiKey = '';
let _conn = null;
let _activeStream = null;
let _autoScroll = true;
let _logFilter = { error: true, warn: true, info: true, debug: true };
let _tasks = {};
let _deferredPrompt = null;

document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(location.search);
  _apiKey = params.get('token') || localStorage.getItem('clawctl_token') || '';
  if (!_apiKey) showToast('未设置 API Key，请在 URL 后加 ?token=xxx', 'error');
  initTabs(); initBottomTabs();
  loadActiveStreams(); loadHistory(); loadStatus();
  setupSSEAllStreams();
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault(); _deferredPrompt = e;
    const btn = document.getElementById('btn-install');
    if (btn) btn.style.display = 'flex';
  });
});

function initTabs() {
  document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}
function initBottomTabs() {
  document.querySelectorAll('.btm-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab(btn.dataset.tab);
      document.querySelectorAll('.btm-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}
function switchTab(tabId) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('panel-' + tabId)?.classList.add('active');
  document.querySelector('.topbar-tabs .tab[data-tab="'+tabId+'"]')?.classList.add('active');
  if (tabId === 'logs') loadActiveStreams();
  if (tabId === 'dag') loadDAGTemplates();
  if (tabId === 'status') loadStatus();
}
async function api(path, options) {
  options = options || {};
  const resp = await fetch(API_BASE + path, {
    ...options,
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + _apiKey, ...(options.headers||{}) },
  });
  if (!resp.ok) { const err = await resp.json().catch(() => ({})); throw new Error(err.error || 'HTTP '+resp.status); }
  return resp.json();
}
function updateConnDot(status) {
  const dot = document.getElementById('conn-dot');
  if (!dot) return;
  dot.className = 'dot';
  if (status==='connected') dot.classList.add('dot-green');
  else if (status==='connecting') dot.classList.add('dot-yellow');
  else dot.classList.add('dot-red');
}
function toggleConnection() {
  if (_conn) { _conn.close(); _conn=null; updateConnDot('disconnected'); showToast('SSE 连接已断开','info'); }
  else { setupSSEAllStreams(); showToast('正在连接...','info'); }
}
function setupSSEAllStreams() {
  if (_conn) _conn.close();
  updateConnDot('connecting');
  _conn = new EventSource(API_BASE+'/stream/subscribe/all?token='+encodeURIComponent(_apiKey));
  _conn.addEventListener('stream_list', e => { const d=JSON.parse(e.data); updateStreamSelector(d.streams||[]); });
  _conn.addEventListener('heartbeat', () => updateConnDot('connected'));
  _conn.addEventListener('stream_start', e => { onStreamStart(JSON.parse(e.data)); });
  _conn.addEventListener('stream_chunk', e => { const d=JSON.parse(e.data); appendLog(d.task_id, d.content, d.level, d.timestamp); });
  _conn.addEventListener('stream_section', e => { const d=JSON.parse(e.data); appendLog(d.task_id, d.content, 'section', d.timestamp); });
  _conn.addEventListener('stream_progress', e => { const d=JSON.parse(e.data); onProgressUpdate(d.task_id, d.progress, d.message); });
  _conn.addEventListener('stream_complete', e => { onStreamComplete(JSON.parse(e.data)); });
  _conn.addEventListener('stream_history', e => { const d=JSON.parse(e.data); appendLog(d.task_id, d.content, d.level, d.timestamp); });
  _conn.onerror = () => { updateConnDot('disconnected'); setTimeout(() => { if(!_conn||_conn.readyState===EventSource.CLOSED) setupSSEAllStreams(); }, 3000); };
  _conn.onopen = () => updateConnDot('connected');
}
let _currentLogTaskId = null;
function updateStreamSelector(streams) {
  const sel = document.getElementById('stream-select');
  if (!sel) return;
  const cur = sel.value;
  sel.innerHTML = '<option value="">— 选择任务流 —</option>';
  streams.forEach(s => {
    sel.innerHTML += '<option value="'+s.task_id+'">'+s.agent_name+' · '+s.task_id.slice(-8)+' · '+s.status+'</option>';
  });
  if (cur && streams.find(s=>s.task_id===cur)) sel.value = cur;
}
function loadActiveStreams() {
  api('/stream/active').then(d => {
    updateStreamSelector(d.active_streams||[]);
    renderActiveTasks(d.active_streams||[]);
  }).catch(()=>{});
}
function switchStream() {
  const taskId = document.getElementById('stream-select').value;
  _currentLogTaskId = taskId;
  const viewer = document.getElementById('log-viewer');
  if (!taskId) { viewer.innerHTML='<div class="log-empty">📡 选择左侧任务流查看实时日志</div>'; return; }
  viewer.innerHTML='<div class="log-empty">🔄 正在连接日志流...</div>';
  const es = new EventSource(API_BASE+'/stream/subscribe/'+taskId+'?token='+encodeURIComponent(_apiKey));
  es.addEventListener('stream_start', () => { viewer.innerHTML=''; });
  ['stream_history','stream_chunk','stream_section','stream_code'].forEach(ev => {
    es.addEventListener(ev, e => { const d=JSON.parse(e.data); appendLogToViewer(viewer, d.content, d.level||'info', d.timestamp); });
  });
  es.addEventListener('stream_progress', e => {
    const d=JSON.parse(e.data);
    appendLogToViewer(viewer, '📊 ['+d.progress+'%] '+d.message, 'info', d.timestamp);
  });
  es.addEventListener('stream_complete', e => {
    const d=JSON.parse(e.data);
    appendLogToViewer(viewer, '\n✅ 任务结束 ('+d.duration_ms+'ms)', 'success', d.timestamp);
    es.close();
  });
  es.onerror = () => { viewer.innerHTML+='\n<span class="lvl-warn">连接断开</span>'; es.close(); };
}
function appendLog(taskId, content, level, timestamp) {
  if (taskId !== _currentLogTaskId) return;
  const viewer = document.getElementById('log-viewer');
  if (viewer) appendLogToViewer(viewer, content, level, timestamp);
}
function appendLogToViewer(viewer, content, level, timestamp) {
  const ts = timestamp ? new Date(timestamp).toLocaleTimeString('zh-CN',{hour12:false}) : '';
  if (level==='code') {
    const el=document.createElement('span'); el.className='log-code'; el.textContent=content; viewer.appendChild(el);
  } else {
    const el=document.createElement('span');
    el.className='log-line lvl-'+(level||'info');
    el.innerHTML = (ts ? '<span class="log-ts">'+ts+'</span>' : '')+escapeHtml(content);
    viewer.appendChild(el);
  }
  if (_autoScroll) viewer.scrollTop = viewer.scrollHeight;
}
function applyLogFilter() {
  _logFilter.error = document.getElementById('filter-error')?.checked ?? true;
  _logFilter.warn = document.getElementById('filter-warn')?.checked ?? true;
  _logFilter.info = document.getElementById('filter-info')?.checked ?? true;
  _logFilter.debug = document.getElementById('filter-debug')?.checked ?? true;
}
function toggleAutoScroll() {
  _autoScroll = !_autoScroll;
  document.getElementById('auto-scroll-indicator').textContent = _autoScroll ? '✅' : '❌';
}
function clearLogViewer() {
  const v = document.getElementById('log-viewer');
  if (v) v.innerHTML='<div class="log-empty">📡 日志已清空</div>';
}
function renderActiveTasks(streams) {
  const c = document.getElementById('active-tasks');
  if (!c) return;
  if (!streams||!streams.length) { c.innerHTML='<div class="empty-state">暂无运行中的任务</div>'; return; }
  c.innerHTML = streams.map(s => '<div class="task-card active-task" onclick="subscribeStream(\''+s.task_id+'\')">'+
    '<div class="task-card-progress" id="prog-'+s.task_id.replace(/[^a-zA-Z0-9]/g,'_')+'" style="width:0%"></div>'+
    '<div class="task-icon">'+getTaskIcon(s.status)+'</div>'+
    '<div class="task-info"><div class="task-name">'+escapeHtml(s.agent_name)+'</div>'+
    '<div class="task-meta"><span class="task-badge badge-'+s.status+'">'+s.status+'</span>'+
    '<span>ID: '+s.task_id.slice(-8)+'</span><span>'+(s.started_at?timeAgo(s.started_at):'刚刚')+'</span></div></div>'+
    '<div class="task-actions"><button class="btn-icon" onclick="event.stopPropagation();subscribeStream(\''+s.task_id+'\')" title="查看日志">📜</button></div>'+
    '</div>').join('');
}
async function loadHistory() {
  try {
    const [histData, taskHist] = await Promise.all([
      api('/stream/history?limit=20'),
      api('/tasks/history?limit=20').catch(() => ({tasks:[]})),
    ]);
    const history = [...(histData.history||[]),...(taskHist.tasks||[])]
      .sort((a,b)=>(b.started_at||b.created_at||'')>(a.started_at||a.created_at||'')?1:-1).slice(0,20);
    document.getElementById('history-count').textContent = history.length;
    const c = document.getElementById('history-tasks');
    if (!history.length) { c.innerHTML='<div class="empty-state">暂无历史任务</div>'; return; }
    c.innerHTML = history.map(t => '<div class="task-card" onclick="subscribeStream(\''+t.task_id+'\')">'+
      '<div class="task-icon">'+getTaskIcon(t.status)+'</div>'+
      '<div class="task-info"><div class="task-name">'+escapeHtml(t.agent_name||t.name||t.task_id)+'</div>'+
      '<div class="task-meta"><span class="task-badge badge-'+(t.status||'pending')+'">'+(t.status||'pending')+'</span>'+
      '<span>'+(t.duration_ms?(t.duration_ms/1000).toFixed(1)+'s':'—')+'</span>'+
      '<span>'+timeAgo(t.started_at||t.created_at)+'</span></div>'+
      (t.error?'<div style="color:var(--error);font-size:0.75rem;margin-top:4px">❌ '+escapeHtml(t.error.slice(0,60))+'</div>':'')+'</div></div>'
    ).join('');
  } catch(e) { console.error(e); }
}
function refreshTasks() { loadActiveStreams(); loadHistory(); showToast('已刷新','success'); }
function onStreamStart(d) { _tasks[d.task_id]=d; loadActiveStreams(); }
function onProgressUpdate(taskId, progress) {
  const el = document.getElementById('prog-'+taskId.replace(/[^a-zA-Z0-9]/g,'_'));
  if (el) el.style.width=progress+'%';
}
function onStreamComplete(d) { loadActiveStreams(); loadHistory(); showToast('✅ 任务 '+d.task_id.slice(-8)+' 完成','success'); }
function subscribeStream(taskId) { _currentLogTaskId=taskId; switchTab('logs'); setTimeout(() => { const s=document.getElementById('stream-select'); if(s){s.value=taskId;switchStream();} }, 50); }
async function execNlCommand() {
  const text = document.getElementById('nl-command').value.trim();
  if (!text) { showToast('请输入命令','error'); return; }
  if (!_apiKey) { showToast('请先设置 API Key','error'); return; }
  try {
    const result = await api('/stream/nl/execute', {method:'POST', body:JSON.stringify({text})});
    document.getElementById('nl-command').value='';
    showToast('🚀 任务已启动: '+(result.intent||'unknown'),'info');
    _currentLogTaskId=result.task_id;
    switchTab('logs');
    setTimeout(() => { const s=document.getElementById('stream-select'); if(s&&result.task_id){s.value=result.task_id;switchStream();} }, 200);
  } catch(e) { showToast('执行失败: '+e.message,'error'); }
}
function openNewTaskModal() { document.getElementById('new-task-modal').classList.add('active'); document.getElementById('task-name').focus(); }
function closeModal() { document.getElementById('new-task-modal').classList.remove('active'); }
async function submitNewTask() {
  const name = document.getElementById('task-name').value.trim();
  const paramsText = document.getElementById('task-params').value.trim();
  const notify = document.getElementById('task-notify').checked;
  if (!paramsText) { showToast('任务描述不能为空','error'); return; }
  closeModal(); showToast('🚀 正在启动任务...','info');
  try {
    const result = await api('/stream/execute', {method:'POST', body:JSON.stringify({name:name||paramsText.slice(0,20), action:'spawn', params:{task:paramsText, runtime:'subagent'}, notify})});
    _currentLogTaskId=result.task_id;
    switchTab('logs');
    setTimeout(() => { const s=document.getElementById('stream-select'); if(s&&result.task_id){s.value=result.task_id;switchStream();} }, 200);
    showToast('✅ 任务已启动: '+(result.task_id?.slice(-8)),'success');
  } catch(e) { showToast('启动失败: '+e.message,'error'); }
}
const _dagDefinitions = {
  'morning-brief': { nodes:[{id:'fetch',label:'抓取资讯',icon:'🔍',x:100,y:80},{id:'analyze',label:'技术分析',icon:'🔬',x:300,y:80},{id:'report',label:'生成简报',icon:'📝',x:500,y:80}], edges:[{from:'fetch',to:'analyze'},{from:'analyze',to:'report'}] },
  'deep-research': { nodes:[{id:'ai-news',label:'AI动态',icon:'🤖',x:80,y:50},{id:'papers',label:'论文搜索',icon:'📄',x:280,y:50},{id:'biz',label:'商业洞察',icon:'💼',x:280,y:140},{id:'synthesize',label:'综合分析',icon:'🧠',x:480,y:95},{id:'report',label:'深度报告',icon:'📝',x:680,y:95}], edges:[{from:'ai-news',to:'synthesize'},{from:'papers',to:'synthesize'},{from:'biz',to:'synthesize'},{from:'synthesize',to:'report'}] },
  'ai-news-daily': { nodes:[{id:'fetch',label:'抓取',icon:'🔍',x:100,y:95},{id:'filter',label:'过滤去重',icon:'🧹',x:300,y:95},{id:'summarize',label:'摘要生成',icon:'✂️',x:500,y:50},{id:'translate',label:'翻译',icon:'🌐',x:500,y:140},{id:'publish',label:'发布推送',icon:'📨',x:700,y:95}], edges:[{from:'fetch',to:'filter'},{from:'filter',to:'summarize'},{from:'filter',to:'translate'},{from:'summarize',to:'publish'},{from:'translate',to:'publish'}] },
};
let _dagState = {};
async function loadDAGTemplates() {
  try { const d = await api('/dag/templates'); const sel = document.getElementById('dag-select'); if(sel&&d.templates) { sel.innerHTML='<option value="">— 选择 DAG 模板 —</option>'; d.templates.forEach(t => { sel.innerHTML+='<option value="'+t.id+'">'+(t.name||t.id)+'</option>'; }); } } catch(e) {}
}
function loadDAG() {
  const id = document.getElementById('dag-select')?.value;
  const c = document.getElementById('dag-container');
  if (!id||!_dagDefinitions[id]) { c.innerHTML='<div class="dag-empty">⬆ 选择一个 DAG 模板查看可视化</div>'; return; }
  _dagState={}; renderDAG(id, _dagDefinitions[id]);
}
function renderDAG(id, def) {
  const c = document.getElementById('dag-container');
  const svgW = Math.max(800, ...def.nodes.map(n=>n.x))+80;
  const svgH = Math.max(200, ...def.nodes.map(n=>n.y))+100;
  const edgePaths = def.edges.map(e => {
    const f = def.nodes.find(n=>n.id===e.from), t = def.nodes.find(n=>n.id===e.to);
    return '<path class="dag-edge" d="M '+(f.x+90)+' '+(f.y+20)+' C '+((f.x+90+t.x)/2)+' '+(f.y+20)+', '+((f.x+90+t.x)/2)+' '+(t.y+20)+', '+t.x+' '+(t.y+20)+'" />';
  }).join('');
  const nodeHTML = def.nodes.map(n => {
    const st = _dagState[n.id]||'pending';
    const bg = st==='running'?'#0ea5e9':st==='success'?'#22c55e':st==='failed'?'#ef4444':'#334155';
    return '<g class="dag-node" id="node-'+n.id+'" transform="translate('+n.x+','+n.y+')" onclick="toggleNodeStatus(\''+id+'\',\''+n.id+'\')">'+
      '<rect class="node-box" x="0" y="0" width="90" height="44" rx="8" fill="'+bg+'" opacity="0.9"/>'+
      '<text class="node-icon" x="45" y="18" text-anchor="middle" fill="white" font-size="14">'+n.icon+'</text>'+
      '<text class="node-label" x="45" y="34" text-anchor="middle" fill="white" font-size="11">'+n.label+'</text></g>';
  }).join('');
  c.innerHTML = '<svg class="dag-svg" viewBox="0 0 '+svgW+' '+svgH+'" style="height:'+svgH+'px">'+
    '<defs><marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#475569"/></marker></defs>'+
    edgePaths+nodeHTML+'</svg>';
}
function toggleNodeStatus(dagId, nodeId) {
  const statuses=['pending','running','success','failed','skipped'];
  const cur=_dagState[nodeId]||'pending';
  _dagState[nodeId]=statuses[(statuses.indexOf(cur)+1)%statuses.length];
  renderDAG(dagId, _dagDefinitions[dagId]);
}
async function executeSelectedDAG() {
  const id = document.getElementById('dag-select')?.value;
  if (!id) { showToast('请先选择 DAG 模板','error'); return; }
  showToast('🚀 正在执行 DAG...','info');
  try {
    _dagDefinitions[id].nodes.forEach(n => {_dagState[n.id]='running';});
    renderDAG(id, _dagDefinitions[id]);
    await api('/dag/'+id+'/execute', {method:'POST'});
    showToast('✅ DAG 执行已触发','success');
    setTimeout(() => {
      _dagDefinitions[id].nodes.forEach(n => {_dagState[n.id]='success';});
      renderDAG(id, _dagDefinitions[id]);
    }, 2000);
  } catch(e) {
    _dagDefinitions[id].nodes.forEach(n => {_dagState[n.id]='failed';});
    renderDAG(id, _dagDefinitions[id]);
    showToast('DAG 执行失败: '+e.message,'error');
  }
}
async function loadStatus() {
  try {
    const [status, monitor] = await Promise.all([api('/status'), api('/monitor/current').catch(()=>({}))]);
    const s = (name, val, cls) => { const el=document.getElementById(name); if(el){el.textContent=val;el.className='status-value '+(cls||'');} };
    s('s-openclaw', status.openclaw_connected?'✅ 已连接':'❌ 未连接', status.openclaw_connected?'good':'bad');
    s('s-active', status.tasks?.running??'—','');
    s('s-sessions', status.tasks?.total??'—','');
    if (monitor.memory) s('s-memory', (monitor.memory.used_percent||0).toFixed(1)+'%','');
    if (monitor.requests) s('s-requests', monitor.requests.total??'—','');
    s('s-last-update', new Date().toLocaleTimeString('zh-CN',{hour12:false}),'');
    try {
      const alerts = await api('/monitor/alerts?limit=5');
      const c = document.getElementById('alert-list');
      if (c) {
        if (!alerts.alerts?.length) c.innerHTML='<div class="empty-state">✅ 系统运行正常，无告警</div>';
        else c.innerHTML=alerts.alerts.map(a=>'<div class="alert-item '+(a.level==='warning'?'warn':'')+'"><div>'+(a.message||JSON.stringify(a))+'</div><div class="alert-time">⏱ '+timeAgo(a.created_at)+'</div></div>').join('');
      }
    } catch(e2) {}
  } catch(e) { console.error(e); }
  if (document.getElementById('panel-status')?.classList.contains('active')) setTimeout(loadStatus, 10000);
}
function subscribeStream(taskId) { _currentLogTaskId=taskId; switchTab('logs'); setTimeout(() => { const s=document.getElementById('stream-select'); if(s){s.value=taskId;switchStream();} }, 50); }
function installApp() { if(!_deferredPrompt){showToast('当前浏览器不支持安装 App','error');return;} _deferredPrompt.prompt(); _deferredPrompt.userChoice.then(r=>{if(r.outcome==='accepted')showToast('✅ App 安装中...','success');_deferredPrompt=null;}); }
function getTaskIcon(s) { return {running:'⚡',success:'✅',failed:'❌',pending:'⏳',queued:'🔜',cancelled:'🚫',skipped:'⏭'}[s]||'📋'; }
function escapeHtml(s) { if(!s)return''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function timeAgo(iso) { if(!iso)return'—'; const d=Date.now()-new Date(iso).getTime(); if(d<60000)return'刚刚'; if(d<3600000)return Math.floor(d/60000)+'分钟前'; if(d<86400000)return Math.floor(d/3600000)+'小时前'; return Math.floor(d/86400000)+'天前'; }
function showToast(msg, type) {
  const c=document.getElementById('toast-container');
  const t=document.createElement('div'); t.className='toast '+(type||'info'); t.textContent=msg; c.appendChild(t);
  setTimeout(()=>t.remove(), 3500);
}
