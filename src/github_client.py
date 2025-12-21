"""GitHub API client for portfolio data integration.

Provides methods to fetch user repositories, contributions, and profile
information from GitHub API for portfolio enrichment.
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


@dataclass
class GithubConfig:
    """Configuration for GitHub API client."""
    token: str
    api_url: str = "https://api.github.com"
    timeout: int = 30
    per_page: int = 100
    rate_limit_requests: int = 60
    rate_limit_period: int = 3600  # 1 hour


class GitHubClient:
    """Async GitHub API client for portfolio data extraction."""

    def __init__(self, config: GithubConfig):
        """Initialize GitHub API client."""
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Hybrid-Portfolio-System"
        }
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, endpoint: str, method: str = "GET", **kwargs
    ) -> Dict:
        """Make authenticated request to GitHub API."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = urljoin(self.config.api_url, endpoint)
        try:
            async with self.session.request(
                method, url, headers=self.headers, timeout=self.config.timeout, **kwargs
            ) as response:
                if response.status == 401:
                    logger.error("GitHub authentication failed")
                    raise ValueError("Invalid GitHub token")
                elif response.status == 404:
                    logger.warning(f"Resource not found: {endpoint}")
                    return {}
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {endpoint}")
            return {}
        except aiohttp.ClientError as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return {}

    async def get_user(self, username: str) -> Dict:
        """Fetch GitHub user profile information."""
        return await self._make_request(f"/users/{username}")

    async def get_repositories(
        self, username: str, sort: str = "updated"
    ) -> List[Dict]:
        """Fetch user repositories with pagination."""
        repos = []
        page = 1
        while True:
            data = await self._make_request(
                f"/users/{username}/repos",
                params={
                    "sort": sort,
                    "direction": "desc",
                    "per_page": self.config.per_page,
                    "page": page
                }
            )
            if not data:
                break
            if isinstance(data, list):
                repos.extend(data)
                if len(data) < self.config.per_page:
                    break
            page += 1
        return repos

    async def get_repository_details(
        self, owner: str, repo: str
    ) -> Dict:
        """Fetch detailed repository information."""
        return await self._make_request(f"/repos/{owner}/{repo}")

    async def get_repository_languages(
        self, owner: str, repo: str
    ) -> Dict[str, int]:
        """Fetch programming languages used in repository."""
        return await self._make_request(f"/repos/{owner}/{repo}/languages") or {}

    async def get_repository_topics(
        self, owner: str, repo: str
    ) -> List[str]:
        """Fetch repository topics/tags."""
        data = await self._make_request(
            f"/repos/{owner}/{repo}/topics",
            headers={**self.headers, "Accept": "application/vnd.github.mercy-preview+json"}
        )
        return data.get("names", []) if data else []

    async def get_starred_repositories(
        self, username: str
    ) -> List[Dict]:
        """Fetch repositories starred by user."""
        starred = []
        page = 1
        while True:
            data = await self._make_request(
                f"/users/{username}/starred",
                params={"per_page": self.config.per_page, "page": page}
            )
            if not data or not isinstance(data, list):
                break
            starred.extend(data)
            if len(data) < self.config.per_page:
                break
            page += 1
        return starred

    async def get_user_events(
        self, username: str, event_type: str = None
    ) -> List[Dict]:
        """Fetch user public events."""
        endpoint = f"/users/{username}/events"
        if event_type:
            endpoint += f"/{event_type}"
        return await self._make_request(endpoint) or []

    async def extract_portfolio_data(
        self, username: str
    ) -> Dict:
        """Extract comprehensive portfolio data from GitHub."""
        try:
            user_data = await self.get_user(username)
            if not user_data:
                return {}

            repos = await self.get_repositories(username)
            starred = await self.get_starred_repositories(username)

            # Process repositories
            enriched_repos = []
            for repo in repos[:20]:  # Limit to top 20 repos
                languages = await self.get_repository_languages(username, repo["name"])
                topics = await self.get_repository_topics(username, repo["name"])
                enriched_repos.append({
                    "name": repo["name"],
                    "description": repo.get("description"),
                    "url": repo["html_url"],
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language"),
                    "languages": languages,
                    "topics": topics,
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at")
                })

            return {
                "user": {
                    "login": user_data.get("login"),
                    "name": user_data.get("name"),
                    "bio": user_data.get("bio"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email"),
                    "company": user_data.get("company"),
                    "blog": user_data.get("blog"),
                    "public_repos": user_data.get("public_repos"),
                    "followers": user_data.get("followers"),
                    "following": user_data.get("following")
                },
                "repositories": enriched_repos,
                "starred_count": len(starred),
                "extracted_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to extract portfolio data: {e}")
            return {}
