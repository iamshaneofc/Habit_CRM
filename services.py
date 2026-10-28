from datetime import date, datetime, timedelta
import calendar
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Habit, HabitLog

def get_week_range(target_date: Optional[date] = None) -> Tuple[date, date]:
    """Returns the Monday and Sunday for the week of the given date."""
    if target_date is None:
        target_date = date.today()
    # Monday is weekday 0 in Python
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def get_week_details(target_date: Optional[date] = None) -> dict:
    """
    Returns Monday through Sunday date details for the weekly view.
    """
    today = date.today()
    if target_date is None:
        target_date = today

    monday, sunday = get_week_range(target_date)
    
    days = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        current_day = monday + timedelta(days=i)
        days.append({
            "date": current_day,
            "date_str": current_day.isoformat(),
            "day_name": day_names[i],
            "day_number": current_day.day,
            "month_name": current_day.strftime("%b"),
            "is_today": current_day == today,
            "is_future": current_day > today
        })

    prev_week = monday - timedelta(days=7)
    next_week = monday + timedelta(days=7)

    return {
        "monday": monday,
        "sunday": sunday,
        "monday_str": monday.isoformat(),
        "sunday_str": sunday.isoformat(),
        "week_number": monday.isocalendar()[1],
        "year": monday.year,
        "days": days,
        "prev_week_str": prev_week.isoformat(),
        "next_week_str": next_week.isoformat(),
        "is_current_week": (monday <= today <= sunday)
    }

def calculate_habit_streak(habit_id: int, db: Session, user_id: Optional[int] = None) -> dict:
    """Calculates current streak and longest streak for a habit."""
    log_query = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed == True
    )
    if user_id is not None:
        log_query = log_query.filter(HabitLog.user_id == user_id)
    logs = log_query.order_by(HabitLog.date.desc()).all()

    if not logs:
        return {"current_streak": 0, "longest_streak": 0, "total_completed": 0}

    completed_dates = {log.date for log in logs}
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Current streak calculation
    current_streak = 0
    check_date = today if today in completed_dates else yesterday

    while check_date in completed_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Longest streak calculation
    sorted_dates = sorted(list(completed_dates))
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for d in sorted_dates:
        if prev_date is None:
            temp_streak = 1
        elif d == prev_date + timedelta(days=1):
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        prev_date = d

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_completed": len(completed_dates)
    }

def get_weekly_grid(db: Session, target_date: Optional[date] = None, user_id: Optional[int] = None) -> dict:
    """
    Builds the complete weekly matrix for habits and tick status Monday-Sunday for a specific user.
    """
    week_info = get_week_details(target_date)
    monday = week_info["monday"]
    sunday = week_info["sunday"]

    habit_query = db.query(Habit).filter(Habit.is_active == True)
    if user_id is not None:
        habit_query = habit_query.filter(Habit.user_id == user_id)
    habits = habit_query.order_by(Habit.display_order.asc(), Habit.id.asc()).all()

    habit_ids = [h.id for h in habits]

    # Query all logs within the week range in one efficient batch query
    if habit_ids:
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id.in_(habit_ids),
            HabitLog.date >= monday,
            HabitLog.date <= sunday
        ).all()
    else:
        logs = []

    # Map (habit_id, date_str) -> log object
    log_map = {(log.habit_id, log.date.isoformat()): log for log in logs}

    habit_rows = []
    daily_completions = {day["date_str"]: 0 for day in week_info["days"]}
    total_possible_checks = len(habits) * 7 if habits else 1
    total_completed_checks = 0

    for habit in habits:
        streak_info = calculate_habit_streak(habit.id, db, user_id=user_id)
        days_status = []
        habit_week_completed = 0

        for day in week_info["days"]:
            d_str = day["date_str"]
            log_item = log_map.get((habit.id, d_str))
            is_done = log_item.completed if log_item else False
            note_content = log_item.notes if log_item else None

            if is_done:
                habit_week_completed += 1
                daily_completions[d_str] += 1
                total_completed_checks += 1

            days_status.append({
                "date_str": d_str,
                "is_completed": is_done,
                "notes": note_content,
                "is_today": day["is_today"],
                "is_future": day["is_future"]
            })

        completion_pct = round((habit_week_completed / 7) * 100) if 7 > 0 else 0

        habit_rows.append({
            "habit": habit,
            "days": days_status,
            "week_completed": habit_week_completed,
            "week_target": 7,
            "completion_pct": completion_pct,
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"]
        })

    # Prepare daily stats for Chart.js
    daily_chart_data = []
    for day in week_info["days"]:
        count = daily_completions[day["date_str"]]
        pct = round((count / len(habits) * 100)) if habits else 0
        daily_chart_data.append({
            "day_name": day["day_name"],
            "date_str": day["date_str"],
            "completed_count": count,
            "total_habits": len(habits),
            "percentage": pct
        })

    overall_pct = round((total_completed_checks / total_possible_checks) * 100) if total_possible_checks else 0
    best_streak = max([r["longest_streak"] for r in habit_rows], default=0)
    best_current_streak = max([r["current_streak"] for r in habit_rows], default=0)

    return {
        "week_info": week_info,
        "habits_count": len(habits),
        "habit_rows": habit_rows,
        "daily_chart_data": daily_chart_data,
        "overall_pct": overall_pct,
        "total_completed_checks": total_completed_checks,
        "best_streak": best_streak,
        "best_current_streak": best_current_streak
    }

def get_monthly_summary(db: Session, year: int, month: int, user_id: Optional[int] = None) -> dict:
    """
    Computes monthly statistics, category breakdown, and progress for filters for a specific user.
    """
    num_days = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)

    habit_query = db.query(Habit).filter(Habit.is_active == True)
    if user_id is not None:
        habit_query = habit_query.filter(Habit.user_id == user_id)
    habits = habit_query.all()
    habit_ids = [h.id for h in habits]

    if habit_ids:
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id.in_(habit_ids),
            HabitLog.date >= start_date,
            HabitLog.date <= end_date,
            HabitLog.completed == True
        ).all()
    else:
        logs = []

    # Category distribution for chart
    categories = {}
    habit_completion_count = {h.id: 0 for h in habits}

    for log in logs:
        habit_completion_count[log.habit_id] = habit_completion_count.get(log.habit_id, 0) + 1

    for h in habits:
        cat = h.category
        cnt = habit_completion_count.get(h.id, 0)
        categories[cat] = categories.get(cat, 0) + cnt

    total_logs = len(logs)
    max_possible = len(habits) * num_days if habits else 1
    month_pct = round((total_logs / max_possible) * 100) if max_possible > 0 else 0

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days_in_month": num_days,
        "total_completions": total_logs,
        "completion_rate_pct": month_pct,
        "category_distribution": categories,
        "habits_count": len(habits)
    }
