from abc import ABC, abstractmethod
from dto.circuit import QuantumCircuitDefinition

class QuantumAlgorithmPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def build_circuit(self, **kwargs) -> QuantumCircuitDefinition:
        pass
