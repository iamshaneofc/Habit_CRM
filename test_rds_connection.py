"""
AWS RDS Database Connectivity & Diagnostics Tool for Habit CRM
==============================================================
Use this script to test and troubleshoot your AWS RDS PostgreSQL / MySQL connection.
It checks:
  1. Environment variable configuration
  2. DNS resolution of your AWS RDS endpoint
  3. TCP socket reachability (checks AWS Security Group inbound rules)
  4. Database authentication and SSL handshake
  5. Table creation (schema migration)
  6. Default 10 habits seeding in AWS RDS
"""

import os
import sys
import socket
import time
from dotenv import load_dotenv

# Force load latest .env
load_dotenv(override=True)

def print_banner():
    print("=" * 65)
    print("      HABIT CRM - AWS RDS CONNECTIVITY & DIAGNOSTIC TOOL      ")
    print("=" * 65)

def test_dns_and_socket(host: str, port: int) -> bool:
    print(f"\n[1/4] Checking DNS Resolution & Network Reachability:")
    print(f"      Target: {host}:{port}")
    
    # 1. DNS Resolution
    try:
        ip = socket.gethostbyname(host)
        print(f"      [OK] DNS resolved successfully -> {ip}")
    except socket.gaierror as e:
        print(f"      [FAILED] Cannot resolve hostname '{host}'.")
        print(f"      Details: {e}")
        print("      Troubleshooting tip: Check for typos in your RDS endpoint string.")
        return False

    # 2. TCP Port Connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        latency = round((time.time() - start_time) * 1000, 2)
        sock.close()

        if result == 0:
            print(f"      [OK] TCP Port {port} is OPEN and reachable (Latency: {latency} ms)")
            return True
        else:
            print(f"      [FAILED] Connection refused or timed out on port {port}.")
            print_security_group_help(port)
            return False
    except Exception as e:
        print(f"      [FAILED] Socket error: {e}")
        print_security_group_help(port)
        return False

def print_security_group_help(port: int):
    print("\n" + "!" * 65)
    print("  COMMON AWS RDS GOTCHA: VPC SECURITY GROUP INBOUND RULES")
    print("!" * 65)
    print("  Your RDS instance could not be reached. Common causes:")
    print(f"  1. In the AWS RDS Console, your instance must have 'Publicly Accessible' = Yes")
    print(f"  2. In your VPC Security Group (Inbound Rules), add a rule:")
    print(f"     - Type: PostgreSQL (or MySQL)")
    print(f"     - Port: {port}")
    print(f"     - Source: 'My IP' (or 0.0.0.0/0 for testing)")
    print("!" * 65 + "\n")

def main():
    print_banner()

    from config import config
    db_url = config.get_database_url()
    db_type = config.DB_TYPE

    print(f"Current DB Mode: {db_type.upper()}")
    print(f"Database Target: {config.get_display_info()['target']}")

    if "sqlite" in db_url:
        print("\nNotice: You are currently running in local SQLite mode.")
        print("To test AWS RDS, configure your .env file with:")
        print("  DB_TYPE=postgres")
        print("  RDS_HOSTNAME=your-rds-endpoint.xxxxxx.us-east-1.rds.amazonaws.com")
        print("  RDS_PORT=5432")
        print("  RDS_DB_NAME=habit_crm_db")
        print("  RDS_USERNAME=postgres")
        print("  RDS_PASSWORD=your_password")
        print("\nTesting local SQLite database integrity instead...")
        from database import engine, Base, SessionLocal
        from models import Habit
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        count = db.query(Habit).count()
        db.close()
        print(f"[OK] Local SQLite is working cleanly. Total habits: {count}")
        return

    # For AWS RDS PostgreSQL or MySQL:
    host = config.RDS_HOSTNAME
    port = config.RDS_PORT

    if not host:
        print("[ERROR] RDS_HOSTNAME is missing in .env")
        sys.exit(1)

    # Step 1: DNS & Socket
    if not test_dns_and_socket(host, port):
        print("\nCannot establish TCP connection to AWS RDS. Fix network/security group settings.")
        sys.exit(1)

    # Step 2: SQLAlchemy Connection & Auth
    print(f"\n[2/4] Testing SQLAlchemy Connection & Authentication...")
    try:
        from database import engine, Base, SessionLocal
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print(f"      [OK] Successfully connected to database engine!")
            print(f"      Engine Version: {result[0] if result else 'Unknown'}")
    except Exception as e:
        print(f"      [FAILED] Database authentication error:")
        print(f"      {e}")
        print("      Troubleshooting tip: Verify RDS_USERNAME, RDS_PASSWORD, and RDS_DB_NAME.")
        sys.exit(1)

    # Step 3: Schema Migration
    print(f"\n[3/4] Creating / Verifying Database Tables (habits, habit_logs)...")
    try:
        from models import Habit, HabitLog
        Base.metadata.create_all(bind=engine)
        print("      [OK] Tables 'habits' and 'habit_logs' are ready in AWS RDS.")
    except Exception as e:
        print(f"      [FAILED] Error creating tables: {e}")
        sys.exit(1)

    # Step 4: Seed Default Habits
    print(f"\n[4/4] Checking and Seeding Default Habits...")
    try:
        from seed_data import seed_default_habits
        db = SessionLocal()
        seed_default_habits(db, force=False, seed_sample_logs=True)
        total_habits = db.query(Habit).count()
        db.close()
        print(f"      [OK] Database initialized with {total_habits} active habits.")
    except Exception as e:
        print(f"      [FAILED] Error during data seeding: {e}")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("  SUCCESS: AWS RDS is 100% connected, migrated, and ready!")
    print("  You can now start the application with: uvicorn main:app --reload")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
