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
