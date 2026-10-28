import os
from datetime import date, datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config import config
import database
from database import Base, get_db, check_and_stabilize_db
from models import Habit, HabitLog, User
import auth
from auth import get_current_user, get_current_user_optional, SESSION_COOKIE_NAME, check_rate_limit
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

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Ensure directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ========================================================
# Pydantic Schemas for API Requests
# ========================================================
class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format.")
        return clean

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format.")
        return clean

class ToggleRequest(BaseModel):
    habit_id: int
    date: str  # YYYY-MM-DD
    notes: Optional[str] = None

class HabitLogNoteRequest(BaseModel):
    habit_id: int
    date: str  # YYYY-MM-DD
    notes: Optional[str] = Field(None, max_length=255)

class HabitCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field("General", max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field("🎯", max_length=10)
    color: Optional[str] = Field("#10b981", max_length=20)
    daily_target: Optional[int] = Field(1, ge=1, le=100)
    display_order: Optional[int] = 0

class HabitUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=20)
    daily_target: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

# ========================================================
# Web Pages
# ========================================================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: Optional[User] = Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, current_user: Optional[User] = Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/logout")
async def logout_redirect():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    week_date: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Main Habit Tracking Dashboard.
    Requires authentication; redirects unauthenticated visitors to /login.
    """
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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

    # Auto-seed default habits for fresh user accounts
    user_habit_count = db.query(Habit).filter(Habit.user_id == current_user.id).count()
    if user_habit_count == 0:
        seed_default_habits(db, force=False, seed_sample_logs=True, user_id=current_user.id)

    grid = services.get_weekly_grid(db, target_dt, user_id=current_user.id)
    monthly_stats = services.get_monthly_summary(db, current_year, current_month, user_id=current_user.id)
    db_info = config.get_display_info()

    # List of months for filter dropdown
    months_list = [
        {"num": i, "name": datetime(2000, i, 1).strftime("%B"), "is_selected": i == current_month}
        for i in range(1, 13)
    ]
    current_calendar_year = today.year
    years_list = list(range(current_calendar_year - 2, current_calendar_year + 3))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "grid": grid,
        "monthly_stats": monthly_stats,
        "db_info": db_info,
        "today_str": today.isoformat(),
        "selected_month": current_month,
        "selected_year": current_year,
        "months_list": months_list,
        "years_list": years_list
    })

# ========================================================
# REST API Endpoints: Authentication
# ========================================================
@app.post("/api/auth/register")
async def register_api(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user account with rate limit protection."""
    check_rate_limit(request, action="register", max_attempts=10, window_seconds=60)

    clean_email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        email=clean_email,
        hashed_password=auth.hash_password(payload.password),
        full_name=payload.full_name.strip() if payload.full_name else None,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Seed initial default habits for the new user
    seed_default_habits(db, force=False, seed_sample_logs=True, user_id=user.id)

    token = auth.create_access_token({"sub": str(user.id), "email": user.email})
    response = JSONResponse({
        "success": True,
        "message": "Account created successfully.",
        "token": token,
        "user": user.to_dict()
    })
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=config.is_production(),
        max_age=7 * 24 * 3600
    )
    return response

