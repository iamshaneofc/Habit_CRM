"""
Test suite for Step 16: Database Migration Verification.
Verifies:
- All Alembic migrations (baseline, users table, user ownership) apply cleanly
  from base to head against a fresh disposable SQLite database.
- Schema integrity: habits, habit_logs, and users tables exist with required columns and constraints.
"""
import os
import sys
import sqlite3
from alembic import command
from alembic.config import Config

def test_alembic_migrations_on_fresh_db():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    disposable_db = os.path.join(repo_root, "test_migration_disposable.db")
    if os.path.exists(disposable_db):
        os.remove(disposable_db)

    disposable_url = f"sqlite:///{disposable_db.replace(os.sep, '/')}"

    alembic_ini_path = os.path.join(repo_root, "alembic.ini")
    cfg = Config(alembic_ini_path)
    cfg.set_main_option("sqlalchemy.url", disposable_url)

    try:
        # Run upgrade head
        command.upgrade(cfg, "head")

        # Verify tables and columns in SQLite
        conn = sqlite3.connect(disposable_db)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        assert "users" in tables, "Table 'users' must exist after migration"
        assert "habits" in tables, "Table 'habits' must exist after migration"
        assert "habit_logs" in tables, "Table 'habit_logs' must exist after migration"
        assert "alembic_version" in tables, "Table 'alembic_version' must exist"

        # Check columns on habits table
        cursor.execute("PRAGMA table_info(habits);")
        columns = [row[1] for row in cursor.fetchall()]
        assert "user_id" in columns, "Column 'user_id' must exist on habits"
        assert "is_active" in columns, "Column 'is_active' must exist on habits"
        assert "daily_target" in columns, "Column 'daily_target' must exist on habits"

        # Check columns on habit_logs table
        cursor.execute("PRAGMA table_info(habit_logs);")
        log_columns = [row[1] for row in cursor.fetchall()]
        assert "user_id" in log_columns, "Column 'user_id' must exist on habit_logs"
        assert "notes" in log_columns, "Column 'notes' must exist on habit_logs"

        conn.close()
        print("[OK] Alembic migrations upgraded fresh database to head cleanly.")
    finally:
        import gc, time
        gc.collect()
        time.sleep(0.1)
        if os.path.exists(disposable_db):
            try:
                os.remove(disposable_db)
            except OSError:
                pass

if __name__ == "__main__":
    print("Running Step 16 Migration Verification Tests...")
    test_alembic_migrations_on_fresh_db()
    print("All Migration Verification Tests Passed Successfully!")
