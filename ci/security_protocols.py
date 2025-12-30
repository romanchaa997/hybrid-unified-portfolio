"""Security Protocols for system defense and threat mitigation."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import hashlib
import hmac

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW, MEDIUM, HIGH, CRITICAL = 1, 2, 3, 4

@dataclass
class SecurityEvent:
    event_id: str
    event_type: str
    threat_level: ThreatLevel
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict = field(default_factory=dict)
    mitigated: bool = False

class AccessControl:
    def __init__(self):
        self.users = {}
        self.permissions = {}
        logger.info("Access Control initialized")
    
    def create_user(self, user_id: str, role: str) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = {"role": role, "created": datetime.now()}
        self.permissions[user_id] = self._get_role_permissions(role)
        return True
    
    def _get_role_permissions(self, role: str) -> List[str]:
        roles = {"admin": ["read", "write", "delete", "execute"],
                 "user": ["read", "write"],
                 "guest": ["read"]}
        return roles.get(role, [])
    
    def check_permission(self, user_id: str, action: str) -> bool:
        return action in self.permissions.get(user_id, [])

class EncryptionManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        logger.info("Encryption Manager initialized")
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return self.hash_password(password) == hashed
    
    def create_hmac(self, data: str) -> str:
        return hmac.new(self.secret_key, data.encode(), hashlib.sha256).hexdigest()

class SecurityProtocolSystem:
    def __init__(self, secret_key: str = "default-key"):
        self.access_control = AccessControl()
        self.encryption = EncryptionManager(secret_key)
        self.security_events: List[SecurityEvent] = []
        self.threat_counters = {}
        logger.info("Security Protocol System initialized")
    
    def detect_threat(self, event_type: str, details: Dict) -> Optional[SecurityEvent]:
        threat_level = self._assess_threat(event_type)
        event = SecurityEvent(f"event-{len(self.security_events)}", event_type, threat_level, details=details)
        self.security_events.append(event)
        
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._mitigate_threat(event)
            event.mitigated = True
        
        logger.warning(f"Threat detected: {event_type} - {threat_level.name}")
        return event
    
    def _assess_threat(self, event_type: str) -> ThreatLevel:
        threats = {"unauthorized_access": ThreatLevel.CRITICAL, "invalid_token": ThreatLevel.HIGH,
                   "unusual_activity": ThreatLevel.MEDIUM, "deprecated_api": ThreatLevel.LOW}
        return threats.get(event_type, ThreatLevel.LOW)
    
    def _mitigate_threat(self, event: SecurityEvent) -> None:
        logger.critical(f"Mitigating threat: {event.event_type}")
    
    def get_security_status(self) -> Dict:
        return {"total_events": len(self.security_events),
                "mitigated_events": sum(1 for e in self.security_events if e.mitigated),
                "threat_summary": self._get_threat_summary()}
    
    def _get_threat_summary(self) -> Dict:
        return {level.name: sum(1 for e in self.security_events if e.threat_level == level)
                for level in ThreatLevel}

if __name__ == "__main__":
    sec = SecurityProtocolSystem()
    sec.access_control.create_user("admin", "admin")
    event = sec.detect_threat("unauthorized_access", {"ip": "192.168.1.1"})
    print(f"Status: {sec.get_security_status()}")
