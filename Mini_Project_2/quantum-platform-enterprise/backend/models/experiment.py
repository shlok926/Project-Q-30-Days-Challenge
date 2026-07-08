import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON as JSONB, String as ARRAY
from sqlalchemy.types import Uuid as UUID
from database.base import Base
from core.state_machine import ExperimentStatus

class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[ExperimentStatus] = mapped_column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT)
    
    algorithm: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=True)
    backend_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    tags: Mapped[list[str]] = mapped_column(JSONB, default=[])
    version: Mapped[int] = mapped_column(default=1)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    configuration: Mapped[dict] = mapped_column(JSONB, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
