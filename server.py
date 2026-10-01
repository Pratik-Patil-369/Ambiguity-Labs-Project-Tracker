import http.server
import socketserver
import json
import subprocess
import os
import time
from urllib.parse import urlparse, parse_qs

PORT = 8088
PYTHON_STB = "/home/pratik/.local/share/uv/tools/snorkelai-stb/bin/python3"
STB_BIN = "/home/pratik/.local/bin/stb"

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
    "d2673bdf-fff4-45d3-9a65-8eeb9b416625": "pmu-fault-localization",
    "66b3dbb0-3026-4b54-a441-8a3b34764a76": "workflows-assessment-task-01",
    "f3ffa96f-4ddf-4696-97c8-b868cff8580a": "capacitor-bank-controlled-switching-design"
}

CACHE = {
    "projects": None,
    "projects_time": 0,
    "submissions": {},
    "submissions_time": {}
}

def get_all_assigned_projects():
    now = time.time()
    if CACHE["projects"] and (now - CACHE["projects_time"]) < 60:
        return CACHE["projects"]

    try:
        script = "from snorkelai_stb.utils import get_assigned_projects; import json; print(json.dumps(get_assigned_projects()))"
        res = subprocess.run([PYTHON_STB, "-c", script], capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and res.stdout.strip():
            raw_projects = json.loads(res.stdout.strip())
            projects = []
            for p in raw_projects:
                projects.append({
                    "name": p.get("name"),
                    "id": p.get("project_id"),
                    "submitter": p.get("submitter", False),
                    "reviewer": p.get("reviewer", False)
                })
            if projects:
                CACHE["projects"] = projects
                CACHE["projects_time"] = now
                return projects
    except Exception as e:
        print(f"Error in get_all_assigned_projects: {e}")

    default_projects = [
        {"name": "CDG_Starfish_Pilot_uTYAV_Coding_V3", "id": "bf595aee-ae7d-471d-9047-5662498079bd", "submitter": True, "reviewer": False},
        {"name": "CDG_Starfish_Pilot_uTYAV_Coding", "id": "cb869485-67bf-4aba-85aa-fc63a7d82e19", "submitter": True, "reviewer": False},
        {"name": "[Asimov - General] Workflows Assessment", "id": "9d4d5c89-5f04-479a-a83d-242d702079ca", "submitter": True, "reviewer": False}
    ]
    return default_projects

def get_submissions(project_id):
    now = time.time()
    if project_id in CACHE["submissions"] and (now - CACHE["submissions_time"].get(project_id, 0)) < 15:
        return CACHE["submissions"][project_id]

    try:
        script = f"""
from snorkelai_stb import assignment_utils
from snorkelai_stb.utils import TaskCategory
import json
items = assignment_utils.list_assignments(None, TaskCategory.SUBMISSION)
filtered = [i for i in items if not '{project_id}' or i.get('project_id') == '{project_id}']
print(json.dumps(filtered))
"""
        res = subprocess.run([PYTHON_STB, "-c", script], capture_output=True, text=True, timeout=15)
        if res.returncode == 0 and res.stdout.strip():
            raw_list = json.loads(res.stdout.strip())
            subs = []
            for idx, item in enumerate(raw_list, 1):
                sub_id = item.get("submission_id", "")
                raw_folder = item.get("folder_name", "")
                resolved_folder = KNOWN_FOLDERS.get(sub_id, raw_folder if raw_folder else f"task-{sub_id[:8]}")
                subs.append({
                    "num": str(idx),
                    "id": sub_id,
                    "created": item.get("created_at", ""),
                    "folder": resolved_folder,
                    "state": item.get("assignment_state", ""),
                    "payment": item.get("payment_status", "")
                })
            CACHE["submissions"][project_id] = subs
            CACHE["submissions_time"][project_id] = now
            return subs
    except Exception as e:
        print(f"Error calling list_assignments for {project_id}: {e}")

    return CACHE["submissions"].get(project_id, [])

def get_feedback(sub_id):
    try:
        helper_code = r'''
from snorkelai_stb.submission_utils import get_assignment_id_for_submission
from snorkelai_stb.utils import get_daas_resource
import json, sys

sub_id = sys.argv[1]
assignment_id, proj_id = get_assignment_id_for_submission(sub_id, None)
task = get_daas_resource(f"/assignment/{assignment_id}", "GET")
sections = []

accept_notes = (task.get("accept_notes") or "").strip()
if accept_notes:
    sections.append("🎉 REVIEWER ACCEPT NOTES:\n" + accept_notes)

revision_notes = (task.get("revision_notes") or "").strip()
if revision_notes:
    sections.append("📝 REVISION NOTES:\n" + revision_notes)

rebuttal_notes = (task.get("rebuttal_notes") or "").strip()
if rebuttal_notes:
    sections.append("💬 REBUTTAL NOTES:\n" + rebuttal_notes)

user_reviews = task.get("user_reviews") or []
for r in user_reviews:
    payload = r.get("review_payload") or {}
    for k, v in payload.items():
        if k.startswith("textarea-") and isinstance(v, str) and v.strip():
            sections.append("📋 REVIEWER COMMENTS:\n" + v.strip())

task_docs = task.get("task_documents") or []
for d in task_docs:
    sub_doc = d.get("submission_document") or {}
    ts = (sub_doc.get("text_summary") or "").strip()
    if ts:
        sections.append("📊 EVALUATION SUMMARY:\n" + ts)
    qcs = (sub_doc.get("quality_check_summary") or "").strip()
    if qcs:
        sections.append("✅ QUALITY CHECK SUMMARY:\n" + qcs)

sd = task.get("static_document") or {}
if isinstance(sd, dict):
    sd_inner = sd.get("static_document") or {}
    fb = (sd_inner.get("Feedback") or sd.get("Feedback") or "").strip()
    if fb:
        sections.append("📋 PRIOR QC / AUDIT REVIEWER FEEDBACK:\n" + fb)

eval_notes = (task.get("eval_revision_notes") or "").strip()
if eval_notes:
    sections.append("⚡ AUTOEVAL NOTES:\n" + eval_notes)

if not sections:
    sections.append("ℹ️ TASK DETAILS:\nNo additional reviewer notes recorded for this submission yet.")

output_text = ("\n\n" + "="*75 + "\n\n").join(sections)
print(json.dumps(output_text))
'''
        res = subprocess.run([PYTHON_STB, "-c", helper_code, sub_id], capture_output=True, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout.strip())
    except Exception as e:
        print(f"Error fetching direct task notes: {e}")

    try:
        res = subprocess.run([STB_BIN, "submissions", "feedback", sub_id], capture_output=True, text=True, timeout=25)
        return res.stdout if res.stdout else res.stderr
    except Exception as e:
        return f"Error fetching feedback: {str(e)}"

from api.index import handler as ApiHandler

class DashboardHandler(ApiHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("/home/pratik/Desktop/Internship/task_dashboard/index.html", "rb") as f:
                self.wfile.write(f.read())
            return
        # Delegate all other paths to the Vercel-compatible API handler
        super().do_GET()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"High-Speed Dashboard Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
