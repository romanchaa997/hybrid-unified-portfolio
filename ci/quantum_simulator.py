"""Quantum Simulator for probabilistic decision making and optimization."""
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)

class QuantumState(Enum):
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COLLAPSED = "collapsed"
    MIXED = "mixed"

@dataclass
class Qubit:
    """Represents a quantum bit."""
    alpha: complex  # Probability amplitude for |0>
    beta: complex   # Probability amplitude for |1>
    state: QuantumState = QuantumState.SUPERPOSITION

    @property
    def prob_zero(self) -> float:
        return abs(self.alpha) ** 2

    @property
    def prob_one(self) -> float:
        return abs(self.beta) ** 2

    def measure(self) -> int:
        """Collapse to classical bit."""
        rand = random.random()
        self.state = QuantumState.COLLAPSED
        return 0 if rand < self.prob_zero else 1

class QuantumSimulator:
    """Quantum computing simulator for probabilistic optimization."""

    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.qubits: List[Qubit] = []
        self._initialize_qubits()
        logger.info(f"Quantum Simulator initialized with {num_qubits} qubits")

    def _initialize_qubits(self) -> None:
        """Initialize qubits in |0> state."""
        for _ in range(self.num_qubits):
            self.qubits.append(Qubit(alpha=1.0+0j, beta=0.0+0j))

    def apply_hadamard(self, qubit_index: int) -> None:
        """Apply Hadamard gate for superposition."""
        q = self.qubits[qubit_index]
        new_alpha = (q.alpha + q.beta) / math.sqrt(2)
        new_beta = (q.alpha - q.beta) / math.sqrt(2)
        q.alpha = new_alpha
        q.beta = new_beta
        q.state = QuantumState.SUPERPOSITION

    def apply_pauli_x(self, qubit_index: int) -> None:
        """Apply Pauli-X gate (NOT gate)."""
        q = self.qubits[qubit_index]
        q.alpha, q.beta = q.beta, q.alpha

    def apply_cnot(self, control: int, target: int) -> None:
        """Apply CNOT gate for entanglement."""
        if abs(self.qubits[control].beta) > 0.5:
            self.apply_pauli_x(target)
        self.qubits[target].state = QuantumState.ENTANGLED

    def measure_all(self) -> List[int]:
        """Measure all qubits."""
        return [q.measure() for q in self.qubits]

    def optimize_choice(self, options: List[float]) -> Tuple[int, float]:
        """Use quantum superposition to find optimal choice."""
        num_options = len(options)
        if num_options == 0:
            return 0, 0.0
        
        # Simulate quantum sampling
        best_idx = 0
        best_value = options[0]
        samples = 100
        
        for _ in range(samples):
            # Create superposition
            for i in range(min(self.num_qubits, math.ceil(math.log2(num_options)))):
                self.apply_hadamard(i)
            
            # Measure and check
            measurement = self.measure_all()
            idx = sum(measurement[i] * (2 ** i) for i in range(len(measurement))) % num_options
            
            if options[idx] > best_value:
                best_value = options[idx]
                best_idx = idx
        
        return best_idx, best_value

    def get_quantum_state(self) -> Dict:
        """Get current quantum state."""
        return {
            "num_qubits": self.num_qubits,
            "qubits": [
                {
                    "alpha": str(q.alpha),
                    "beta": str(q.beta),
                    "prob_0": q.prob_zero,
                    "prob_1": q.prob_one,
                    "state": q.state.value
                }
                for q in self.qubits
            ]
        }

if __name__ == "__main__":
    sim = QuantumSimulator(4)
    options = [10.5, 15.3, 8.2, 20.1, 12.7]
    idx, value = sim.optimize_choice(options)
    print(f"Best option: index {idx}, value {value}")
