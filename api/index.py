from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
from urllib.parse import urlparse, parse_qs, quote

BASE_API_URL = "https://experts.snorkel-ai.com/api/v1"

KNOWN_FOLDERS = {
    "a950ea00-7f0e-406a-9adb-9ad3f809edc2": "oscillator-coulomb-viscous-damping",
    "a4ea349a-0163-4b58-bd26-c12a505c9c51": "xrd-williamson-hall-strain-size-v2",
    "db9464ea-a3a2-499a-97cb-16b23a5c9e75": "bolt-loosening-vs-thermal-stiffness_v2",
    "544734c6-cdce-44ac-b253-5a72f9fd9430": "battery-hppc-dcir-partitioning",
    "dfa255ca-9aae-4d5c-8ebd-e798f38c1540": "power-grid-capacitor-switching-vs-fault",
    "ebf12aa5-4931-40d0-a461-ba5c41ce8d34": "sparse-identification-nonautonomous-dynamics",
    "d0eac590-aa50-428e-9a86-548df27fd0e8": "thz_tds_drude_smith_inversion",
    "fc628f92-d6c8-414f-8542-5d72af8d89fe": "bearing-fault-variable-speed",
    "e67890ec-6744-4388-bd5d-8b020eee1ebc": "bearing-fault-variable-speed-v2",
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
    "f3ffa96f-4ddf-4696-97c8-b868cff8580a": "capacitor-bank-controlled-switching-design",
    "cab522f2-6caf-402e-97cb-7fcfb70f02a8": "dsc-mri-perfusion-aif-deconv",
    "75f996f3-17aa-4673-b569-d21a9ef3f104": "fluid-structure-interaction-parameter-inference",
    "7879db76-3895-426e-a2b9-f4dcd88f8bed": "modal-damage-detection",
    "dbcc63c7-4f56-4104-a9c7-97957bf8555a": "fmcw-radar-target-extraction-deghosting",
    "0a3fc595-74fe-4062-8dec-5ccdbf925a8d": "sgs-closure-backscatter-calibration",
    "39f009c3-cdaf-42bb-b472-b1d69fba3f32": "polymer-dma-master-curve",
    "d6920367-5487-4c69-896b-aa21315520e8": "nomoto-rudder-autopilot-zigzag-certification",
    "320c0500-3991-49ca-8066-fee57ce2e218": "mav-balance-calibration",
    "7ce93bd5-561e-48f5-8fd6-f3763f4fb391": "concrete-canal-lining-rapid-drawdown-uplift-retrofit",
    "96467fc6-78b1-4ee8-a5a8-8dfce60f86e0": "qoco-sensitivity-certification"
}

FALLBACK_PROJECTS = [
    {"name": "CDG_Starfish_Pilot_uTYAV_Coding_V3", "id": "bf595aee-ae7d-471d-9047-5662498079bd"},
    {"name": "CDG_Starfish_Pilot_uTYAV_Coding", "id": "cb869485-67bf-4aba-85aa-fc63a7d82e19"},
    {"name": "[Asimov - General] Workflows Assessment", "id": "9d4d5c89-5f04-479a-a83d-242d702079ca"}
]

FALLBACK_V3_SUBS = [
    {
        "num": "1",
        "id": "f3ffa96f-4ddf-4696-97c8-b868cff8580a",
        "created": "10/01 03:34",
        "folder": "capacitor-bank-controlled-switching-design",
        "state": "OFFERED",
        "payment": "PENDING"
    }
]

