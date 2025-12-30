"""Neural Network Adapter for ML integration and model execution."""
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class ActivationFunction(Enum):
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    LINEAR = "linear"

@dataclass
class Layer:
    units: int
    activation: ActivationFunction = ActivationFunction.RELU
    weights: Optional[np.ndarray] = None
    bias: Optional[np.ndarray] = None

class NeuralNetworkAdapter:
    """Adapter for neural network execution and prediction."""
    
    def __init__(self, name: str = "NN-001"):
        self.name = name
        self.layers: List[Layer] = []
        self.is_trained = False
        logger.info(f"Neural Network Adapter {name} initialized")
    
    def add_layer(self, units: int, activation: ActivationFunction = ActivationFunction.RELU) -> None:
        """Add a layer to the network."""
        layer = Layer(units=units, activation=activation)
        if len(self.layers) > 0:
            prev_units = self.layers[-1].units
            layer.weights = np.random.randn(prev_units, units) * 0.01
            layer.bias = np.zeros((1, units))
        self.layers.append(layer)
    
    def _activate(self, x: np.ndarray, activation: ActivationFunction) -> np.ndarray:
        """Apply activation function."""
        if activation == ActivationFunction.RELU:
            return np.maximum(0, x)
        elif activation == ActivationFunction.SIGMOID:
            return 1 / (1 + np.exp(-x))
        elif activation == ActivationFunction.TANH:
            return np.tanh(x)
        return x
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward propagation."""
        output = x
        for layer in self.layers:
            if layer.weights is not None:
                output = np.dot(output, layer.weights) + layer.bias
                output = self._activate(output, layer.activation)
        return output
    
    def predict(self, inputs: List[float]) -> np.ndarray:
        """Make prediction on input."""
        x = np.array(inputs).reshape(1, -1)
        return self.forward(x)
    
    def get_architecture(self) -> Dict:
        """Get network architecture."""
        return {
            "name": self.name,
            "num_layers": len(self.layers),
            "layers": [{"units": l.units, "activation": l.activation.value} for l in self.layers]
        }

if __name__ == "__main__":
    nn = NeuralNetworkAdapter("SimpleNN")
    nn.add_layer(10)
    nn.add_layer(5)
    nn.add_layer(1, ActivationFunction.SIGMOID)
    prediction = nn.predict([0.5, -0.2])
    print(f"Prediction: {prediction}")
