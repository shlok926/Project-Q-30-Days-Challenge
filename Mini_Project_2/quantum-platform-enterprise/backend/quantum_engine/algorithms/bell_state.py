from algorithms.base import QuantumAlgorithmPlugin
from dto.circuit import QuantumCircuitDefinition
from circuits.builder import CircuitBuilder

class BellStateAlgorithm(QuantumAlgorithmPlugin):
    @property
    def name(self) -> str:
        return "bell_state"

    def build_circuit(self, **kwargs) -> QuantumCircuitDefinition:
        builder = CircuitBuilder()
        builder.create_register(qubits=2, clbits=2)
        
        # Apply H gate on qubit 0
        builder.add_gate("h", target=[0])
        
        # Apply CX gate control=0, target=1
        builder.add_gate("cx", control=[0], target=[1])
        
        # Measure
        builder.add_measurement(0, 0)
        builder.add_measurement(1, 1)
        
        return builder.build()
