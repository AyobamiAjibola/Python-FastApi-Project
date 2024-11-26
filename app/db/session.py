from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/menupk_dev_db"

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "sessionmaker" class
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session
