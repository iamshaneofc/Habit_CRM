# ⚡ Habit CRM — Personal Consistency Operating System (Phase 1)

> **A secure, high-performance Habit Tracking System built with Python, FastAPI, SQLAlchemy ORM, Alembic migrations, Chart.js, and native AWS RDS (PostgreSQL/MySQL) readiness.**

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-8A2BE2.svg)](https://alembic.sqlalchemy.org/)
[![AWS RDS Ready](https://img.shields.io/badge/AWS%20RDS-PostgreSQL%20%2F%20MySQL-orange?logo=amazon-aws)](https://aws.amazon.com/rds/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Product Overview & Phase 1 Scope

**Habit CRM** is the foundational consistency engine of a future personal Life OS. 

### Phase 1 Objectives & Deliverables
- **Reliable Weekly Tracking**: Dominant Monday–Sunday grid with one-click toggles, date boundaries, and future-date locking.
- **Authentication & Security**: Multi-user support with bcrypt-hashed passwords, signed JWT tokens in secure HTTP-only cookies, IP-based rate limiting, and security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`).
- **Strict Data Isolation**: Server-enforced user ownership on habits, completion logs, notes, and analytics.
- **Habit Lifecycle & Archival**: Safe soft-deletion (`archive`) preserving historical logs and metrics, with instant restoration and explicit hard-deletion.
- **Habit Reflection Notes**: Day-specific reflection notes with modal management and cell badge indicators.
- **Analytics & Real-time Charts**: Current and longest streak calculation, 7-day daily completion trend bar/line chart, category distribution donut, and top performer star habit insight.
- **Responsive Layout & Accessibility**: High-contrast glassmorphic dark theme, sticky habit headers on mobile horizontal scroll, 38px+ touch targets, keyboard focus outlines (`:focus-visible`), modal dialog accessibility, and reduced-motion support.
- **Database Migrations & Reliability**: Version-controlled Alembic schema migrations and dev-mode fallback to local SQLite when remote databases are unreachable.

*Note: Future Life OS modules (Tasks & Schedule, Knowledge & Journal, Skills, AI Assistant, Projects & Goals) are deliberately deferred to future development phases.*

---

## 🏗️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10–3.14) | High-performance asynchronous web APIs and page routing |
| **Database ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Relational database mapping with connection pooling and batch queries |
| **Schema Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Version-controlled database schema evolution with batch SQLite support |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict request schema, email format, and boundary validation |
| **Authentication** | [PyJWT](https://pyjwt.readthedocs.io/) & [Bcrypt](https://pypi.org/project/bcrypt/) | Stateless signed JWTs, salt-hashed passwords, HTTP-only session cookies |
| **Frontend Templates** | [Jinja2](https://palletsprojects.com/p/jinja/) | Server-rendered HTML with component partials and CSRF/session cookies |
| **Data Visualizations** | [Chart.js 4.4](https://www.chartjs.org/) | Responsive interactive canvas charts for weekly trends and category donuts |
| **Styling** | Custom Vanilla CSS | Tailored dark glassmorphic design system with zero external CSS frameworks |
| **Databases Supported** | SQLite (Dev) / PostgreSQL / MySQL | Local development database with seamless AWS RDS cloud deployment |

---

## 📁 Repository Structure

```
Habit_CRM/
├── alembic/                    # Database migration configuration & scripts
│   ├── versions/               # Version-controlled migration revisions
│   │   ├── f4e30b9e76d1_baseline_habits_and_logs.py
│   │   ├── e0c9f3d4842b_add_users_table.py
│   │   └── 5fb6a13d78f9_add_user_ownership.py
│   └── env.py                  # Alembic environment and connection builder
├── backups/                    # Local database backups and JSON baselines
│   ├── habits_baseline.db
│   └── baseline_backup.json
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Design tokens, glassmorphism, responsive breakpoints
│   └── js/
│       └── app.js              # Optimistic UI toggling, Chart.js updates, note modals
├── templates/                  # Server-rendered Jinja2 templates
│   ├── index.html              # Main dashboard (dominant tracker + right visual sidebar)
│   ├── login.html              # Secure user sign-in page
│   └── register.html           # New user registration page
├── tests/                      # Automated test suite (13 test modules)
│   ├── test_step6_dates.py
│   ├── test_step7_crud_archival.py
│   ├── test_step8_habit_logs.py
│   ├── test_step9_metrics_streaks.py
│   ├── test_step10_charts.py
│   ├── test_step11_controls.py
│   ├── test_step12_ui_layout.py
│   ├── test_step13_visual_elements.py
│   ├── test_step14_responsive_a11y.py
│   ├── test_step15_security.py
│   ├── test_step16_user_isolation.py
│   ├── test_step16_migrations.py
│   ├── test_step17_performance.py
│   └── test_step18_e2e_journey.py
├── auth.py                     # Password hashing, JWT token handling, rate limiting
├── config.py                   # Environment configuration & sanitized display info
├── database.py                 # Engine initialization, get_db session dependency
├── main.py                     # FastAPI application endpoints & security middleware
├── models.py                   # Relational ORM models (User, Habit, HabitLog)
├── services.py                 # Monday-Sunday date logic, streak algorithms, metrics
├── seed_data.py                # User-specific default 10 foundational habits seeder
├── test_rds_connection.py      # Network, DNS, and database connectivity diagnostic tool
├── run_all_tests.py            # Consolidated master automated test runner
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration file
├── .env.example                # Safe environment variable template (placeholders only)
├── PHASE_1_STATUS.md           # Implementation checklist and commit tracker
└── README.md                   # Comprehensive technical documentation
```

---

## 💻 Prerequisites

- **Python**: Version `3.10` or higher (`3.11`, `3.12`, or `3.14` tested and verified).
- **Package Manager**: `pip` (included with standard Python installations).
- **Git**: For version control and deployment.
- **Optional**: AWS Account with RDS PostgreSQL or MySQL instance for cloud database deployment.

---

## 🛠️ Local Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/iamshaneofc/Habit_CRM.git
cd Habit_CRM
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to suit your environment:
```ini
# Application Environment
ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=generate_a_secure_random_key_here

# Database Selection: sqlite | postgres | mysql
DB_TYPE=sqlite
SQLITE_DB_PATH=habits.db

# AWS RDS Configuration (Required only when DB_TYPE=postgres or mysql)
RDS_HOSTNAME=your-rds-endpoint.xxxxxx.us-east-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=habit_crm_db
RDS_USERNAME=your_db_username
RDS_PASSWORD=your_db_password
RDS_SSLMODE=prefer
```

> **🔒 Security Notice**: Never commit `.env` or real database passwords. `.gitignore` is configured to prevent staging secrets, database files, and SSL certificates.

---

## 🗄️ Database Migrations

This project uses **Alembic** for schema migrations.

### Apply All Migrations (Upgrade to Head)
```bash
python -m alembic upgrade head
```

### Check Current Migration Revision
```bash
python -m alembic current
```

### Generate a New Migration Revision (After Model Changes)
```bash
python -m alembic revision --autogenerate -m "describe_change"
```

### Roll Back Last Migration
```bash
python -m alembic downgrade -1
```

---

## 🧪 Running Automated Tests

A comprehensive suite of **13 test modules** protects against domain, authorization, and UI regressions.

### Run All Test Suites via Master Runner
```bash
python run_all_tests.py
```

Expected output:
```
======================================================================
          HABIT CRM — PHASE 1 MASTER AUTOMATED TEST SUITE          
======================================================================
Executing 13 test suites...

--> Running: Step 6: Dates & Weekly Boundaries (tests/test_step6_dates.py)... [PASS]
--> Running: Step 7: Habit CRUD & Archival (tests/test_step7_crud_archival.py)... [PASS]
--> Running: Step 8: Habit Logs & Reflection Notes (tests/test_step8_habit_logs.py)... [PASS]
--> Running: Step 9: Metrics, Streaks & Analytics (tests/test_step9_metrics_streaks.py)... [PASS]
--> Running: Step 10: Dynamic Charts & Data Endpoints (tests/test_step10_charts.py)... [PASS]
--> Running: Step 11: Controls & Form Validation (tests/test_step11_controls.py)... [PASS]
--> Running: Step 12: Desktop Layout & Grid Structure (tests/test_step12_ui_layout.py)... [PASS]
--> Running: Step 13: Top Performer & Consistency Insights (tests/test_step13_visual_elements.py)... [PASS]
--> Running: Step 14: Responsive Breakpoints & Accessibility (tests/test_step14_responsive_a11y.py)... [PASS]
--> Running: Step 15: Security Hardening & Rate Limiting (tests/test_step15_security.py)... [PASS]
--> Running: Step 16: Cross-User Isolation & Auth Boundaries (tests/test_step16_user_isolation.py)... [PASS]
--> Running: Step 16: Alembic Migrations on Fresh DB (tests/test_step16_migrations.py)... [PASS]
--> Running: Step 17: Performance & Query Optimization (tests/test_step17_performance.py)... [PASS]
--> Running: Step 18: 20-Point End-to-End User Journey (tests/test_step18_e2e_journey.py)... [PASS]

Total Suites: 13 | Passed: 13 | Failed: 0
All 13 test suites passed successfully! Regression coverage confirmed.
```

### Run Specific Test Modules
```bash
# Test 20-point end-to-end user journey
python tests/test_step18_e2e_journey.py

# Test user isolation and cross-account authorization boundaries
python tests/test_step16_user_isolation.py

# Test database migrations on disposable database
python tests/test_step16_migrations.py
```

---

## 🚀 Starting the Application

Start the local development server with Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

Open your browser at:
👉 **`http://localhost:8000`**

- Unauthenticated visitors are automatically directed to `/login`.
- Click **"Sign Up"** (`/register`) to create your personal account.
- New accounts are automatically seeded with the 10 foundational habits.

---

## ☁️ AWS RDS Database Deployment

To connect Habit CRM to an **Amazon Web Services (AWS) RDS** PostgreSQL or MySQL database:

### 1. Test Network & Firewall Connectivity
Run the built-in diagnostic tool to test DNS resolution, port reachability, and authentication before starting the server:
```bash
python test_rds_connection.py
```

### 2. Common Security Group Configuration
In the AWS Console:
- Navigate to **RDS > Databases > Your Database**.
- Ensure **Publicly Accessible** is set to `Yes` (if accessing outside AWS VPC).
- In the VPC Security Group **Inbound Rules**, add:
  - **Type**: `PostgreSQL` (port `5432`) or `MySQL` (port `3306`).
  - **Source**: `My IP` (recommended) or your application server's static IP.

### 3. Graceful Fallback in Development
If AWS RDS is configured in `.env` but cannot be reached (e.g., DNS failure, offline network), the application automatically logs a diagnostic message and falls back to local SQLite (`habits.db`) to ensure a zero-friction local development experience.

---

## 💾 Backup & Data Recovery

### SQLite (Local Development)
- Regular snapshots of `habits.db` are stored in `backups/`.
- A baseline JSON snapshot of the initial default records is available at `backups/baseline_backup.json`.
- To create a fresh backup:
  ```bash
  # Windows PowerShell
  Copy-Item habits.db "backups\habits_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
  
  # Linux / macOS
  cp habits.db backups/habits_backup_$(date +%Y%m%d_%H%M%S).db
  ```

### AWS RDS (Cloud Production)
- Enable **Automated Backups** in AWS RDS console (recommended retention: 7 to 35 days).
- Create a manual DB snapshot prior to performing major migrations or destructive maintenance.

---

## ⚠️ Known Limitations & Deployment Considerations

1. **Production Deployment**:
   - The application has completed end-to-end local testing. For production internet deployment, configure HTTPS termination (e.g. via Nginx reverse proxy, AWS ALB, or Cloudflare) with `ENV=production` to enforce `secure=True` session cookies.
2. **Offline Remote RDS in Local Environment**:
   - The remote RDS endpoint specified in the default environment is unreachable without active VPC routing; local development safely falls back to SQLite.
3. **Session Cookies**:
   - Session cookies utilize `SameSite=Lax` and `HttpOnly`. In production, ensure the client accesses the dashboard via HTTPS.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
