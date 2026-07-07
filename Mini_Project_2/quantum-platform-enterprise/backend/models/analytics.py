import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.base import Base

class DailyAggregation(Base):
    __tablename__ = "daily_aggregations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metric_name: Mapped[str] = mapped_column(String, index=True)
    metric_value: Mapped[float] = mapped_column(Float, default=0.0)
    dimensions: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
