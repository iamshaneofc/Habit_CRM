import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
import database
from main import app

def test_controls_and_validation():
    database.check_and_stabilize_db()
    with TestClient(app) as client:
        # Register user
        user_email = "controls_test@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Controls Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        # 1. Test empty habit name validation
        empty_res = client.post("/api/habits", json={"name": ""}, cookies=cookies)
        assert empty_res.status_code == 422
        errors = empty_res.json()["detail"]
        assert any("name" in str(err) for err in errors)
        print("[OK] Empty habit name blocked with clear 422 validation detail.")

        # 2. Test invalid daily target (< 1)
        target_res = client.post("/api/habits", json={"name": "Valid Name", "daily_target": 0}, cookies=cookies)
        assert target_res.status_code == 422
        print("[OK] Daily target < 1 blocked with 422 validation detail.")

        # 3. Test valid creation
        good_res = client.post("/api/habits", json={
            "name": "Mindful Breathing",
            "category": "Mindfulness",
            "daily_target": 1
        }, cookies=cookies)
        assert good_res.status_code == 200
        habit_id = good_res.json()["habit"]["id"]
        print("[OK] Valid habit created successfully.")

        # 4. Clean up habit
        client.delete(f"/api/habits/{habit_id}?permanent=true", cookies=cookies)
        print("[OK] Habit cleanly deleted.")

if __name__ == "__main__":
    test_controls_and_validation()
    print("\nALL STEP 11 CONTROL & VALIDATION TESTS PASSED!")
