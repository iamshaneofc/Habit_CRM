import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from fastapi.testclient import TestClient
import database
from main import app
from services import get_week_range, get_week_details, get_monthly_summary
from models import User, Habit

def test_date_services():
    # 1. Verify Monday to Sunday range
    test_d = date(2026, 10, 28) # Wednesday
    mon, sun = get_week_range(test_d)
    assert mon == date(2026, 10, 26), f"Expected Monday 2026-10-26, got {mon}"
    assert sun == date(2026, 11, 1), f"Expected Sunday 2026-11-01, got {sun}"
    assert mon.weekday() == 0
    assert sun.weekday() == 6

    # 2. Verify week details
    details = get_week_details(test_d)
    assert len(details["days"]) == 7
    assert details["days"][0]["day_name"] == "Mon"
    assert details["days"][6]["day_name"] == "Sun"
    assert details["prev_week_str"] == "2026-10-19"
    assert details["next_week_str"] == "2026-11-02"

    # 3. Leap year check (2024 is a leap year)
    leap_d = date(2024, 2, 29) # Leap day Thursday
    leap_mon, leap_sun = get_week_range(leap_d)
    assert leap_mon == date(2024, 2, 26)
    assert leap_sun == date(2024, 3, 3)

    print("[OK] Date services and boundary calculations verified successfully.")

def test_api_date_navigation_and_future_rejection():
    with TestClient(app) as client:
        # Register a test user
        reg_resp = client.post("/api/auth/register", json={
            "email": "datetest@example.com",
            "password": "Password123!",
            "full_name": "Date Tester"
        })
        assert reg_resp.status_code in [200, 400] # 200 or already registered
        
        login_resp = client.post("/api/auth/login", json={
            "email": "datetest@example.com",
            "password": "Password123!"
        })
        assert login_resp.status_code == 200
        cookies = login_resp.cookies

        # Get dashboard for year 2025, month 5
        resp_2025 = client.get("/?month=5&year=2025", cookies=cookies)
        assert resp_2025.status_code == 200
        assert "May" in resp_2025.text

        # Get dashboard for leap year 2024, month 2
        resp_2024 = client.get("/?month=2&year=2024", cookies=cookies)
        assert resp_2024.status_code == 200
        assert "February" in resp_2024.text

        # Get habit ID
        db = database.SessionLocal()
        user = db.query(User).filter(User.email == "datetest@example.com").first()
        habit = db.query(Habit).filter(Habit.user_id == user.id).first()
        habit_id = habit.id
        db.close()

        # Try to toggle habit for a FUTURE date -> must fail with 400
        future_date = (date.today() + timedelta(days=2)).isoformat()
        future_resp = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": future_date
        }, cookies=cookies)
        assert future_resp.status_code == 400, f"Expected 400, got {future_resp.status_code}: {future_resp.text}"
        assert "Future dates cannot be marked complete" in future_resp.text
        print("[OK] API correctly blocked future-date habit completion with 400 Bad Request.")

        # Try to toggle habit for TODAY -> must succeed
        today_str = date.today().isoformat()
        today_resp = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies)
        assert today_resp.status_code == 200, f"Expected 200, got {today_resp.status_code}: {today_resp.text}"
        print("[OK] API successfully completed habit for today.")

if __name__ == "__main__":
    test_date_services()
    test_api_date_navigation_and_future_rejection()
    print("\nALL STEP 6 DATE TESTS PASSED!")
