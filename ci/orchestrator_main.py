#!/usr/bin/env python3
"""Orchestrator Main: Central hub coordinating all Phase 2+ components.

Integrates:
- BatteryMonitor for power state tracking
- ManusClient for project management
- WebhookHandler for incoming events
- AlertingSystem for health monitoring
- WebDashboard for metrics visualization
- PerformanceProfiler for deep analysis
- EnergyOptimizer for battery optimization
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """Central orchestration hub for all system components."""
    
    def __init__(self):
        self.battery_monitor = None
        self.manus_client = None
        self.webhook_handler = None
        self.alerting_system = None
        self.web_dashboard = None
        self.performance_profiler = None
        self.energy_optimizer = None
        self.is_running = False
        self.components_status: Dict[str, bool] = {}
        self.start_time = None
    
    async def initialize_components(self) -> None:
        """Initialize all system components."""
        logger.info("Initializing system components...")
        
        # Dynamic imports to avoid circular dependencies
        try:
            from battery_monitor import BatteryMonitor
            self.battery_monitor = BatteryMonitor()
            self.components_status['battery_monitor'] = True
            logger.info("✓ BatteryMonitor initialized")
        except Exception as e:
            logger.error(f"✗ BatteryMonitor initialization failed: {e}")
            self.components_status['battery_monitor'] = False
        
        try:
            from manus_client import ManusClient
            self.manus_client = ManusClient(
                api_key="",  # Load from env in production
                base_url="https://api.manus.im"
            )
            self.components_status['manus_client'] = True
            logger.info("✓ ManusClient initialized")
        except Exception as e:
            logger.error(f"✗ ManusClient initialization failed: {e}")
            self.components_status['manus_client'] = False
        
        try:
            from webhook_handler import WebhookHandler
            self.webhook_handler = WebhookHandler(secret_key="")
            self.components_status['webhook_handler'] = True
            logger.info("✓ WebhookHandler initialized")
        except Exception as e:
            logger.error(f"✗ WebhookHandler initialization failed: {e}")
            self.components_status['webhook_handler'] = False
        
        try:
            from alerting_system import AlertingSystem
            self.alerting_system = AlertingSystem()
            self.components_status['alerting_system'] = True
            logger.info("✓ AlertingSystem initialized")
        except Exception as e:
            logger.error(f"✗ AlertingSystem initialization failed: {e}")
            self.components_status['alerting_system'] = False
        
        try:
            from web_dashboard import DashboardApp
            self.web_dashboard = DashboardApp()
            self.components_status['web_dashboard'] = True
            logger.info("✓ WebDashboard initialized")
        except Exception as e:
            logger.error(f"✗ WebDashboard initialization failed: {e}")
            self.components_status['web_dashboard'] = False
    
    async def start_all_services(self) -> None:
        """Start all services in parallel."""
        self.is_running = True
        self.start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("STARTING HYBRID UNIFIED PORTFOLIO ORCHESTRATION SYSTEM")
        logger.info(f"Start Time: {self.start_time}")
        logger.info("=" * 60)
        
        await self.initialize_components()
        
        # Create tasks for all services
        tasks = []
        
        # Monitor battery continuously
        if self.battery_monitor:
            tasks.append(
                asyncio.create_task(
                    self._monitor_battery_loop(),
                    name="battery_monitor"
                )
            )
        
        # Start webhook server
        if self.webhook_handler:
            tasks.append(
                asyncio.create_task(
                    self.webhook_handler.start(host="127.0.0.1", port=8001),
                    name="webhook_handler"
                )
            )
        
        # Start web dashboard
        if self.web_dashboard:
            tasks.append(
                asyncio.create_task(
                    self.web_dashboard.start(host="0.0.0.0", port=8000),
                    name="web_dashboard"
                )
            )
        
        # Health check loop
        tasks.append(
            asyncio.create_task(
                self._health_check_loop(),
                name="health_check"
            )
        )
        
        logger.info(f"Started {len(tasks)} services in parallel")
        
        try:
            # Run all tasks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            await self.shutdown()
    
    async def _monitor_battery_loop(self) -> None:
        """Continuous battery monitoring loop."""
        logger.info("Battery monitor loop started")
        interval = 10
        
        while self.is_running:
            try:
                metrics = await self.battery_monitor.get_power_metrics()
                battery_capacity = metrics['battery']['capacity']
                is_charging = metrics['battery']['status'] == 'Charging'
                
                logger.debug(
                    f"Battery: {battery_capacity}% "
                    f"({'charging' if is_charging else 'discharging'})"
                )
                
                # Check alert conditions
                if self.alerting_system:
                    await self.alerting_system.check_metrics(metrics)
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Battery monitor error: {e}")
                await asyncio.sleep(interval)
    
    async def _health_check_loop(self) -> None:
        """Periodic health check of all components."""
        logger.info("Health check loop started")
        
        while self.is_running:
            try:
                uptime = datetime.now() - self.start_time
                active_components = sum(1 for v in self.components_status.values() if v)
                total_components = len(self.components_status)
                
                logger.info(
                    f"[HEALTH] Uptime: {uptime.total_seconds():.0f}s | "
                    f"Components: {active_components}/{total_components} active"
                )
                
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of all services."""
        logger.info("=" * 60)
        logger.info("INITIATING GRACEFUL SHUTDOWN")
        logger.info("=" * 60)
        
        self.is_running = False
        uptime = datetime.now() - self.start_time
        
        logger.info(f"System uptime: {uptime}")
        logger.info(f"Components status: {self.components_status}")
        logger.info("Orchestration system stopped")
    
    def get_status(self) -> Dict:
        """Get current system status."""
        return {
            'is_running': self.is_running,
            'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'components': self.components_status,
            'timestamp': datetime.now().isoformat(),
        }

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('orchestration.log')
        ]
    )
    
    orchestrator = SystemOrchestrator()
    
    try:
        await orchestrator.start_all_services()
    except KeyboardInterrupt:
        await orchestrator.shutdown()
    except Exception as e:
        logger.critical(f"Orchestrator crashed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
