"""Monitoring and Observability Stack for metrics, tracing, and logging."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Span:
    trace_id: str
    span_id: str
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str
    context: Dict = field(default_factory=dict)
    trace_id: Optional[str] = None

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.history: List[Metric] = []
    
    def record_metric(self, name: str, value: float, metric_type: MetricType,
                     labels: Optional[Dict[str, str]] = None) -> None:
        metric = Metric(name, metric_type, value, labels=labels or {})
        self.metrics[name] = metric
        self.history.append(metric)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        return self.metrics.get(name)
    
    def get_histogram(self, name: str, time_window_seconds: int = 300) -> Dict:
        cutoff = time.time() - time_window_seconds
        relevant = [m for m in self.history if (m.timestamp.timestamp() > cutoff) and m.name == name]
        values = [m.value for m in relevant]
        return {"count": len(values), "sum": sum(values),
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0}

class TracingSystem:
    def __init__(self):
        self.spans: Dict[str, List[Span]] = {}
        self.current_span_stack = []
    
    def start_span(self, trace_id: str, operation_name: str) -> Span:
        span_id = f"span-{len(self.current_span_stack)}"
        span = Span(trace_id, span_id, operation_name, time.time())
        self.current_span_stack.append(span)
        if trace_id not in self.spans:
            self.spans[trace_id] = []
        self.spans[trace_id].append(span)
        return span
    
    def end_span(self) -> Optional[Span]:
        if self.current_span_stack:
            span = self.current_span_stack.pop()
            span.end_time = time.time()
            return span
        return None
    
    def add_tag(self, key: str, value: str) -> None:
        if self.current_span_stack:
            self.current_span_stack[-1].tags[key] = value
    
    def get_trace(self, trace_id: str) -> Optional[List[Span]]:
        return self.spans.get(trace_id)

class LogAggregator:
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.levels_count: Dict[str, int] = {}
    
    def log(self, level: str, message: str, context: Optional[Dict] = None,
            trace_id: Optional[str] = None) -> None:
        entry = LogEntry(datetime.now(), level, message, context or {}, trace_id)
        self.logs.append(entry)
        self.levels_count[level] = self.levels_count.get(level, 0) + 1
    
    def get_logs_by_level(self, level: str) -> List[LogEntry]:
        return [log for log in self.logs if log.level == level]
    
    def get_trace_logs(self, trace_id: str) -> List[LogEntry]:
        return [log for log in self.logs if log.trace_id == trace_id]

class ObservabilityStack:
    def __init__(self, name: str = "Observability-001"):
        self.name = name
        self.metrics = MetricsCollector()
        self.tracer = TracingSystem()
        self.logger = LogAggregator()
        logger.info(f"Observability Stack {name} initialized")
    
    def get_health_status(self) -> Dict:
        return {"name": self.name, "metrics_count": len(self.metrics.metrics),
                "traces_count": len(self.tracer.spans), "logs_count": len(self.logger.logs),
                "log_levels": self.logger.levels_count}
