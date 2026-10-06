const $ = s => document.querySelector(s);
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const terminal = new Set(['completed','awaiting_approval','needs_clarification','failed','cancelled']);
const crew = {
  email: {icon:'✉',role:'Communication',color:'#e5bc92'},
  planner: {icon:'◷',role:'Time & priorities',color:'#d0e8a0'},
  tutor: {icon:'⌁',role:'Personal knowledge',color:'#bcaedc'},
  fitness: {icon:'↗',role:'Training & recovery',color:'#a7c8d4'},
  code: {icon:'⌘',role:'Engineering',color:'#cabd9a'}
};
let overview, history = [], current = null, stream = null, activeTab = 'response', activeView = 'dashboard';
function title(value) { return String(value ?? '').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase()); }
function time(value) { return new Date(value).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',timeZone:overview?.mode.timezone ?? 'America/New_York'}); }
function date(value) { return new Date(value).toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:overview?.mode.timezone ?? 'America/New_York'}); }
function error(message) { $('#error-banner').textContent = message; $('#error-banner').classList.toggle('hidden',!message); }
async function api(path, options={}) {
  const response = await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...options.headers}});
  const body = await response.json();
  if(!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status}). Check your input.`);
  return body;
}
function switchView(view) {
  activeView = view;
  document.querySelectorAll('.view').forEach(el=>el.classList.toggle('hidden',el.id !== view+'-view'));
  document.querySelectorAll('.nav-item').forEach(el=>el.classList.toggle('active',el.dataset.view===view));
  const headings = {
    dashboard:['Command center','A little less chaos.<br>A lot more coordination.','One request. The right agents. A plan you can actually use.'],
    history:['Execution history','Every workflow.<br>Every decision.','Inspect previous runs, agent outputs and the state behind each result.'],
    automations:['Automations','A rhythm for<br>your everyday.','Morning priorities, afternoon check-ins, and an evening reset.'],
    integrations:['Integrations','Your ecosystem,<br>connected.','Service boundaries keep your apps independent and your workflows coordinated.']
  };
  $('#breadcrumb').textContent = headings[view][0];
  $('#page-title').innerHTML = headings[view][1];
  $('#page-description').textContent = headings[view][2];
}
async function refresh() {
  [overview,history] = await Promise.all([api('/overview'),api('/runs')]);
  $('#connection-text').textContent = 'Backend online';
  $('#connection-dot').classList.remove('offline');
  $('#demo-date').textContent = new Date(overview.data.date+'T12:00:00').toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'});
  $('#timezone').textContent = overview.mode.timezone;
  $('#footer-mode').textContent = 'OPENAI + JEV / SAMPLE DATA';
  const m = overview.metrics;
  $('#metrics').innerHTML = [
    ['◈','Specialized agents','05','One shared state'],['↗','Workflows run',m.runs,'Recent 50 runs'],
    ['◎','Awaiting approval',m.pending,'You stay in control'],['◷','Avg. workflow time',(m.average_ms/1000).toFixed(1)+'s',overview.mode.reasoner+' reasoning']
  ].map(([icon,label,value,note])=>`<div class="metric"><span class="metric-icon">${icon}</span><div><div class="metric-label">${escapeHTML(label)}</div><strong>${escapeHTML(value)}</strong></div><small>${escapeHTML(note)}</small></div>`).join('');
  $('#calendar-list').innerHTML = [...overview.data.calendar_events].sort((a,b)=>a.start.localeCompare(b.start)).map(e=>`<div class="calendar-item"><span class="calendar-time">${escapeHTML(time(e.start))}</span><div class="calendar-title">${escapeHTML(e.title)}<small>${escapeHTML(time(e.start))} – ${escapeHTML(time(e.end))}</small></div></div>`).join('');
  $('#task-count').textContent = overview.data.tasks.filter(t=>!t.completed).length;
  $('#task-list').innerHTML = overview.data.tasks.map(t=>`<div class="task-item ${t.completed?'done':''}"><input type="checkbox" id="task-${escapeHTML(t.id)}" data-task="${escapeHTML(t.id)}" ${t.completed?'checked':''}><label for="task-${escapeHTML(t.id)}">${escapeHTML(t.title)}<small>Due ${escapeHTML(date(t.due))} · ${t.minutes} min</small></label></div>`).join('');
  const f = overview.data.fitness;
  $('#fitness-context').textContent = `${f.weekly_sessions} sessions this week. Up next: ${f.next_workout.toLowerCase()} · ${f.duration_minutes} min.`;
  renderHistory(); renderSchedules(); renderIntegrations();
}
function renderCrew() {
  $('#agent-grid').innerHTML = Object.entries(crew).map(([name,agent])=>{
    const status = current?.agents[name]?.status ?? 'idle';
    const selected = current?.agent_sequence.includes(name);
    return `<div class="agent-card ${selected?'active':''} ${status}" style="--agent-color:${agent.color}" title="${escapeHTML(current?.agents[name]?.summary || agent.role)}"><span class="agent-icon">${agent.icon}</span><div class="agent-name">${title(name)}</div><div class="agent-role">${agent.role}</div><div class="agent-status">${status==='completed'?'✓ ':status==='running'?'◌ ':''}${status==='idle'&&selected?'Queued':title(status)}</div></div>`;
  }).join('');
  if(!current) return;
  const status = current.workflow_status;
  $('#run-status').textContent = title(status);
  $('#run-status').className = 'pill '+(status==='running'||status==='queued'?'running':status==='failed'?'failed':'');
  $('#routing-title').textContent = current.selected_workflow ? title(current.selected_workflow)+' · '+title(current.decision.gate) : 'Jev · Decision layer';
  $('#routing-description').textContent = current.decision.escalation || current.decision.reason || 'Routing your request…';
  $('#confidence').textContent = current.decision.confidence == null ? '—' : Math.round(current.decision.confidence*100)+'%';
  $('#confidence').title = current.decision.provider === 'user selection' ? 'Explicit workflow; no model confidence' : current.decision.provider === 'openrouter/jev' ? 'Confidence returned by Jev through OpenRouter' : 'Historical rule-based score; not returned by Jev';
  $('#workflow-path').innerHTML = ['REQUEST','ROUTER',...current.agent_sequence.map(n=>n.toUpperCase()),'RESPONSE'].map(escapeHTML).join('<span>→</span>');
  $('#run-meta').textContent = `${current.id.slice(0,8)} · ${(current.metrics.duration_ms/1000).toFixed(1)}s · ${current.tool_results.length} tool calls · ${current.metrics.model_calls} model calls`;
  $('#cancel-button').classList.toggle('hidden',terminal.has(status));
}
function renderOutput() {
  if(!current) return;
  const r = current;
  let content='';
  if(activeTab==='response') {
    content = `<div class="response-request">${escapeHTML(r.user_input)}</div>`;
    if(r.metrics.reasoner === 'demo') content += '<div class="info-note">Historical run using simulated reasoning. Submit the request again to use OpenAI and Jev.</div>';
    else if(r.metrics.reasoner === 'claude') content += '<div class="info-note">Historical run using Claude narration and rule-based routing. New requests use OpenAI and Jev.</div>';
    if(r.error) content += `<div class="error-banner">${escapeHTML(r.error)}</div><button class="button" data-retry="${r.id}">Retry request ↗</button>`;
    else if(!r.final_response) content += `<div class="empty-state"><div class="empty-symbol">◌</div><h3>${r.current_agent ? title(r.current_agent)+' is working' : 'Workflow queued'}</h3><p>Follow progress in Activity or inspect Shared state.</p></div>`;
    else content += `<div class="response-text">${escapeHTML(r.final_response)}</div>`;
    if(r.code_output?.coder_output?.artifact) content += `<details><summary>Generated code example</summary><pre>${escapeHTML(r.code_output.coder_output.artifact)}</pre><small>Example only. Generated test cases have not been executed.</small></details>`;
    if(r.proposed_actions.length) content += `<div class="actions"><h3>Proposed calendar blocks</h3>${r.proposed_actions.map(a=>`<div class="action"><div><strong>${escapeHTML(a.title)}</strong><small>${escapeHTML(time(a.payload.start))} – ${escapeHTML(time(a.payload.end))} · ${escapeHTML(a.target)}</small></div>${a.status==='pending'?`<div class="action-buttons"><button class="button small" data-action="${a.id}" data-decision="reject">Reject</button><button class="button small primary" data-action="${a.id}" data-decision="approve">Approve ↗</button></div>`:`<span class="pill">${title(a.status)}</span>`}</div>`).join('')}</div>`;
  } else if(activeTab==='activity') {
    content = r.events.map(e=>`<div class="event"><time>${escapeHTML(time(e.at))}</time><div><strong>${escapeHTML(e.node)}</strong><p>${escapeHTML(e.message)}</p></div></div>`).join('') || '<p>Waiting for the first graph event.</p>';
  } else if(activeTab==='state') {
    content = `<div class="eyebrow">PERSISTED SNAPSHOT · REVISION ${r.revision}</div><p style="font-size:11px">Each agent writes its output here. Later agents read it through LangGraph.</p><details open><summary>Full workflow state</summary><pre>${escapeHTML(JSON.stringify(r,null,2))}</pre></details><button class="button small" id="download-state">Download JSON ↓</button>`;
  } else {
    content = r.sources.length ? r.sources.map(s=>`<div class="source-item"><h3>${escapeHTML(s.title)}</h3><small>${escapeHTML(s.source)} · relevance ${s.relevance}</small><p>${escapeHTML(r.retrieved_documents.find(d=>d.id===s.id)?.content || '')}</p></div>`).join('') : '<div class="empty-state"><h3>No documents retrieved yet.</h3><p>Source citations appear when Tutor or Code retrieves knowledge.</p></div>';
    content += `<details><summary>Service and tool results (${r.tool_results.length})</summary><pre>${escapeHTML(JSON.stringify(r.tool_results,null,2))}</pre></details>`;
  }
  $('#output-content').innerHTML = content;
}
async function selectRun(run) {
  if(stream) {stream.close();stream=null;}
  current = run; switchView('dashboard'); renderCrew();renderOutput();
  if(terminal.has(run.workflow_status)) return;
  const observedId = run.id;
  stream = new EventSource(`/api/runs/${run.id}/events`);
  stream.addEventListener('state',async event=>{
    if(current?.id!==observedId) return;
    current = JSON.parse(event.data);renderCrew();renderOutput();
    if(terminal.has(current.workflow_status)) {stream?.close();stream=null;try{await refresh();}catch(e){error(e.message);}}
  });
  stream.onerror = async()=>{
    stream?.close();stream=null;
    try {const latest = await api('/runs/'+observedId);if(current?.id!==observedId)return;await selectRun(latest);}
    catch(e){error('Live updates disconnected. Refresh to reconnect.');}
  };
}
async function submit() {
  const input = $('#request-input').value.trim();
  if(!input) {$('#request-input').focus();return;}
  const button = $('#run-button');button.disabled=true;error('');
  try {const run = await api('/runs',{method:'POST',body:JSON.stringify({user_input:input,workflow:$('#workflow-select').value})});activeTab='response';setTabs();await selectRun(run);}
  catch(e){error(e.message);}finally{button.disabled=false;}
}
function setTabs(){document.querySelectorAll('.tab').forEach(el=>{const active=el.dataset.tab===activeTab;el.classList.toggle('active',active);el.setAttribute('aria-selected',String(active));});}
function renderHistory() {
  $('#history-list').innerHTML = history.length ? history.map(r=>`<div class="history-item"><div class="history-main"><strong>${escapeHTML(r.user_input)}</strong><small>${escapeHTML(date(r.created_at))} · ${escapeHTML(time(r.created_at))} · ${escapeHTML(r.agent_sequence.map(title).join(' → ') || 'Routing')} · ${(r.metrics.duration_ms/1000).toFixed(1)}s</small></div><span class="pill ${r.workflow_status==='failed'?'failed':''}">${title(r.workflow_status)}</span><button class="button small" data-open-run="${r.id}">Inspect ↗</button></div>`).join('') : '<div class="empty-state"><h3>A clean slate.</h3><p>Your completed and active workflows will appear here.</p></div>';
}
function renderSchedules() {
  $('#schedule-list').innerHTML = overview.schedules.map(s=>`<section class="panel schedule-card"><span class="eyebrow">SCHEDULED WORKFLOW</span><h2>${title(s.id)}</h2><div class="schedule-time">${String(s.hour).padStart(2,'0')}:${String(s.minute).padStart(2,'0')}</div><form data-schedule="${s.id}"><label>Hour <input type="number" name="hour" value="${s.hour}" min="0" max="23" required></label><label>Minute <input type="number" name="minute" value="${s.minute}" min="0" max="59" required></label><div class="schedule-controls"><label><input type="checkbox" name="enabled" ${s.enabled?'checked':''}> Enable daily schedule</label></div><small>${escapeHTML(s.timezone)} · ${s.next_run?'Next: '+escapeHTML(date(s.next_run))+' '+escapeHTML(time(s.next_run)):'Currently paused'}</small><div class="schedule-buttons"><button class="button small" type="submit">Save schedule</button><button class="button small primary" type="button" data-run-schedule="${s.id}">Run now ↗</button></div></form></section>`).join('');
  $('#notification-list').innerHTML = [...overview.data.notifications].reverse().slice(0,10).map(n=>`<div class="history-item"><div class="history-main"><strong>${escapeHTML(n.content.slice(0,140))}…</strong></div><button class="button small" data-open-run="${n.run_id}">Inspect ↗</button></div>`).join('') || '<div class="empty-state"><h3>Nothing delivered yet.</h3><p>Run a digest or check-in to see a notification here.</p></div>';
}
function renderIntegrations() {
  $('#integration-list').innerHTML = overview.integrations.map(i=>`<section class="panel integration-card"><div class="integration-icon">⌘</div><div><h2>${escapeHTML(i.name)}</h2><span class="pill">${title(i.status)}</span><p>${escapeHTML(i.todo)}</p></div></section>`).join('');
}
$('#run-form').addEventListener('submit',event=>{event.preventDefault();submit();});
$('#request-input').addEventListener('keydown',event=>{if(event.key==='Enter'&&(event.metaKey||event.ctrlKey)){event.preventDefault();submit();}});
document.addEventListener('click',async event=>{
  const button = event.target.closest('button');if(!button)return;
  try {
    if(button.dataset.view){switchView(button.dataset.view);await refresh();}
    if(button.dataset.prompt){switchView('dashboard');$('#request-input').value=button.dataset.prompt;$('#workflow-select').value='auto';$('#request-input').focus();}
    if(button.dataset.tab){activeTab=button.dataset.tab;setTabs();renderOutput();}
    if(button.dataset.openRun){await selectRun(await api('/runs/'+button.dataset.openRun));}
    if(button.dataset.retry){$('#request-input').value=current.user_input;$('#workflow-select').value=current.requested_workflow;await submit();}
    if(button.dataset.action){button.disabled=true;current=await api(`/runs/${current.id}/actions/${button.dataset.action}`,{method:'POST',body:JSON.stringify({decision:button.dataset.decision})});renderCrew();renderOutput();await refresh();}
    if(button.dataset.runSchedule){button.disabled=true;await selectRun(await api('/schedules/'+button.dataset.runSchedule+'/run',{method:'POST'}));}
    if(button.id==='cancel-button'){current=await api('/runs/'+current.id+'/cancel',{method:'POST'});renderCrew();renderOutput();}
    if(button.id==='refresh-history')await refresh();
    if(button.id==='reset-button'){button.disabled=true;await api('/demo/reset',{method:'POST'});await refresh();if(current){current=await api('/runs/'+current.id);renderCrew();renderOutput();}error('');}
    if(button.id==='download-state'){const url=URL.createObjectURL(new Blob([JSON.stringify(current,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`caesaros-${current.id}.json`;a.click();URL.revokeObjectURL(url);}
  }catch(e){error(e.message);}finally{button.disabled=false;}
});
document.addEventListener('change',async event=>{
  if(!event.target.dataset.task)return;
  event.target.disabled=true;
  try{await api('/tasks/'+event.target.dataset.task,{method:'PATCH',body:JSON.stringify({completed:event.target.checked})});await refresh();}catch(e){event.target.checked=!event.target.checked;error(e.message);}finally{event.target.disabled=false;}
});
document.addEventListener('submit',async event=>{
  const form=event.target;if(!form.dataset.schedule)return;event.preventDefault();
  const values=new FormData(form);const button=form.querySelector('button[type=submit]');button.disabled=true;
  try{await api('/schedules/'+form.dataset.schedule,{method:'PATCH',body:JSON.stringify({enabled:values.has('enabled'),hour:Number(values.get('hour')),minute:Number(values.get('minute'))})});await refresh();error('');}catch(e){error(e.message);}finally{button.disabled=false;}
});
renderCrew();
refresh().then(async()=>{const active=history.find(r=>!terminal.has(r.workflow_status));if(active)await selectRun(active);}).catch(e=>{error('Could not reach the backend. '+e.message);$('#connection-text').textContent='Backend offline';$('#connection-dot').classList.add('offline');});
