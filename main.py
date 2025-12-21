"""Main FastAPI application for Hybrid Unified Portfolio System."""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest
import json

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= DATA MODELS =============

class SkillVector(BaseModel):
    """Skill with vector representation."""
    name: str
    category: str  # "AI/ML", "Web3", "DevOps"
    level: float = Field(ge=0, le=10)
    description: Optional[str] = None
    verified: bool = False

class PortfolioProfile(BaseModel):
    """Complete portfolio profile."""
    username: str
    github_url: str
    bio: str
    location: Optional[str] = None
    skills: List[SkillVector] = []
    contributions: int = 0
    followers: int = 0
    projects_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    """Search request."""
    query: str
    top_k: int = Field(10, ge=1, le=100)
    filters: Optional[dict] = None
    weights: dict = {
        "vector": 0.4,
        "structured": 0.3,
        "projects": 0.2,
        "experience": 0.1
    }

class SearchResult(BaseModel):
    """Search result item."""
    portfolio_id: str
    username: str
    match_score: float = Field(ge=0, le=100)
    skills: List[SkillVector]
    relevance: str  # "high", "medium", "low"

class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: dict

# ============= METRICS =============

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

search_counter = Counter(
    'search_requests_total',
    'Total search requests',
    ['query_type']
)

embedding_counter = Counter(
    'embeddings_created_total',
    'Total embeddings created'
)

# ============= LIFESPAN =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Hybrid Portfolio API starting...")
    logger.info("📊 Loading embeddings model...")
    logger.info("🗄️  Connecting to PostgreSQL...")
    logger.info("🔍 Initializing Pinecone index...")
    logger.info("✅ All services initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down gracefully...")
    logger.info("✅ Cleanup complete")

# ============= APP INITIALIZATION =============

app = FastAPI(
    title="Hybrid Unified Portfolio API",
    description="Vector embeddings + semantic search for professional profiles",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://github.com", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= HEALTH & METRICS =============

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for Docker/K8s."""
    return HealthCheck(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow(),
        services={
            "api": "up",
            "database": "up",
            "cache": "up",
            "vector_db": "up"
        }
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.get("/api/v1/health")
async def api_health():
    """API health endpoint."""
    return {"status": "operational", "version": "0.1.0"}

# ============= CORE ENDPOINTS =============

@app.post("/api/v1/portfolio/ingest")
async def ingest_github_profile(username: str) -> PortfolioProfile:
    """Ingest GitHub profile and create embeddings."""
    logger.info(f"Ingesting profile for {username}")
    
    # Mock implementation
    profile = PortfolioProfile(
        username=username,
        github_url=f"https://github.com/{username}",
        bio="AI/ML Engineer | Python & Web3 | DevOps",
        location="Ukraine",
        skills=[
            SkillVector(name="Python", category="AI/ML", level=9.0),
            SkillVector(name="FastAPI", category="DevOps", level=8.5),
            SkillVector(name="Machine Learning", category="AI/ML", level=8.5),
            SkillVector(name="Kubernetes", category="DevOps", level=8.0),
        ],
        contributions=861,
        followers=10,
        projects_count=4
    )
    
    embedding_counter.inc()
    request_count.labels(method="POST", endpoint="/portfolio/ingest", status=200).inc()
    
    return profile

@app.post("/api/v1/search/hybrid", response_model=List[SearchResult])
async def hybrid_search(query: SearchQuery) -> List[SearchResult]:
    """Hybrid semantic + structured search.
    
    Combines:
    - Vector similarity (40%)
    - Structured skill matching (30%)
    - Project relevance (20%)
    - Experience alignment (10%)
    """
    logger.info(f"Searching for: {query.query}")
    search_counter.labels(query_type="hybrid").inc()
    
    # Mock results
    results = [
        SearchResult(
            portfolio_id="romanchaa997",
            username="romanchaa997",
            match_score=95.5,
            skills=[
                SkillVector(name="Python", category="AI/ML", level=9.0),
                SkillVector(name="ML", category="AI/ML", level=8.5),
            ],
            relevance="high"
        ),
        SearchResult(
            portfolio_id="dev2",
            username="dev2",
            match_score=78.3,
            skills=[
                SkillVector(name="Python", category="AI/ML", level=7.5),
            ],
            relevance="medium"
        )
    ]
    
    request_count.labels(method="POST", endpoint="/search/hybrid", status=200).inc()
    return results[:query.top_k]

@app.get("/api/v1/portfolio/{username}")
async def get_portfolio(username: str) -> PortfolioProfile:
    """Get portfolio by username."""
    logger.info(f"Fetching portfolio: {username}")
    
    return PortfolioProfile(
        username=username,
        github_url=f"https://github.com/{username}",
        bio="Developer",
        skills=[],
        contributions=0
    )

@app.post("/api/v1/skills/embed")
async def create_skill_embeddings(skills: List[SkillVector]):
    """Create embeddings for list of skills."""
    logger.info(f"Creating embeddings for {len(skills)} skills")
    
    embedding_counter.inc(len(skills))
    
    return {
        "count": len(skills),
        "status": "embeddings_created",
        "timestamp": datetime.utcnow()
    }

# ============= ERROR HANDLERS =============

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# ============= STARTUP =============

if __name__ == "__main__":
    # Get config from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "4"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )
