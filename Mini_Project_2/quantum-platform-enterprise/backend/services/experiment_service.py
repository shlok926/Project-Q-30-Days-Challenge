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
