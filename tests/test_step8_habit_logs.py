import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from fastapi.testclient import TestClient
import database
from main import app
from models import User, Habit, HabitLog

def test_habit_logs_and_notes():
    with TestClient(app) as client:
        # Register and login
        user_email = "log_tester@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Log Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        # Get first habit for this user
        db = database.SessionLocal()
        user = db.query(User).filter(User.email == user_email).first()
        habit = db.query(Habit).filter(Habit.user_id == user.id).first()
        habit_id = habit.id
        db.close()

        today_str = date.today().isoformat()

        # Check initial state for today
        db = database.SessionLocal()
        existing_log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == date.today()
        ).first()
        initial_completed = existing_log.completed if existing_log else False
        db.close()

        # 1. First toggle -> flips state
        res1 = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert res1.status_code == 200
        assert res1.json()["completed"] == (not initial_completed)
        print(f"[OK] Habit toggled from {initial_completed} to {not initial_completed}.")

        # 2. Second toggle -> flips back to initial state (reversible)
        res2 = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert res2.status_code == 200
        assert res2.json()["completed"] == initial_completed
        print(f"[OK] Habit toggled back to {initial_completed} (reversible).")

        # 3. Third toggle -> flips again
        res3 = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert res3.status_code == 200
        assert res3.json()["completed"] == (not initial_completed)

        # Verify no duplicate logs were created in the database
        db = database.SessionLocal()
        logs_count = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == date.today()
        ).count()
        assert logs_count == 1, f"Expected exactly 1 log record, found {logs_count}"
        db.close()
        print("[OK] Duplicate log check: Exactly 1 record exists in habit_logs for (habit_id, date).")

        # 4. Attach reflection note
        note_text = "Felt energized, completed in morning."
        note_res = client.post("/api/habits/notes", json={
            "habit_id": habit_id,
            "date": today_str,
            "notes": note_text
        }, cookies=cookies)
        assert note_res.status_code == 200
        assert note_res.json()["log"]["notes"] == note_text
        print("[OK] Reflection note attached successfully.")

        # Verify note is returned in weekly grid
        dash_res = client.get("/", cookies=cookies)
        assert note_text in dash_res.text
        print("[OK] Reflection note verified in dashboard weekly grid HTML.")

        # 5. Future date note rejection
        future_str = (date.today() + timedelta(days=3)).isoformat()
        future_note_res = client.post("/api/habits/notes", json={
            "habit_id": habit_id,
            "date": future_str,
            "notes": "Future note"
        }, cookies=cookies)
        assert future_note_res.status_code == 400
        print("[OK] Future date note correctly rejected with 400.")

        # 6. Past week logging
        past_date = date.today() - timedelta(days=8)
        past_str = past_date.isoformat()
        past_res = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": past_str
        }, cookies=cookies)
        assert past_res.status_code == 200
        assert past_res.json()["completed"] is True

        db = database.SessionLocal()
        past_log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == past_date
        ).first()
        assert past_log is not None
        assert past_log.completed is True
        db.close()
        print("[OK] Historical week logging verified successfully.")

if __name__ == "__main__":
    test_habit_logs_and_notes()
    print("\nALL STEP 8 LOG & INTERACTION TESTS PASSED!")
