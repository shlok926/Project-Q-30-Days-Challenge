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
