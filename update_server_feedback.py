import re

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'r') as f:
    code = f.read()

# Replace get_feedback in server.py to extract accept_notes, revision_notes, quality check, and full feedback
new_get_feedback = r'''def get_feedback(sub_id):
    try:
        # Query assignment data directly via snorkelai_stb API
        script = f"""
from snorkelai_stb.submission_utils import get_assignment_id_for_submission
from snorkelai_stb.utils import get_daas_resource
import json

assignment_id, proj_id = get_assignment_id_for_submission('{sub_id}', None)
task = get_daas_resource(f'/assignment/{assignment_id}', 'GET')

sections = []
accept_notes = (task.get('accept_notes') or '').strip()
if accept_notes:
    sections.append(f"🎉 REVIEWER ACCEPT NOTES:\n{accept_notes}")

revision_notes = (task.get('revision_notes') or '').strip()
if revision_notes:
    sections.append(f"📝 REVISION NOTES:\n{revision_notes}")

rebuttal_notes = (task.get('rebuttal_notes') or '').strip()
if rebuttal_notes:
    sections.append(f"💬 REBUTTAL NOTES:\n{rebuttal_notes}")

user_reviews = task.get('user_reviews') or []
for r in user_reviews:
    payload = r.get('review_payload') or {}
    for k, v in payload.items():
        if k.startswith('textarea-') and isinstance(v, str) and v.strip():
            sections.append(f"📋 REVIEWER COMMENTS:\n{v.strip()}")

task_docs = task.get('task_documents') or []
for d in task_docs:
    sub_doc = d.get('submission_document') or {}
    ts = (sub_doc.get('text_summary') or '').strip()
    if ts:
        sections.append(f"📊 EVALUATION SUMMARY:\n{ts}")
    qcs = (sub_doc.get('quality_check_summary') or '').strip()
    if qcs:
        sections.append(f"✅ QUALITY CHECK SUMMARY:\n{qcs}")

if sections:
    print(json.dumps("\\n\\n" + ("="*75) + "\\n\\n".join([""] + sections)))
else:
    print(json.dumps("No notes or reviewer comments recorded for this task."))
"""
        res = subprocess.run([PYTHON_STB, "-c", script], capture_output=True, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout.strip())
    except Exception as e:
        print(f"Error fetching direct task notes: {e}")

    # Fallback to CLI
    try:
        res = subprocess.run([STB_BIN, "submissions", "feedback", sub_id], capture_output=True, text=True, timeout=25)
        return res.stdout if res.stdout else res.stderr
    except Exception as e:
        return f"Error fetching feedback: {str(e)}"
'''

# Find def get_feedback(sub_id): and replace it
pattern = r'def get_feedback\(sub_id\):.*?(?=class DashboardHandler)'
code = re.sub(pattern, new_get_feedback + "\n", code, flags=re.DOTALL)

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'w') as f:
    f.write(code)

print("SERVER_FEEDBACK_UPDATED_SUCCESSFULLY")
