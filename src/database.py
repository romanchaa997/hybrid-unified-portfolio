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



# ============== DATABASE OPTIMIZATIONS ==============

from contextlib import contextmanager
from functools import wraps
from time import time
import threading

class DatabasePool:
    """Connection pool manager for optimized database access."""
    
    def __init__(self, min_size: int = 5, max_size: int = 20, timeout: int = 30):
        """Initialize connection pool.
        
        Args:
            min_size: Minimum connections to maintain
            max_size: Maximum connections allowed
            timeout: Connection timeout in seconds
        """
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self._connections = []
        self._available = threading.Semaphore(max_size)
        self._lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize minimum connections."""
        for _ in range(self.min_size):
            conn = self._create_connection()
            if conn:
                self._connections.append(conn)
    
    def _create_connection(self):
        """Create new database connection."""
        try:
            return get_database_manager().engine.connect()
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool."""
        if not self._available.acquire(timeout=self.timeout):
            raise TimeoutError("No available database connections")
        
        conn = None
        try:
            with self._lock:
                if self._connections:
                    conn = self._connections.pop()
                else:
                    conn = self._create_connection()
            
            if conn:
                yield conn
        finally:
            if conn:
                with self._lock:
                    self._connections.append(conn)
            self._available.release()


def db_query_cache(ttl: int = 300):
    """Decorator for caching database query results.
    
    Args:
        ttl: Cache time-to-live in seconds
    """
    def decorator(func):
        cache = {}
        timestamps = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from arguments
            cache_key = str((args, tuple(sorted(kwargs.items()))))
            
            # Check cache validity
            if cache_key in cache:
                cached_time = timestamps.get(cache_key, 0)
                if time() - cached_time < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cache[cache_key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = result
            timestamps[cache_key] = time()
            
            # Limit cache size
            if len(cache) > 100:
                oldest_key = min(timestamps, key=timestamps.get)
                del cache[oldest_key]
                del timestamps[oldest_key]
            
            return result
        
        return wrapper
    return decorator


class DatabaseMetrics:
    """Track database performance metrics."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.query_count = 0
        self.total_time = 0
        self.error_count = 0
        self._lock = threading.Lock()
    
    def record_query(self, duration: float, success: bool = True):
        """Record query execution.
        
        Args:
            duration: Query execution time in seconds
            success: Whether query succeeded
        """
        with self._lock:
            self.query_count += 1
            self.total_time += duration
            if not success:
                self.error_count += 1
    
    def get_stats(self) -> dict:
        """Get current performance statistics."""
        with self._lock:
            avg_time = self.total_time / self.query_count if self.query_count > 0 else 0
            return {
                "total_queries": self.query_count,
                "average_time": avg_time,
                "total_time": self.total_time,
                "error_count": self.error_count,
                "error_rate": self.error_count / self.query_count if self.query_count > 0 else 0
            }


# Global database metrics instance
_db_metrics = DatabaseMetrics()

def get_db_metrics() -> DatabaseMetrics:
    """Get global database metrics instance."""
    return _db_metrics
