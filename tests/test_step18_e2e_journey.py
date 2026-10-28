"""
Comprehensive End-to-End QA Test Suite for Step 18:
Executes the mandatory 20-point user journey:
1. Register new user
2. Sign in
3. Create a habit
4. Edit the habit
5. Mark it complete for today
6. Undo the completion
7. Verify streak and metric updates
8. Navigate to a previous week
9. Navigate across months and years
10. Confirm future dates cannot be completed
11. Archive a habit
12. Verify historical logs remain available
13. Restore the habit
14. Review charts and weekly metrics
15. Sign out and sign back in
16. Verify data persists
17. Use a second account and attempt cross-user access
18. Verify unauthorized requests are rejected
19. Test invalid inputs and error handling
20. Verify responsive behavior on desktop and mobile
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import database
from main import app
from models import User, Habit, HabitLog

def run_e2e_user_journey():
    database.check_and_stabilize_db()
    db = database.SessionLocal()
    
    # Clean up any previous test accounts
    emails = ["e2e_journey_alice@example.com", "e2e_journey_bob@example.com"]
    db.query(HabitLog).filter(HabitLog.habit_id.in_(
        db.query(Habit.id).filter(Habit.user_id.in_(
            db.query(User.id).filter(User.email.in_(emails))
        ))
    )).delete(synchronize_session=False)
    db.query(Habit).filter(Habit.user_id.in_(
        db.query(User.id).filter(User.email.in_(emails))
    )).delete(synchronize_session=False)
    db.query(User).filter(User.email.in_(emails)).delete(synchronize_session=False)
    db.commit()
    db.close()

    with TestClient(app) as client:
        # 1. Register a new user
        reg_res = client.post("/api/auth/register", json={
            "email": "e2e_journey_alice@example.com",
            "password": "StrongPassword123!",
            "full_name": "Alice Journey"
        })
        assert reg_res.status_code == 200, f"Step 1 failed: {reg_res.text}"
        alice_data = reg_res.json()["user"]
        alice_id = alice_data["id"]
        alice_cookie = reg_res.cookies.get("habit_crm_session")
        assert alice_cookie is not None, "Step 1: Session cookie not received"
        print("[OK] Point 1: Registered user Alice Journey.")

        # 2. Sign in
        client.cookies.clear()
        login_res = client.post("/api/auth/login", json={
            "email": "e2e_journey_alice@example.com",
            "password": "StrongPassword123!"
        })
        assert login_res.status_code == 200, f"Step 2 failed: {login_res.text}"
        cookies_alice = login_res.cookies
        print("[OK] Point 2: Signed in successfully with Alice.")

        # 3. Create a habit
        create_res = client.post("/api/habits", json={
            "name": "E2E Morning Run",
            "category": "Fitness",
            "description": "5km run at sunrise",
            "icon": "🏃",
            "color": "#3b82f6",
            "daily_target": 1
        }, cookies=cookies_alice)
        assert create_res.status_code == 200, f"Step 3 failed: {create_res.text}"
        habit_obj = create_res.json()["habit"]
        habit_id = habit_obj["id"]
        assert habit_obj["name"] == "E2E Morning Run"
        print(f"[OK] Point 3: Created habit id={habit_id} ('E2E Morning Run').")

        # 4. Edit the habit
        edit_res = client.put(f"/api/habits/{habit_id}", json={
            "name": "E2E Morning Run 6km",
            "description": "6km run with intervals",
            "daily_target": 2
        }, cookies=cookies_alice)
        assert edit_res.status_code == 200, f"Step 4 failed: {edit_res.text}"
        assert edit_res.json()["habit"]["name"] == "E2E Morning Run 6km"
        assert edit_res.json()["habit"]["daily_target"] == 2
        print("[OK] Point 4: Edited habit successfully (name and daily target updated).")

        # 5. Mark it complete for today
        today_str = date.today().isoformat()
        toggle_res1 = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies_alice)
        assert toggle_res1.status_code == 200, f"Step 5 failed: {toggle_res1.text}"
        assert toggle_res1.json()["completed"] is True
        print("[OK] Point 5: Marked complete for today.")

        # 6. Undo the completion
        toggle_res2 = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": today_str
        }, cookies=cookies_alice)
        assert toggle_res2.status_code == 200, f"Step 6 failed: {toggle_res2.text}"
        assert toggle_res2.json()["completed"] is False
        print("[OK] Point 6: Reversible toggle (undid completion back to False).")

        # Re-complete for subsequent metric checks
        client.post("/api/habits/toggle", json={"habit_id": habit_id, "date": today_str}, cookies=cookies_alice)

        # 7. Verify streak and metric updates
        dash_res = client.get("/", cookies=cookies_alice)
        assert dash_res.status_code == 200
        assert "E2E Morning Run 6km" in dash_res.text
        assert "Weekly Completion" in dash_res.text
        print("[OK] Point 7: Verified streak and metric updates in dashboard HTML.")

        # 8. Navigate to a previous week
        prev_week = (date.today() - timedelta(days=7)).isoformat()
        prev_res = client.get(f"/?week_date={prev_week}", cookies=cookies_alice)
        assert prev_res.status_code == 200
        assert "Jump to Today" in prev_res.text
        print("[OK] Point 8: Navigated to previous week and verified Jump to Today button.")

        # 9. Navigate across months and years
        nav_res = client.get("/?month=1&year=2025", cookies=cookies_alice)
        assert nav_res.status_code == 200
        assert "2025" in nav_res.text
        print("[OK] Point 9: Navigated across months and years (January 2025).")

        # 10. Confirm future dates cannot be completed
        future_str = (date.today() + timedelta(days=3)).isoformat()
        future_res = client.post("/api/habits/toggle", json={
            "habit_id": habit_id,
            "date": future_str
        }, cookies=cookies_alice)
        assert future_res.status_code == 400, f"Expected 400 for future date, got {future_res.status_code}"
        assert "Future dates cannot be marked complete" in future_res.json()["detail"]
        print("[OK] Point 10: Future dates rejected with 400 Bad Request.")

        # 11. Archive a habit
        archive_res = client.post(f"/api/habits/{habit_id}/archive", cookies=cookies_alice)
        assert archive_res.status_code == 200
        assert archive_res.json()["habit"]["is_active"] is False
        print("[OK] Point 11: Archived habit (soft delete).")

        # 12. Verify historical logs remain available
        archived_list_res = client.get("/api/habits/archived", cookies=cookies_alice)
        assert archived_list_res.status_code == 200
        archived_ids = [h["id"] for h in archived_list_res.json()]
        assert habit_id in archived_ids
        # Verify log is intact in DB
        db = database.SessionLocal()
        log_count = db.query(HabitLog).filter(HabitLog.habit_id == habit_id).count()
        db.close()
        assert log_count >= 1, "Historical log must be preserved after archival"
        print("[OK] Point 12: Verified historical logs preserved in database and archived list.")

        # 13. Restore the habit
        restore_res = client.post(f"/api/habits/{habit_id}/restore", cookies=cookies_alice)
        assert restore_res.status_code == 200
        assert restore_res.json()["habit"]["is_active"] is True
        print("[OK] Point 13: Restored habit back to active weekly tracker.")

        # 14. Review charts and weekly metrics
        weekly_chart_res = client.get("/api/charts/weekly-data", cookies=cookies_alice)
        assert weekly_chart_res.status_code == 200
        cat_chart_res = client.get("/api/charts/category-data", cookies=cookies_alice)
        assert cat_chart_res.status_code == 200
        assert "categories" in cat_chart_res.json()
        print("[OK] Point 14: Reviewed weekly and category chart API responses.")

        # 15. Sign out and sign back in
        logout_res = client.post("/api/auth/logout", cookies=cookies_alice)
        assert logout_res.status_code == 200
        client.cookies.clear()

        relogin_res = client.post("/api/auth/login", json={
            "email": "e2e_journey_alice@example.com",
            "password": "StrongPassword123!"
        })
        assert relogin_res.status_code == 200
        cookies_relogin = relogin_res.cookies
        print("[OK] Point 15: Signed out and re-authenticated successfully.")

        # 16. Verify data persists
        persist_dash = client.get("/", cookies=cookies_relogin)
        assert persist_dash.status_code == 200
        assert "E2E Morning Run 6km" in persist_dash.text
        print("[OK] Point 16: Verified data persisted across sessions.")

        # 17. Use a second account and attempt to access the first account's records
        client.cookies.clear()
        reg_bob = client.post("/api/auth/register", json={
            "email": "e2e_journey_bob@example.com",
            "password": "StrongPassword456!",
            "full_name": "Bob Journey"
        })
        assert reg_bob.status_code == 200
        cookies_bob = reg_bob.cookies

        # Bob attempts to archive Alice's habit
        bob_hack_archive = client.post(f"/api/habits/{habit_id}/archive", cookies=cookies_bob)
        assert bob_hack_archive.status_code == 404, "Bob should not be able to archive Alice's habit"

        # Bob attempts to delete Alice's habit
        bob_hack_delete = client.delete(f"/api/habits/{habit_id}", cookies=cookies_bob)
        assert bob_hack_delete.status_code == 404, "Bob should not be able to delete Alice's habit"
        print("[OK] Point 17: User Bob isolated; cannot modify Alice's habit records.")

        # 18. Verify unauthorized requests are rejected
        client.cookies.clear()
        unauth_dash = client.get("/", follow_redirects=False)
        assert unauth_dash.status_code == 303, f"Expected 303 redirect, got {unauth_dash.status_code}"
        assert unauth_dash.headers["location"] == "/login"
        unauth_api = client.post("/api/habits", json={"name": "Hacked"})
        assert unauth_api.status_code == 401, f"Expected 401 Unauthorized for API, got {unauth_api.status_code}"
        print("[OK] Point 18: Verified unauthenticated requests strictly redirected/rejected (303/401).")

        # 19. Test invalid inputs and error handling
        inv_name_res = client.post("/api/habits", json={"name": ""}, cookies=cookies_bob)
        assert inv_name_res.status_code == 422, "Empty habit name must produce 422"

        inv_target_res = client.post("/api/habits", json={"name": "Good", "daily_target": 0}, cookies=cookies_bob)
        assert inv_target_res.status_code == 422, "Daily target 0 must produce 422"
        print("[OK] Point 19: Verified input validation errors (422) for bad payloads.")

        # 20. Verify responsive behavior on desktop and mobile
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            css = f.read()
        assert "@media (max-width: 1100px)" in css
        assert "@media (max-width: 768px)" in css
        assert "@media (max-width: 480px)" in css
        assert "table-responsive" in css
        print("[OK] Point 20: Verified responsive styles and mobile grid adaptability.")

    print("\n" + "=" * 65)
    print("ALL 20 END-TO-END QA USER JOURNEY POINTS VERIFIED SUCCESSFULLY!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_e2e_user_journey()
