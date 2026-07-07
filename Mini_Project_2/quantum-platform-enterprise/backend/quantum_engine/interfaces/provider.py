from abc import ABC, abstractmethod
from typing import List, Dict, Any

class QuantumProvider(ABC):
    @abstractmethod
    def get_backend(self, name: str) -> "QuantumBackend":
        pass
        
    @abstractmethod
    def available_backends(self) -> List["QuantumBackend"]:
        pass

class QuantumBackend(ABC):
    @abstractmethod
    def execute(self, circuit: "CircuitExecutionRequest") -> "CircuitExecutionResponse":
        pass
