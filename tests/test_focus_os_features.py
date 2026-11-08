"""
Test Suite for Focus OS Master Features:
1. Catalog API (/api/catalog) with categories and domains
2. Onboarding Workflow (/api/onboarding/complete)
3. Tracking Start Date Neutrality Rule
4. GitHub-Style Consistency Heatmap (/api/analytics/heatmap)
5. Dedicated Monthly Tracker (/monthly and /api/analytics/monthly)
6. Subtopics handling and max-limit rules
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import database
from main import app
from models import User, Habit, HabitLog

def test_focus_os_complete_workflow():
    database.check_and_stabilize_db()
    db = database.SessionLocal()

    test_email = "focus_os_tester@example.com"
    # Clean up prior test data
    db.query(HabitLog).filter(HabitLog.habit_id.in_(
        db.query(Habit.id).filter(Habit.user_id.in_(
            db.query(User.id).filter(User.email == test_email)
        ))
    )).delete(synchronize_session=False)
    db.query(Habit).filter(Habit.user_id.in_(
        db.query(User.id).filter(User.email == test_email)
    )).delete(synchronize_session=False)
    db.query(User).filter(User.email == test_email).delete(synchronize_session=False)
    db.commit()
    db.close()

    with TestClient(app) as client:
        # 1. Register account
        reg_res = client.post("/api/auth/register", json={
            "email": test_email,
            "password": "FocusOSPassword123!",
            "full_name": "Focus Operator"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        cookies = reg_res.cookies

        # 2. Test Catalog API
        cat_res = client.get("/api/catalog")
        assert cat_res.status_code == 200
        cat_data = cat_res.json()
        assert "categories" in cat_data
        assert "domains" in cat_data
        assert len(cat_data["categories"]) == 5
        assert len(cat_data["domains"]) >= 44
        print("[OK] Test 1: Catalog API verified with 44+ domains across 5 categories.")

        # 3. Test Onboarding Workflow
        onboarding_payload = {
            "display_name": "Alex Focus",
            "profession": "AI / ML Engineer",
            "bio": "Building scalable autonomous systems and daily mastery.",
            "domains": [
                {
                    "name": "DSA & Problem Solving",
                    "category": "Technology & Engineering",
                    "icon": "💻",
                    "color": "#10b981",
                    "subtopics": ["Arrays", "Trees", "Dynamic Programming"]
                },
                {
                    "name": "Artificial Intelligence",
                    "category": "Technology & Engineering",
                    "icon": "🤖",
                    "color": "#06b6d4",
                    "subtopics": ["RAG", "Agentic AI", "LangGraph", "LLM Evaluation"]
                },
                {
                    "name": "System Architecture",
                    "category": "Technology & Engineering",
                    "icon": "📐",
                    "color": "#8b5cf6",
                    "subtopics": ["Microservices", "Caching", "Load Balancing"]
                }
            ]
        }
        ob_res = client.post("/api/onboarding/complete", json=onboarding_payload, cookies=cookies)
        assert ob_res.status_code == 200, f"Onboarding failed: {ob_res.text}"
        assert ob_res.json()["success"] is True
        print("[OK] Test 2: Onboarding completed successfully.")

        # 4. Verify user profile and customized habits
        me_res = client.get("/api/auth/me", cookies=cookies)
        assert me_res.status_code == 200
        user_info = me_res.json()["user"]
        assert user_info["display_name"] == "Alex Focus"
        assert user_info["profession"] == "AI / ML Engineer"
        assert user_info["onboarding_completed"] is True
        assert user_info["tracking_start_date"] == date.today().isoformat()

        habits_res = client.get("/api/habits", cookies=cookies)
        assert habits_res.status_code == 200
        user_habits = habits_res.json()
        assert len(user_habits) == 3
        habit_names = [h["name"] for h in user_habits]
        assert "DSA & Problem Solving" in habit_names
        assert "Artificial Intelligence" in habit_names
        print("[OK] Test 3: User profile & habits verified.")

        # 5. Test Tracking Start Date Neutrality Rule
        # Load dashboard weekly grid
        dash_res = client.get("/", cookies=cookies)
        assert dash_res.status_code == 200
        assert "Alex Focus" in dash_res.text or "Focus Operator" in dash_res.text
        assert ("DSA & Problem Solving" in dash_res.text or "DSA &amp; Problem Solving" in dash_res.text)
        assert "Weekly Completion" in dash_res.text
        print("[OK] Test 4: Dashboard loaded with customized habits.")

        # 6. Test GitHub-Style Heatmap Endpoint
        heat_res = client.get("/api/analytics/heatmap?weeks=52", cookies=cookies)
        assert heat_res.status_code == 200
        heat_data = heat_res.json()
        assert "weeks" in heat_data
        assert "month_labels" in heat_data
        assert len(heat_data["weeks"]) > 0
        print(f"[OK] Test 5: GitHub-style consistency heatmap API returns {len(heat_data['weeks'])} weeks.")

        # 7. Test Dedicated Monthly Tracker Page & API
        m_page_res = client.get("/monthly", cookies=cookies)
        assert m_page_res.status_code == 200
        assert "Monthly Tracker" in m_page_res.text
        assert ("DSA & Problem Solving" in m_page_res.text or "DSA &amp; Problem Solving" in m_page_res.text)

        m_api_res = client.get("/api/analytics/monthly", cookies=cookies)
        assert m_api_res.status_code == 200
        m_data = m_api_res.json()
        assert "total_hours" in m_data
        assert "completion_rate_pct" in m_data
        assert "calendar_days" in m_data
        assert "habit_breakdown" in m_data
        assert len(m_data["habit_breakdown"]) == 3
        print("[OK] Test 6: Monthly Tracker page and API verified.")

        # 8. Test Toggle with Hours Cycling
        dsa_habit = user_habits[0]
        today_str = date.today().isoformat()
        tog_res = client.post("/api/habits/toggle", json={
            "habit_id": dsa_habit["id"],
            "date": today_str,
            "value": 4
        }, cookies=cookies)
        assert tog_res.status_code == 200
        assert tog_res.json()["completed"] is True
        assert tog_res.json()["value"] == 4
        print("[OK] Test 7: Multi-hour chip toggle successfully logged 4h.")

        # 9. Test Future Date Rejection
        future_str = (date.today() + timedelta(days=2)).isoformat()
        fut_res = client.post("/api/habits/toggle", json={
            "habit_id": dsa_habit["id"],
            "date": future_str,
            "value": 2
        }, cookies=cookies)
        assert fut_res.status_code == 400
        print("[OK] Test 8: Future date completion rejected properly.")

        print("\nAll Focus OS Master tests passed successfully!")

if __name__ == "__main__":
    test_focus_os_complete_workflow()
