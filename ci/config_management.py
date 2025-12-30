config_management.py"""Configuration Management System for dynamic config handling."""
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigLevel(Enum):
    DEFAULT, ENV, USER, SYSTEM = 1, 2, 3, 4

@dataclass
class ConfigValue:
    value: Any
    level: ConfigLevel
    updated_at: datetime
    mutable: bool = True

class ConfigManager:
    def __init__(self, name: str = "Config-001"):
        self.name = name
        self.configs: Dict[str, ConfigValue] = {}
        self.defaults: Dict[str, Any] = {}
        self.validators: Dict[str, callable] = {}
        logger.info(f"Config Manager {name} initialized")
    
    def set_default(self, key: str, value: Any) -> None:
        self.defaults[key] = value
        self.configs[key] = ConfigValue(value, ConfigLevel.DEFAULT, datetime.now())
    
    def set(self, key: str, value: Any, level: ConfigLevel = ConfigLevel.USER,
            mutable: bool = True) -> bool:
        if key in self.configs:
            if not self.configs[key].mutable:
                logger.warning(f"Config {key} is immutable")
                return False
        self.configs[key] = ConfigValue(value, level, datetime.now(), mutable)
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        if key in self.configs:
            return self.configs[key].value
        return default
    
    def register_validator(self, key: str, validator: callable) -> None:
        self.validators[key] = validator
    
    def validate(self, key: str, value: Any) -> bool:
        if key in self.validators:
            return self.validators[key](value)
        return True
    
    def get_all(self) -> Dict[str, Any]:
        return {k: v.value for k, v in self.configs.items()}
    
    def export(self) -> str:
        return json.dumps(self.get_all(), default=str)
    
    def import_config(self, json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            for key, value in data.items():
                self.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
