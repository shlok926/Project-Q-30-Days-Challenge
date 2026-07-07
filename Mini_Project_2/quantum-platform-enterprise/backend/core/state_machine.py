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
