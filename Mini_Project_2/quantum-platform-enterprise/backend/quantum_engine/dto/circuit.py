from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QuantumCircuitDefinition(BaseModel):
    num_qubits: int
    num_clbits: int
    operations: List[Dict[str, Any]]

class CircuitMetadata(BaseModel):
    name: str
    description: Optional[str]
    optimization_level: int = 1

class CircuitExecutionRequest(BaseModel):
    definition: QuantumCircuitDefinition
    metadata: CircuitMetadata
    shots: int = 1024

class CircuitExecutionResponse(BaseModel):
    job_id: str
    status: str
    counts: Optional[Dict[str, int]]
    execution_time_ms: float
