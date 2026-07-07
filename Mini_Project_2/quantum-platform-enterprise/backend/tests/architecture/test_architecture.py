import os
import ast

def get_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def test_domain_independence():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    models_dir = os.path.join(backend_dir, "models")
    
    if not os.path.exists(models_dir):
        return

    for root, _, files in os.walk(models_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                imports = get_imports(filepath)
                for imp in imports:
                    assert not imp.startswith("api"), f"Architecture Violation: Model {file} imports API layer ({imp})"

def test_quantum_engine_independence():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    qe_dir = os.path.join(backend_dir, "quantum_engine")
    
    if not os.path.exists(qe_dir):
        return

    for root, _, files in os.walk(qe_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                imports = get_imports(filepath)
                for imp in imports:
                    assert not imp.startswith("api"), f"Architecture Violation: Quantum Engine {file} imports API layer ({imp})"
                    assert not imp.startswith("repositories"), f"Architecture Violation: Quantum Engine {file} imports Repositories ({imp})"
