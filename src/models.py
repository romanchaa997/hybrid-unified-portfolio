"""Database models for portfolio system using SQLAlchemy ORM.

Defines models for users, portfolios, skills, projects, and search history
with vector embeddings and metadata storage.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for portfolio owners."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    github_username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    github_profile_url = Column(String(255), nullable=True)
    github_api_token = Column(String(255), nullable=True)  # Encrypted
    follower_count = Column(Integer, default=0)
    public_repos_count = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Portfolio(Base):
    """Portfolio model containing user's portfolio data."""
    __tablename__ = "portfolios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    summary_embedding = Column(String(4000), nullable=True)  # Serialized numpy array
    embedding_model = Column(String(255), default="sentence-transformers/all-MiniLM-L6-v2")
    visibility = Column(String(50), default="public")  # public, private, unlisted
    view_count = Column(Integer, default=0)
    search_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    tags = Column(JSON, nullable=True)  # List of tags
    metadata = Column(JSON, nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    skills = relationship("Skill", back_populates="portfolio", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="portfolio", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_user_visibility", "user_id", "visibility"),)


class Skill(Base):
    """Skill model for user technical and soft skills."""
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=True, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    skill_category = Column(String(100), nullable=False)  # technical, soft, domain, etc
    proficiency_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert
    years_of_experience = Column(Float, default=0.0)
    endorsement_count = Column(Integer, default=0)
    skill_embedding = Column(String(4000), nullable=True)  # Serialized embedding vector
    description = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)  # Projects that demonstrate skill
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="skills")
    portfolio = relationship("Portfolio", back_populates="skills")

    __table_args__ = (Index("idx_skill_category", "skill_category"),)


class Project(Base):
    """Project model for portfolio projects."""
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=True, index=True)
    github_repo_id = Column(Integer, nullable=True, index=True)
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_url = Column(String(255), nullable=True)
    repository_url = Column(String(255), nullable=True)
    technologies = Column(JSON, nullable=True)  # List of tech stack
    featured_image_url = Column(String(255), nullable=True)
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    language = Column(String(100), nullable=True)
    project_embedding = Column(String(4000), nullable=True)  # Serialized embedding
    summary_embedding = Column(String(4000), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    portfolio = relationship("Portfolio", back_populates="projects")

    __table_args__ = (Index("idx_repository", "github_repo_id"),)


class SearchHistory(Base):
    """Search history model for tracking portfolio searches."""
    __tablename__ = "search_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_query = Column(String(512), nullable=False)
    search_type = Column(String(50), default="hybrid")  # hybrid, vector, keyword
    results_count = Column(Integer, default=0)
    top_result_id = Column(String(36), nullable=True)
    query_embedding = Column(String(4000), nullable=True)
    search_duration_ms = Column(Integer, default=0)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    session_id = Column(String(36), nullable=True, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (Index("idx_search_query", "search_query"), Index("idx_created_at", "created_at"))


class EmbeddingCache(Base):
    """Cache for generated embeddings to avoid recomputation."""
    __tablename__ = "embedding_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # skill, project, portfolio, text
    content_id = Column(String(36), nullable=False)
    embedding_vector = Column(String(4000), nullable=False)  # Serialized numpy array
    embedding_model = Column(String(255), default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dim = Column(Integer, default=384)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)

    __table_args__ = (Index("idx_content_type", "content_type"),)


class PortfolioRating(Base):
    """Rating model for portfolio quality assessment."""
    __tablename__ = "portfolio_ratings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=False, index=True)
    rating_value = Column(Float, nullable=False)  # 1.0-5.0
    comment = Column(Text, nullable=True)
    reviewer_email = Column(String(255), nullable=True)
    rating_criteria = Column(JSON, nullable=True)  # Design, content, presentation, etc
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
