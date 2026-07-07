from abc import ABC, abstractmethod

class QuantumCompiler(ABC):
    @abstractmethod
    def compile(self, definition: "QuantumCircuitDefinition", backend: "QuantumBackend") -> "CompiledCircuit":
        pass
