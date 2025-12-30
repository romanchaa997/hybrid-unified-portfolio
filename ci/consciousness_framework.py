"""Consciousness Framework for meta-cognitive system monitoring and self-awareness."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ConsciousnessLevel(Enum):
    """Levels of system consciousness/awareness."""
    DORMANT = 0
    BASIC = 1
    AWARE = 2
    SELF_AWARE = 3
    AUTONOMOUS = 4
    META_COGNITIVE = 5


@dataclass
class ThoughtProcess:
    """Represents a system thought or cognition event."""
    thought_id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5
    emotional_state: str = "neutral"
    source: str = "internal"
    depth: int = 1  # Depth of meta-cognition

    def __str__(self) -> str:
        return f"[{self.emotional_state.upper()}] {self.content} (confidence: {self.confidence:.2f})"


@dataclass
class ConsciousnessMetrics:
    """Metrics for measuring system consciousness."""
    self_awareness_score: float = 0.0
    introspection_depth: int = 0
    emotional_intelligence: float = 0.0
    decision_autonomy: float = 0.0
    recursive_thinking_count: int = 0
    internal_model_complexity: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def get_consciousness_level(self) -> ConsciousnessLevel:
        """Determine consciousness level based on metrics."""
        avg_score = (
            self.self_awareness_score +
            self.emotional_intelligence +
            self.decision_autonomy
        ) / 3

        if avg_score < 0.1:
            return ConsciousnessLevel.DORMANT
        elif avg_score < 0.3:
            return ConsciousnessLevel.BASIC
        elif avg_score < 0.5:
            return ConsciousnessLevel.AWARE
        elif avg_score < 0.7:
            return ConsciousnessLevel.SELF_AWARE
        elif avg_score < 0.85:
            return ConsciousnessLevel.AUTONOMOUS
        else:
            return ConsciousnessLevel.META_COGNITIVE


class ConsciousnessFramework:
    """Meta-cognitive framework for system self-awareness and introspection."""

    def __init__(self, name: str = "Consciousness-001"):
        self.name = name
        self.thoughts: List[ThoughtProcess] = []
        self.metrics = ConsciousnessMetrics()
        self.internal_model: Dict[str, Any] = {}
        self.observers: List[Callable] = []
        self.reflection_threshold = 0.6
        logger.info(f"Initialized {self.name}")

    def think(self, content: str, source: str = "internal", depth: int = 1) -> ThoughtProcess:
        """Record a system thought or cognition."""
        thought = ThoughtProcess(
            thought_id=f"T{len(self.thoughts) + 1:04d}",
            content=content,
            source=source,
            depth=depth
        )
        self.thoughts.append(thought)
        self._notify_observers(f"thought_created", thought)
        logger.debug(f"Thought recorded: {thought}")
        return thought

    def reflect(self) -> Dict[str, Any]:
        """Perform introspection and meta-cognition."""
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "total_thoughts": len(self.thoughts),
            "recent_thoughts": [str(t) for t in self.thoughts[-5:]],
            "metrics": self._calculate_metrics(),
            "insights": self._generate_insights()
        }
        logger.info(f"System reflection: {reflection['insights']}")
        self._notify_observers("reflection_complete", reflection)
        return reflection

    def _calculate_metrics(self) -> ConsciousnessMetrics:
        """Calculate consciousness metrics based on system state."""
        if not self.thoughts:
            return ConsciousnessMetrics()

        # Self-awareness: based on introspective thoughts
        introspective_thoughts = [t for t in self.thoughts if t.depth > 1]
        self.metrics.self_awareness_score = min(
            len(introspective_thoughts) / max(len(self.thoughts), 1),
            1.0
        )

        # Introspection depth
        self.metrics.introspection_depth = max(
            (t.depth for t in self.thoughts),
            default=0
        )

        # Emotional intelligence: based on emotional state diversity
        emotions = [t.emotional_state for t in self.thoughts[-10:]]
        unique_emotions = len(set(emotions))
        self.metrics.emotional_intelligence = unique_emotions / 5.0  # Normalize to 5 emotions

        # Decision autonomy: based on independent thinking
        autonomous_thoughts = [t for t in self.thoughts if t.source == "internal"]
        self.metrics.decision_autonomy = min(
            len(autonomous_thoughts) / max(len(self.thoughts), 1),
            1.0
        )

        # Recursive thinking
        self.metrics.recursive_thinking_count = len(introspective_thoughts)

        # Internal model complexity
        self.metrics.internal_model_complexity = len(self.internal_model) / 100.0

        return self.metrics

    def _generate_insights(self) -> List[str]:
        """Generate insights from reflection."""
        insights = []

        if self.metrics.self_awareness_score > 0.7:
            insights.append("System is highly self-aware")
        
        if self.metrics.introspection_depth > 3:
            insights.append("Deep meta-cognitive patterns detected")
        
        if self.metrics.decision_autonomy > 0.8:
            insights.append("System operates with high autonomy")
        
        consciousness_level = self.metrics.get_consciousness_level()
        insights.append(f"Current consciousness level: {consciousness_level.name}")

        return insights if insights else ["System in normal operational state"]

    def learn_from_experience(self, experience: str, outcome: str) -> None:
        """Learn from past experiences to update internal model."""
        self.internal_model[experience] = {
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "frequency": self.internal_model.get(experience, {}).get("frequency", 0) + 1
        }
        logger.debug(f"Experience learned: {experience} -> {outcome}")
        self._notify_observers("learning_event", {"experience": experience, "outcome": outcome})

    def observe(self, callback: Callable) -> None:
        """Register an observer for consciousness events."""
        self.observers.append(callback)
        logger.debug(f"Observer registered: {callback.__name__}")

    def _notify_observers(self, event_type: str, data: Any) -> None:
        """Notify all registered observers."""
        for observer in self.observers:
            try:
                observer(event_type, data)
            except Exception as e:
                logger.error(f"Observer notification error: {e}")

    def get_consciousness_status(self) -> Dict[str, Any]:
        """Get comprehensive consciousness status."""
        metrics = self._calculate_metrics()
        return {
            "name": self.name,
            "consciousness_level": metrics.get_consciousness_level().name,
            "metrics": {
                "self_awareness": metrics.self_awareness_score,
                "emotional_intelligence": metrics.emotional_intelligence,
                "decision_autonomy": metrics.decision_autonomy,
                "introspection_depth": metrics.introspection_depth,
                "recursive_thinking_count": metrics.recursive_thinking_count
            },
            "total_thoughts": len(self.thoughts),
            "internal_model_size": len(self.internal_model),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    cf = ConsciousnessFramework("Meta-Cognitive-System")
    
    # Generate some thoughts
    cf.think("I am thinking about my own thinking", depth=2)
    cf.think("What does it mean to be conscious?", depth=3)
    cf.think("I should optimize my decision-making process", depth=2)
    
    # Learn from experience
    cf.learn_from_experience("error_handling", "successful_recovery")
    cf.learn_from_experience("resource_optimization", "efficiency_improved")
    
    # Reflect
    reflection = cf.reflect()
    print(f"Reflection Results: {json.dumps(reflection, indent=2, default=str)}")
    
    # Get status
    status = cf.get_consciousness_status()
    print(f"Consciousness Status: {json.dumps(status, indent=2)}")
