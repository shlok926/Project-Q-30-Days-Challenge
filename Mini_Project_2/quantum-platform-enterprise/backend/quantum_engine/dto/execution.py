from pydantic import BaseModel
from typing import Dict, Any, Optional
from dto.circuit import CircuitExecutionRequest, CircuitExecutionResponse

class ExecutionReport(BaseModel):
    execution_id: str
    compilation_time_ms: float
    execution_time_ms: float
    queue_time_ms: float = 0.0
    provider_name: str
    provider_version: Optional[str] = None
    backend_name: str
    backend_version: Optional[str] = None
    runtime_version: Optional[str] = None
    simulator_type: str
    optimization_level: int
    ibm_job_id: Optional[str] = None
    warnings: list[str] = []
    errors: list[str] = []
    statistics: Dict[str, Any] = {}
