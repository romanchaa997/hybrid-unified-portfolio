#!/usr/bin/env python3
"""Battery Monitor: Real-time system power state tracking.

Monitors /proc/acpi/battery and /proc/acpi/ac_adapter for:
- Battery percentage and status
- Discharge/charge rate
- Remaining time estimation
- AC adapter connection status
- Energy thresholds for alerting
"""

import os
import re
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class BatteryState:
    """Battery state information."""
    capacity: int  # 0-100%
    charge_rate: float  # mA
    discharge_rate: float  # mA
    remaining_time: timedelta
    status: str  # Charging, Discharging, Full, Unknown
    temperature: float  # Celsius
    voltage: float  # mV
    current: float  # mA
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_critical(self) -> bool:
        """Check if battery is in critical state."""
        return self.capacity <= 5
    
    @property
    def is_low(self) -> bool:
        """Check if battery is low."""
        return self.capacity <= 20
    
    @property
    def is_healthy(self) -> bool:
        """Check if battery is healthy."""
        return self.capacity >= 80 and self.status != "Full"

@dataclass
class ACAdapterState:
    """AC adapter state information."""
    connected: bool
    power_level: Optional[float] = None  # Watts
    timestamp: datetime = field(default_factory=datetime.now)

class BatteryMonitor:
    """Monitor system battery and power state."""
    
    BATTERY_PATH = Path("/proc/acpi/battery")
    AC_ADAPTER_PATH = Path("/proc/acpi/ac_adapter")
    
    def __init__(self):
        self.battery_state: Optional[BatteryState] = None
        self.ac_adapter_state: Optional[ACAdapterState] = None
        self.history: list[BatteryState] = []
        self.max_history = 1000
        
    async def read_battery_info(self, battery_name: str = "BAT0") -> Optional[Dict[str, str]]:
        """Read battery info from /proc/acpi/battery."""
        try:
            battery_file = self.BATTERY_PATH / battery_name / "info"
            if not battery_file.exists():
                logger.warning(f"Battery file not found: {battery_file}")
                return None
                
            with open(battery_file, 'r') as f:
                content = f.read()
            
            info = {}
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower()] = value.strip()
            return info
        except Exception as e:
            logger.error(f"Error reading battery info: {e}")
            return None
    
    async def read_battery_state(self, battery_name: str = "BAT0") -> Optional[Dict[str, str]]:
        """Read battery state from /proc/acpi/battery."""
        try:
            state_file = self.BATTERY_PATH / battery_name / "state"
            if not state_file.exists():
                logger.warning(f"Battery state file not found: {state_file}")
                return None
                
            with open(state_file, 'r') as f:
                content = f.read()
            
            state = {}
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    state[key.strip().lower()] = value.strip()
            return state
        except Exception as e:
            logger.error(f"Error reading battery state: {e}")
            return None
    
    async def read_ac_adapter_status(self, adapter_name: str = "ACAD") -> Optional[Dict[str, str]]:
        """Read AC adapter status from /proc/acpi/ac_adapter."""
        try:
            adapter_file = self.AC_ADAPTER_PATH / adapter_name / "state"
            if not adapter_file.exists():
                logger.warning(f"AC adapter file not found: {adapter_file}")
                return None
                
            with open(adapter_file, 'r') as f:
                content = f.read()
            
            state = {}
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    state[key.strip().lower()] = value.strip()
            return state
        except Exception as e:
            logger.error(f"Error reading AC adapter: {e}")
            return None
    
    def _extract_int(self, value: str) -> int:
        """Extract integer from value string."""
        match = re.search(r'\d+', value)
        return int(match.group()) if match else 0
    
    def _extract_float(self, value: str) -> float:
        """Extract float from value string."""
        match = re.search(r'\d+\.?\d*', value)
        return float(match.group()) if match else 0.0
    
    async def update_battery_state(self, battery_name: str = "BAT0") -> None:
        """Update current battery state."""
        info = await self.read_battery_info(battery_name)
        state = await self.read_battery_state(battery_name)
        
        if not state:
            return
        
        # Parse state values
        capacity_percent = self._extract_int(state.get('remaining capacity', '0'))
        if info:
            capacity_percent = int((capacity_percent / self._extract_int(info.get('design capacity', '100'))) * 100)
        
        present_rate = self._extract_int(state.get('present rate', '0'))
        remaining_capacity = self._extract_int(state.get('remaining capacity', '0'))
        current_voltage = self._extract_int(state.get('present voltage', '12000')) / 1000  # Convert to V
        
        # Calculate remaining time
        if present_rate > 0:
            hours = remaining_capacity / present_rate if present_rate > 0 else 0
            remaining_time = timedelta(hours=hours)
        else:
            remaining_time = timedelta(0)
        
        battery_status = state.get('charging state', 'Unknown').strip()
        
        self.battery_state = BatteryState(
            capacity=capacity_percent,
            charge_rate=present_rate if battery_status == 'charging' else 0,
            discharge_rate=present_rate if battery_status == 'discharging' else 0,
            remaining_time=remaining_time,
            status=battery_status,
            temperature=self._extract_float(state.get('temperature', '25')),
            voltage=current_voltage,
            current=present_rate
        )
        
        # Keep history
        self.history.append(self.battery_state)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    async def update_ac_adapter_state(self, adapter_name: str = "ACAD") -> None:
        """Update AC adapter state."""
        adapter = await self.read_ac_adapter_status(adapter_name)
        
        if not adapter:
            return
        
        state_value = adapter.get('state', 'off-line').strip().lower()
        self.ac_adapter_state = ACAdapterState(
            connected=state_value == 'on-line'
        )
    
    async def get_power_metrics(self) -> Dict:
        """Get current power metrics."""
        await self.update_battery_state()
        await self.update_ac_adapter_state()
        
        return {
            'battery': {
                'capacity': self.battery_state.capacity if self.battery_state else 0,
                'status': self.battery_state.status if self.battery_state else 'Unknown',
                'remaining_time': str(self.battery_state.remaining_time) if self.battery_state else None,
                'discharge_rate': self.battery_state.discharge_rate if self.battery_state else 0,
                'charge_rate': self.battery_state.charge_rate if self.battery_state else 0,
                'temperature': self.battery_state.temperature if self.battery_state else 0,
                'is_critical': self.battery_state.is_critical if self.battery_state else False,
                'is_low': self.battery_state.is_low if self.battery_state else False,
            },
            'ac_adapter': {
                'connected': self.ac_adapter_state.connected if self.ac_adapter_state else False,
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def monitor_continuous(self, interval: int = 10) -> None:
        """Continuously monitor battery state."""
        logger.info(f"Starting battery monitor with {interval}s interval")
        
        while True:
            try:
                metrics = await self.get_power_metrics()
                
                # Log critical states
                if metrics['battery']['is_critical']:
                    logger.critical(f"CRITICAL BATTERY: {metrics['battery']['capacity']}%")
                elif metrics['battery']['is_low']:
                    logger.warning(f"LOW BATTERY: {metrics['battery']['capacity']}%")
                else:
                    logger.debug(f"Battery: {metrics['battery']['capacity']}% | AC: {metrics['ac_adapter']['connected']}")
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in battery monitor: {e}")
                await asyncio.sleep(interval)

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    monitor = BatteryMonitor()
    
    # Get initial metrics
    metrics = await monitor.get_power_metrics()
    print(json.dumps(metrics, indent=2, default=str))
    
    # Start continuous monitoring
    try:
        await monitor.monitor_continuous(interval=10)
    except KeyboardInterrupt:
        logger.info("Battery monitor stopped")

if __name__ == "__main__":
    asyncio.run(main())
