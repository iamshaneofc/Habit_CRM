import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from fastapi.testclient import TestClient
import database
from main import app
from services import calculate_habit_streak, get_weekly_grid, get_monthly_summary
from models import User, Habit, HabitLog

def test_streak_calculations():
    database.check_and_stabilize_db()
    db = database.SessionLocal()
    # Clean up any leftover test user
    old_user = db.query(User).filter(User.email == "streak_tester@example.com").first()
    if old_user:
        db.query(HabitLog).filter(HabitLog.user_id == old_user.id).delete()
        db.query(Habit).filter(Habit.user_id == old_user.id).delete()
        db.delete(old_user)
        db.commit()

    user = User(email="streak_tester@example.com", hashed_password="pw", full_name="Streak Tester")
    db.add(user)
    db.commit()
    db.refresh(user)

    habit = Habit(user_id=user.id, name="Streak Run", category="Health")
    db.add(habit)
    db.commit()
    db.refresh(habit)

    today = date.today()
    yest = today - timedelta(days=1)
    d2 = today - timedelta(days=2)
    d3 = today - timedelta(days=3)
    d5 = today - timedelta(days=5)
    d6 = today - timedelta(days=6)

    # 1. Zero logs
    stats = calculate_habit_streak(habit.id, db, user_id=user.id)
    assert stats["current_streak"] == 0
    assert stats["longest_streak"] == 0
    print("[OK] Zero completions -> current: 0, longest: 0.")

    # 2. Case A: 3 consecutive days ending today (today, yest, d2)
    for d in [today, yest, d2]:
        db.add(HabitLog(user_id=user.id, habit_id=habit.id, date=d, completed=True))
    db.commit()
    stats = calculate_habit_streak(habit.id, db, user_id=user.id)
    assert stats["current_streak"] == 3
    assert stats["longest_streak"] == 3
    print("[OK] 3 consecutive days ending today -> current: 3, longest: 3.")

    # 3. Case B: Today incomplete, yesterday & d2 complete (grace period for today)
    today_log = db.query(HabitLog).filter(HabitLog.habit_id == habit.id, HabitLog.date == today).first()
    today_log.completed = False
    db.commit()
    stats = calculate_habit_streak(habit.id, db, user_id=user.id)
    assert stats["current_streak"] == 2
    assert stats["longest_streak"] == 2
    print("[OK] Today incomplete, yesterday complete (grace period) -> current: 2, longest: 2.")

    # 4. Case C: Missed yesterday & today, but d2, d3, d4 complete (3 consecutive days)
    yest_log = db.query(HabitLog).filter(HabitLog.habit_id == habit.id, HabitLog.date == yest).first()
    yest_log.completed = False
    d4 = today - timedelta(days=4)
    db.add(HabitLog(user_id=user.id, habit_id=habit.id, date=d3, completed=True))
    db.add(HabitLog(user_id=user.id, habit_id=habit.id, date=d4, completed=True))
    db.commit()
    stats = calculate_habit_streak(habit.id, db, user_id=user.id)
    assert stats["current_streak"] == 0
    assert stats["longest_streak"] == 3
    print("[OK] Yesterday and today incomplete -> current: 0, longest: 3.")

    # 5. Case D: Broken run with longer past run (gap on d3 & d4, past run on d5-d8 = 4 days)
    for offset in [5, 6, 7, 8]:
        past_d = today - timedelta(days=offset)
        db.add(HabitLog(user_id=user.id, habit_id=habit.id, date=past_d, completed=True))
    # Gap on d3 and d4
    db.query(HabitLog).filter(HabitLog.habit_id == habit.id, HabitLog.date.in_([d3, d4])).update({"completed": False})
    # Make today & yesterday complete
    today_log.completed = True
    yest_log.completed = True
    db.commit()
    stats = calculate_habit_streak(habit.id, db, user_id=user.id)
    assert stats["current_streak"] == 3 # today, yest, d2
    assert stats["longest_streak"] == 4 # d5, d6, d7, d8
    print("[OK] Broken run -> current: 3, longest: 4.")

    # Cleanup test records
    db.query(HabitLog).filter(HabitLog.user_id == user.id).delete()
    db.query(Habit).filter(Habit.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    db.close()

def test_metrics_accuracy_and_empty_state():
    with TestClient(app) as client:
        # Register new empty user (without seeding)
        user_email = "empty_tester@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Empty Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        cookies = login_res.cookies

        # Archive habits for this user to test active habits empty state
        db = database.SessionLocal()
        user = db.query(User).filter(User.email == user_email).first()
        db.query(Habit).filter(Habit.user_id == user.id).update({"is_active": False})
        db.commit()
        db.close()

        # Check empty state rendering
        dash_res = client.get("/", cookies=cookies)
        assert dash_res.status_code == 200
        assert "No active habits tracked yet" in dash_res.text
        assert "0%" in dash_res.text
        print("[OK] Empty state rendered cleanly with 0 active habits and 0% completion.")

if __name__ == "__main__":
    test_streak_calculations()
    test_metrics_accuracy_and_empty_state()
    print("\nALL STEP 9 METRICS & STREAKS TESTS PASSED!")
