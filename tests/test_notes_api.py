import os
import sys
from datetime import date, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
from main import app
from models import User, Habit, Note

def test_notes_crud_and_filtering():
    database.upgrade_schema()
    client = TestClient(app)

    # 1. Create a note for today
    today_str = date.today().isoformat()
    res = client.post("/api/notes", json={
        "title": "Mastering Dynamic Programming",
        "content": "Solved 3 2D-DP problems on LeetCode: Edit Distance, Maximal Square.",
        "date": today_str,
        "tag": "DSA",
        "category": "Technology & Engineering",
        "is_pinned": True
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    note_id = data["note"]["id"]
    assert data["note"]["title"] == "Mastering Dynamic Programming"
    assert data["note"]["tag"] == "DSA"
    assert data["note"]["is_pinned"] is True

    # 2. Create another note for yesterday
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    res2 = client.post("/api/notes", json={
        "title": "Docker Multi-stage Builds",
        "content": "Optimized production image size from 1.2GB down to 180MB.",
        "date": yesterday_str,
        "tag": "DevOps",
        "category": "Technology & Engineering"
    })
    assert res2.status_code == 200
    note2_id = res2.json()["note"]["id"]

    # 3. List notes without filter
    res_list = client.get("/api/notes")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 2
    # Verify pinned note is first
    assert list_data["notes"][0]["is_pinned"] is True

    # 4. Filter notes by tag "DSA"
    res_tag = client.get("/api/notes?tag=DSA")
    assert res_tag.status_code == 200
    tag_notes = res_tag.json()["notes"]
    assert any(n["id"] == note_id for n in tag_notes)
    assert not any(n["id"] == note2_id for n in tag_notes)

    # 5. Filter notes by date (today)
    res_date = client.get(f"/api/notes?date={today_str}")
    assert res_date.status_code == 200
    date_notes = res_date.json()["notes"]
    assert any(n["id"] == note_id for n in date_notes)

    # 6. Search notes by keyword
    res_search = client.get("/api/notes?search=LeetCode")
    assert res_search.status_code == 200
    search_notes = res_search.json()["notes"]
    assert any(n["id"] == note_id for n in search_notes)

    # 7. Update note
    res_update = client.put(f"/api/notes/{note_id}", json={
        "title": "Mastering Dynamic Programming (Updated)",
        "content": "Solved 4 problems now including Knapsack."
    })
    assert res_update.status_code == 200
    assert res_update.json()["note"]["title"] == "Mastering Dynamic Programming (Updated)"

    # 8. Toggle pin
    res_pin = client.post(f"/api/notes/{note_id}/pin")
    assert res_pin.status_code == 200
    assert res_pin.json()["is_pinned"] is False

    # 9. Calendar summary
    res_cal = client.get(f"/api/notes/calendar-summary?year={date.today().year}&month={date.today().month}")
    assert res_cal.status_code == 200
    cal_data = res_cal.json()
    assert today_str in cal_data["notes_by_date"]
    assert cal_data["notes_by_date"][today_str] >= 1

    # 10. Delete notes
    res_del1 = client.delete(f"/api/notes/{note_id}")
    assert res_del1.status_code == 200
    res_del2 = client.delete(f"/api/notes/{note2_id}")
    assert res_del2.status_code == 200

    # Verify deleted
    res_check = client.get(f"/api/notes/{note_id}")
    assert res_check.status_code == 404
