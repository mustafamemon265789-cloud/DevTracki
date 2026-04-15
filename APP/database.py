from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
import os

# Get database URL from settings or environment
database_url = settings.database_url

# Railway provides DATABASE_URL but uses postgres:// which SQLAlchemy doesn't accept
# We need to convert it to postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create engine with proper settings for Railway
engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
)

def create_db_and_tables():
    """Create all database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session