import os
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, GroverOperator
from qiskit.quantum_info import Statevector

out_dir = r"D:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\frontend\public\circuits"
os.makedirs(out_dir, exist_ok=True)

# 1. Bell State
qc1 = QuantumCircuit(2)
qc1.h(0)
qc1.cx(0, 1)
qc1.measure_all()
qc1.draw('mpl', filename=os.path.join(out_dir, 'bell_state.png'), style='iqx-dark')

# 2. QFT
qc2 = QuantumCircuit(4)
qc2.append(QFT(4), range(4))
qc2.measure_all()
qc2.draw('mpl', filename=os.path.join(out_dir, 'qft.png'), style='iqx-dark')

# 3. Grover (simple 2 qubit)
qc3 = QuantumCircuit(2)
qc3.h([0,1])
qc3.cz(0,1) # Oracle for |11>
qc3.h([0,1])
qc3.z([0,1])
qc3.cz(0,1)
qc3.h([0,1])
qc3.measure_all()
qc3.draw('mpl', filename=os.path.join(out_dir, 'grover_search.png'), style='iqx-dark')

# 4. Teleportation
qc4 = QuantumCircuit(3, 3)
qc4.h(1)
qc4.cx(1, 2)
qc4.cx(0, 1)
qc4.h(0)
qc4.measure([0,1], [0,1])
qc4.cx(1, 2)
qc4.cz(0, 2)
qc4.measure(2, 2)
qc4.draw('mpl', filename=os.path.join(out_dir, 'quantum_teleportation.png'), style='iqx-dark')

print("All circuits generated!")
