import asyncio
import uuid
from database.session import engine
from database.base import Base
# Import all models to ensure they are registered with Base
from models.user import User, RoleEnum
from models.experiment import Experiment
from models.analytics import DailyAggregation
from models.execution_history import ExecutionHistory
from models.audit import AuditLog
from core.security.password import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Database schema created.")

    # Seed initial data
    from database.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@quantum.com",
            username="admin",
            password_hash=get_password_hash("admin123"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        print("Admin user created (admin@quantum.com).")

if __name__ == "__main__":
    asyncio.run(init_db())
