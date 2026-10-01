import os

server_py_content = r'''import http.server
import socketserver
import json
import subprocess
import os
import time
from urllib.parse import urlparse, parse_qs

PORT = 8088
STB_BIN = "/home/pratik/.local/bin/stb"
PYTHON_STB = "/home/pratik/.local/share/uv/tools/snorkelai-stb/bin/python3"

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
    "66b3dbb0-3026-4b54-a441-8a3b34764a76": "workflows-assessment-task-01"
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
        # Use Python client inside uv virtualenv to query assigned projects directly
        cmd = [
            PYTHON_STB, "-c",
            "from snorkelai_stb.utils import get_assigned_projects; import json; print(json.dumps(get_assigned_projects()))"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
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
        print(f"Error fetching assigned projects: {e}")

    # Fallback default projects
    default_projects = [
        {"name": "CDG_Starfish_Pilot_uTYAV_Coding", "id": "cb869485-67bf-4aba-85aa-fc63a7d82e19", "submitter": True, "reviewer": False},
        {"name": "[Asimov - General] Workflows Assessment", "id": "9d4d5c89-5f04-479a-a83d-242d702079ca", "submitter": True, "reviewer": False}
    ]
    return default_projects

def get_submissions(project_id):
    now = time.time()
    if project_id in CACHE["submissions"] and (now - CACHE["submissions_time"].get(project_id, 0)) < 20:
        return CACHE["submissions"][project_id]

    try:
        res = subprocess.run([STB_BIN, "submissions", "list", "-p", project_id], capture_output=True, text=True, timeout=45)
        lines = res.stdout.strip().split('\n')
        subs = []
        for line in lines:
            if '│' in line and not 'Submission ID' in line:
                parts = [p.strip() for p in line.split('│')[1:-1]]
                if len(parts) >= 5 and parts[0].isdigit():
                    sub_id = parts[1]
                    created_at = parts[2]
                    
                    if len(parts) >= 6:
                        # 6 column table (with Folder Name)
                        raw_folder = parts[3]
                        state = parts[4]
                        payment = parts[5]
                    else:
                        # 5 column table (without Folder Name, e.g. Asimov)
                        raw_folder = ""
                        state = parts[3]
                        payment = parts[4]

                    resolved_folder = KNOWN_FOLDERS.get(sub_id, raw_folder if raw_folder else f"task-{sub_id[:8]}")
                    subs.append({
                        "num": parts[0],
                        "id": sub_id,
                        "created": created_at,
                        "folder": resolved_folder,
                        "state": state,
                        "payment": payment
                    })
        if subs:
            CACHE["submissions"][project_id] = subs
            CACHE["submissions_time"][project_id] = now
            return subs
        elif project_id in CACHE["submissions"]:
            return CACHE["submissions"][project_id]
        return []
    except Exception as e:
        print(f"Error in get_submissions for {project_id}: {e}")
        return CACHE["submissions"].get(project_id, [])

def get_feedback(sub_id):
    try:
        res = subprocess.run([STB_BIN, "submissions", "feedback", sub_id], capture_output=True, text=True, timeout=30)
        output = res.stdout if res.stdout else res.stderr
        
        # Check if output points to a directory
        for line in output.split('\n'):
            if "Feedback written to" in line:
                path = line.split("Feedback written to")[-1].strip()
                if os.path.exists(path):
                    if os.path.isdir(path):
                        # read notes.txt or files inside
                        notes_path = os.path.join(path, "notes.txt")
                        if os.path.exists(notes_path):
                            with open(notes_path, "r", encoding="utf-8", errors="ignore") as f:
                                return f.read().strip() or output
                    elif os.path.isfile(path):
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            return f.read().strip() or output
        return output
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
            projects = get_all_assigned_projects()
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
        print(f"Dashboard Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
'''

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'w') as f:
    f.write(server_py_content)

print("SERVER_PY_UPDATED_SUCCESSFULLY")
