from dto.circuit import QuantumCircuitDefinition
from exceptions.quantum_exceptions import InvalidCircuit

class CircuitValidator:
    @staticmethod
    def validate(definition: QuantumCircuitDefinition) -> bool:
        if definition.num_qubits <= 0:
            raise InvalidCircuit("Number of qubits must be greater than 0.")
        return True
