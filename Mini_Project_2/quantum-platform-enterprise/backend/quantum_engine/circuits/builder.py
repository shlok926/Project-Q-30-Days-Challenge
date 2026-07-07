from typing import List, Dict, Any
from dto.circuit import QuantumCircuitDefinition

class CircuitBuilder:
    def __init__(self):
        self.num_qubits = 0
        self.num_clbits = 0
        self.operations = []

    def create_register(self, qubits: int, clbits: int = 0):
        self.num_qubits = qubits
        self.num_clbits = clbits
        return self

    def add_gate(self, name: str, target: List[int], control: List[int] = None, params: List[float] = None):
        self.operations.append({
            "type": "gate",
            "name": name,
            "target": target,
            "control": control or [],
            "params": params or []
        })
        return self

    def add_measurement(self, qubit: int, clbit: int):
        self.operations.append({
            "type": "measure",
            "qubit": qubit,
            "clbit": clbit
        })
        return self

    def reset(self):
        self.num_qubits = 0
        self.num_clbits = 0
        self.operations = []
        return self

    def build(self) -> QuantumCircuitDefinition:
        return QuantumCircuitDefinition(
            num_qubits=self.num_qubits,
            num_clbits=self.num_clbits,
            operations=self.operations
        )
