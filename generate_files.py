import os

index_html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Benchmark Task Monitor - Snorkel AI / Starfish</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-main: #0B0F19;
      --bg-card: #131B2E;
      --bg-card-hover: #19233C;
      --border-color: #232E4A;
      --text-main: #F1F5F9;
      --text-muted: #94A3B8;
      --primary: #3B82F6;
      --primary-hover: #2563EB;
      
      --status-accepted-bg: rgba(16, 185, 129, 0.12);
      --status-accepted-text: #34D399;
      --status-accepted-border: rgba(16, 185, 129, 0.3);
      
      --status-review-bg: rgba(245, 158, 11, 0.12);
      --status-review-text: #FBBF24;
      --status-review-border: rgba(245, 158, 11, 0.3);

      --status-eval-bg: rgba(168, 85, 247, 0.12);
      --status-eval-text: #C084FC;
      --status-eval-border: rgba(168, 85, 247, 0.3);

      --status-revision-bg: rgba(244, 63, 94, 0.12);
      --status-revision-text: #FB7185;
      --status-revision-border: rgba(244, 63, 94, 0.3);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 60px;
    }
    header {
      background: rgba(19, 27, 46, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-container { display: flex; align-items: center; gap: 12px; }
    .logo-badge {
      background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
      width: 38px; height: 38px; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 20px; color: #fff;
      box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
    }
    .logo-text h1 { font-size: 18px; font-weight: 700; letter-spacing: -0.02em; }
    .logo-text p { font-size: 12px; color: var(--text-muted); }
    .header-actions { display: flex; align-items: center; gap: 16px; }
    .select-project {
      background: var(--bg-card); border: 1px solid var(--border-color);
      color: var(--text-main); padding: 8px 16px; border-radius: 8px;
      font-size: 14px; font-weight: 500; cursor: pointer; outline: none;
    }
    .btn {
      background: var(--primary); color: white; border: none;
      padding: 8px 16px; border-radius: 8px; font-size: 14px;
      font-weight: 500; cursor: pointer; display: inline-flex;
      align-items: center; gap: 8px; transition: all 0.2s;
    }
    .btn:hover { background: var(--primary-hover); }
    .btn-secondary {
      background: var(--bg-card); border: 1px solid var(--border-color);
      color: var(--text-main);
    }
    .btn-secondary:hover { background: var(--bg-card-hover); }
    .container { max-width: 1400px; margin: 0 auto; padding: 32px; }
    .stats-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px; margin-bottom: 32px;
    }
    .stat-card {
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 12px; padding: 20px; display: flex;
      flex-direction: column; gap: 8px; position: relative; overflow: hidden;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }
    .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
    .stat-total::before { background: var(--primary); }
    .stat-accepted::before { background: var(--status-accepted-text); }
    .stat-review::before { background: var(--status-review-text); }
    .stat-eval::before { background: var(--status-eval-text); }
    .stat-revision::before { background: var(--status-revision-text); }
    .stat-title { font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .stat-value { font-size: 32px; font-weight: 700; line-height: 1; }
    .controls-bar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
    .search-box { position: relative; flex: 1; max-width: 400px; }
    .search-box input {
      width: 100%; background: var(--bg-card); border: 1px solid var(--border-color);
      color: var(--text-main); padding: 10px 16px 10px 38px; border-radius: 8px;
      font-size: 14px; outline: none; transition: border-color 0.2s;
    }
    .search-box input:focus { border-color: var(--primary); }
    .search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 14px; pointer-events: none; }
    .filter-pills { display: flex; gap: 8px; flex-wrap: wrap; }
    .pill {
      background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-muted);
      padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer;
      transition: all 0.2s;
    }
    .pill:hover { background: var(--bg-card-hover); color: var(--text-main); }
    .pill.active { background: rgba(59, 130, 246, 0.15); border-color: var(--primary); color: var(--primary); font-weight: 600; }
    .table-container {
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th {
      background: rgba(15, 23, 42, 0.6); padding: 14px 20px; font-size: 12px;
      font-weight: 600; color: var(--text-muted); text-transform: uppercase;
      letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color);
    }
    td { padding: 16px 20px; border-bottom: 1px solid rgba(35, 46, 74, 0.5); font-size: 14px; vertical-align: middle; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background-color: var(--bg-card-hover); }
    .task-folder { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; color: #E2E8F0; }
    .task-id { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted); }
    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    .badge-dot { width: 6px; height: 6px; border-radius: 50%; }
    .badge-accepted { background: var(--status-accepted-bg); color: var(--status-accepted-text); border: 1px solid var(--status-accepted-border); }
    .badge-accepted .badge-dot { background: var(--status-accepted-text); }
    .badge-review { background: var(--status-review-bg); color: var(--status-review-text); border: 1px solid var(--status-review-border); }
    .badge-review .badge-dot { background: var(--status-review-text); }
    .badge-eval { background: var(--status-eval-bg); color: var(--status-eval-text); border: 1px solid var(--status-eval-border); }
    .badge-eval .badge-dot { background: var(--status-eval-text); }
    .badge-revision { background: var(--status-revision-bg); color: var(--status-revision-text); border: 1px solid var(--status-revision-border); }
    .badge-revision .badge-dot { background: var(--status-revision-text); }
    .btn-action {
      background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color);
      color: var(--text-main); padding: 6px 12px; border-radius: 6px; font-size: 12px;
      font-weight: 500; cursor: pointer; transition: all 0.2s;
    }
    .btn-action:hover { background: var(--primary); border-color: var(--primary); color: #fff; }
    .modal-overlay {
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(4px);
      display: none; align-items: center; justify-content: center; z-index: 1000; padding: 20px;
    }
    .modal-overlay.active { display: flex; }
    .modal-card {
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 16px; width: 100%; max-width: 850px; max-height: 85vh;
      display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }
    .modal-header {
      padding: 20px 24px; border-bottom: 1px solid var(--border-color);
      display: flex; justify-content: space-between; align-items: center;
    }
    .modal-title { font-size: 16px; font-weight: 600; }
    .btn-close {
      background: transparent; border: none; color: var(--text-muted);
      font-size: 20px; cursor: pointer; line-height: 1; padding: 4px; border-radius: 4px;
    }
    .btn-close:hover { color: var(--text-main); background: var(--bg-card-hover); }
    .modal-body {
      padding: 24px; overflow-y: auto; font-family: 'JetBrains Mono', monospace;
      font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-word;
      color: #E2E8F0; background: #090D16;
    }
    .loading-spinner {
      display: inline-block; width: 16px; height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 50%;
      border-top-color: #fff; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .empty-state { text-align: center; padding: 48px; color: var(--text-muted); }
  </style>
</head>
<body>
  <header>
    <div class="logo-container">
      <div class="logo-badge">⚡</div>
      <div class="logo-text">
        <h1>Task Monitor</h1>
        <p>Benchmark Submission Hub & Feedback</p>
      </div>
    </div>
    <div class="header-actions">
      <select id="projectSelect" class="select-project" onchange="changeProject(this.value)">
        <option value="cb869485-67bf-4aba-85aa-fc63a7d82e19">CDG_Starfish_Pilot_uTYAV_Coding</option>
      </select>
      <button class="btn btn-secondary" onclick="loadData(true)">
        <span id="refreshIcon">↻</span> Refresh
      </button>
    </div>
  </header>

  <div class="container">
    <div class="stats-grid">
      <div class="stat-card stat-total">
        <span class="stat-title">Total Tasks</span>
        <span class="stat-value" id="statTotal">--</span>
      </div>
      <div class="stat-card stat-accepted">
        <span class="stat-title">Accepted</span>
        <span class="stat-value" id="statAccepted" style="color: var(--status-accepted-text);">--</span>
      </div>
      <div class="stat-card stat-review">
        <span class="stat-title">Review Pending</span>
        <span class="stat-value" id="statReview" style="color: var(--status-review-text);">--</span>
      </div>
      <div class="stat-card stat-eval">
        <span class="stat-title">Evaluation Pending</span>
        <span class="stat-value" id="statEval" style="color: var(--status-eval-text);">--</span>
      </div>
      <div class="stat-card stat-revision">
        <span class="stat-title">Needs Revision</span>
        <span class="stat-value" id="statRevision" style="color: var(--status-revision-text);">--</span>
      </div>
    </div>

    <div class="controls-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search by folder or ID..." oninput="filterData()">
      </div>
      <div class="filter-pills">
        <div class="pill active" onclick="setStatusFilter('ALL', this)">All</div>
        <div class="pill" onclick="setStatusFilter('ACCEPTED', this)">Accepted</div>
        <div class="pill" onclick="setStatusFilter('REVIEW_PENDING', this)">Review Pending</div>
        <div class="pill" onclick="setStatusFilter('EVALUATION_PENDING', this)">Evaluation Pending</div>
        <div class="pill" onclick="setStatusFilter('NEEDS_REVISION', this)">Needs Revision</div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 50px;">#</th>
            <th>Task / Folder</th>
            <th>Submission ID</th>
            <th>Created Date</th>
            <th>Status</th>
            <th style="text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody id="submissionsTableBody">
          <tr>
            <td colspan="6" class="empty-state">
              <div class="loading-spinner"></div>
              <div style="margin-top: 10px;">Fetching task submissions...</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="modal-overlay" id="feedbackModal" onclick="closeModalOnBackdrop(event)">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title" id="modalTitle">Submission Feedback</div>
        <button class="btn-close" onclick="closeModal()">✕</button>
      </div>
      <pre class="modal-body" id="modalContent">Fetching feedback...</pre>
    </div>
  </div>

  <script>
    let allSubmissions = [];
    let currentFilter = 'ALL';
    let currentProjectId = 'cb869485-67bf-4aba-85aa-fc63a7d82e19';

    async function fetchProjects() {
      try {
        const res = await fetch('/api/projects');
        const projects = await res.json();
        const select = document.getElementById('projectSelect');
        select.innerHTML = '';
        projects.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = p.name;
          if (p.name.includes('Starfish') || p.id === currentProjectId) opt.selected = true;
          select.appendChild(opt);
        });
        currentProjectId = select.value;
      } catch (err) {
        console.error('Error fetching projects:', err);
      }
    }

    async function loadData(manual = false) {
      const refreshBtn = document.getElementById('refreshIcon');
      if (manual) refreshBtn.style.animation = 'spin 0.6s linear';
      try {
        const res = await fetch('/api/submissions?project=' + encodeURIComponent(currentProjectId));
        allSubmissions = await res.json();
        updateStats();
        renderTable();
      } catch (err) {
        console.error('Error loading submissions:', err);
        document.getElementById('submissionsTableBody').innerHTML = '<tr><td colspan="6" class="empty-state" style="color: #F87171;">Failed to load data.</td></tr>';
      } finally {
        setTimeout(() => refreshBtn.style.animation = '', 600);
      }
    }

    function updateStats() {
      const total = allSubmissions.length;
      const accepted = allSubmissions.filter(s => s.state && (s.state.toUpperCase().includes('ACCEPTED') || s.state.toUpperCase().includes('COMPLETED'))).length;
      const review = allSubmissions.filter(s => s.state && (s.state.toUpperCase().includes('REVIEW_PENDING') || s.state.toUpperCase().includes('OFFERED'))).length;
      const evaluation = allSubmissions.filter(s => s.state && s.state.toUpperCase().includes('EVALUATION_PENDING')).length;
      const revision = allSubmissions.filter(s => s.state && s.state.toUpperCase().includes('NEEDS_REVISION')).length;

      document.getElementById('statTotal').textContent = total;
      document.getElementById('statAccepted').textContent = accepted;
      document.getElementById('statReview').textContent = review;
      document.getElementById('statEval').textContent = evaluation;
      document.getElementById('statRevision').textContent = revision;
    }

    function getBadgeClass(state) {
      if (!state) return 'badge-review';
      const s = state.toUpperCase();
      if (s.includes('ACCEPTED') || s.includes('COMPLETED')) return 'badge-accepted';
      if (s.includes('REVIEW_PENDING') || s.includes('OFFERED')) return 'badge-review';
      if (s.includes('EVALUATION_PENDING')) return 'badge-eval';
      if (s.includes('NEEDS_REVISION')) return 'badge-revision';
      return 'badge-review';
    }

    function formatState(state) {
      return (state || '').replace(/_/g, ' ');
    }

    function renderTable() {
      const tbody = document.getElementById('submissionsTableBody');
      const search = (document.getElementById('searchInput').value || '').toLowerCase().trim();

      const filtered = allSubmissions.filter(s => {
        const matchesFilter = currentFilter === 'ALL' || (s.state && s.state.toUpperCase().includes(currentFilter));
        const folderStr = (s.folder || '').toLowerCase();
        const idStr = (s.id || '').toLowerCase();
        const numStr = (s.num || '').toString();
        const matchesSearch = !search || folderStr.includes(search) || idStr.includes(search) || numStr.includes(search);
        return matchesFilter && matchesSearch;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No matching task submissions found.</td></tr>';
        return;
      }

      let htmlRows = '';
      for (const s of filtered) {
        htmlRows += '<tr>' +
          '<td style="color: var(--text-muted); font-weight: 500;">' + s.num + '</td>' +
          '<td><div class="task-folder">📁 ' + escapeHtml(s.folder) + '</div></td>' +
          '<td><span class="task-id">' + s.id + '</span></td>' +
          '<td style="color: var(--text-muted); font-size: 13px;">' + s.created + '</td>' +
          '<td><span class="badge ' + getBadgeClass(s.state) + '"><span class="badge-dot"></span>' + formatState(s.state) + '</span></td>' +
          '<td style="text-align: right;"><button class="btn-action" onclick="viewFeedback(\'' + s.id + '\', \'' + escapeHtml(s.folder) + '\')">View Feedback</button></td>' +
          '</tr>';
      }
      tbody.innerHTML = htmlRows;
    }

    function setStatusFilter(filter, el) {
      currentFilter = filter;
      document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
      el.classList.add('active');
      renderTable();
    }

    function filterData() {
      renderTable();
    }

    function changeProject(id) {
      currentProjectId = id;
      loadData();
    }

    async function viewFeedback(id, folder) {
      const modal = document.getElementById('feedbackModal');
      const title = document.getElementById('modalTitle');
      const content = document.getElementById('modalContent');

      title.textContent = 'Feedback: ' + folder + ' (' + id.slice(0, 8) + '...)';
      content.textContent = 'Loading feedback via stb submissions feedback...';
      modal.classList.add('active');

      try {
        const res = await fetch('/api/feedback?id=' + encodeURIComponent(id));
        const data = await res.json();
        content.textContent = data.feedback || 'No feedback or evaluation output recorded yet.';
      } catch (err) {
        content.textContent = 'Failed to load feedback: ' + err.message;
      }
    }

    function closeModal() {
      document.getElementById('feedbackModal').classList.remove('active');
    }

    function closeModalOnBackdrop(e) {
      if (e.target.id === 'feedbackModal') closeModal();
    }

    function escapeHtml(text) {
      return (text || '').replace(/[&<>"']/g, function(m) {
        return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'}[m];
      });
    }

    (async () => {
      await fetchProjects();
      await loadData();
      setInterval(() => loadData(false), 30000);
    })();
  </script>
</body>
</html>
'''

server_py_content = r'''import http.server
import socketserver
import json
import subprocess
import os
import time
from urllib.parse import urlparse, parse_qs

PORT = 8088
STB_BIN = "/home/pratik/.local/bin/stb"

# Folder names lookup for known tasks in Starfish
KNOWN_FOLDERS = {
    "a950ea00-7f0e-406a-9adb-9ad3f809edc2": "oscillator-coulomb-viscous-damping",
    "a4ea349a-0163-4b58-bd26-c12a505c9c51": "xrd-williamson-hall-strain-size-v2",
    "db9464ea-a3a2-499a-97cb-16b23a5c9e75": "bolt-loosening-vs-thermal-stiffness_v2",
    "544734c6-cdce-44ac-b253-5a72f9fd9430": "battery-hppc-dcir-partitioning",
    "dfa255ca-9aae-4d5c-8ebd-e798f38c1540": "power-grid-capacitor-switching-vs-fault",
    "ebf12aa5-4931-40d0-a461-ba5c41ce8d34": "sparse-identification-nonautonomous-dynamics",
    "d0eac590-aa50-428e-9a86-548df27fd0e8": "thz_tds_drude_smith_inversion",
    "fc628f92-d6c8-414f-8542-5d72af8d89fe": "bearing-fault-variable-speed",
    "e67890ec-6744-4388-bd5d-8b020eee1ebc": "shm-thermal-damage-decoupling",
    "c286186f-c5d5-440b-95de-9b2984b0add4": "drt-impedance-diagnostics",
    "4ba7ce7e-5da8-46eb-b500-60adb919d8f1": "eis-circuit-discrimination",
    "72c7b048-b2c7-4709-b0c2-0a307cb7314e": "spectroscopy-conflict",
    "b5f298d4-42bd-4000-9b65-41dd9d39ab15": "pk-compartmental-modeling",
    "33d9a82a-42e4-42b6-b163-a22a49351e32": "corrosion-rate-eis-polarization",
    "0f56a4e8-85a7-47c3-9e94-edee3dc713af": "battery-dqdv-soh",
    "0b91a985-42a6-4b00-a6e3-2b1e0d6f03d5": "seismic-event-discrimination",
    "ae8f4448-bff5-4c61-b955-058f9866eb91": "telemetry-falsification",
    "d2673bdf-fff4-45d3-9a65-8eeb9b416625": "pmu-fault-localization"
}

# Cache submissions for 15s to keep UI snappy
CACHE = {
    "submissions": {},
    "timestamp": {}
}

def get_projects():
    try:
        res = subprocess.run([STB_BIN, "projects", "list"], capture_output=True, text=True, timeout=20)
        lines = res.stdout.strip().split('\n')
        projects = []
        for line in lines:
            if '│' in line and not 'ID' in line and not 'Name' in line:
                parts = [p.strip() for p in line.split('│')[1:-1]]
                if len(parts) >= 2 and parts[0] and parts[1]:
                    projects.append({
                        "name": parts[0],
                        "id": parts[1]
                    })
        if not projects:
            projects = [{"name": "CDG_Starfish_Pilot_uTYAV_Coding", "id": "cb869485-67bf-4aba-85aa-fc63a7d82e19"}]
        return projects
    except Exception as e:
        return [{"name": "CDG_Starfish_Pilot_uTYAV_Coding", "id": "cb869485-67bf-4aba-85aa-fc63a7d82e19"}]

def get_submissions(project_id):
    now = time.time()
    if project_id in CACHE["submissions"] and (now - CACHE["timestamp"].get(project_id, 0)) < 15:
        return CACHE["submissions"][project_id]

    try:
        res = subprocess.run([STB_BIN, "submissions", "list", "-p", project_id], capture_output=True, text=True, timeout=60)
        lines = res.stdout.strip().split('\n')
        subs = []
        for line in lines:
            if '│' in line and not 'Submission ID' in line:
                parts = [p.strip() for p in line.split('│')[1:-1]]
                if len(parts) >= 6 and parts[0].isdigit():
                    sub_id = parts[1]
                    raw_folder = parts[3]
                    resolved_folder = KNOWN_FOLDERS.get(sub_id, raw_folder if raw_folder else "task-folder")
                    subs.append({
                        "num": parts[0],
                        "id": sub_id,
                        "created": parts[2],
                        "folder": resolved_folder,
                        "state": parts[4],
                        "payment": parts[5]
                    })
        if subs:
            CACHE["submissions"][project_id] = subs
            CACHE["timestamp"][project_id] = now
            return subs
        elif project_id in CACHE["submissions"]:
            return CACHE["submissions"][project_id]
        return []
    except Exception as e:
        print(f"Error in get_submissions: {e}")
        return CACHE["submissions"].get(project_id, [])

def get_feedback(sub_id):
    try:
        res = subprocess.run([STB_BIN, "submissions", "feedback", sub_id], capture_output=True, text=True, timeout=30)
        return res.stdout if res.stdout else res.stderr
    except Exception as e:
        return f"Error fetching feedback: {str(e)}"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("/home/pratik/Desktop/Internship/task_dashboard/index.html", "rb") as f:
                self.wfile.write(f.read())
            return
            
        elif parsed.path == "/api/projects":
            projects = get_projects()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(projects).encode("utf-8"))
            return
            
        elif parsed.path == "/api/submissions":
            qs = parse_qs(parsed.query)
            proj_id = qs.get("project", ["cb869485-67bf-4aba-85aa-fc63a7d82e19"])[0]
            subs = get_submissions(proj_id)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(subs).encode("utf-8"))
            return
            
        elif parsed.path == "/api/feedback":
            qs = parse_qs(parsed.query)
            sub_id = qs.get("id", [""])[0]
            if not sub_id:
                fb = "No submission ID provided."
            else:
                fb = get_feedback(sub_id)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"feedback": fb}).encode("utf-8"))
            return
            
        else:
            self.send_error(404, "File Not Found")

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Dashboard Server started at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
'''

with open('/home/pratik/Desktop/Internship/task_dashboard/index.html', 'w') as f:
    f.write(index_html_content)

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'w') as f:
    f.write(server_py_content)

print("ALL_FILES_GENERATED_SUCCESSFULLY")