FALLBACK_V1_SUBS = [
    {"num": "1", "id": "a950ea00-7f0e-406a-9adb-9ad3f809edc2", "created": "08/26 19:55", "folder": "oscillator-coulomb-viscous-damping", "state": "ACCEPTED", "payment": "PAYOUT_SUBMITTED"},
    {"num": "2", "id": "a4ea349a-0163-4b58-bd26-c12a505c9c51", "created": "08/26 21:00", "folder": "xrd-williamson-hall-strain-size-v2", "state": "ACCEPTED", "payment": "PAYOUT_SUBMITTED"},
    {"num": "3", "id": "db9464ea-a3a2-499a-97cb-16b23a5c9e75", "created": "08/26 21:05", "folder": "bolt-loosening-vs-thermal-stiffness_v2", "state": "ACCEPTED", "payment": "PAYOUT_SUBMITTED"},
    {"num": "4", "id": "544734c6-cdce-44ac-b253-5a72f9fd9430", "created": "08/26 21:10", "folder": "battery-hppc-dcir-partitioning", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "5", "id": "dfa255ca-9aae-4d5c-8ebd-e798f38c1540", "created": "08/26 21:15", "folder": "power-grid-capacitor-switching-vs-fault", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "6", "id": "ebf12aa5-4931-40d0-a461-ba5c41ce8d34", "created": "08/26 21:20", "folder": "sparse-identification-nonautonomous-dynamics", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "7", "id": "d0eac590-aa50-428e-9a86-548df27fd0e8", "created": "08/26 21:25", "folder": "thz_tds_drude_smith_inversion", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "8", "id": "c286186f-c5d5-440b-95de-9b2984b0add4", "created": "08/26 21:30", "folder": "drt-impedance-diagnostics", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "9", "id": "b5f298d4-42bd-4000-9b65-41dd9d39ab15", "created": "08/26 21:35", "folder": "pk-compartmental-modeling", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "10", "id": "0f56a4e8-85a7-47c3-9e94-edee3dc713af", "created": "08/26 21:40", "folder": "battery-dqdv-soh", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "11", "id": "0b91a985-42a6-4b00-a6e3-2b1e0d6f03d5", "created": "08/26 21:45", "folder": "seismic-event-discrimination", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "12", "id": "ae8f4448-bff5-4c61-b955-058f9866eb91", "created": "08/26 21:50", "folder": "telemetry-falsification", "state": "ACCEPTED", "payment": "PENDING"},
    {"num": "13", "id": "d2673bdf-fff4-45d3-9a65-8eeb9b416625", "created": "08/26 21:55", "folder": "pmu-fault-localization", "state": "ACCEPTED", "payment": "PENDING"}
]

