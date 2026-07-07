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
