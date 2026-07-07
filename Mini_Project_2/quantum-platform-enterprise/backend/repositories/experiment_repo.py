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
