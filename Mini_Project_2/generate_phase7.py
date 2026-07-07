import os

base_dir = r"d:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\backend"

files = {
    "core/events.py": """
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DomainEventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any):
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    await handler(payload)
                except Exception as e:
                    logger.error(f"Error handling event {event_type}: {e}")

event_bus = DomainEventBus()

class EventTypes:
    EXPERIMENT_CREATED = "ExperimentCreated"
    EXPERIMENT_QUEUED = "ExperimentQueued"
    EXPERIMENT_COMPLETED = "ExperimentCompleted"
    JOB_FAILED = "JobFailed"
    PROVIDER_UNAVAILABLE = "ProviderUnavailable"
""",
    "core/state_machine.py": """
from core.exceptions.base import BusinessRuleError
import enum

class ExperimentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"

class ExperimentStateMachine:
    _transitions = {
        ExperimentStatus.DRAFT: [ExperimentStatus.VALIDATED, ExperimentStatus.ARCHIVED],
        ExperimentStatus.VALIDATED: [ExperimentStatus.DRAFT, ExperimentStatus.QUEUED, ExperimentStatus.ARCHIVED],
        ExperimentStatus.QUEUED: [ExperimentStatus.RUNNING, ExperimentStatus.CANCELLED, ExperimentStatus.FAILED],
        ExperimentStatus.RUNNING: [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED, ExperimentStatus.CANCELLED],
        ExperimentStatus.COMPLETED: [ExperimentStatus.ARCHIVED],
        ExperimentStatus.FAILED: [ExperimentStatus.QUEUED, ExperimentStatus.ARCHIVED],
        ExperimentStatus.CANCELLED: [ExperimentStatus.DRAFT, ExperimentStatus.ARCHIVED],
        ExperimentStatus.ARCHIVED: [ExperimentStatus.DRAFT]
    }

    @classmethod
    def can_transition(cls, current: ExperimentStatus, target: ExperimentStatus) -> bool:
        return target in cls._transitions.get(current, [])

    @classmethod
    def validate_transition(cls, current: ExperimentStatus, target: ExperimentStatus):
        if not cls.can_transition(current, target):
            raise BusinessRuleError(f"Cannot transition from {current} to {target}")
""",
    "models/experiment.py": """
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from database.base import Base
from core.state_machine import ExperimentStatus

class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[ExperimentStatus] = mapped_column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT)
    
    algorithm: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=True)
    backend_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    version: Mapped[int] = mapped_column(default=1)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    configuration: Mapped[dict] = mapped_column(JSONB, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
""",
    "models/execution_history.py": """
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.base import Base

class ExecutionHistory(Base):
    __tablename__ = "execution_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False)
    
    ibm_job_id: Mapped[str] = mapped_column(String, nullable=True)
    provider: Mapped[str] = mapped_column(String)
    backend: Mapped[str] = mapped_column(String)
    
    shots: Mapped[int] = mapped_column(Integer, default=1024)
    queue_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    compilation_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    execution_report: Mapped[dict] = mapped_column(JSONB, default={})
    
    errors: Mapped[list[str]] = mapped_column(JSONB, default=[])
    warnings: Mapped[list[str]] = mapped_column(JSONB, default=[])
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
""",
    "repositories/experiment_repo.py": """
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models.experiment import Experiment
from repositories.base import BaseRepository
import uuid

class ExperimentRepository(BaseRepository[Experiment]):
    def __init__(self):
        super().__init__(Experiment)

    async def get_by_owner(self, db: AsyncSession, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Experiment]:
        query = select(Experiment).filter(Experiment.owner_id == owner_id, Experiment.is_deleted == False).order_by(desc(Experiment.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

experiment_repo = ExperimentRepository()
""",
    "schemas/experiment.py": """
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from core.state_machine import ExperimentStatus

class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None
    algorithm: str
    provider: Optional[str] = None
    backend_name: Optional[str] = None
    tags: List[str] = []
    configuration: Dict[str, Any] = {}

class ExperimentCreate(ExperimentBase):
    pass

class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None
    is_favorite: Optional[bool] = None

class ExperimentResponse(ExperimentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: ExperimentStatus
    version: int
    is_favorite: bool
    is_template: bool
    created_at: datetime
    updated_at: datetime
    executed_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
""",
    "services/experiment_service.py": """
from sqlalchemy.ext.asyncio import AsyncSession
from models.experiment import Experiment
from schemas.experiment import ExperimentCreate, ExperimentUpdate
from repositories.experiment_repo import experiment_repo
from core.state_machine import ExperimentStateMachine, ExperimentStatus
from core.exceptions.base import AuthorizationError, ResourceNotFound
from core.events import event_bus, EventTypes
import uuid

class ExperimentService:
    @staticmethod
    async def create_experiment(db: AsyncSession, obj_in: ExperimentCreate, owner_id: uuid.UUID) -> Experiment:
        data = obj_in.model_dump()
        data["owner_id"] = owner_id
        experiment = await experiment_repo.create(db, obj_in=data)
        
        await event_bus.publish(EventTypes.EXPERIMENT_CREATED, {"experiment_id": str(experiment.id)})
        return experiment

    @staticmethod
    async def get_experiment(db: AsyncSession, id: uuid.UUID, current_user_id: uuid.UUID, is_admin: bool = False) -> Experiment:
        exp = await experiment_repo.get(db, id=id)
        if not exp or exp.is_deleted:
            raise ResourceNotFound("Experiment not found")
        if exp.owner_id != current_user_id and not is_admin:
            raise AuthorizationError("Access denied")
        return exp

    @staticmethod
    async def update_status(db: AsyncSession, experiment: Experiment, new_status: ExperimentStatus) -> Experiment:
        ExperimentStateMachine.validate_transition(experiment.status, new_status)
        experiment.status = new_status
        db.add(experiment)
        await db.commit()
        await db.refresh(experiment)
        return experiment

    @staticmethod
    async def soft_delete(db: AsyncSession, experiment: Experiment) -> Experiment:
        experiment.is_deleted = True
        db.add(experiment)
        await db.commit()
        return experiment
""",
    "api/v1/endpoints/experiments.py": """
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database.session import get_db
from models.user import User
from schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentUpdate
from services.experiment_service import ExperimentService
from api.deps import get_current_user
from repositories.experiment_repo import experiment_repo
import uuid

router = APIRouter()

@router.post("", response_model=ExperimentResponse)
async def create_experiment(
    *,
    db: AsyncSession = Depends(get_db),
    experiment_in: ExperimentCreate,
    current_user: User = Depends(get_current_user)
):
    return await ExperimentService.create_experiment(db, experiment_in, current_user.id)

@router.get("", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await experiment_repo.get_by_owner(db, current_user.id, skip=skip, limit=limit)

@router.get("/{id}", response_model=ExperimentResponse)
async def get_experiment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role.value == "admin"
    return await ExperimentService.get_experiment(db, id, current_user.id, is_admin)

@router.delete("/{id}", response_model=ExperimentResponse)
async def delete_experiment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exp = await ExperimentService.get_experiment(db, id, current_user.id)
    return await ExperimentService.soft_delete(db, exp)
"""
}

import os
for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

main_path = os.path.join(base_dir, "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_code = f.read()

if "from api.v1.endpoints import auth, users" in main_code:
    main_code = main_code.replace(
        "from api.v1.endpoints import auth, users",
        "from api.v1.endpoints import auth, users, experiments"
    )

if "app.include_router(users.router" in main_code and "experiments.router" not in main_code:
    users_router_str = 'app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])'
    exp_router_str = 'app.include_router(experiments.router, prefix=f"{settings.API_V1_STR}/experiments", tags=["Experiments"])'
    main_code = main_code.replace(users_router_str, f"{users_router_str}\n{exp_router_str}")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_code)
