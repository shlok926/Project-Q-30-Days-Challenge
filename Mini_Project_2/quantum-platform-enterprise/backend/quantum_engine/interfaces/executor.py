from abc import ABC, abstractmethod

class QuantumExecutor(ABC):
    @abstractmethod
    def run(self, execution_context: "ExecutionContext") -> "ExecutionResult":
        pass
