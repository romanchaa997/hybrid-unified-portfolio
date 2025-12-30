#!/usr/bin/env python3
"""Webhook Handler: Process incoming Manus project management webhooks.

Handles webhooks from Manus API for:
- Task status changes
- Project updates
- Commit linking
- Resource allocation changes
- Energy usage events
"""

import asyncio
import logging
import hmac
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)

@dataclass
class WebhookPayload:
    """Webhook payload structure."""
    event_type: str
    event_id: str
    timestamp: str
    resource_type: str
    resource_id: str
    data: Dict[str, Any]
    action: str

@dataclass
class WebhookEvent:
    """Processed webhook event."""
    type: str
    timestamp: datetime
    resource: str
    action: str
    payload: Dict[str, Any]
    processed_at: datetime

class WebhookHandler:
    """Handle incoming webhooks from Manus."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key
        self.app = FastAPI(title="Manus Webhook Handler")
        self.event_handlers: Dict[str, list[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        @self.app.post("/webhooks/manus")
        async def handle_webhook(
            request: Request,
            background_tasks: BackgroundTasks
        ):
            """Handle incoming webhook from Manus."""
            try:
                # Verify webhook signature if secret key is set
                if self.secret_key:
                    signature = request.headers.get("X-Manus-Signature")
                    if not await self._verify_signature(request, signature):
                        raise HTTPException(status_code=401, detail="Invalid signature")
                
                payload = await request.json()
                webhook_event = await self.process_webhook(payload)
                
                # Process in background
                background_tasks.add_task(
                    self._emit_event,
                    webhook_event
                )
                
                return JSONResponse(
                    {"status": "received", "event_id": webhook_event.payload.get("event_id")},
                    status_code=202
                )
            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                return JSONResponse(
                    {"status": "error", "message": str(e)},
                    status_code=400
                )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "webhook-handler"}
    
    async def _verify_signature(self, request: Request, signature: str) -> bool:
        """Verify webhook signature."""
        try:
            body = await request.body()
            expected_signature = hmac.new(
                self.secret_key.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def process_webhook(self, payload: Dict[str, Any]) -> WebhookEvent:
        """Process webhook payload."""
        try:
            event_type = payload.get("event_type", "unknown")
            resource_type = payload.get("resource_type", "")
            action = payload.get("action", "")
            
            webhook_event = WebhookEvent(
                type=event_type,
                timestamp=datetime.fromisoformat(
                    payload.get("timestamp", datetime.now().isoformat())
                ),
                resource=resource_type,
                action=action,
                payload=payload,
                processed_at=datetime.now()
            )
            
            logger.info(
                f"Webhook processed: {event_type} on {resource_type} "
                f"({action}) - {payload.get('event_id', 'no-id')}"
            )
            
            return webhook_event
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable
    ) -> None:
        """Register event handler for webhook event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Handler registered for event type: {event_type}")
    
    async def _emit_event(self, event: WebhookEvent) -> None:
        """Emit webhook event to registered handlers."""
        handlers = self.event_handlers.get(event.type, [])
        
        if not handlers:
            logger.debug(f"No handlers registered for event type: {event.type}")
            return
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error executing handler for {event.type}: {e}")
    
    async def start(self, host: str = "127.0.0.1", port: int = 8001) -> None:
        """Start webhook server."""
        import uvicorn
        
        logger.info(f"Starting webhook handler on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

# Built-in event handlers
async def handle_task_update(event: WebhookEvent) -> None:
    """Handle task update webhook."""
    data = event.payload.get("data", {})
    task_id = event.payload.get("resource_id")
    action = event.action
    
    logger.info(f"Task {task_id} {action}: {data}")

async def handle_project_update(event: WebhookEvent) -> None:
    """Handle project update webhook."""
    data = event.payload.get("data", {})
    project_id = event.payload.get("resource_id")
    
    logger.info(f"Project {project_id} updated: {data}")

async def handle_commit_linked(event: WebhookEvent) -> None:
    """Handle commit linked to task webhook."""
    data = event.payload.get("data", {})
    task_id = event.payload.get("resource_id")
    commit = data.get("commit_hash")
    
    logger.info(f"Commit {commit} linked to task {task_id}")

async def handle_resource_allocation(event: WebhookEvent) -> None:
    """Handle resource allocation change."""
    data = event.payload.get("data", {})
    resource_type = data.get("resource_type")
    amount = data.get("amount")
    
    logger.info(f"Resource allocation: {resource_type}={amount}")

async def handle_energy_event(event: WebhookEvent) -> None:
    """Handle energy-related event."""
    data = event.payload.get("data", {})
    event_severity = data.get("severity", "info")
    energy_level = data.get("energy_level")
    
    logger.warning(
        f"Energy event [{event_severity}]: {energy_level}% - {data.get('message', '')}"
    )

async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create webhook handler
    handler = WebhookHandler(secret_key="your-secret-key")
    
    # Register built-in handlers
    handler.register_handler("task.updated", handle_task_update)
    handler.register_handler("task.created", handle_task_update)
    handler.register_handler("project.updated", handle_project_update)
    handler.register_handler("commit.linked", handle_commit_linked)
    handler.register_handler("resource.allocated", handle_resource_allocation)
    handler.register_handler("energy.alert", handle_energy_event)
    
    logger.info("Starting Manus Webhook Handler")
    
    # Start server
    await handler.start(host="0.0.0.0", port=8001)

if __name__ == "__main__":
    asyncio.run(main())
