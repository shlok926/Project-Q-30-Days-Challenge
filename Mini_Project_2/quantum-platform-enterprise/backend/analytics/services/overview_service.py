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
