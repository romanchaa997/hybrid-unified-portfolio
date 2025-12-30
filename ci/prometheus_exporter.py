#!/usr/bin/env python3
"""Prometheus Exporter: Metrics collection and export."""

import asyncio, logging, json, time
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """Export system metrics in Prometheus format."""
    
    def __init__(self, port: int = 8002):
        self.port = port
        self.metrics: Dict[str, float] = {}
        self.start_time = time.time()
    
    def _format_metric(self, name: str, value: float, help_text: str = "") -> str:
        """Format metric in Prometheus text format."""
        lines = []
        if help_text:
            lines.append(f"# HELP {name} {help_text}")
        lines.append(f"{name} {value}")
        return "\n".join(lines)
    
    async def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system metrics."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'system_uptime_seconds': time.time() - self.start_time,
                'cpu_usage_percent': cpu_percent,
                'memory_usage_bytes': memory.used,
                'memory_total_bytes': memory.total,
                'memory_percent': memory.percent,
            }
        except Exception as e:
            logger.error(f"Metric collection error: {e}")
            return {}
    
    async def generate_metrics_text(self) -> str:
        """Generate Prometheus metrics text output."""
        metrics = await self.collect_system_metrics()
        self.metrics.update(metrics)
        
        lines = []
        lines.append("# HELP system_metrics Hybrid Unified Portfolio system metrics")
        lines.append("# TYPE system_metrics gauge")
        
        for key, value in self.metrics.items():
            lines.append(f"system_{key} {value}")
        
        lines.append(f"exporter_scrape_timestamp_seconds {time.time()}")
        return "\n".join(lines) + "\n"
    
    async def start_server(self):
        """Start Prometheus metrics server."""
        logger.info(f"Starting Prometheus exporter on port {self.port}")
        # In production: use aiohttp or FastAPI to serve /metrics endpoint
        logger.info("Metrics endpoint: http://localhost:{}/metrics".format(self.port))
    
    def get_metrics(self) -> Dict:
        """Get current metrics."""
        return {'metrics': self.metrics, 'timestamp': datetime.now().isoformat()}

async def main():
    logging.basicConfig(level=logging.INFO)
    exporter = PrometheusExporter()
    output = await exporter.generate_metrics_text()
    print(output)

if __name__ == "__main__":
    asyncio.run(main())
