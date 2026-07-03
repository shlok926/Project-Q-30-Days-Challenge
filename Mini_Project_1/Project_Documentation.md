# 🛡️ Quantum Randomness Laboratory & Password Generator

## 📌 Project Overview
This mini-project was built as the capstone for **Days 1 to 10** of the Project-Q Quantum Challenge. It demonstrates the practical application of Quantum Foundations by creating a **Quantum Random Number Generator (QRNG)** and scaling it into a **Quantum-Secured Password Generator**.

## 🧠 The Theory: Classical vs Quantum Randomness

### Classical Randomness (Pseudo-Random)
Classical computers are deterministic. When you ask Python for a random number (`random.randint()`), it uses a mathematical formula and a "seed" (usually the current system time) to generate a number that *looks* random. However, if a hacker knows the seed and the algorithm, they can perfectly predict the output.

### Quantum Randomness (True Randomness)
Quantum computers operate on probabilities. By taking a Qubit initialized at $|0\rangle$ and applying a **Hadamard (H) Gate**, we place it into an equal superposition:
$$ |+\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle $$

When we **measure** this qubit, the quantum wave function collapses. The universe dictates that there is exactly a 50% chance of it collapsing to a `0` and a 50% chance of it collapsing to a `1`. 
**This is fundamentally unpredictable and physically random.**

---

## 🏗️ Architecture & Scripts

### 1. `qrng.py` (The Core Engine)
Creates a 1-qubit circuit, applies a Hadamard gate, measures it, and simulates the collapse 1000 times to generate raw random numbers.

### 2. `histogram.py` (Visualization)
Uses Qiskit's `plot_histogram` combined with `matplotlib` to visually prove that the distribution of 0s and 1s is nearly perfectly equal, adhering to quantum probability mechanics.

### 3. `statistics.py` (Mathematical Proof)
Calculates the **Mean** and **Standard Deviation** of the 1000 shots. Since the probability is 0.5, the mean should hover around 500, proving the uniform distribution of our quantum coin flips.

### 4. `quantum_password.py` (The USP Application)
**How it works:**
1. We initialize a **6-qubit circuit**.
2. We apply a Hadamard gate to all 6 qubits, creating $2^6 = 64$ possible measurement outcomes (from `000000` to `111111`).
3. We define a custom 64-character set string (`A-Z`, `a-z`, `0-9`, `!`, `@`).
4. We take exactly 16 shots (measurements). 
5. Each shot collapses the 6 qubits into a binary string. We convert that binary string to a decimal integer (0 to 63) and use it as an index to pick a character from our set.
6. The result is a 16-character password where each character was chosen by a quantum event!

## 🔐 Why This Matters for Cybersecurity
As classical computing power grows, pseudo-random generators become weaker. Cryptography relies heavily on randomness (e.g., generating encryption keys). By utilizing QRNGs, we ensure that our generated keys and passwords are mathematically and physically immune to prediction, paving the way for Post-Quantum Cryptography standards.
