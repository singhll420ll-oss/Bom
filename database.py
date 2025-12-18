"""
Database configuration with SQLAlchemy 2.0 async support
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,  # Health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def check_connection(self) -> bool:
        """Check database connection health"""
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    async def reconnect(self) -> bool:
        """Attempt to reconnect to database"""
        try:
            # Dispose old connections
            await self.engine.dispose()
            
            # Create new engine
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.LOG_LEVEL == "DEBUG",
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Update session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            # Test connection
            return await self.check_connection()
        except Exception as e:
            logger.error(f"Database reconnection failed: {e}")
            return False
    
    async def execute_with_retry(self, operation, max_retries: int = 3):
        """Execute database operation with retry logic"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                async with self.session_factory() as session:
                    return await operation(session)
            except SQLAlchemyError as e:
                last_exception = e
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    if not await self.check_connection():
                        await self.reconnect()
        
        if last_exception:
            raise last_exception
    
    async def batch_operation(self, operations: list, batch_size: int = 100):
        """Execute multiple operations in batches"""
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            
            async with self.session_factory() as session:
                try:
                    batch_results = []
                    for operation in batch:
                        result = await operation(session)
                        batch_results.append(result)
                    
                    await session.commit()
                    results.extend(batch_results)
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Batch operation failed: {e}")
                    raise
        
        return results

# Global database manager instance
db_manager = DatabaseManager()

# Query logging in debug mode
if settings.LOG_LEVEL == "DEBUG":
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logger.debug(f"Query: {statement}")
    
    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        logger.debug(f"Query completed in {total:.2f}s")

# Transaction utilities
class TransactionManager:
    """Transaction management utilities"""
    
    @staticmethod
    async def transaction(session: AsyncSession, operations: list):
        """Execute multiple operations in a single transaction"""
        try:
            results = []
            for operation in operations:
                result = await operation(session)
                results.append(result)
            
            await session.commit()
            return results
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
    
    @staticmethod
    async def savepoint(session: AsyncSession, operation):
        """Execute operation with savepoint for partial rollback"""
        async with session.begin_nested():
            try:
                result = await operation(session)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Savepoint operation failed: {e}")
                raise

# Database initialization utilities
async def init_database():
    """Initialize database with tables and indexes"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Create indexes (if not already created)
            from sqlalchemy import Index
            
            # Add any additional indexes here if needed
            
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def drop_database():
    """Drop all database tables (use with caution)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database dropped successfully")
    except Exception as e:
        logger.error(f"Database drop failed: {e}")
        raise

# Export utilities
__all__ = [
    "engine",
    "AsyncSessionLocal", 
    "Base",
    "get_db",
    "db_manager",
    "TransactionManager",
    "init_database",
    "drop_database"
]