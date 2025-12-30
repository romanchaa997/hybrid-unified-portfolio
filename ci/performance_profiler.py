#!/usr/bin/env python3
"""Performance Profiler: Deep system analysis and trend detection.

Monitors:
- Per-core CPU metrics and thermal data
- Memory fragmentation and allocation patterns
- Process-level resource usage
- I/O operations and disk performance
- Power consumption trends
- Performance degradation detection
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

@dataclass
class CoreMetrics:
    """Per-core CPU metrics."""
    core_id: int
    usage_percent: float
    frequency_mhz: float
    temperature: Optional[float] = None
    load: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ThermalZone:
    """Thermal zone information."""
    zone_id: str
    name: str
    temperature: float
    max_temp: float
    crit_temp: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceProfiler:
    """Deep performance analysis system."""
    
    def __init__(self):
        self.core_metrics: Dict[int, CoreMetrics] = {}
        self.thermal_zones: Dict[str, ThermalZone] = {}
        self.metrics_history: List[Dict] = []
        self.max_history = 2000
        self.degradation_detected = False
        self.performance_baseline: Optional[float] = None
    
    async def profile_cpu_cores(self) -> Dict[int, CoreMetrics]:
        """Profile individual CPU cores."""
        try:
            import psutil
            
            core_count = psutil.cpu_count(logical=False) or 1
            cpu_freq = psutil.cpu_freq(percpu=True) if hasattr(psutil, 'cpu_freq') else []
            
            for i in range(psutil.cpu_count(logical=True) or 1):
                try:
                    # Get per-core usage (requires Linux /proc/stat)
                    cpu_usage = psutil.cpu_percent(interval=0.1, percpu=True)[i] if i < len(psutil.cpu_percent(percpu=True)) else 0
                    
                    freq = cpu_freq[i].current if i < len(cpu_freq) else 0
                    
                    self.core_metrics[i] = CoreMetrics(
                        core_id=i,
                        usage_percent=cpu_usage,
                        frequency_mhz=freq,
                        temperature=self._get_core_temperature(i)
                    )
                except Exception as e:
                    logger.debug(f"Error profiling core {i}: {e}")
            
            return self.core_metrics
        except Exception as e:
            logger.error(f"CPU profiling error: {e}")
            return {}
    
    def _get_core_temperature(self, core_id: int) -> Optional[float]:
        """Get temperature for a specific core."""
        try:
            # Try reading from /sys/class/thermal
            thermal_path = f"/sys/class/thermal/thermal_zone{core_id}/temp"
            try:
                with open(thermal_path) as f:
                    temp_milli = int(f.read().strip())
                    return temp_milli / 1000.0
            except:
                # Try psutil if available
                try:
                    import psutil
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, readings in temps.items():
                            if core_id < len(readings):
                                return readings[core_id].current
                except:
                    pass
        except Exception as e:
            logger.debug(f"Thermal reading error for core {core_id}: {e}")
        return None
    
    async def profile_memory(self) -> Dict:
        """Profile memory usage and fragmentation."""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'physical': {
                    'total': memory.total,
                    'used': memory.used,
                    'available': memory.available,
                    'percent': memory.percent,
                    'active': getattr(memory, 'active', 0),
                    'inactive': getattr(memory, 'inactive', 0),
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent,
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Memory profiling error: {e}")
            return {}
    
    async def detect_thermal_zones(self) -> Dict[str, ThermalZone]:
        """Detect and profile thermal zones."""
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            
            for zone_name, readings in temps.items():
                for i, reading in enumerate(readings):
                    zone_id = f"{zone_name}_{i}"
                    self.thermal_zones[zone_id] = ThermalZone(
                        zone_id=zone_id,
                        name=reading.label or f"{zone_name}_{i}",
                        temperature=reading.current,
                        max_temp=reading.high or 100,
                        crit_temp=reading.critical
                    )
            
            return self.thermal_zones
        except Exception as e:
            logger.debug(f"Thermal zone detection error: {e}")
            return {}
    
    async def detect_performance_degradation(self) -> bool:
        """Detect CPU throttling or performance degradation."""
        try:
            if not self.performance_baseline:
                # Set baseline
                import psutil
                self.performance_baseline = psutil.cpu_freq().max if hasattr(psutil, 'cpu_freq') else 3000
                return False
            
            # Check current frequency against baseline
            import psutil
            current_freq = psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') else 3000
            degradation_ratio = current_freq / self.performance_baseline
            
            # If running at <80% of baseline, flag degradation
            if degradation_ratio < 0.8:
                self.degradation_detected = True
                logger.warning(f"Performance degradation detected: {degradation_ratio*100:.1f}% of baseline")
                return True
            
            self.degradation_detected = False
            return False
        except Exception as e:
            logger.error(f"Degradation detection error: {e}")
            return False
    
    async def get_full_profile(self) -> Dict:
        """Get complete system profile."""
        profile = {
            'timestamp': datetime.now().isoformat(),
            'cores': {str(cid): {
                'usage': m.usage_percent,
                'frequency_mhz': m.frequency_mhz,
                'temperature': m.temperature
            } for cid, m in self.core_metrics.items()},
            'memory': await self.profile_memory(),
            'thermal_zones': {zid: {
                'name': z.name,
                'temp': z.temperature,
                'max': z.max_temp
            } for zid, z in self.thermal_zones.items()},
            'degradation_detected': await self.detect_performance_degradation()
        }
        
        self.metrics_history.append(profile)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        return profile

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    profiler = PerformanceProfiler()
    
    logger.info("Starting performance profiler")
    
    # Get initial profile
    await profiler.profile_cpu_cores()
    await profiler.detect_thermal_zones()
    profile = await profiler.get_full_profile()
    
    print(json.dumps(profile, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
