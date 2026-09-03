from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. PostgreSQL connection URL: postgresql://username:password@localhost:5432/database_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ikofi_db"

# 2. Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create a SessionLocal class for database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for defining database models
Base = declarative_base()

# 5. Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()