"""Autonomous Agent System for self-healing infrastructure."""
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class AgentState(Enum):
    IDLE, ACTIVE, LEARNING, HEALING = "idle", "active", "learning", "healing"

@dataclass
class AgentAction:
    action_type: str
    parameters: Dict = field(default_factory=dict)
    priority: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class AutonomousAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = AgentState.IDLE
        self.memory, self.capabilities = [], []
        logger.info(f"Agent {agent_id} initialized")
    
    async def perceive(self, sensor_data: Dict) -> bool:
        self.memory.append({"sensor_data": sensor_data, "timestamp": datetime.now()})
        return True
    
    async def decide(self) -> Optional[AgentAction]:
        if self.memory and "error" in self.memory[-1].get("sensor_data", {}):
            return AgentAction(action_type="heal", priority=10)
        return None
    
    async def act(self, action: AgentAction) -> bool:
        try:
            self.state = AgentState.ACTIVE
            if action.action_type == "heal":
                self.state = AgentState.HEALING
                await asyncio.sleep(0.1)
            self.state = AgentState.IDLE
            return True
        except Exception as e:
            logger.error(f"Action failed: {e}")
            return False

class AutonomousAgentSystem:
    def __init__(self, num_agents: int = 4):
        self.agents = {f"agent-{i}": AutonomousAgent(f"agent-{i}") for i in range(num_agents)}
        logger.info(f"System with {num_agents} agents initialized")
    
    async def run_cycle(self) -> Dict:
        results = {}
        for agent_id, agent in self.agents.items():
            if action := await agent.decide():
                results[agent_id] = {"action": action.action_type, "success": await agent.act(action)}
        return results
    
    def get_status(self) -> Dict:
        return {"agents": len(self.agents), "statuses": [a.state.value for a in self.agents.values()]}
