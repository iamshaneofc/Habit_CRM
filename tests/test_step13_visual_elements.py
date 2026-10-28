import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
import database
from main import app
from services import get_weekly_grid

def test_step13_visual_elements():
    database.check_and_stabilize_db()
    with TestClient(app) as client:
        # Register and login user
        user_email = "visual_tester@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Visual Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        # 1. Verify services returns most_consistent_habit
        from models import User
        db = database.SessionLocal()
        user = db.query(User).filter(User.email == user_email).first()
        grid = get_weekly_grid(db, user_id=user.id)
        db.close()

        assert "most_consistent_habit" in grid
        assert grid["most_consistent_habit"] is not None
        assert "name" in grid["most_consistent_habit"]
        assert "week_completed" in grid["most_consistent_habit"]
        print(f"[OK] Most consistent habit identified: {grid['most_consistent_habit']['name']}")

        # 2. Verify dashboard HTML contains visual elements
        dash_res = client.get("/", cookies=cookies)
        assert dash_res.status_code == 200
        html = dash_res.text

        assert "Top Performer" in html
        assert "Star Habit" in html
        assert "Consistency Insight" in html
        assert "Weekly Consistency" in html
        print("[OK] Top Performer and Consistency Insight visual cards rendered.")

if __name__ == "__main__":
    test_step13_visual_elements()
    print("\nALL STEP 13 VISUAL ELEMENTS TESTS PASSED!")
