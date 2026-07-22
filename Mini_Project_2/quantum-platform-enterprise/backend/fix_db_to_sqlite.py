import os
import glob

models_dir = os.path.join(os.path.dirname(__file__), "models")

for filepath in glob.glob(os.path.join(models_dir, "*.py")):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace PostgreSQL specific imports with generic ones
    content = content.replace(
        "from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY",
        "from sqlalchemy import JSON as JSONB, String as ARRAY\nfrom sqlalchemy.types import Uuid as UUID"
    )
    content = content.replace(
        "from sqlalchemy.dialects.postgresql import UUID, JSONB",
        "from sqlalchemy import JSON as JSONB\nfrom sqlalchemy.types import Uuid as UUID"
    )
    content = content.replace(
        "from sqlalchemy.dialects.postgresql import UUID",
        "from sqlalchemy.types import Uuid as UUID"
    )
    content = content.replace("UUID(as_uuid=True)", "UUID")
    
    with open(filepath, "w") as f:
        f.write(content)

print("Models updated for SQLite compatibility.")

# Update settings.py
settings_path = os.path.join(os.path.dirname(__file__), "core", "config", "settings.py")
with open(settings_path, "r") as f:
    settings_content = f.read()

settings_content = settings_content.replace(
    'POSTGRES_SERVER: str = "postgresql+asyncpg://postgres:postgres@localhost/quantum_db"',
    'POSTGRES_SERVER: str = "sqlite+aiosqlite:///./quantum_db.sqlite3"'
)

with open(settings_path, "w") as f:
    f.write(settings_content)

print("settings.py updated for SQLite.")
