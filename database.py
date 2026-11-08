import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import config

logger = logging.getLogger("habit_crm.database")

def create_app_engine(database_url: str):
    connect_args = {}
    engine_kwargs = {}
    if "sqlite" in database_url:
        connect_args = {"check_same_thread": False}
    else:
        # AWS RDS / PostgreSQL connection pooling settings
        engine_kwargs = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,     # Detect and reconnect dropped connections
            "pool_recycle": 1800,      # Recycle connections after 30 minutes
        }
    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)

DATABASE_URL = config.get_database_url()
engine = create_app_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def check_and_stabilize_db():
    """
    Verifies DB reachability on startup.
    If remote DB fails in development mode and fallback is enabled,
    switches safely to local SQLite to ensure the application starts reliably.
    """
    global engine, SessionLocal, DATABASE_URL
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        logger.info("Database connection established successfully.")
        config._db_checked = True
        return True, "connected"
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e).splitlines()[0]}"
        if not config.is_production() and config.DB_FALLBACK_SQLITE and "sqlite" not in DATABASE_URL:
            logger.warning(
                "Configured DB (%s) unreachable in development: %s. Falling back to local SQLite (%s).",
                config.DB_TYPE, err_msg, config.SQLITE_DB_PATH
            )
            fallback_url = f"sqlite:///{config.SQLITE_DB_PATH}"
            DATABASE_URL = fallback_url
            engine = create_app_engine(fallback_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            from config import DatabaseConfig
            DatabaseConfig._active_fallback = True
            config._active_fallback = True
            config._db_checked = True
            upgrade_schema(engine)
            return True, "fallback_sqlite"
        logger.error("Database connection failure: %s", err_msg)
        return False, err_msg

def upgrade_schema(eng=None):
    """
    Safely adds any missing columns across SQLite or PostgreSQL tables
    to guarantee zero data loss and seamless evolution.
    """
    if eng is None:
        eng = engine
    from sqlalchemy import inspect
    try:
        insp = inspect(eng)
        tables = insp.get_table_names()
        # 1. Users table
        if "users" in tables:
            user_cols = {c["name"] for c in insp.get_columns("users")}
            with eng.connect() as conn:
                if "display_name" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(100);"))
                if "profession" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN profession VARCHAR(100);"))
                if "bio" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(255);"))
                if "onboarding_completed" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0;"))
                if "tracking_start_date" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN tracking_start_date DATE;"))
                if "timezone" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';"))
                conn.commit()

        # 2. Habits table
        if "habits" in tables:
            habit_cols = {c["name"] for c in insp.get_columns("habits")}
            with eng.connect() as conn:
                if "subtopics" not in habit_cols:
                    conn.execute(text("ALTER TABLE habits ADD COLUMN subtopics TEXT;"))
                if "activation_date" not in habit_cols:
                    conn.execute(text("ALTER TABLE habits ADD COLUMN activation_date DATE;"))
                if "archived_at" not in habit_cols:
                    conn.execute(text("ALTER TABLE habits ADD COLUMN archived_at DATETIME;"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Schema upgrade check note: {e}")

def get_db():
    """FastAPI database session dependency with transactional safety."""
    if not getattr(config, "_db_checked", False):
        check_and_stabilize_db()
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
