from exceptions.quantum_exceptions import (
    QuantumEngineError, ProviderAuthError, BackendOffline,
    HardwareQueueError, ExecutionTimeout
)
import logging

logger = logging.getLogger(__name__)

def map_ibm_exception(e: Exception) -> QuantumEngineError:
    err_str = str(e).lower()
    if "auth" in err_str or "unauthorized" in err_str:
        logger.error("Provider Authentication Error (Details masked)")
        return ProviderAuthError("Failed to authenticate with IBM Quantum.")
    if "offline" in err_str or "not found" in err_str:
        return BackendOffline("The requested IBM backend is offline or not found.")
    if "queue" in err_str or "capacity" in err_str:
        return HardwareQueueError("Hardware queue overflow or capacity reached.")
    if "timeout" in err_str:
        return ExecutionTimeout("IBM Runtime job timed out.")
    return QuantumEngineError(f"IBM Execution Error: {str(e)}")
