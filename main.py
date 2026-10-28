import os
from datetime import date, datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import config
import database
from database import Base, get_db, check_and_stabilize_db
from models import Habit, HabitLog
from seed_data import seed_default_habits
import services

# Setup database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify and stabilize connection before creating tables
    ok, status = check_and_stabilize_db()
    if not ok:
        print(f"[CRITICAL] Database connection failed: {status}")
        if config.is_production():
            raise RuntimeError(f"Database unavailable: {status}")
    else:
        try:
            # Ensure tables exist
            Base.metadata.create_all(bind=database.engine)
            # Seed default 10 habits if table is empty
            db = database.SessionLocal()
            try:
                seed_default_habits(db, force=False, seed_sample_logs=True)
            finally:
                db.close()
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
            if config.is_production():
                raise
    yield

app = FastAPI(
    title="Habit CRM - Habit Tracking System",
    description="Python Habit Tracker with AWS RDS support, interactive weekly Monday-Sunday tracking and analytics",
    version="1.0.0",
    lifespan=lifespan
)

# Ensure directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ========================================================
# Pydantic Schemas for API Requests
# ========================================================
class ToggleRequest(BaseModel):
    habit_id: int
    date: str  # YYYY-MM-DD

class HabitCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field("General", max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field("🎯", max_length=10)
    color: Optional[str] = Field("#10b981", max_length=20)
    display_order: Optional[int] = 0

class HabitUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

# ========================================================
# Web Pages
# ========================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    week_date: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Main Habit Tracking Dashboard.
    Shows the current Monday-to-Sunday view, month filters, streak metrics, and visual charts.
    """
    today = date.today()
    target_dt = today

    if week_date:
        try:
            target_dt = date.fromisoformat(week_date)
        except ValueError:
            target_dt = today
    elif month and year:
        # Jump to first week of requested month
        try:
            target_dt = date(year, month, 1)
        except ValueError:
            target_dt = today

    current_year = target_dt.year
    current_month = target_dt.month

    grid = services.get_weekly_grid(db, target_dt)
    monthly_stats = services.get_monthly_summary(db, current_year, current_month)
    db_info = config.get_display_info()

    # List of months for filter dropdown
    months_list = [
        {"num": i, "name": datetime(2000, i, 1).strftime("%B"), "is_selected": i == current_month}
        for i in range(1, 13)
    ]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "grid": grid,
        "monthly_stats": monthly_stats,
        "db_info": db_info,
        "today_str": today.isoformat(),
        "selected_month": current_month,
        "selected_year": current_year,
        "months_list": months_list
    })

# ========================================================
# REST API Endpoints
# ========================================================
@app.post("/api/habits/toggle")
async def toggle_habit_day(payload: ToggleRequest, db: Session = Depends(get_db)):
    """
    Toggles completion tick for a habit on a specific date.
    Returns the new state, streak count, and daily completion % for instant UI update.
    """
    try:
        log_date = date.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    habit = db.query(Habit).filter(Habit.id == payload.habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = db.query(HabitLog).filter(
        HabitLog.habit_id == payload.habit_id,
        HabitLog.date == log_date
    ).first()

    if log:
        log.completed = not log.completed
        log.value = 1 if log.completed else 0
        new_state = log.completed
    else:
        new_state = True
        log = HabitLog(
            habit_id=payload.habit_id,
            date=log_date,
            completed=True,
            value=1
        )
        db.add(log)

    db.commit()

    streak_info = services.calculate_habit_streak(payload.habit_id, db)
    
    # Calculate updated overall week completion
    monday, sunday = services.get_week_range(log_date)
    week_logs_count = db.query(HabitLog).filter(
        HabitLog.date >= monday,
        HabitLog.date <= sunday,
        HabitLog.completed == True
    ).count()

    total_active_habits = db.query(Habit).filter(Habit.is_active == True).count()
    overall_week_pct = round((week_logs_count / (total_active_habits * 7)) * 100) if total_active_habits > 0 else 0

    return {
        "success": True,
        "habit_id": payload.habit_id,
        "date": payload.date,
        "completed": new_state,
        "current_streak": streak_info["current_streak"],
        "longest_streak": streak_info["longest_streak"],
        "overall_week_pct": overall_week_pct
    }

@app.get("/api/habits")
async def get_habits(db: Session = Depends(get_db)):
    """Fetch all habits."""
    habits = db.query(Habit).order_by(Habit.display_order.asc(), Habit.id.asc()).all()
    return [h.to_dict() for h in habits]

@app.post("/api/habits")
async def create_habit(payload: HabitCreateRequest, db: Session = Depends(get_db)):
    """Add a new custom habit."""
    habit = Habit(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        icon=payload.icon or "🎯",
        color=payload.color or "#10b981",
        display_order=payload.display_order or 0,
        is_active=True
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return {"success": True, "habit": habit.to_dict()}

@app.put("/api/habits/{habit_id}")
async def update_habit(habit_id: int, payload: HabitUpdateRequest, db: Session = Depends(get_db)):
    """Change / customize an existing habit."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if payload.name is not None:
        habit.name = payload.name
    if payload.category is not None:
        habit.category = payload.category
    if payload.description is not None:
        habit.description = payload.description
    if payload.icon is not None:
        habit.icon = payload.icon
    if payload.color is not None:
        habit.color = payload.color
    if payload.is_active is not None:
        habit.is_active = payload.is_active
    if payload.display_order is not None:
        habit.display_order = payload.display_order

    db.commit()
    db.refresh(habit)
    return {"success": True, "habit": habit.to_dict()}

@app.delete("/api/habits/{habit_id}")
async def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """Delete a habit and its associated logs."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return {"success": True, "message": f"Habit '{habit.name}' deleted"}

@app.post("/api/habits/reset-defaults")
async def reset_default_habits(db: Session = Depends(get_db)):
    """Reset to the original 10 default habits."""
    seed_default_habits(db, force=True, seed_sample_logs=True)
    return {"success": True, "message": "Reset to 10 default habits successfully"}

@app.get("/api/charts/weekly-data")
async def get_weekly_chart_data(week_date: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns day-by-day Monday through Sunday completion data for Chart.js."""
    target_dt = date.fromisoformat(week_date) if week_date else date.today()
    grid = services.get_weekly_grid(db, target_dt)
    return {
        "labels": [d["day_name"] for d in grid["daily_chart_data"]],
        "completed": [d["completed_count"] for d in grid["daily_chart_data"]],
        "percentages": [d["percentage"] for d in grid["daily_chart_data"]],
        "total_habits": grid["habits_count"]
    }

@app.get("/api/database/status")
async def database_status():
    """Returns database configuration and connectivity status securely."""
    is_connected = False
    try:
        from sqlalchemy import text
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            is_connected = True
    except Exception:
        is_connected = False

    return {
        "status": "connected" if is_connected else "disconnected",
        "info": config.get_display_info(),
        "is_fallback": getattr(config, "_active_fallback", False)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.APP_HOST, port=config.APP_PORT, reload=True)

