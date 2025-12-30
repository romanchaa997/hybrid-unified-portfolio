#!/usr/bin/env python3
"""Manus API Client: Real integration with Manus project manager.

Provides:
- Project status sync
- Task creation/update
- Commit → task linking
- Real-time webhook handling
"""

import os
import json
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

try:
    import httpx
except ImportError:
    httpx = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ManusSyncPayload:
    """Data to sync with Manus."""
    project_id: str
    energy_level: str
    consciousness_scores: Dict
    deployment_policy: Dict
    metrics: Dict
    timestamp: str


class ManusClient:
    """Client for Manus API integration."""

    def __init__(self, api_token: Optional[str] = None, base_url: str = "https://manus.im/api"):
        self.api_token = api_token or os.getenv("MANUS_API_TOKEN")
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0) if httpx else None
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def sync_project_status(self, payload: ManusSyncPayload) -> bool:
        """Push orchestrator state to Manus.
        
        Endpoint: POST /projects/{project_id}/sync
        """
        if not self.client:
            logger.warning("httpx not installed, skipping Manus sync")
            return False

        try:
            response = await self.client.post(
                f"{self.base_url}/projects/{payload.project_id}/sync",
                json={
                    "energy_level": payload.energy_level,
                    "consciousness_scores": payload.consciousness_scores,
                    "deployment_policy": payload.deployment_policy,
                    "metrics": payload.metrics,
                    "timestamp": payload.timestamp,
                },
                headers=self.headers,
            )
            response.raise_for_status()
            logger.info(f"Synced with Manus: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Manus sync failed: {e}")
            return False

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        priority: str = "medium",
        tags: List[str] = None,
    ) -> Optional[Dict]:
        """Create a task in Manus when issue detected.
        
        Endpoint: POST /projects/{project_id}/tasks
        """
        if not self.client:
            logger.warning("httpx not installed, skipping task creation")
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/projects/{project_id}/tasks",
                json={
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "tags": tags or [],
                    "created_at": datetime.now().isoformat(),
                },
                headers=self.headers,
            )
            response.raise_for_status()
            logger.info(f"Created task: {title}")
            return response.json()
        except Exception as e:
            logger.error(f"Task creation failed: {e}")
            return None

    async def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update task status when energy/consciousness changes.
        
        Endpoint: PATCH /tasks/{task_id}
        """
        if not self.client:
            return False

        try:
            response = await self.client.patch(
                f"{self.base_url}/tasks/{task_id}",
                json=updates,
                headers=self.headers,
            )
            response.raise_for_status()
            logger.info(f"Updated task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Task update failed: {e}")
            return False

    async def link_commit_to_task(
        self, task_id: str, commit_sha: str, repo: str
    ) -> bool:
        """Link Git commit to Manus task.
        
        Endpoint: POST /tasks/{task_id}/commits
        """
        if not self.client:
            return False

        try:
            response = await self.client.post(
                f"{self.base_url}/tasks/{task_id}/commits",
                json={
                    "commit_sha": commit_sha,
                    "repo": repo,
                    "linked_at": datetime.now().isoformat(),
                },
                headers=self.headers,
            )
            response.raise_for_status()
            logger.info(f"Linked commit {commit_sha} to task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Commit linking failed: {e}")
            return False

    async def get_project_tasks(self, project_id: str) -> Optional[List[Dict]]:
        """Fetch all tasks for a project.
        
        Endpoint: GET /projects/{project_id}/tasks
        """
        if not self.client:
            return None

        try:
            response = await self.client.get(
                f"{self.base_url}/projects/{project_id}/tasks",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch tasks: {e}")
            return None

    async def handle_webhook(self, payload: Dict) -> bool:
        """Handle webhook from Manus (task created/updated).
        
        Called when Manus notifies about task changes.
        """
        try:
            event_type = payload.get("event_type")
            task_data = payload.get("task")

            if event_type == "task.created":
                logger.info(f"Manus task created: {task_data.get('title')}")
                # Trigger orchestrator to re-evaluate priorities
                return True

            elif event_type == "task.updated":
                logger.info(f"Manus task updated: {task_data.get('id')}")
                # Update internal state based on task changes
                return True

            elif event_type == "task.completed":
                logger.info(f"Manus task completed: {task_data.get('id')}")
                return True

            else:
                logger.warning(f"Unknown webhook event: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            return False

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()


async def main():
    """Demo: sync orchestrator state with Manus."""
    client = ManusClient()

    payload = ManusSyncPayload(
        project_id="bakhmach-hub",
        energy_level="MEDIUM",
        consciousness_scores={
            "integration": 70,
            "wellbeing": 65,
            "stability": 75,
            "mode": "SAFE",
        },
        deployment_policy={"bakhmach": True, "portfolio": False},
        metrics={"uptime": 99.9, "error_rate": 0.2},
        timestamp=datetime.now().isoformat(),
    )

    # Sync with Manus
    await client.sync_project_status(payload)

    # Create task if energy low
    if payload.energy_level == "LOW":
        await client.create_task(
            "bakhmach-hub",
            title="Low energy detected",
            description="System running on low battery. Consider plugging in.",
            priority="high",
            tags=["infrastructure", "energy"],
        )

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