def resolve_api_key(req_handler):
    # 1. Check custom header from browser client
    client_key = req_handler.headers.get("X-Snorkel-Key")
    if client_key and client_key.strip():
        return client_key.strip()
    
    # 2. Check Authorization Bearer header
    auth_header = req_handler.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return token

    # 3. Check Vercel server environment variable
    env_key = os.environ.get("SNORKEL_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 4. Check local machine config file (when running locally)
    config_path = os.path.expanduser("~/.config/stb/config.ini")
    if os.path.exists(config_path):
        try:
            import configparser
            cp = configparser.ConfigParser()
            cp.read(config_path)
            if cp.has_section("auth") and "api_key" in cp["auth"]:
                return cp["auth"]["api_key"].strip()
        except Exception:
            pass

    return None

def fetch_projects_dynamic(api_key):
    """Dynamically fetches all assigned projects from Snorkel API for this user."""
    headers = {"x-key": api_key, "Accept": "application/json"}
    req = urllib.request.Request(f"{BASE_API_URL}/users/me", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        user_data = json.loads(resp.read().decode())
    
    attr = user_data.get("attribute_data") or {}
    assigned = attr.get("assigned_projects") or []
    
    projects = []
    seen = set()
    for p in assigned:
        pid = p.get("project_id")
        name = p.get("name")
        if pid and pid not in seen:
            seen.add(pid)
            projects.append({"name": name, "id": pid})
            
    # Always sort so Starfish projects appear at the top
    projects.sort(key=lambda x: (not ("Starfish" in x["name"]), x["name"]))
    return projects

ASSIGNMENT_REMAPPINGS = {
    "READY_TO_PACKAGE": "ACCEPTED",
    "READY_TO_DELIVER": "ACCEPTED",
    "DELIVERED": "ACCEPTED",
    "COMPLETED": "REVIEW_PENDING",
}

def fetch_assignments_dynamic(api_key, project_id):
    """Dynamically fetches assignments for the user, filtered by project."""
    headers = {"x-key": api_key, "Accept": "application/json"}
    
    # 1. Get user email
    req_me = urllib.request.Request(f"{BASE_API_URL}/users/me", headers=headers)
    with urllib.request.urlopen(req_me, timeout=10) as resp:
        user_data = json.loads(resp.read().decode())
        email = user_data.get("email")
    if not email:
        raise ValueError("User email not found")

    # 2. Get assignments
    url = f"{BASE_API_URL}/assignments?assignee={quote(email, safe='')}"
    req_assign = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req_assign, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        raw_list = data.get("assignments") or []

    filtered = [a for a in raw_list if not project_id or a.get("project_id") == project_id]
    
    subs = []
    for idx, a in enumerate(filtered, 1):
        task_id = a.get("task_id") or a.get("assignment_id") or ""
        folder = KNOWN_FOLDERS.get(task_id, a.get("task_title") or f"task-{task_id[:8]}")
        raw_created = a.get("created_at") or ""
        created = raw_created[5:16].replace("-", "/") if len(raw_created) >= 16 else raw_created
        raw_status = a.get("status", "")
        state = ASSIGNMENT_REMAPPINGS.get(raw_status, raw_status)
        subs.append({
            "num": str(idx),
            "id": task_id,
            "created": created,
            "folder": folder,
            "state": state,
            "payment": a.get("payment_status", "PENDING")
        })
    return subs

def resolve_assignment_id_dynamic(api_key, target_id):
    """Resolves task_id or submission_id to assignment_id for querying /assignment/{id}."""
    try:
        user_info = fetch_user_info(api_key)
        email = user_info.get("email")
        if email:
            headers = {"x-key": api_key, "Accept": "application/json"}
            url = f"{BASE_API_URL}/assignments?assignee={quote(email, safe='')}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for a in data.get("assignments") or []:
                    if a.get("task_id") == target_id or a.get("assignment_id") == target_id:
                        return a.get("assignment_id")
    except Exception as e:
        print(f"Error resolving assignment ID: {e}")
    return target_id

def fetch_feedback_dynamic(api_key, sub_id):
    """Fetches reviewer and audit notes for an assignment."""
    headers = {"x-key": api_key, "Accept": "application/json"}
    try:
        assignment_id = resolve_assignment_id_dynamic(api_key, sub_id)
        url = f"{BASE_API_URL}/assignment/{assignment_id}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            task = json.loads(resp.read().decode())
            sections = []
            accept_notes = (task.get("accept_notes") or "").strip()
            if accept_notes:
                sections.append("🎉 REVIEWER ACCEPT NOTES:\n" + accept_notes)
            revision_notes = (task.get("revision_notes") or "").strip()
            if revision_notes:
                sections.append("📝 REVISION NOTES:\n" + revision_notes)
            
            # Reviewer comments
            user_reviews = task.get("user_reviews") or []
            for r in user_reviews:
                payload = r.get("review_payload") or {}
                for k, v in payload.items():
                    if k.startswith("textarea-") and isinstance(v, str) and v.strip():
                        sections.append("📋 REVIEWER COMMENTS:\n" + v.strip())

            # Evaluation & QC summary
            task_docs = task.get("task_documents") or []
            for d in task_docs:
                sub_doc = d.get("submission_document") or {}
                ts = (sub_doc.get("text_summary") or "").strip()
                if ts:
                    sections.append("📊 EVALUATION SUMMARY:\n" + ts)
                qcs = (sub_doc.get("quality_check_summary") or "").strip()
                if qcs:
                    sections.append("✅ QUALITY CHECK SUMMARY:\n" + qcs)

            # Prior QC / Audit Feedback in static document
            sd = task.get("static_document") or {}
            if isinstance(sd, dict):
                sd_inner = sd.get("static_document") or sd
                fb = (sd_inner.get("Feedback") or "").strip()
                if fb:
                    sections.append("📋 PRIOR QC / AUDIT REVIEWER FEEDBACK:\n" + fb)

            eval_notes = (task.get("eval_revision_notes") or "").strip()
            if eval_notes:
                sections.append("⚡ AUTOEVAL NOTES:\n" + eval_notes)

            if sections:
                return ("\n\n" + "="*75 + "\n\n").join(sections)
    except Exception as e:
        print(f"Error fetching assignment dynamic feedback: {e}")
        
    return "ℹ️ TASK DETAILS:\nNo additional reviewer notes recorded for this submission yet."

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Snorkel-Key, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        api_key = resolve_api_key(self)

        if path.endswith("/projects"):
            projects = []
            if api_key:
                try:
                    projects = fetch_projects_dynamic(api_key)
                except Exception as e:
                    print(f"Dynamic project fetch failed: {e}")
                
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(projects).encode("utf-8"))

        elif path.endswith("/submissions"):
            qs = parse_qs(parsed.query)
            proj_id = qs.get("project", [""])[0]
            subs = []
            if api_key and proj_id:
                try:
                    subs = fetch_assignments_dynamic(api_key, proj_id)
                except Exception as e:
                    print(f"Dynamic assignments fetch failed: {e}")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(subs).encode("utf-8"))

        elif path.endswith("/feedback"):
            qs = parse_qs(parsed.query)
            sub_id = qs.get("id", [""])[0]
            if not api_key:
                fb = "🔒 Please connect your Snorkel API key to view submission feedback."
            else:
                fb = fetch_feedback_dynamic(api_key, sub_id) if sub_id else "No submission ID provided."
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"feedback": fb}).encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")
