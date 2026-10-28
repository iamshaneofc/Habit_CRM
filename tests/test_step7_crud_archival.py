import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date
from fastapi.testclient import TestClient
import database
from main import app
from models import User, Habit, HabitLog

def test_habit_crud_and_archival():
    with TestClient(app) as client:
        # 1. Register test user
        user_email = "crud_test@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "CRUD Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        # 2. Test input validation
        bad_res = client.post("/api/habits", json={
            "name": "",  # invalid: min_length=1
            "daily_target": 0 # invalid: ge=1
        }, cookies=cookies)
        assert bad_res.status_code == 422, f"Expected 422 for invalid input, got {bad_res.status_code}"
        print("[OK] Invalid habit creation blocked with 422 Unprocessable Entity.")

        # 3. Create a valid custom habit
        create_res = client.post("/api/habits", json={
            "name": "Write 500 Words",
            "category": "Productivity",
            "icon": "✍️",
            "color": "#6366f1",
            "daily_target": 2,
            "description": "Daily deep writing"
        }, cookies=cookies)
        assert create_res.status_code == 200
        created_data = create_res.json()["habit"]
        habit_id = created_data["id"]
        assert created_data["name"] == "Write 500 Words"
        assert created_data["daily_target"] == 2
        assert created_data["is_active"] is True
        print("[OK] Valid habit created with daily_target=2.")

        # 4. Edit habit
        edit_res = client.put(f"/api/habits/{habit_id}", json={
            "name": "Write 1000 Words",
            "daily_target": 3
        }, cookies=cookies)
        assert edit_res.status_code == 200
        assert edit_res.json()["habit"]["name"] == "Write 1000 Words"
        assert edit_res.json()["habit"]["daily_target"] == 3
        print("[OK] Habit edited successfully.")

        # 5. Log a completion for today
        today_str = date.today().isoformat()
        toggle_res = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert toggle_res.status_code == 200
        print("[OK] Completion logged for today before archival.")

        # 6. Archive habit (soft delete)
        archive_res = client.post(f"/api/habits/{habit_id}/archive", cookies=cookies)
        assert archive_res.status_code == 200
        assert archive_res.json()["habit"]["is_active"] is False

        # Verify habit is hidden from active tracker
        dash_res = client.get("/", cookies=cookies)
        assert "Write 1000 Words" not in dash_res.text

        # Verify historical habit log is PRESERVED in database
        db = database.SessionLocal()
        preserved_log = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == date.today()
        ).first()
        assert preserved_log is not None, "Log was accidentally deleted on archive!"
        assert preserved_log.completed is True
        db.close()
        print("[OK] Habit archived: hidden from active tracker while historical logs are preserved.")

        # 7. Verify habit is listed in archived endpoint
        archived_res = client.get("/api/habits/archived", cookies=cookies)
        assert archived_res.status_code == 200
        archived_ids = [h["id"] for h in archived_res.json()]
        assert habit_id in archived_ids
        print("[OK] Habit retrieved from /api/habits/archived.")

        # 8. Restore habit
        restore_res = client.post(f"/api/habits/{habit_id}/restore", cookies=cookies)
        assert restore_res.status_code == 200
        assert restore_res.json()["habit"]["is_active"] is True

        dash_restored = client.get("/", cookies=cookies)
        assert "Write 1000 Words" in dash_restored.text
        print("[OK] Habit successfully restored to active tracker.")

        # 9. Permanent deletion
        perm_res = client.delete(f"/api/habits/{habit_id}?permanent=true", cookies=cookies)
        assert perm_res.status_code == 200
        db = database.SessionLocal()
        deleted_habit = db.query(Habit).filter(Habit.id == habit_id).first()
        assert deleted_habit is None
        deleted_log = db.query(HabitLog).filter(HabitLog.habit_id == habit_id).first()
        assert deleted_log is None
        db.close()
        print("[OK] Permanent deletion explicitly wiped habit and cascaded logs.")

if __name__ == "__main__":
    test_habit_crud_and_archival()
    print("\nALL STEP 7 CRUD & ARCHIVAL TESTS PASSED!")
