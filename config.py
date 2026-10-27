import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()

class DatabaseConfig:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")

    # DB selection: 'sqlite' | 'postgres' | 'mysql'
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").lower()

    # SQLite
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "habits.db")

    # AWS RDS Connection Parameters
    RDS_HOSTNAME: Optional[str] = os.getenv("RDS_HOSTNAME")
    RDS_PORT: int = int(os.getenv("RDS_PORT", "5432"))
    RDS_DB_NAME: str = os.getenv("RDS_DB_NAME", "habit_crm_db")
    RDS_USERNAME: Optional[str] = os.getenv("RDS_USERNAME")
    RDS_PASSWORD: Optional[str] = os.getenv("RDS_PASSWORD")

    # Direct URL Override
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    @classmethod
    def get_database_url(cls) -> str:
        """Returns SQLAlchemy-compatible connection string."""
        if cls.DATABASE_URL and cls.DATABASE_URL.strip():
            return cls.DATABASE_URL.strip()

        if cls.DB_TYPE == "postgres" or cls.DB_TYPE == "postgresql":
            if not cls.RDS_HOSTNAME or not cls.RDS_USERNAME:
                raise ValueError("PostgreSQL/RDS configuration requires RDS_HOSTNAME and RDS_USERNAME")
            pwd = f":{cls.RDS_PASSWORD}" if cls.RDS_PASSWORD else ""
            return f"postgresql+psycopg2://{cls.RDS_USERNAME}{pwd}@{cls.RDS_HOSTNAME}:{cls.RDS_PORT}/{cls.RDS_DB_NAME}"

        elif cls.DB_TYPE == "mysql":
            if not cls.RDS_HOSTNAME or not cls.RDS_USERNAME:
                raise ValueError("MySQL/RDS configuration requires RDS_HOSTNAME and RDS_USERNAME")
            pwd = f":{cls.RDS_PASSWORD}" if cls.RDS_PASSWORD else ""
            return f"mysql+pymysql://{cls.RDS_USERNAME}{pwd}@{cls.RDS_HOSTNAME}:{cls.RDS_PORT}/{cls.RDS_DB_NAME}"

        # Default fallback: SQLite
        return f"sqlite:///{cls.SQLITE_DB_PATH}"

    @classmethod
    def get_display_info(cls) -> dict:
        """Helper to show connection metadata on the dashboard."""
        url = cls.get_database_url()
        if "sqlite" in url:
            return {
                "engine": "SQLite (Local Dev)",
                "target": cls.SQLITE_DB_PATH,
                "is_rds": False
            }
        elif "postgresql" in url or "postgres" in url:
            return {
                "engine": "PostgreSQL (AWS RDS Ready)",
                "target": cls.RDS_HOSTNAME or "Custom Endpoint",
                "is_rds": True
            }
        elif "mysql" in url:
            return {
                "engine": "MySQL (AWS RDS Ready)",
                "target": cls.RDS_HOSTNAME or "Custom Endpoint",
                "is_rds": True
            }
        return {
            "engine": "SQL Database",
            "target": "Custom Database",
            "is_rds": False
        }

config = DatabaseConfig()
