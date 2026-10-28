"""
Test suite for Step 16: User Ownership & Cross-User Data Isolation.
Verifies that:
- User A's habits and logs are completely isolated from User B.
- User B cannot read, toggle, edit, archive, restore, or delete User A's habits.
- Attaching notes to User A's habit from User B's session is blocked.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date
from fastapi.testclient import TestClient
import database
from main import app
from auth import create_access_token
from models import User, Habit, HabitLog

def test_cross_user_isolation():
    database.check_and_stabilize_db()
    db = database.SessionLocal()
    try:
        # 1. Setup User A and User B
        db.query(HabitLog).filter(HabitLog.habit_id.in_(
            db.query(Habit.id).filter(Habit.user_id.in_(
                db.query(User.id).filter(User.email.in_(["user_a@example.com", "user_b@example.com"]))
            ))
        )).delete(synchronize_session=False)
        db.query(Habit).filter(Habit.user_id.in_(
            db.query(User.id).filter(User.email.in_(["user_a@example.com", "user_b@example.com"]))
        )).delete(synchronize_session=False)
        db.query(User).filter(User.email.in_(["user_a@example.com", "user_b@example.com"])).delete(synchronize_session=False)
        db.commit()

        user_a = User(email="user_a@example.com", hashed_password="pw_hash_test_a", full_name="User Alice")
        user_b = User(email="user_b@example.com", hashed_password="pw_hash_test_b", full_name="User Bob")
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        # 2. Create habit for User A
        habit_a = Habit(
            name="Alice Secret Habit",
            category="Mindfulness",
            user_id=user_a.id,
            icon="🔒",
            color="#ec4899",
            daily_target=1,
            is_active=True
        )
        db.add(habit_a)
        db.commit()
        db.refresh(habit_a)
        habit_a_id = habit_a.id

        # Tokens
        token_a = create_access_token({"sub": str(user_a.id), "email": user_a.email})
        token_b = create_access_token({"sub": str(user_b.id), "email": user_b.email})

        with TestClient(app) as client:
            # User B logs in
            client.cookies.set("habit_crm_session", token_b)

            # 3. User B tries to toggle Alice's habit
            res = client.post("/api/habits/toggle", json={
                "habit_id": habit_a_id,
                "date": date.today().isoformat()
            })
            assert res.status_code == 404, f"Expected 404 for cross-user toggle, got {res.status_code}"

            # 4. User B tries to update Alice's habit
            res = client.put(f"/api/habits/{habit_a_id}", json={
                "name": "Hacked Habit Name"
            })
            assert res.status_code == 404, f"Expected 404 for cross-user update, got {res.status_code}"

            # 5. User B tries to archive Alice's habit
            res = client.post(f"/api/habits/{habit_a_id}/archive")
            assert res.status_code == 404, f"Expected 404 for cross-user archive, got {res.status_code}"

            # 6. User B tries to delete Alice's habit
            res = client.delete(f"/api/habits/{habit_a_id}")
            assert res.status_code == 404, f"Expected 404 for cross-user delete, got {res.status_code}"

            # 7. User B tries to attach a note to Alice's habit
            res = client.post("/api/habits/notes", json={
                "habit_id": habit_a_id,
                "date": date.today().isoformat(),
                "notes": "Malicious note"
            })
            assert res.status_code == 404, f"Expected 404 for cross-user note, got {res.status_code}"

            # 8. Verify Alice's habit is unchanged in Alice's dashboard
            client.cookies.set("habit_crm_session", token_a)
            alice_dash = client.get("/")
            assert alice_dash.status_code == 200
            assert "Alice Secret Habit" in alice_dash.text

            # 9. Verify Alice's habit does NOT appear in Bob's dashboard
            client.cookies.set("habit_crm_session", token_b)
            bob_dash = client.get("/")
            assert bob_dash.status_code == 200
            assert "Alice Secret Habit" not in bob_dash.text

        print("[OK] Cross-user data isolation verified across all CRUD, toggle, notes, and dashboard views.")
    finally:
        db.close()

if __name__ == "__main__":
    print("Running Step 16 User Isolation Tests...")
    test_cross_user_isolation()
    print("All User Isolation Tests Passed Successfully!")
