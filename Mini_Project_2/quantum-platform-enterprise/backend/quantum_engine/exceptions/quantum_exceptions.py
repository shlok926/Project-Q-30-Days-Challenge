class QuantumEngineError(Exception):
    pass

class CircuitCompilationError(QuantumEngineError):
    pass

class ProviderUnavailable(QuantumEngineError):
    pass

class BackendOffline(QuantumEngineError):
    pass

class InvalidCircuit(QuantumEngineError):
    pass

class NoiseModelError(QuantumEngineError):
    pass

class ExecutionTimeout(QuantumEngineError):
    pass

class HardwareQueueError(QuantumEngineError):
    pass

class ProviderAuthError(QuantumEngineError):
    pass
