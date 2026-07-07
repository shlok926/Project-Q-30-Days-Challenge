from interfaces.provider import QuantumProvider, QuantumBackend
from adapters.qiskit_adapter import QiskitAdapter
from dto.circuit import CircuitExecutionRequest, CircuitExecutionResponse
from qiskit_aer import Aer
from qiskit import transpile
import uuid
import time

class AerSimulatorBackend(QuantumBackend):
    def __init__(self, backend_name: str):
        self.backend_name = backend_name
        self.backend = Aer.get_backend(backend_name)
        
    def execute(self, request: CircuitExecutionRequest) -> CircuitExecutionResponse:
        start_time = time.time()
        
        # Convert our agnostic DTO to Qiskit QuantumCircuit
        qc = QiskitAdapter.to_qiskit(request.definition)
        
        # Compile
        compiled_circuit = transpile(qc, self.backend, optimization_level=request.metadata.optimization_level)
        
        # Execute
        job = self.backend.run(compiled_circuit, shots=request.shots)
        result = job.result()
        
        # Normalize
        counts = result.get_counts() if request.shots > 0 else None
        
        execution_time = (time.time() - start_time) * 1000
        
        return CircuitExecutionResponse(
            job_id=str(uuid.uuid4()),
            status="COMPLETED",
            counts=counts,
            execution_time_ms=execution_time
        )

class AerProvider(QuantumProvider):
    def get_backend(self, name: str) -> QuantumBackend:
        if name not in ["qasm_simulator", "statevector_simulator"]:
            name = "qasm_simulator"
        return AerSimulatorBackend(name)
        
    def available_backends(self) -> list:
        return [AerSimulatorBackend("qasm_simulator"), AerSimulatorBackend("statevector_simulator")]
