#!/usr/bin/env python3
"""Web Dashboard: Real-time system metrics visualization.

Provides a web-based dashboard for monitoring:
- Battery status and energy metrics
- CPU and memory usage
- Network activity
- Task processing status
- Energy consumption trends
- System health status
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

logger = logging.getLogger(__name__)

class SystemMetrics:
    """Collect system metrics for dashboard."""
    
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.max_history = 500
        self.connected_clients: List[WebSocket] = []
    
    async def collect_metrics(self) -> Dict:
        """Collect current system metrics."""
        import psutil
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        net_io = psutil.net_io_counters()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
            },
            'memory': {
                'percent': memory.percent,
                'available_mb': memory.available / (1024**2),
                'used_mb': memory.used / (1024**2),
                'total_mb': memory.total / (1024**2),
            },
            'disk': {
                'percent': disk.percent,
                'free_gb': disk.free / (1024**3),
                'used_gb': disk.used / (1024**3),
                'total_gb': disk.total / (1024**3),
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
            }
        }
        
        # Keep history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        return metrics
    
    async def broadcast(self, message: str) -> None:
        """Broadcast message to all connected clients."""
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                self.connected_clients.remove(client)
    
    def get_stats(self) -> Dict:
        """Get aggregated statistics from history."""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m['cpu']['percent'] for m in self.metrics_history]
        memory_values = [m['memory']['percent'] for m in self.metrics_history]
        
        return {
            'cpu_avg': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'cpu_min': min(cpu_values),
            'memory_avg': sum(memory_values) / len(memory_values),
            'memory_max': max(memory_values),
            'memory_min': min(memory_values),
            'sample_count': len(self.metrics_history),
        }

class DashboardApp:
    """Web dashboard application."""
    
    def __init__(self):
        self.app = FastAPI(title="System Dashboard")
        self.metrics = SystemMetrics()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Serve dashboard HTML."""
            return HTML_DASHBOARD
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current metrics."""
            metrics = await self.metrics.collect_metrics()
            return JSONResponse(metrics)
        
        @self.app.get("/api/history")
        async def get_history(limit: int = 100):
            """Get metrics history."""
            return JSONResponse(self.metrics.metrics_history[-limit:])
        
        @self.app.get("/api/stats")
        async def get_stats():
            """Get aggregated statistics."""
            return JSONResponse(self.metrics.get_stats())
        
        @self.app.websocket("/ws/metrics")
        async def websocket_metrics(websocket: WebSocket):
            """WebSocket endpoint for real-time metrics."""
            await websocket.accept()
            self.metrics.connected_clients.append(websocket)
            
            try:
                while True:
                    # Receive heartbeat
                    data = await websocket.receive_text()
                    
                    if data == "ping":
                        # Collect metrics and send
                        metrics = await self.metrics.collect_metrics()
                        await websocket.send_json(metrics)
                    elif data == "stats":
                        stats = self.metrics.get_stats()
                        await websocket.send_json({"stats": stats})
            except WebSocketDisconnect:
                self.metrics.connected_clients.remove(websocket)
                logger.info("Client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.metrics.connected_clients:
                    self.metrics.connected_clients.remove(websocket)
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start dashboard server."""
        logger.info(f"Starting dashboard on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            margin-bottom: 30px;
            text-align: center;
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0,212,255,0.3);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            border-color: rgba(0,212,255,0.8);
            box-shadow: 0 0 20px rgba(0,212,255,0.2);
        }
        .metric-name {
            font-size: 14px;
            color: #00d4ff;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 10px;
        }
        .metric-unit {
            font-size: 14px;
            color: #888;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            transition: width 0.3s ease;
            border-radius: 3px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff00;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .connection-status {
            text-align: center;
            padding: 10px;
            background: rgba(0,212,255,0.1);
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="status-indicator"></span>System Dashboard</h1>
        <div class="connection-status">Status: <span id="status">Connecting...</span></div>
        <div class="metrics-grid" id="metrics"></div>
    </div>
    
    <script>
        const ws = new WebSocket('ws://' + window.location.host + '/ws/metrics');
        
        ws.onopen = function() {
            document.getElementById('status').textContent = 'Connected';
            setInterval(() => ws.send('ping'), 1000);
        };
        
        ws.onmessage = function(event) {
            const metrics = JSON.parse(event.data);
            renderMetrics(metrics);
        };
        
        ws.onerror = function() {
            document.getElementById('status').textContent = 'Error';
        };
        
        function renderMetrics(data) {
            const container = document.getElementById('metrics');
            
            const cards = [
                {
                    name: 'CPU Usage',
                    value: data.cpu.percent.toFixed(1),
                    unit: '%',
                    percent: data.cpu.percent
                },
                {
                    name: 'Memory Usage',
                    value: data.memory.used_mb.toFixed(0),
                    unit: `MB / ${data.memory.total_mb.toFixed(0)}MB (${data.memory.percent.toFixed(1)}%)`,
                    percent: data.memory.percent
                },
                {
                    name: 'Disk Usage',
                    value: data.disk.used_gb.toFixed(1),
                    unit: `GB / ${data.disk.total_gb.toFixed(1)}GB (${data.disk.percent.toFixed(1)}%)`,
                    percent: data.disk.percent
                },
                {
                    name: 'Network (Sent)',
                    value: (data.network.bytes_sent / (1024**3)).toFixed(2),
                    unit: 'GB',
                    percent: 0
                }
            ];
            
            container.innerHTML = cards.map(card => `
                <div class="metric-card">
                    <div class="metric-name">${card.name}</div>
                    <div class="metric-value">${card.value}</div>
                    <div class="metric-unit">${card.unit}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(card.percent, 100)}%"></div>
                    </div>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dashboard = DashboardApp()
    await dashboard.start(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
