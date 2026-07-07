from dto.circuit import QuantumCircuitDefinition
from qiskit import QuantumCircuit

class QiskitAdapter:
    @staticmethod
    def to_qiskit(definition: QuantumCircuitDefinition) -> QuantumCircuit:
        qc = QuantumCircuit(definition.num_qubits, definition.num_clbits)
        
        for op in definition.operations:
            if op["type"] == "gate":
                gate_name = op["name"]
                targets = op["target"]
                controls = op.get("control", [])
                params = op.get("params", [])
                
                # Dynamic mapping for standard gates
                if gate_name == "h":
                    qc.h(targets[0])
                elif gate_name == "x":
                    qc.x(targets[0])
                elif gate_name == "cx":
                    qc.cx(controls[0], targets[0])
            elif op["type"] == "measure":
                qc.measure(op["qubit"], op["clbit"])
                
        return qc
