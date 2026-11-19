import os
import sys
from datetime import date, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
from main import app
from auth import create_access_token
from models import User, Habit, Note

def test_full_v2_features_e2e():
    """Comprehensive End-to-End Test for Focus OS V2 Features: Notes, Settings, Goals, Notifications, Pages."""
    database.upgrade_schema()
    client = TestClient(app)

    # 1. Test unauthenticated /notes page returns 200 (Notes page is public/demo accessible)
    r_notes = client.get("/notes")
    assert r_notes.status_code == 200
    assert "Focus Notes" in r_notes.text or "All Notes" in r_notes.text

    # 2. Get or create demo user and set valid auth session
    db = database.SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@habitcrm.com").first()
        if not demo_user:
            demo_user = User(email="demo@habitcrm.com", hashed_password="hashed_demo_pw", full_name="Demo User")
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        user_id = demo_user.id
    finally:
        db.close()

    token = create_access_token({"sub": str(user_id)})
    client.cookies.set("habit_crm_session", token)
    client.headers["Authorization"] = f"Bearer {token}"

    # 3. Test Dashboard and Monthly Pages return 200 for authenticated user
    r_dash = client.get("/")
    assert r_dash.status_code == 200
    assert "FOCUS OS" in r_dash.text or "focus-os" in r_dash.text

    r_monthly = client.get("/monthly")
    assert r_monthly.status_code == 200
    assert "Monthly Tracker" in r_monthly.text

    # 4. Test Settings API GET & PUT
    r_settings_get = client.get("/api/settings")
    assert r_settings_get.status_code == 200
    settings_data = r_settings_get.json()
    assert settings_data["success"] is True
    assert "settings" in settings_data

    r_settings_put = client.put("/api/settings", json={
        "display_name": "Senior Full-Stack Architect",
        "daily_hour_target": 10,
        "theme_preference": "dark",
        "notifications_enabled": True
    })
    assert r_settings_put.status_code == 200
    assert r_settings_put.json()["settings"]["daily_hour_target"] == 10
    assert r_settings_put.json()["settings"]["display_name"] == "Senior Full-Stack Architect"

    # 5. Test Weekly Goals API GET & PUT
    r_goals_put = client.put("/api/settings/weekly-goals", json={
        "weekly_goals": [
            {"id": 1, "emoji": "🎯", "text": "Ship High-Performance Feature", "color": "#10b981", "checked": True},
            {"id": 2, "emoji": "🚀", "text": "Deploy to Vercel Serverless", "color": "#38bdf8", "checked": True},
            {"id": 3, "emoji": "📚", "text": "Deep Work 50h", "color": "#8b5cf6", "checked": False},
            {"id": 4, "emoji": "💪", "text": "Gym 4x Weekly", "color": "#f59e0b", "checked": False},
            {"id": 5, "emoji": "🧘", "text": "Meditate Daily", "color": "#ec4899", "checked": False}
        ]
    })
    assert r_goals_put.status_code == 200
    goals_resp = r_goals_put.json()
    assert len(goals_resp["weekly_goals"]) == 5

    r_goals_get = client.get("/api/settings/weekly-goals")
    assert r_goals_get.status_code == 200
    assert r_goals_get.json()["weekly_goals"][0]["text"] == "Ship High-Performance Feature"

    # 6. Test Data Export API
    r_export = client.get("/api/settings/export")
    assert r_export.status_code == 200
    export_json = r_export.json()
    assert "habits" in export_json
    assert "weekly_goals" in export_json
    assert "notes" in export_json

    # 7. Test Notifications API
    r_notif = client.get("/api/notifications")
    assert r_notif.status_code == 200
    notif_data = r_notif.json()
    assert "notifications" in notif_data

    r_clear = client.post("/api/notifications/clear")
    assert r_clear.status_code == 200
    assert r_clear.json()["success"] is True

    # 8. Test Notes CRUD, Tagging, Pinning & Date Filtering
    today_str = date.today().isoformat()
    r_create_note = client.post("/api/notes", json={
        "title": "E2E Architecture Note",
        "content": "Fully verified all 10 deployment steps end to end.",
        "date": today_str,
        "tag": "DevOps",
        "category": "Technology & Engineering",
        "is_pinned": True
    })
    assert r_create_note.status_code == 200
    created_note = r_create_note.json()["note"]
    note_id = created_note["id"]
    assert created_note["title"] == "E2E Architecture Note"
    assert created_note["is_pinned"] is True

    # Test Pin Toggle
    r_pin = client.post(f"/api/notes/{note_id}/pin")
    assert r_pin.status_code == 200
    assert r_pin.json()["is_pinned"] is False

    # Test Notes Filter by Tag
    r_tag_filter = client.get("/api/notes?tag=DevOps")
    assert r_tag_filter.status_code == 200
    assert any(n["id"] == note_id for n in r_tag_filter.json()["notes"])

    # Test Note Update
    r_update = client.put(f"/api/notes/{note_id}", json={
        "title": "E2E Architecture Note Updated",
        "content": "Updated content successfully verified.",
        "date": today_str,
        "tag": "Architecture",
        "is_pinned": True
    })
    assert r_update.status_code == 200
    assert r_update.json()["note"]["title"] == "E2E Architecture Note Updated"

    # Test Note Delete
    r_del = client.delete(f"/api/notes/{note_id}")
    assert r_del.status_code == 200
    assert r_del.json()["success"] is True
