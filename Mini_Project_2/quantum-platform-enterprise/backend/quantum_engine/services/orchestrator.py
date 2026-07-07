from dto.circuit import CircuitExecutionRequest, CircuitExecutionResponse
from dto.execution import ExecutionReport
from interfaces.provider import QuantumProvider
from validators.circuit_validator import CircuitValidator
import uuid
import time

class ExecutionOrchestrator:
    def __init__(self, factory):
        self.factory = factory
        
    def execute(self, request: CircuitExecutionRequest, provider_type: str = "aer") -> CircuitExecutionResponse:
        start_time = time.time()
        
        # 1. Validate Circuit
        CircuitValidator.validate(request.definition)
        
        # 2. Select Provider
        provider = self.factory.get_provider(provider_type)
        
        # 3. Get Backend
        backend = provider.get_backend("qasm_simulator")
        
        # 4. Compile & Execute via Backend Abstraction
        # The backend encapsulates Compilation -> Execution -> Result Normalization
        response = backend.execute(request)
        
        execution_time = (time.time() - start_time) * 1000
        response.execution_time_ms = execution_time
        
        return response
