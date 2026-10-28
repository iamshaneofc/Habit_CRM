from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Habit, HabitLog

DEFAULT_HABITS = [
    {
        "name": "Morning Workout",
        "category": "Fitness",
        "description": "30 mins strength training, jogging, or stretching",
        "icon": "🏋️",
        "color": "#3b82f6",
        "display_order": 1
    },
    {
        "name": "Drink 2.5L Water",
        "category": "Health",
        "description": "Maintain hydration with 8-10 glasses daily",
        "icon": "💧",
        "color": "#06b6d4",
        "display_order": 2
    },
    {
        "name": "Read 20 Pages",
        "category": "Learning",
        "description": "Read non-fiction, books, or technical articles",
        "icon": "📚",
        "color": "#8b5cf6",
        "display_order": 3
    },
    {
        "name": "15-min Meditation",
        "category": "Mindfulness",
        "description": "Mindful breathing and mental calmness",
        "icon": "🧘",
        "color": "#10b981",
        "display_order": 4
    },
    {
        "name": "Deep Work (2 hrs)",
        "category": "Productivity",
        "description": "Undistracted high-impact focus session",
        "icon": "🎯",
        "color": "#f59e0b",
        "display_order": 5
    },
    {
        "name": "Healthy Meal / No Junk",
        "category": "Nutrition",
        "description": "Whole food meals, limit refined sugar and processed foods",
        "icon": "🥗",
        "color": "#84cc16",
        "display_order": 6
    },
    {
        "name": "AWS & Tech Practice",
        "category": "Career",
        "description": "Hands-on labs: AWS RDS, Cloud, Python, DevOps",
        "icon": "💻",
        "color": "#6366f1",
        "display_order": 7
    },
    {
        "name": "Sleep by 11:00 PM",
        "category": "Recovery",
        "description": "7-8 hours quality sleep for recovery",
        "icon": "🌙",
        "color": "#ec4899",
        "display_order": 8
    },
    {
        "name": "8,000 Steps Daily",
        "category": "Activity",
        "description": "Evening walking or moving throughout the day",
        "icon": "👟",
        "color": "#14b8a6",
        "display_order": 9
    },
    {
        "name": "Gratitude & Reflection",
        "category": "Mindset",
        "description": "Write 3 wins and highlights before bed",
        "icon": "✍️",
        "color": "#f97316",
        "display_order": 10
    }
]

from typing import Optional

def seed_default_habits(db: Session, force: bool = False, seed_sample_logs: bool = True, user_id: Optional[int] = None):
    """
    Inserts 10 default habits into the database for a specific user or globally.
    Optionally seeds realistic past week data so charts and streak displays shine immediately.
    """
    query = db.query(Habit)
    if user_id is not None:
        query = query.filter(Habit.user_id == user_id)
    else:
        query = query.filter(Habit.user_id.is_(None))

    existing_count = query.count()
    if existing_count > 0 and not force:
        print(f"Database already contains {existing_count} habits for user_id={user_id}. Skipping seed.")
        return

    if force:
        if user_id is not None:
            user_h_ids = [h.id for h in query.all()]
            if user_h_ids:
                db.query(HabitLog).filter(HabitLog.habit_id.in_(user_h_ids)).delete(synchronize_session=False)
            query.delete(synchronize_session=False)
        else:
            db.query(HabitLog).filter(HabitLog.user_id.is_(None)).delete(synchronize_session=False)
            db.query(Habit).filter(Habit.user_id.is_(None)).delete(synchronize_session=False)
        db.commit()

    print(f"Seeding 10 default habits for user_id={user_id}...")
    created_habits = []
    for item in DEFAULT_HABITS:
        habit = Habit(
            user_id=user_id,
            name=item["name"],
            category=item["category"],
            description=item["description"],
            icon=item["icon"],
            color=item["color"],
            display_order=item["display_order"],
            is_active=True
        )
        db.add(habit)
        created_habits.append(habit)

    db.commit()

    # Refresh habits with IDs
    for h in created_habits:
        db.refresh(h)

    # Seed sample checkmarks for current week to showcase visual charts immediately
    if seed_sample_logs:
        today = date.today()
        # Find current Monday
        monday = today - timedelta(days=today.weekday())
        
        sample_pattern = [
            [True, True, True, False, False, False, False], # Habit 1
            [True, True, True, True, True, False, False],  # Habit 2
            [True, False, True, True, False, False, False], # Habit 3
            [True, True, True, True, False, False, False],  # Habit 4
            [True, True, False, True, False, False, False], # Habit 5
            [True, True, True, False, False, False, False], # Habit 6
            [True, True, True, True, False, False, False],  # Habit 7
            [True, True, False, False, False, False, False],# Habit 8
            [True, True, True, True, True, False, False],  # Habit 9
            [True, False, True, True, False, False, False], # Habit 10
        ]

        for idx, habit in enumerate(created_habits):
            pattern = sample_pattern[idx % len(sample_pattern)]
            for day_offset in range(7):
                log_date = monday + timedelta(days=day_offset)
                if log_date <= today:
                    is_completed = pattern[day_offset]
                    log = HabitLog(
                        user_id=user_id,
                        habit_id=habit.id,
                        date=log_date,
                        completed=is_completed,
                        value=1 if is_completed else 0
                    )
                    db.add(log)

        db.commit()
        print("Sample habit logs seeded for the current week!")

    print(f"Successfully seeded {len(created_habits)} habits for user_id={user_id}.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_habits(db, force=True, seed_sample_logs=True)
    finally:
        db.close()
