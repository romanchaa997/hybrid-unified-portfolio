"""Database connection and session management for portfolio system.

Handles database initialization, session creation, and lifecycle management
with connection pooling and error handling.
"""

import logging
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, Optional
import os

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:password@localhost/hybrid_portfolio"
)

DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, database_url: str = DATABASE_URL, echo: bool = DATABASE_ECHO):
        """Initialize database manager."""
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.session_factory = None
        self.scoped_session = None

    def initialize(self):
        """Initialize database engine and session factory."""
        try:
            # Determine connection pool based on database type
            poolclass = QueuePool
            connect_args = {}

            if "sqlite" in self.database_url.lower():
                poolclass = NullPool
                connect_args = {"check_same_thread": False}
            elif "postgresql" in self.database_url:
                connect_args = {
                    "connect_timeout": DATABASE_POOL_TIMEOUT,
                    "application_name": "hybrid_portfolio"
                }

            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                poolclass=poolclass,
                pool_size=DATABASE_POOL_SIZE,
                max_overflow=DATABASE_MAX_OVERFLOW,
                pool_timeout=DATABASE_POOL_TIMEOUT,
                pool_recycle=DATABASE_POOL_RECYCLE,
                connect_args=connect_args
            )

            # Add event listeners
            self._setup_event_listeners()

            # Create session factory
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Create scoped session for thread-local access
            self.scoped_session = scoped_session(self.session_factory)

            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _setup_event_listeners(self):
        """Setup database event listeners for monitoring and optimization."""
        @event.listens_for(Engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Configure connection on connect."""
            if "postgresql" in self.database_url:
                # Enable connection timeout for PostgreSQL
                dbapi_conn.timeout = DATABASE_POOL_TIMEOUT

        @event.listens_for(Engine, "engine_disposed")
        def receive_engine_disposed(engine):
            """Log when engine is disposed."""
            logger.debug("Database engine disposed")

    def get_session(self) -> Session:
        """Get a new database session."""
        if self.session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.session_factory()

    def get_scoped_session(self) -> Session:
        """Get scoped session (thread-local)."""
        if self.scoped_session is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.scoped_session

    @contextmanager
    def session_context(self) -> Generator[Session, None, None]:
        """Context manager for database session."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connections."""
        if self.scoped_session:
            self.scoped_session.remove()
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            with self.session_context() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def create_all_tables(self):
        """Create all database tables."""
        try:
            from .models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize()
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    manager = get_database_manager()
    with manager.session_context() as session:
        yield session


async def init_db():
    """Initialize database on application startup."""
    try:
        manager = get_database_manager()
        manager.create_all_tables()
        if manager.health_check():
            logger.info("Database initialization successful")
        else:
            logger.warning("Database health check failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections on application shutdown."""
    manager = get_database_manager()
    manager.close()
