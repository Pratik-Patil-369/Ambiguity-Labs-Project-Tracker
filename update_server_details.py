import re

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'r') as f:
    code = f.read()

new_get_feedback = r'''def get_feedback(sub_id):
    try:
        py_cmd = (
            "from snorkelai_stb.submission_utils import get_assignment_id_for_submission\n"
            "from snorkelai_stb.utils import get_daas_resource\n"
            "import json\n"
            f"assignment_id, proj_id = get_assignment_id_for_submission('{sub_id}', None)\n"
            "task = get_daas_resource(f'/assignment/{assignment_id}', 'GET')\n"
            "sections = []\n"
            "accept_notes = (task.get('accept_notes') or '').strip()\n"
            "if accept_notes:\n"
            "    sections.append('🎉 REVIEWER ACCEPT NOTES:\\n' + accept_notes)\n"
            "revision_notes = (task.get('revision_notes') or '').strip()\n"
            "if revision_notes:\n"
            "    sections.append('📝 REVISION NOTES:\\n' + revision_notes)\n"
            "rebuttal_notes = (task.get('rebuttal_notes') or '').strip()\n"
            "if rebuttal_notes:\n"
            "    sections.append('💬 REBUTTAL NOTES:\\n' + rebuttal_notes)\n"
            "user_reviews = task.get('user_reviews') or []\n"
            "for r in user_reviews:\n"
            "    payload = r.get('review_payload') or dict()\n"
            "    for k, v in payload.items():\n"
            "        if k.startswith('textarea-') and isinstance(v, str) and v.strip():\n"
            "            sections.append('📋 REVIEWER COMMENTS:\\n' + v.strip())\n"
            "task_docs = task.get('task_documents') or []\n"
            "for d in task_docs:\n"
            "    sub_doc = d.get('submission_document') or dict()\n"
            "    ts = (sub_doc.get('text_summary') or '').strip()\n"
            "    if ts:\n"
            "        sections.append('📊 EVALUATION SUMMARY:\\n' + ts)\n"
            "    qcs = (sub_doc.get('quality_check_summary') or '').strip()\n"
            "    if qcs:\n"
            "        sections.append('✅ QUALITY CHECK SUMMARY:\\n' + qcs)\n"
            "if not sections:\n"
            "    status = str(task.get('status') or task.get('assignment_state') or 'ACCEPTED')\n"
            "    sections.append('ℹ️ STATUS DETAILS:\\nThis task was accepted directly on the platform without additional reviewer notes.')\n"
            "output_text = ('\\n\\n' + '='*75 + '\\n\\n').join(sections)\n"
            "print(json.dumps(output_text))\n"
        )
        res = subprocess.run([PYTHON_STB, "-c", py_cmd], capture_output=True, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout.strip())
    except Exception as e:
        print(f"Error fetching direct task notes: {e}")

    try:
        res = subprocess.run([STB_BIN, "submissions", "feedback", sub_id], capture_output=True, text=True, timeout=25)
        return res.stdout if res.stdout else res.stderr
    except Exception as e:
        return f"Error fetching feedback: {str(e)}"
'''

pattern = r'def get_feedback\(sub_id\):.*?(?=class DashboardHandler)'
code = re.sub(pattern, new_get_feedback + "\n", code, flags=re.DOTALL)

with open('/home/pratik/Desktop/Internship/task_dashboard/server.py', 'w') as f:
    f.write(code)

print("SERVER_DETAILS_UPDATED")
