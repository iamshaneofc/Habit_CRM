import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date
from fastapi.testclient import TestClient
import database
from main import app
from models import User, Habit, HabitLog

def test_charts_api():
    database.check_and_stabilize_db()
    with TestClient(app) as client:
        # Register test user
        user_email = "chart_tester@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Chart Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        # 1. Test weekly chart data endpoint
        week_res = client.get("/api/charts/weekly-data", cookies=cookies)
        assert week_res.status_code == 200
        week_data = week_res.json()
        assert len(week_data["labels"]) == 7
        assert week_data["labels"] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        assert len(week_data["completed"]) == 7
        assert len(week_data["percentages"]) == 7
        assert week_data["total_habits"] >= 10
        print("[OK] /api/charts/weekly-data returned 7-day Monday-Sunday matrix.")

        # 2. Test category chart data endpoint
        cat_res = client.get("/api/charts/category-data", cookies=cookies)
        assert cat_res.status_code == 200
        cat_data = cat_res.json()
        assert "categories" in cat_data
        assert isinstance(cat_data["categories"], dict)
        assert cat_data["total_completions"] >= 0
        print("[OK] /api/charts/category-data returned category distribution dictionary.")

        # 3. Dynamic update test: Toggle today's completion and verify chart updates
        db = database.SessionLocal()
        user = db.query(User).filter(User.email == user_email).first()
        habit = db.query(Habit).filter(Habit.user_id == user.id).first()
        habit_id = habit.id
        today_str = date.today().isoformat()
        db.close()

        # Capture count before
        today_idx = date.today().weekday()
        count_before = week_data["completed"][today_idx]

        # Toggle habit
        toggle_res = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert toggle_res.status_code == 200
        new_completed_state = toggle_res.json()["completed"]

        # Fetch chart data again
        week_res2 = client.get("/api/charts/weekly-data", cookies=cookies)
        assert week_res2.status_code == 200
        count_after = week_res2.json()["completed"][today_idx]

        if new_completed_state:
            assert count_after == count_before + 1
        else:
            assert count_after == count_before - 1
        print("[OK] Chart data endpoint dynamically reflects toggled completion.")

if __name__ == "__main__":
    test_charts_api()
    print("\nALL STEP 10 CHART DATA TESTS PASSED!")
