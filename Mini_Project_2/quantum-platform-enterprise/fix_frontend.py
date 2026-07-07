import os

frontend_dir = r"d:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\frontend"

for root, dirs, files in os.walk(frontend_dir):
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    if ".next" in dirs:
        dirs.remove(".next")
        
    for f in files:
        if f.endswith('.ts') or f.endswith('.tsx') or f.endswith('.js') or f.endswith('.json'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8') as file:
                    c = file.read()
                if '\\n' in c:
                    c = c.replace('\\n', '\n')
                    with open(p, 'w', encoding='utf-8') as file:
                        file.write(c)
            except Exception as e:
                pass
