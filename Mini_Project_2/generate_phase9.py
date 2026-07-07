import os

base_dir = r"d:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\backend"

files = {
    "pyproject.toml": """
[tool.poetry]
name = "quantum-platform-enterprise"
version = "0.1.0"
description = "Enterprise Quantum Platform"
authors = ["Admin <admin@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.100.0"
uvicorn = "^0.23.0"
sqlalchemy = "^2.0.0"
pydantic = "^2.0.0"
pydantic-settings = "^2.0.0"
alembic = "^1.11.0"
asyncpg = "^0.28.0"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
prometheus-client = "^0.17.0"
qiskit = "^1.0.0"
qiskit-aer = "^0.14.0"
qiskit-ibm-runtime = "^0.23.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.7.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
ruff = "^0.0.280"
mypy = "^1.4.1"
bandit = "^1.7.5"
safety = "^2.3.5"

[tool.ruff]
line-length = 100
select = ["E", "F", "B", "I", "N", "UP", "S"]
ignore = []

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
strict = True
ignore_missing_imports = True
""",
    "core/middleware/security.py": """
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
""",
    "tests/architecture/test_architecture.py": """
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
"""
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

main_path = os.path.join(base_dir, "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_code = f.read()

if "from core.middleware.security import SecurityHeadersMiddleware" not in main_code:
    main_code = main_code.replace(
        "from core.middleware.logging_middleware import EnterpriseLoggingMiddleware",
        "from core.middleware.logging_middleware import EnterpriseLoggingMiddleware\nfrom core.middleware.security import SecurityHeadersMiddleware"
    )

if "app.add_middleware(SecurityHeadersMiddleware)" not in main_code:
    main_code = main_code.replace(
        "app.add_middleware(EnterpriseLoggingMiddleware)",
        "app.add_middleware(EnterpriseLoggingMiddleware)\napp.add_middleware(SecurityHeadersMiddleware)"
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_code)
