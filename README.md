# ⚡ Habit CRM - Modern Habit Tracking System

> **A Python-based Habit Tracking CRM and Visual Analytics Platform built with FastAPI, SQLAlchemy, and native AWS RDS (PostgreSQL/MySQL) support.**

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![AWS RDS Ready](https://img.shields.io/badge/AWS%20RDS-PostgreSQL%20%2F%20MySQL-orange?logo=amazon-aws)](https://aws.amazon.com/rds/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Key Features

- **🗓️ Monday-to-Sunday Weekly Grid**: Displays the current week from Monday to Sunday with date headers, today highlighter, and 1-click interactive checkmarks.
- **🎯 10 Default Foundational Habits**: Pre-seeded with 10 habits spanning Fitness, Health, Learning, Mindfulness, Productivity, Nutrition, Cloud & Tech, and Sleep.
- **✏️ Fully Changeable & Customizable**: Add new habits, edit habit names/categories/icons/colors, or delete habits directly from the interface.
- **📅 Month & Week Filters**: Select any month (Jan–Dec) or jump across weeks (`‹ Prev Week`, `Next Week ›`, `Jump to Today`) with dynamic date calculations.
- **📊 Visual Charts & Analytics**:
  - **Weekly Trend Chart (Chart.js)**: Dual-axis Bar & Line chart tracking habits completed and completion percentages across Monday through Sunday.
  - **Category Donut Chart**: Breakdown of habit distribution and focus areas.
  - **Live Streak Counter**: Automatic calculation of current consecutive streaks and longest streaks.
- **☁️ AWS RDS Database Ready**:
  - Seamlessly toggle between local development (`SQLite`) and cloud database (`AWS RDS PostgreSQL` or `MySQL`) via `.env`.
  - Built-in connection pooling, auto-reconnect, and connection health diagnostics tool.

---

## 🏗️ Architecture

```
Habit_CRM/
├── main.py                  # FastAPI Application, Page Routes, & REST API
├── config.py                # Environment configuration & DB connection builder
├── database.py              # SQLAlchemy engine, session factory, & connection pooling
├── models.py                # Habit & HabitLog relational models with constraints
├── services.py              # Monday-Sunday date logic, streak calculation & chart aggregations
├── seed_data.py             # 10 default habits & initial week log generator
├── test_rds_connection.py   # Interactive AWS RDS connection diagnostic & migration tool
├── templates/
│   └── index.html           # Modern glassmorphic dashboard template (Jinja2)
├── static/
│   ├── css/style.css        # Dark theme styling, animations & responsive grid
│   └── js/app.js            # Chart.js charts, asynchronous tick toggles & modals
├── requirements.txt         # Project dependencies
├── .env.example             # Environment template (Local SQLite & AWS RDS)
└── README.md                # Comprehensive documentation & AWS RDS tutorial
```

---

## 🚀 Quick Start (Running Locally)

### 1. Clone the Repository
```bash
git clone https://github.com/iamshaneofc/Habit_CRM.git
cd Habit_CRM
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Launch
```bash
# Optional: customize .env (defaults to local SQLite if not configured)
cp .env.example .env

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## ☁️ Connecting to AWS RDS (Step-by-Step Learning Guide)

This application is engineered specifically to help you test and learn **Amazon Web Services (AWS) Relational Database Service (RDS)**.

### Step 1: Create an RDS Instance in AWS
1. Open the [AWS Management Console](https://console.aws.amazon.com/rds).
2. Choose **Databases** > **Create database**.
3. Choose **Standard create** and select **PostgreSQL** (or **MySQL**).
4. Under **Templates**, select **Free tier** (uses `db.t3.micro` or `db.t4g.micro`).
5. Configure DB settings:
   - **DB instance identifier**: `habit-crm-db`
   - **Master username**: `postgres`
   - **Master password**: *Choose a secure password*
6. In **Connectivity**:
   - **Public access**: Select **Yes** (required to connect from your local machine).
   - **VPC security group**: Choose or create a security group.
7. Under **Additional configuration**:
   - **Initial database name**: `habit_crm_db`
8. Click **Create database** (takes 3-5 minutes to become `Available`).

---

### Step 2: Configure AWS Security Group Inbound Rules
> **⚠️ Critical Gotcha**: By default, AWS blocks incoming external traffic.

1. In the RDS Console, click your new database instance.
2. Under **Connectivity & security**, click the link under **VPC security groups**.
3. Click the security group ID, select **Inbound rules**, and click **Edit inbound rules**.
4. Add a rule:
   - **Type**: `PostgreSQL` (Port `5432`) or `MySQL/Aurora` (Port `3306`)
   - **Source**: Select `My IP` (recommended for learning) or `Anywhere-IPv4` (`0.0.0.0/0` for testing)
5. Click **Save rules**.

---

### Step 3: Update `.env` with RDS Credentials
Open your `.env` file in the project root and fill in your AWS RDS endpoint details:

```ini
DB_TYPE=postgres
RDS_HOSTNAME=habit-crm-db.cxxxxxxx.us-east-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=habit_crm_db
RDS_USERNAME=postgres
RDS_PASSWORD=your_master_password
```

---

### Step 4: Run the RDS Diagnostics Tool
We created an automated diagnostic tool that tests DNS resolution, firewall/port connectivity, authentication, and creates the required tables automatically:

```bash
python test_rds_connection.py
```

Expected output:
```
=================================================================
      HABIT CRM - AWS RDS CONNECTIVITY & DIAGNOSTIC TOOL      
=================================================================
Current DB Mode: POSTGRES
Database Target: habit-crm-db.cxxxxxxx.us-east-1.rds.amazonaws.com

[1/4] Checking DNS Resolution & Network Reachability:
      [OK] DNS resolved successfully -> 54.210.xxx.xxx
      [OK] TCP Port 5432 is OPEN and reachable (Latency: 65.2 ms)

[2/4] Testing SQLAlchemy Connection & Authentication...
      [OK] Successfully connected to database engine!
      Engine Version: PostgreSQL 16.1

[3/4] Creating / Verifying Database Tables (habits, habit_logs)...
      [OK] Tables 'habits' and 'habit_logs' are ready in AWS RDS.

[4/4] Checking and Seeding Default Habits...
      [OK] Database initialized with 10 active habits.

=================================================================
  SUCCESS: AWS RDS is 100% connected, migrated, and ready!
=================================================================
```

---

### Step 5: Start Habit CRM with AWS RDS
```bash
uvicorn main:app --reload --port 8000
```
The header badge in the application will now illuminate cyan and display:  
**`PostgreSQL (AWS RDS Ready) • AWS RDS`**

---

## 📋 Default 10 Habits

| # | Habit Name | Category | Icon | Target | Description |
|---|---|---|---|---|---|
| 1 | Morning Workout | Fitness | 🏋️ | Daily | 30 mins strength training, jogging, or stretching |
| 2 | Drink 2.5L Water | Health | 💧 | Daily | Maintain hydration with 8-10 glasses daily |
| 3 | Read 20 Pages | Learning | 📚 | Daily | Read non-fiction, books, or technical articles |
| 4 | 15-min Meditation | Mindfulness | 🧘 | Daily | Mindful breathing and mental calmness |
| 5 | Deep Work (2 hrs) | Productivity | 🎯 | Daily | Undistracted high-impact focus session |
| 6 | Healthy Meal / No Junk | Nutrition | 🥗 | Daily | Whole food meals, limit refined sugar |
| 7 | AWS & Tech Practice | Career | 💻 | Daily | Hands-on labs: AWS RDS, Cloud, Python, DevOps |
| 8 | Sleep by 11:00 PM | Recovery | 🌙 | Daily | 7-8 hours quality sleep for recovery |
| 9 | 8,000 Steps Daily | Activity | 👟 | Daily | Evening walking or moving throughout the day |
| 10 | Gratitude & Reflection | Mindset | ✍️ | Daily | Write 3 wins and highlights before bed |

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main interactive Habit CRM weekly dashboard |
| `POST` | `/api/habits/toggle` | Toggles checkmark for habit on a specific date |
| `GET` | `/api/habits` | Retrieves all configured habits |
| `POST` | `/api/habits` | Creates a new habit |
| `PUT` | `/api/habits/{id}` | Updates/customizes an existing habit |
| `DELETE` | `/api/habits/{id}` | Deletes a habit and associated log history |
| `POST` | `/api/habits/reset-defaults` | Resets habits to original 10 foundational habits |
| `GET` | `/api/charts/weekly-data` | Monday-Sunday daily completion dataset for Chart.js |
| `GET` | `/api/database/status` | Current database connection metadata |

---

## 🛠️ Incremental Development Steps

- **Step 1**: Initialize Habit CRM project structure, `.gitignore`, and `requirements.txt`.
- **Step 2**: Setup SQLAlchemy database layer with AWS RDS & SQLite configuration (`config.py`, `database.py`).
- **Step 3**: Define relational models with constraints (`Habit`, `HabitLog` in `models.py`).
- **Step 4**: Implement 10 default habits seed data generator (`seed_data.py`).
- **Step 5**: Add Monday-Sunday weekly date calculations and streak tracking service (`services.py`).
- **Step 6**: Implement FastAPI server, page routing, and REST API endpoints (`main.py`).
- **Step 7**: Build interactive weekly habit tracker grid with Monday-Sunday tick controls (`templates/index.html`).
- **Step 8**: Integrate Chart.js visualizations for weekly trends and monthly analytics (`style.css`, `app.js`).
- **Step 9**: Add AWS RDS database connectivity test suite and migration tool (`test_rds_connection.py`).
- **Step 10**: Add comprehensive README with AWS RDS deployment guide and habit CRM documentation.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
