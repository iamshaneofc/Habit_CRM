import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
import database
from main import app

def test_step12_ui_layout():
    database.check_and_stabilize_db()
    with TestClient(app) as client:
        # Register and login user
        user_email = "ui_tester@example.com"
        client.post("/api/auth/register", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "UI Tester"
        })
        login_res = client.post("/api/auth/login", json={
            "email": user_email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        cookies = login_res.cookies

        dash_res = client.get("/", cookies=cookies)
        assert dash_res.status_code == 200
        html = dash_res.text

        # Verify layout components
        assert "dashboard-body-layout" in html, "Missing 2-column desktop arrangement container"
        assert "dashboard-sidebar" in html, "Missing right-side visual sidebar"
        assert "tracker-section" in html, "Missing dominant weekly tracker section"
        assert "consistency-card" in html, "Missing consistency insight card"

        # Verify 4 top metric cards
        assert "Weekly Completion" in html
        assert "Active Habits" in html
        assert "Total Completions" in html
        assert "Best Streak" in html

        # Verify 7-day Monday - Sunday columns
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            assert d in html

        print("[OK] UI Layout verified: Dominant weekly habit tracker + compact right sidebar + 4 top metrics.")

if __name__ == "__main__":
    test_step12_ui_layout()
    print("\nALL STEP 12 UI LAYOUT TESTS PASSED!")
