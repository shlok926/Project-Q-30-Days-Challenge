import os

base_dir = r"d:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\backend"

folders = [
    "analytics",
    "analytics/metrics",
    "analytics/events",
    "analytics/aggregators",
    "analytics/reports",
    "analytics/insights",
    "analytics/statistics",
    "analytics/alerts",
    "analytics/forecasting",
    "analytics/export",
    "analytics/dto",
    "analytics/services",
    "analytics/repositories",
    "analytics/tests"
]

files = {
    "analytics/metrics/prometheus.py": """
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

EXPERIMENT_CREATED_COUNT = Counter('quantum_experiments_created_total', 'Total number of created experiments')
JOB_EXECUTED_COUNT = Counter('quantum_jobs_executed_total', 'Total number of executed jobs', ['provider', 'backend'])
JOB_FAILED_COUNT = Counter('quantum_jobs_failed_total', 'Total number of failed jobs', ['provider'])

API_LATENCY = Histogram('api_latency_seconds', 'Latency of API responses in seconds', ['endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users in the system')

def get_metrics_response():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
""",
    "analytics/metrics/tracing.py": """
import uuid
from typing import Optional

class TraceContext:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        
    def get_context(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }

def start_span(name: str, context: Optional[TraceContext] = None):
    pass
""",
    "models/analytics.py": """
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
""",
    "analytics/events/subscribers.py": """
from core.events import event_bus, EventTypes
from analytics.metrics.prometheus import EXPERIMENT_CREATED_COUNT, JOB_EXECUTED_COUNT, JOB_FAILED_COUNT
import logging

logger = logging.getLogger(__name__)

async def handle_experiment_created(payload: dict):
    logger.info(f"Analytics captured Experiment Created: {payload.get('experiment_id')}")
    EXPERIMENT_CREATED_COUNT.inc()

async def handle_job_executed(payload: dict):
    provider = payload.get('provider', 'unknown')
    backend = payload.get('backend', 'unknown')
    JOB_EXECUTED_COUNT.labels(provider=provider, backend=backend).inc()

async def handle_job_failed(payload: dict):
    provider = payload.get('provider', 'unknown')
    JOB_FAILED_COUNT.labels(provider=provider).inc()

def setup_analytics_subscriptions():
    event_bus.subscribe(EventTypes.EXPERIMENT_CREATED, handle_experiment_created)
    event_bus.subscribe(EventTypes.EXPERIMENT_QUEUED, handle_job_executed)
    event_bus.subscribe(EventTypes.JOB_FAILED, handle_job_failed)
""",
    "analytics/services/overview_service.py": """
from sqlalchemy.ext.asyncio import AsyncSession
from models.analytics import DailyAggregation
from sqlalchemy.future import select

class AnalyticsOverviewService:
    @staticmethod
    async def get_system_overview(db: AsyncSession):
        return {
            "total_experiments_today": 120,
            "success_rate": 98.5,
            "active_backends": 5,
            "average_queue_time_ms": 450.2
        }
""",
    "api/v1/endpoints/analytics.py": """
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from models.user import User
from api.deps import get_current_user, require_role
from analytics.services.overview_service import AnalyticsOverviewService
from analytics.metrics.prometheus import get_metrics_response

router = APIRouter()

@router.get("/metrics", include_in_schema=False)
async def metrics():
    return get_metrics_response()

@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return await AnalyticsOverviewService.get_system_overview(db)

@router.get("/providers")
async def get_provider_analytics(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "ibm_quantum": {
            "usage_percentage": 75.0,
            "average_queue_time": "12s",
            "health_status": "operational"
        },
        "aer_simulator": {
            "usage_percentage": 25.0,
            "average_queue_time": "0s",
            "health_status": "operational"
        }
    }
"""
}

for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    with open(os.path.join(base_dir, folder, "__init__.py"), "w") as f:
        pass

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

main_path = os.path.join(base_dir, "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_code = f.read()

if "from api.v1.endpoints import auth, users, experiments" in main_code:
    main_code = main_code.replace(
        "from api.v1.endpoints import auth, users, experiments",
        "from api.v1.endpoints import auth, users, experiments, analytics\nfrom analytics.events.subscribers import setup_analytics_subscriptions"
    )

if "setup_logging()" in main_code and "setup_analytics_subscriptions()" not in main_code:
    main_code = main_code.replace("setup_logging()", "setup_logging()\nsetup_analytics_subscriptions()")

if "app.include_router(experiments.router" in main_code and "analytics.router" not in main_code:
    exp_router_str = 'app.include_router(experiments.router, prefix=f"{settings.API_V1_STR}/experiments", tags=["Experiments"])'
    analytics_router_str = 'app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])'
    prom_str = 'app.add_route("/metrics", analytics.metrics)'
    
    main_code = main_code.replace(exp_router_str, f"{exp_router_str}\n{analytics_router_str}\n{prom_str}")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_code)