@app.post("/api/auth/login")
async def login_api(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates a user and issues an HTTP-only session cookie and JWT with brute-force rate limit protection."""
    check_rate_limit(request, action="login", max_attempts=15, window_seconds=60)

    clean_email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    token = auth.create_access_token({"sub": str(user.id), "email": user.email})
    response = JSONResponse({
        "success": True,
        "message": "Signed in successfully.",
        "token": token,
        "user": user.to_dict()
    })
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=config.is_production(),
        max_age=7 * 24 * 3600
    )
    return response

@app.post("/api/auth/logout")
async def logout_api():
    """Clears the session cookie."""
    response = JSONResponse({"success": True, "message": "Signed out successfully."})
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns details for the currently authenticated user."""
    return {"success": True, "user": current_user.to_dict()}

# ========================================================
# REST API Endpoints: Habits
# ========================================================
@app.post("/api/habits/toggle")
async def toggle_habit_day(
    payload: ToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggles completion tick for a user's habit on a specific date.
    Returns the new state, streak count, and daily completion % for instant UI update.
    Rejects future-date checkmark toggling.
    """
    try:
        log_date = date.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    today = date.today()
    if log_date > today:
        raise HTTPException(status_code=400, detail="Future dates cannot be marked complete.")

    habit = db.query(Habit).filter(Habit.id == payload.habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = db.query(HabitLog).filter(
        HabitLog.habit_id == payload.habit_id,
        HabitLog.user_id == current_user.id,
        HabitLog.date == log_date
    ).first()

    if log:
        log.completed = not log.completed
        log.value = 1 if log.completed else 0
        if payload.notes is not None:
            log.notes = payload.notes.strip() if payload.notes else None
        new_state = log.completed
    else:
        new_state = True
        log = HabitLog(
            user_id=current_user.id,
            habit_id=payload.habit_id,
            date=log_date,
            completed=True,
            value=1,
            notes=payload.notes.strip() if payload.notes else None
        )
        db.add(log)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Handle concurrent / duplicate toggle safely
        log = db.query(HabitLog).filter(
            HabitLog.habit_id == payload.habit_id,
            HabitLog.user_id == current_user.id,
            HabitLog.date == log_date
        ).first()
        if log:
            log.completed = not log.completed
            log.value = 1 if log.completed else 0
            if payload.notes is not None:
                log.notes = payload.notes.strip() if payload.notes else None
            new_state = log.completed
            db.commit()

    streak_info = services.calculate_habit_streak(payload.habit_id, db, user_id=current_user.id)
    
    # Calculate updated overall week completion for current_user
    monday, sunday = services.get_week_range(log_date)
    week_logs_count = db.query(HabitLog).filter(
        HabitLog.user_id == current_user.id,
        HabitLog.date >= monday,
        HabitLog.date <= sunday,
        HabitLog.completed == True
    ).count()

    total_active_habits = db.query(Habit).filter(Habit.user_id == current_user.id, Habit.is_active == True).count()
    overall_week_pct = round((week_logs_count / (total_active_habits * 7)) * 100) if total_active_habits > 0 else 0

    return {
        "success": True,
        "habit_id": payload.habit_id,
        "date": payload.date,
        "completed": new_state,
        "notes": log.notes if log else None,
        "current_streak": streak_info["current_streak"],
        "longest_streak": streak_info["longest_streak"],
        "overall_week_pct": overall_week_pct
    }

@app.post("/api/habits/notes")
async def save_habit_log_notes(
    payload: HabitLogNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Attach or update a personal note on a habit log."""
    try:
        log_date = date.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if log_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot attach notes to future dates.")

    habit = db.query(Habit).filter(Habit.id == payload.habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = db.query(HabitLog).filter(
        HabitLog.habit_id == payload.habit_id,
        HabitLog.user_id == current_user.id,
        HabitLog.date == log_date
    ).first()

    if not log:
        log = HabitLog(
            user_id=current_user.id,
            habit_id=payload.habit_id,
            date=log_date,
            completed=False,
            value=0,
            notes=payload.notes.strip() if payload.notes else None
        )
        db.add(log)
    else:
        log.notes = payload.notes.strip() if payload.notes else None

    try:
        db.commit()
        db.refresh(log)
    except IntegrityError:
        db.rollback()
        log = db.query(HabitLog).filter(
            HabitLog.habit_id == payload.habit_id,
            HabitLog.user_id == current_user.id,
            HabitLog.date == log_date
        ).first()
        if log:
            log.notes = payload.notes.strip() if payload.notes else None
            db.commit()
            db.refresh(log)

    return {"success": True, "log": log.to_dict()}

@app.get("/api/habits")
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch all habits for the authenticated user."""
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).order_by(Habit.display_order.asc(), Habit.id.asc()).all()
    return [h.to_dict() for h in habits]

@app.post("/api/habits")
async def create_habit(
    payload: HabitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new custom habit for the authenticated user."""
    habit = Habit(
        user_id=current_user.id,
        name=payload.name.strip(),
        category=payload.category.strip() or "General",
        description=payload.description.strip() if payload.description else None,
        icon=payload.icon or "🎯",
        color=payload.color or "#10b981",
        daily_target=payload.daily_target or 1,
        display_order=payload.display_order or 0,
        is_active=True
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return {"success": True, "habit": habit.to_dict()}

@app.put("/api/habits/{habit_id}")
async def update_habit(
    habit_id: int,
    payload: HabitUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change / customize an existing habit belonging to the user."""
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if payload.name is not None:
        habit.name = payload.name.strip()
    if payload.category is not None:
        habit.category = payload.category.strip()
    if payload.description is not None:
        habit.description = payload.description.strip() if payload.description else None
    if payload.icon is not None:
        habit.icon = payload.icon
    if payload.color is not None:
        habit.color = payload.color
    if payload.daily_target is not None:
        habit.daily_target = payload.daily_target
    if payload.is_active is not None:
        habit.is_active = payload.is_active
    if payload.display_order is not None:
        habit.display_order = payload.display_order

    db.commit()
    db.refresh(habit)
    return {"success": True, "habit": habit.to_dict()}

@app.get("/api/habits/archived")
async def get_archived_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch all archived (soft-deleted) habits for the authenticated user."""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == False
    ).order_by(Habit.id.desc()).all()
    return [h.to_dict() for h in habits]

@app.post("/api/habits/{habit_id}/archive")
async def archive_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft-delete / archive a habit for the user, preserving historical logs."""
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.is_active = False
    db.commit()
    return {"success": True, "message": f"Habit '{habit.name}' archived", "habit": habit.to_dict()}

@app.post("/api/habits/{habit_id}/restore")
async def restore_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore an archived habit back to active tracking."""
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.is_active = True
    db.commit()
    return {"success": True, "message": f"Habit '{habit.name}' restored", "habit": habit.to_dict()}

@app.delete("/api/habits/{habit_id}")
async def delete_habit(
    habit_id: int,
    permanent: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive habit (soft delete, preserving logs) by default.
    Permanent hard deletion with log cascade requires permanent=True query parameter.
    """
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if permanent:
        db.delete(habit)
        db.commit()
        return {"success": True, "message": f"Habit '{habit.name}' permanently deleted"}
    else:
        habit.is_active = False
        db.commit()
        return {"success": True, "message": f"Habit '{habit.name}' archived"}

@app.post("/api/habits/reset-defaults")
async def reset_default_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset to the original 10 default habits for the authenticated user only."""
    seed_default_habits(db, force=True, seed_sample_logs=True, user_id=current_user.id)
    return {"success": True, "message": "Reset to 10 default habits successfully"}

@app.get("/api/charts/weekly-data")
async def get_weekly_chart_data(
    week_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns day-by-day Monday through Sunday completion data for Chart.js for the authenticated user."""
    target_dt = date.fromisoformat(week_date) if week_date else date.today()
    grid = services.get_weekly_grid(db, target_dt, user_id=current_user.id)
    return {
        "labels": [d["day_name"] for d in grid["daily_chart_data"]],
        "completed": [d["completed_count"] for d in grid["daily_chart_data"]],
        "percentages": [d["percentage"] for d in grid["daily_chart_data"]],
        "total_habits": grid["habits_count"]
    }

@app.get("/api/charts/category-data")
async def get_category_chart_data(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns category breakdown and completion totals for Chart.js for the authenticated user."""
    today = date.today()
    y = year or today.year
    m = month or today.month
    monthly_stats = services.get_monthly_summary(db, y, m, user_id=current_user.id)
    return {
        "categories": monthly_stats["category_distribution"],
        "month_name": monthly_stats["month_name"],
        "year": y,
        "total_completions": monthly_stats["total_completions"],
        "completion_rate_pct": monthly_stats["completion_rate_pct"]
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

