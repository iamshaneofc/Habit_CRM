from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import config

DATABASE_URL = config.get_database_url()

# Configure engine connection pooling according to DB type
connect_args = {}
engine_kwargs = {}

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
else:
    # AWS RDS / PostgreSQL connection pooling settings
    engine_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,     # Detect and reconnect dropped AWS RDS connections
        "pool_recycle": 1800,      # Recycle connections after 30 minutes
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
