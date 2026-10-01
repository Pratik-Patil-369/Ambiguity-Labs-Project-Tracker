import re

with open('/home/pratik/Desktop/Internship/task_dashboard/index.html', 'r') as f:
    content = f.read()

# Replace fetchProjects to set default cleanly and support all projects seamlessly
old_fetch = r'''    async function fetchProjects() {
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
    }'''

new_fetch = r'''    async function fetchProjects() {
      try {
        const res = await fetch('/api/projects');
        const projects = await res.json();
        const select = document.getElementById('projectSelect');
        select.innerHTML = '';
        projects.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = p.name;
          if (p.id === currentProjectId || (currentProjectId === '' && p.name.includes('Starfish'))) {
            opt.selected = true;
          }
          select.appendChild(opt);
        });
        currentProjectId = select.value;
      } catch (err) {
        console.error('Error fetching projects:', err);
      }
    }'''

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    with open('/home/pratik/Desktop/Internship/task_dashboard/index.html', 'w') as f:
        f.write(content)
    print("UI_UPDATED_SUCCESSFULLY")
else:
    print("MATCH_NOT_FOUND")
