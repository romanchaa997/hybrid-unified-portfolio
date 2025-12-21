"""Pydantic schemas for API request/response validation.

Defines request and response schemas for FastAPI endpoints with
data validation, documentation, and type hints.
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    SOFT = "soft"
    DOMAIN = "domain"
    LANGUAGE = "language"
    TOOL = "tool"


class SkillBase(BaseModel):
    """Base skill schema."""
    skill_name: str = Field(..., min_length=1, max_length=255, description="Skill name")
    skill_category: SkillCategory = Field(..., description="Skill category")
    proficiency_level: SkillLevel = Field(SkillLevel.INTERMEDIATE, description="Proficiency level")
    years_of_experience: float = Field(default=0.0, ge=0, description="Years of experience")
    description: Optional[str] = Field(None, max_length=1000, description="Skill description")


class SkillCreate(SkillBase):
    """Create skill request schema."""
    pass


class SkillResponse(SkillBase):
    """Skill response schema."""
    id: str = Field(..., description="Skill ID")
    user_id: str = Field(..., description="User ID")
    endorsement_count: int = Field(default=0, ge=0, description="Endorsement count")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema."""
    project_name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: Optional[HttpUrl] = Field(None, description="Repository URL")
    project_url: Optional[HttpUrl] = Field(None, description="Project URL")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")


class ProjectCreate(ProjectBase):
    """Create project request schema."""
    pass


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="User ID")
    stars_count: int = Field(default=0, ge=0, description="GitHub stars")
    forks_count: int = Field(default=0, ge=0, description="GitHub forks")
    language: Optional[str] = Field(None, description="Primary language")
    view_count: int = Field(default=0, ge=0, description="View count")
    rating: float = Field(default=0.0, ge=0, le=5, description="Average rating")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema."""
    github_username: str = Field(..., min_length=1, max_length=255, description="GitHub username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    name: Optional[str] = Field(None, max_length=255, description="Full name")
    bio: Optional[str] = Field(None, max_length=1000, description="Bio")
    location: Optional[str] = Field(None, max_length=255, description="Location")
    company: Optional[str] = Field(None, max_length=255, description="Company")
    website: Optional[HttpUrl] = Field(None, description="Website URL")


class UserCreate(UserBase):
    """Create user request schema."""
    github_api_token: str = Field(..., description="GitHub API token")


class UserResponse(UserBase):
    """User response schema."""
    id: str = Field(..., description="User ID")
    github_profile_url: Optional[str] = Field(None, description="GitHub profile URL")
    follower_count: int = Field(default=0, ge=0, description="Follower count")
    public_repos_count: int = Field(default=0, ge=0, description="Public repos count")
    is_active: bool = Field(default=True, description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    """Base portfolio schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Portfolio title")
    description: Optional[str] = Field(None, description="Portfolio description")
    visibility: str = Field("public", regex="^(public|private|unlisted)$", description="Visibility")
    tags: Optional[List[str]] = Field(None, description="Portfolio tags")


class PortfolioCreate(PortfolioBase):
    """Create portfolio request schema."""
    pass


class PortfolioResponse(PortfolioBase):
    """Portfolio response schema."""
    id: str = Field(..., description="Portfolio ID")
    user_id: str = Field(..., description="User ID")
    view_count: int = Field(default=0, ge=0, description="View count")
    search_count: int = Field(default=0, ge=0, description="Search count")
    rating: float = Field(default=0.0, ge=0, le=5, description="Average rating")
    rating_count: int = Field(default=0, ge=0, description="Rating count")
    is_featured: bool = Field(default=False, description="Featured status")
    skills: List[SkillResponse] = Field(default_factory=list, description="Associated skills")
    projects: List[ProjectResponse] = Field(default_factory=list, description="Associated projects")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Portfolio search request schema."""
    query: str = Field(..., min_length=1, max_length=512, description="Search query")
    search_mode: str = Field("hybrid", regex="^(hybrid|vector|keyword)$", description="Search mode")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    vector_weight: float = Field(0.6, ge=0, le=1, description="Vector search weight")
    keyword_weight: float = Field(0.4, ge=0, le=1, description="Keyword search weight")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

    @validator('vector_weight', 'keyword_weight')
    def weights_sum_to_one(cls, v, values):
        if 'vector_weight' in values:
            total = values['vector_weight'] + v
            if not abs(total - 1.0) < 0.001:
                raise ValueError("Weights must sum to 1.0")
        return v


class SearchResult(BaseModel):
    """Search result schema."""
    item_id: str = Field(..., description="Item ID")
    title: str = Field(..., description="Item title")
    description: Optional[str] = Field(None, description="Item description")
    score: float = Field(..., ge=0, le=1, description="Relevance score")
    match_type: str = Field(..., description="Match type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str = Field(..., description="Original search query")
    mode: str = Field(..., description="Search mode used")
    results_count: int = Field(..., ge=0, description="Total results found")
    results: List[SearchResult] = Field(..., description="Search results")
    execution_time_ms: float = Field(..., ge=0, description="Query execution time")
    timestamp: datetime = Field(..., description="Query timestamp")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., regex="^(healthy|degraded|unhealthy)$", description="Health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Health details")
