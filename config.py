import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()

class DatabaseConfig:
    APP_ENV: str = os.getenv("APP_ENV", "development").lower()
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "habit-crm-insecure-dev-key-change-in-prod")

    # DB selection: 'sqlite' | 'postgres' | 'mysql'
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").lower()

    # SQLite
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "habits.db")

    # AWS RDS Connection Parameters
    RDS_HOSTNAME: Optional[str] = os.getenv("RDS_HOSTNAME")
    RDS_DB_NAME: str = os.getenv("RDS_DB_NAME", "habit_crm_db")
    RDS_USERNAME: Optional[str] = os.getenv("RDS_USERNAME")
    RDS_PASSWORD: Optional[str] = os.getenv("RDS_PASSWORD")

    # Direct URL Override
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Fallback to SQLite in development if remote DB is unreachable
    DB_FALLBACK_SQLITE: bool = os.getenv("DB_FALLBACK_SQLITE", "true").lower() in ("true", "1", "yes")
    _active_fallback: bool = False

    @classmethod
    def is_production(cls) -> bool:
        return cls.APP_ENV == "production"

    @classmethod
    def get_port(cls) -> int:
        port_env = os.getenv("RDS_PORT")
        if port_env and port_env.strip():
            try:
                return int(port_env.strip())
            except ValueError:
                pass
        return 3306 if cls.DB_TYPE == "mysql" else 5432

    @classmethod
    def get_database_url(cls) -> str:
        """Returns SQLAlchemy-compatible connection string."""
        if cls.DATABASE_URL and cls.DATABASE_URL.strip():
            return cls.DATABASE_URL.strip()

        port = cls.get_port()

        if cls.DB_TYPE in ("postgres", "postgresql"):
            if not cls.RDS_HOSTNAME or not cls.RDS_USERNAME:
                raise ValueError("PostgreSQL/RDS configuration requires RDS_HOSTNAME and RDS_USERNAME")
            pwd = f":{cls.RDS_PASSWORD}" if cls.RDS_PASSWORD else ""
            ssl_cert = os.getenv("RDS_SSL_CERT")
            query_params = ""
            if ssl_cert and os.path.exists(ssl_cert):
                query_params = f"?sslmode=verify-full&sslrootcert={ssl_cert}"
            elif os.getenv("RDS_SSLMODE"):
                query_params = f"?sslmode={os.getenv('RDS_SSLMODE')}"
            return f"postgresql+psycopg2://{cls.RDS_USERNAME}{pwd}@{cls.RDS_HOSTNAME}:{port}/{cls.RDS_DB_NAME}{query_params}"

        elif cls.DB_TYPE == "mysql":
            if not cls.RDS_HOSTNAME or not cls.RDS_USERNAME:
                raise ValueError("MySQL/RDS configuration requires RDS_HOSTNAME and RDS_USERNAME")
            pwd = f":{cls.RDS_PASSWORD}" if cls.RDS_PASSWORD else ""
            return f"mysql+pymysql://{cls.RDS_USERNAME}{pwd}@{cls.RDS_HOSTNAME}:{port}/{cls.RDS_DB_NAME}"

        # Default fallback: SQLite
        return f"sqlite:///{cls.SQLITE_DB_PATH}"

    @classmethod
    def get_display_info(cls) -> dict:
        """Helper to show connection metadata on the dashboard securely."""
        if cls._active_fallback:
            return {
                "engine": "SQLite (Dev Fallback)",
                "target": cls.SQLITE_DB_PATH,
                "is_rds": False,
                "fallback_active": True
            }

        url = cls.get_database_url()
        if "sqlite" in url:
            return {
                "engine": "SQLite (Local Dev)",
                "target": cls.SQLITE_DB_PATH,
                "is_rds": False,
                "fallback_active": False
            }
        elif "postgresql" in url or "postgres" in url:
            return {
                "engine": "PostgreSQL (AWS RDS Ready)",
                "target": cls.RDS_HOSTNAME or "Custom Endpoint",
                "is_rds": True,
                "fallback_active": False
            }
        elif "mysql" in url:
            return {
                "engine": "MySQL (AWS RDS Ready)",
                "target": cls.RDS_HOSTNAME or "Custom Endpoint",
                "is_rds": True,
                "fallback_active": False
            }
        return {
            "engine": "SQL Database",
            "target": "Custom Database",
            "is_rds": False,
            "fallback_active": False
        }

config = DatabaseConfig()
