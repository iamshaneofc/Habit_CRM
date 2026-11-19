import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
from main import app

def test_settings_and_notifications_api():
    database.upgrade_schema()
    client = TestClient(app)

    # 1. Get default settings
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()["settings"]
    assert "daily_hour_target" in data
    assert "theme_preference" in data
    assert "weekly_goals" in data
    assert len(data["weekly_goals"]) == 5

    # 2. Update settings
    res_up = client.put("/api/settings", json={
        "display_name": "Senior Operator",
        "profession": "Systems Architect",
        "daily_hour_target": 10,
        "theme_preference": "light",
        "notifications_enabled": True
    })
    assert res_up.status_code == 200
    up_data = res_up.json()["settings"]
    assert up_data["daily_hour_target"] == 10
    assert up_data["theme_preference"] == "light"

    # 3. Get weekly goals
    res_goals = client.get("/api/settings/weekly-goals")
    assert res_goals.status_code == 200
    assert len(res_goals.json()["goals"]) == 5

    # 4. Update weekly goals
    custom_goals = [
        "Deliver System V2",
        "Complete 30 LeetCode Hard",
        "Deploy Kubernetes Cluster",
        "Bench Press 100kg",
        "Sleep 8h Consistently"
    ]
    res_up_goals = client.put("/api/settings/weekly-goals", json={"goals": custom_goals})
    assert res_up_goals.status_code == 200
    assert res_up_goals.json()["goals"] == custom_goals

    # 5. Export user data
    res_export = client.get("/api/settings/export")
    assert res_export.status_code == 200
    exp_data = res_export.json()
    assert "export_version" in exp_data
    assert "habits" in exp_data
    assert "notes" in exp_data

    # 6. Notifications API
    res_notif = client.get("/api/notifications")
    assert res_notif.status_code == 200
    notif_data = res_notif.json()
    assert "notifications" in notif_data
    assert "unread_count" in notif_data
    assert len(notif_data["notifications"]) >= 3

    # 7. Clear notifications
    res_clear = client.post("/api/notifications/clear")
    assert res_clear.status_code == 200
    assert res_clear.json()["success"] is True
