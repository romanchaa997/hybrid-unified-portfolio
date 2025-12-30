#!/usr/bin/env python3
"""Alerting System: Real-time system health monitoring and alerts.

Monitors critical system metrics and triggers alerts for:
- Low battery conditions
- High CPU/memory usage
- Disk space warnings
- Network issues
- Task failures
- Energy threshold violations
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable
import json

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertChannel(Enum):
    """Alert delivery channels."""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SMS = "sms"

@dataclass
class Alert:
    """System alert."""
    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    category: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    source_metric: str = ""
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            'id': self.alert_id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'source_metric': self.source_metric,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
        }

class AlertRule:
    """Rule for triggering alerts."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        metric: str,
        condition: str,  # 'gt', 'lt', 'eq', 'between'
        threshold: float,
        severity: AlertSeverity,
        category: str,
        cooldown: int = 300  # seconds
    ):
        self.rule_id = rule_id
        self.name = name
        self.metric = metric
        self.condition = condition
        self.threshold = threshold
        self.severity = severity
        self.category = category
        self.cooldown = cooldown
        self.last_triggered: Optional[datetime] = None
    
    def should_trigger(self, metric_value: float) -> bool:
        """Check if rule should trigger."""
        now = datetime.now()
        
        # Check cooldown
        if self.last_triggered:
            if (now - self.last_triggered).total_seconds() < self.cooldown:
                return False
        
        # Check condition
        if self.condition == 'gt':
            return metric_value > self.threshold
        elif self.condition == 'lt':
            return metric_value < self.threshold
        elif self.condition == 'eq':
            return metric_value == self.threshold
        elif self.condition == 'gte':
            return metric_value >= self.threshold
        elif self.condition == 'lte':
            return metric_value <= self.threshold
        
        return False
    
    def mark_triggered(self):
        """Mark rule as triggered."""
        self.last_triggered = datetime.now()

class AlertingSystem:
    """Central alerting system."""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.max_alerts = 1000
        self.handlers: Dict[AlertChannel, List[Callable]] = {}
        self.initialized = False
    
    def register_rule(self, rule: AlertRule) -> None:
        """Register alert rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Alert rule registered: {rule.name}")
    
    def register_handler(
        self,
        channel: AlertChannel,
        handler: Callable
    ) -> None:
        """Register alert handler for channel."""
        if channel not in self.handlers:
            self.handlers[channel] = []
        self.handlers[channel].append(handler)
        logger.info(f"Handler registered for channel: {channel.value}")
    
    async def check_metrics(self, metrics: Dict) -> None:
        """Check metrics against alert rules."""
        cpu_percent = metrics.get('cpu', {}).get('percent', 0)
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        battery_percent = metrics.get('battery', {}).get('capacity', 100)
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        
        # Check predefined rules
        checks = [
            (cpu_percent, 'cpu'),
            (memory_percent, 'memory'),
            (battery_percent, 'battery'),
            (disk_percent, 'disk'),
        ]
        
        for value, metric_name in checks:
            for rule in self.rules.values():
                if rule.metric == metric_name and rule.should_trigger(value):
                    alert = self._create_alert(rule, value)
                    await self.trigger_alert(alert)
    
    def _create_alert(self, rule: AlertRule, metric_value: float) -> Alert:
        """Create alert from triggered rule."""
        import uuid
        alert_id = str(uuid.uuid4())[:8]
        
        alert = Alert(
            alert_id=alert_id,
            title=rule.name,
            message=f"Alert: {rule.name} triggered. {rule.metric}={metric_value:.2f}, threshold={rule.threshold}",
            severity=rule.severity,
            category=rule.category,
            source_metric=rule.metric,
            metric_value=metric_value,
            threshold=rule.threshold,
        )
        
        rule.mark_triggered()
        return alert
    
    async def trigger_alert(self, alert: Alert) -> None:
        """Trigger an alert."""
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        if len(self.alert_history) > self.max_alerts:
            self.alert_history.pop(0)
        
        logger.log(
            logging.CRITICAL if alert.severity == AlertSeverity.CRITICAL else logging.WARNING,
            f"Alert [{alert.severity.value.upper()}] {alert.title}: {alert.message}"
        )
        
        # Emit to handlers
        await self._emit_alert(alert)
    
    async def _emit_alert(self, alert: Alert) -> None:
        """Emit alert to registered handlers."""
        for channel, handlers in self.handlers.items():
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler ({channel.value}): {e}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts."""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level."""
        return [a for a in self.alerts if a.severity == severity]
    
    def clear_acknowledged_alerts(self) -> int:
        """Clear acknowledged alerts from active list."""
        count = len([a for a in self.alerts if a.acknowledged])
        self.alerts = [a for a in self.alerts if not a.acknowledged]
        return count

# Built-in handlers
async def log_handler(alert: Alert) -> None:
    """Log alert to file."""
    logger.warning(f"[{alert.severity.value}] {alert.title}: {alert.message}")

async def webhook_handler(alert: Alert, webhook_url: str) -> None:
    """Send alert to webhook."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook_url,
                json=alert.to_dict(),
                timeout=5.0
            )
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")

async def email_handler(alert: Alert, recipients: List[str]) -> None:
    """Send alert via email."""
    logger.info(f"Would send email alert to {recipients}: {alert.title}")

async def slack_handler(alert: Alert, webhook_url: str) -> None:
    """Send alert to Slack."""
    try:
        import httpx
        color = "danger" if alert.severity == AlertSeverity.CRITICAL else "warning"
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value, "short": True},
                        {"title": "Category", "value": alert.category, "short": True},
                    ],
                    "ts": int(alert.timestamp.timestamp()),
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload, timeout=5.0)
    except Exception as e:
        logger.error(f"Slack handler error: {e}")

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    system = AlertingSystem()
    
    # Register alert rules
    system.register_rule(
        AlertRule(
            "cpu_high",
            "High CPU Usage",
            "cpu",
            "gt",
            80.0,
            AlertSeverity.WARNING,
            "performance"
        )
    )
    
    system.register_rule(
        AlertRule(
            "memory_critical",
            "Critical Memory Usage",
            "memory",
            "gt",
            90.0,
            AlertSeverity.CRITICAL,
            "performance"
        )
    )
    
    system.register_rule(
        AlertRule(
            "battery_low",
            "Low Battery",
            "battery",
            "lt",
            20.0,
            AlertSeverity.WARNING,
            "hardware"
        )
    )
    
    system.register_rule(
        AlertRule(
            "battery_critical",
            "Critical Battery",
            "battery",
            "lt",
            5.0,
            AlertSeverity.CRITICAL,
            "hardware"
        )
    )
    
    # Register handlers
    system.register_handler(AlertChannel.LOG, log_handler)
    
    logger.info("Alerting system initialized")
    
    # Example: Check metrics
    test_metrics = {
        'cpu': {'percent': 45.2},
        'memory': {'percent': 60.5},
        'battery': {'capacity': 15},
        'disk': {'percent': 75.3},
    }
    
    await system.check_metrics(test_metrics)
    print(f"Active alerts: {len(system.get_active_alerts())}")

if __name__ == "__main__":
    asyncio.run(main())
