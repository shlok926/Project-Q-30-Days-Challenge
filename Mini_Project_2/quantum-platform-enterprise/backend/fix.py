import os
for root, _, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                c = file.read()
            if '\
' in c:
                c = c.replace('\
', '
')
                with open(p, 'w', encoding='utf-8') as file:
                    file.write(c)
