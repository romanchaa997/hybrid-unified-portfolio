"""Energy Management System for distributed power grid optimization."""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PowerNode:
    """Represents a node in the power distribution network."""
    node_id: str
    location: str
    capacity: float  # MW
    current_load: float = 0.0
    efficiency: float = 0.95
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def available_capacity(self) -> float:
        """Calculate available capacity."""
        return self.capacity - self.current_load

    @property
    def utilization_percent(self) -> float:
        """Calculate utilization percentage."""
        return (self.current_load / self.capacity) * 100 if self.capacity > 0 else 0


@dataclass
class EnergyFlow:
    """Represents energy flow between nodes."""
    source_node: str
    destination_node: str
    amount: float  # MWh
    efficiency: float = 0.98
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def energy_loss(self) -> float:
        """Calculate energy loss during transmission."""
        return self.amount * (1 - self.efficiency)


class EnergyManagementSystem:
    """Distributed energy management system with predictive optimization."""

    def __init__(self, name: str = "EMS-001"):
        self.name = name
        self.nodes: Dict[str, PowerNode] = {}
        self.flows: List[EnergyFlow] = []
        self.history: List[Dict] = []
        self.optimization_enabled = True
        self.demand_forecast: Dict[str, List[float]] = {}
        logger.info(f"Initialized {self.name}")

    def register_node(self, node: PowerNode) -> bool:
        """Register a power node in the system."""
        if node.node_id in self.nodes:
            logger.warning(f"Node {node.node_id} already registered")
            return False
        self.nodes[node.node_id] = node
        self.demand_forecast[node.node_id] = []
        logger.info(f"Registered node {node.node_id}")
        return True

    def update_load(self, node_id: str, load: float) -> bool:
        """Update the load on a specific node."""
        if node_id not in self.nodes:
            logger.error(f"Node {node_id} not found")
            return False
        
        node = self.nodes[node_id]
        if load > node.capacity:
            logger.warning(f"Load {load} exceeds capacity {node.capacity}")
            load = node.capacity
        
        node.current_load = load
        node.timestamp = datetime.now()
        return True

    def route_energy(self, source: str, destination: str, amount: float) -> Optional[EnergyFlow]:
        """Route energy between nodes."""
        if source not in self.nodes or destination not in self.nodes:
            logger.error(f"Invalid nodes: {source} -> {destination}")
            return None
        
        source_node = self.nodes[source]
        if source_node.available_capacity < amount:
            logger.warning(f"Insufficient capacity at {source}")
            return None
        
        flow = EnergyFlow(source, destination, amount)
        self.flows.append(flow)
        
        # Update loads
        source_node.current_load += amount
        self.nodes[destination].current_load -= amount * flow.efficiency
        
        logger.info(f"Energy flow: {source} -> {destination}, {amount} MWh")
        return flow

    def optimize_grid(self) -> Dict[str, float]:
        """Optimize energy distribution across the grid."""
        if not self.optimization_enabled:
            return {}
        
        optimization_metrics = {}
        
        # Calculate total system load
        total_load = sum(n.current_load for n in self.nodes.values())
        total_capacity = sum(n.capacity for n in self.nodes.values())
        
        optimization_metrics['system_utilization'] = (total_load / total_capacity) * 100
        optimization_metrics['total_load'] = total_load
        optimization_metrics['total_capacity'] = total_capacity
        
        # Identify overloaded nodes
        overloaded = [n for n in self.nodes.values() if n.utilization_percent > 85]
        optimization_metrics['overloaded_nodes'] = len(overloaded)
        
        # Identify underutilized nodes
        underutilized = [n for n in self.nodes.values() if n.utilization_percent < 30]
        optimization_metrics['underutilized_nodes'] = len(underutilized)
        
        logger.info(f"Grid optimization complete: {optimization_metrics}")
        return optimization_metrics

    def forecast_demand(self, node_id: str, hours: int = 24) -> List[float]:
        """Forecast energy demand for a node."""
        if node_id not in self.nodes:
            return []
        
        # Simple forecasting based on historical data
        historical = self.demand_forecast.get(node_id, [])
        
        if len(historical) < 24:
            # Use average demand
            avg_demand = np.mean(historical) if historical else 0.5
            forecast = [avg_demand] * hours
        else:
            # Use seasonal averaging
            forecast = []
            for i in range(hours):
                hour_demands = [historical[j] for j in range(i, len(historical), 24)]
                forecast.append(np.mean(hour_demands) if hour_demands else 0.5)
        
        self.demand_forecast[node_id].extend(forecast)
        return forecast

    async def monitor_system(self, interval: int = 60) -> None:
        """Monitor system health and optimize continuously."""
        while True:
            try:
                metrics = self.optimize_grid()
                snapshot = {
                    'timestamp': datetime.now(),
                    'metrics': metrics,
                    'node_states': {n_id: n.utilization_percent for n_id, n in self.nodes.items()}
                }
                self.history.append(snapshot)
                logger.debug(f"System snapshot: {snapshot}")
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        return {
            'name': self.name,
            'nodes': len(self.nodes),
            'active_flows': len(self.flows),
            'optimization_enabled': self.optimization_enabled,
            'metrics': self.optimize_grid()
        }


if __name__ == "__main__":
    # Example usage
    ems = EnergyManagementSystem("EMS-Primary")
    
    # Register nodes
    node1 = PowerNode("N001", "Downtown", 100.0)
    node2 = PowerNode("N002", "Midtown", 150.0)
    node3 = PowerNode("N003", "Uptown", 120.0)
    
    ems.register_node(node1)
    ems.register_node(node2)
    ems.register_node(node3)
    
    # Simulate loads
    ems.update_load("N001", 75.0)
    ems.update_load("N002", 110.0)
    ems.update_load("N003", 85.0)
    
    # Optimize
    status = ems.get_system_status()
    print(f"System Status: {status}")
