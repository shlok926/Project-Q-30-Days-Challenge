from interfaces.provider import QuantumProvider, QuantumBackend
from adapters.qiskit_adapter import QiskitAdapter
from dto.circuit import CircuitExecutionRequest, CircuitExecutionResponse
from dto.provider import ProviderCapabilities
from exceptions.ibm_exceptions import map_ibm_exception
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import transpile
import uuid
import time
import logging

logger = logging.getLogger(__name__)

class IBMRuntimeBackend(QuantumBackend):
    def __init__(self, service: QiskitRuntimeService, backend_name: str):
        self.backend_name = backend_name
        self.service = service
        try:
            self.backend = service.backend(backend_name)
        except Exception as e:
            raise map_ibm_exception(e)
            
    def execute(self, request: CircuitExecutionRequest) -> CircuitExecutionResponse:
        start_time = time.time()
        
        try:
            # Transpilation
            qc = QiskitAdapter.to_qiskit(request.definition)
            comp_start = time.time()
            compiled_circuit = transpile(qc, self.backend, optimization_level=request.metadata.optimization_level)
            compilation_time = (time.time() - comp_start) * 1000
            
            # Execution using Sampler primitive
            sampler = Sampler(backend=self.backend)
            job = sampler.run([compiled_circuit], shots=request.shots)
            
            logger.info("Submitted job to IBM Runtime", extra={"ibm_job_id": job.job_id()})
            
            result = job.result()
            
            # Parsing primitives V2 output
            pub_result = result[0]
            counts = pub_result.data.c.get_counts() if hasattr(pub_result.data, "c") else {}
            
            execution_time = (time.time() - start_time) * 1000
            
            return CircuitExecutionResponse(
                job_id=job.job_id(),
                status=job.status().name,
                counts=counts,
                execution_time_ms=execution_time
            )
        except Exception as e:
            raise map_ibm_exception(e)

class IBMProvider(QuantumProvider):
    def __init__(self, api_token: str):
        try:
            self.service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)
        except Exception as e:
            raise map_ibm_exception(e)
            
    def get_backend(self, name: str) -> QuantumBackend:
        return IBMRuntimeBackend(self.service, name)
        
    def available_backends(self) -> list:
        backends = self.service.backends()
        return [b.name for b in backends]

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_runtime=True,
            supports_sampler=True,
            supports_estimator=True,
            supports_dynamic_circuits=True,
            supports_pulse=True,
            supports_noise=True,
            supports_real_hardware=True,
            supports_simulator=True
        )
