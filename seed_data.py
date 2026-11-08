from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Habit, HabitLog

DEFAULT_HABITS = [
    {
        "name": "DSA",
        "category": "DSA",
        "description": "LeetCode, Patterns",
        "icon": "💻",
        "color": "#10b981",
        "display_order": 1
    },
    {
        "name": "AI/ML",
        "category": "AI/ML",
        "description": "Python, ML, Deep Learning, RAG/LLM, LangChain",
        "icon": "🤖",
        "color": "#06b6d4",
        "display_order": 2
    },
    {
        "name": "DevOps",
        "category": "DevOps",
        "description": "Docker, Kubernetes, AWS",
        "icon": "☁️",
        "color": "#8b5cf6",
        "display_order": 3
    },
    {
        "name": "Cyber",
        "category": "Cyber",
        "description": "Linux, Cybersecurity",
        "icon": "🛡️",
        "color": "#f59e0b",
        "display_order": 4
    },
    {
        "name": "Personal Projects",
        "category": "Growth",
        "description": "Reading, Fitness, Content",
        "icon": "🌱",
        "color": "#84cc16",
        "display_order": 5
    },
    {
        "name": "Deep Work (2 hrs)",
        "category": "Productivity",
        "description": "Undistracted high-impact focus session",
        "icon": "🎯",
        "color": "#f59e0b",
        "display_order": 6
    },
    {
        "name": "Read 20 Pages",
        "category": "Learning",
        "description": "Read non-fiction, books, or technical articles",
        "icon": "📚",
        "color": "#8b5cf6",
        "display_order": 7
    },
    {
        "name": "Morning Workout",
        "category": "Fitness",
        "description": "30 mins strength training, jogging, or stretching",
        "icon": "🏋️",
        "color": "#3b82f6",
        "display_order": 8
    },
    {
        "name": "Drink 2.5L Water",
        "category": "Health",
        "description": "Maintain hydration with 8-10 glasses daily",
        "icon": "💧",
        "color": "#06b6d4",
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


def ensure_demo_user_seeded(db: Session, force_refresh_logs: bool = False):
    """
    Retrieves or creates the showcase demo user account ('demo@habitcrm.com' / 'demo123')
    populated with actual active habits, realistic multi-day completion streaks, 
    reflection notes, and category distributions.
    """
    import auth
    from models import User

    demo_email = "demo@habitcrm.com"
    demo_user = db.query(User).filter(User.email == demo_email).first()

    if not demo_user:
        demo_user = User(
            email=demo_email,
            hashed_password=auth.hash_password("demo123"),
            full_name="Alex Mercer (Demo)",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"Created demo user: {demo_user.email} (id={demo_user.id})")

    # Verify habits exist for demo user and are the Focus OS tracks
    habits = db.query(Habit).filter(Habit.user_id == demo_user.id).order_by(Habit.display_order).all()
    has_dsa = any(h.name == "DSA" for h in habits)
    if not habits or not has_dsa or force_refresh_logs:
        seed_default_habits(db, force=True, seed_sample_logs=False, user_id=demo_user.id)
        habits = db.query(Habit).filter(Habit.user_id == demo_user.id).order_by(Habit.display_order).all()

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    # Check existing logs count for current week
    habit_ids = [h.id for h in habits]
    existing_week_logs = 0
    if habit_ids:
        existing_week_logs = db.query(HabitLog).filter(
            HabitLog.habit_id.in_(habit_ids),
            HabitLog.date >= monday,
            HabitLog.date <= today
        ).count()

    if existing_week_logs == 0 or force_refresh_logs:
        # Wipe old logs for demo user if refreshing
        if habit_ids and force_refresh_logs:
            db.query(HabitLog).filter(HabitLog.habit_id.in_(habit_ids)).delete(synchronize_session=False)
            db.commit()

        # Seed 14 days of realistic logs (past 7 days + current week up to today)
        start_date = today - timedelta(days=13)
        sample_notes = {
            "Morning Workout": {
                today: "Morning outdoor interval run — 5.2 km 🏃‍♂️",
                today - timedelta(days=1): "45 mins functional strength & core workout 💪",
                today - timedelta(days=4): "Track sprint sessions + stretching",
            },
            "Drink 2.5L Water": {
                today: "Reached 2.5L target before 5:00 PM! 💧",
                today - timedelta(days=2): "Hit 3L daily goal with hydration tracking 🍋",
            },
            "Read 20 Pages": {
                today: "Read 25 pages of System Design Interview 📚",
                today - timedelta(days=3): "Finished chapter on distributed caching architectures",
            },
            "15-min Meditation": {
                today - timedelta(days=1): "Evening gratitude meditation, very restorative 🧘",
                today - timedelta(days=5): "Box breathing before team standup",
            },
            "Deep Work (2 hrs)": {
                today: "Deep work sprint: architected API caching layer 🎯",
                today - timedelta(days=2): "2 hours uninterrupted coding on PostgreSQL performance",
            },
            "AWS & Tech Practice": {
                today: "Container deployment & health probe validation 💻",
                today - timedelta(days=3): "AWS RDS PostgreSQL replica simulation & failover test ☁️",
            },
            "8,000 Steps Daily": {
                today: "Hit 9,450 steps with post-lunch walk 👟",
                today - timedelta(days=2): "10,240 steps achieved! Evening nature trail 🌲",
            },
            "Gratitude & Reflection": {
                today: "Grateful for solid team execution and personal consistency ✨",
                today - timedelta(days=1): "Reflected on weekly wins and system improvements",
            }
        }

        # Insert or update logs
        for idx, habit in enumerate(habits):
            notes_dict = sample_notes.get(habit.name, {})
            for d_offset in range(14):
                log_date = start_date + timedelta(days=d_offset)
                if log_date > today:
                    continue

                days_from_today = (today - log_date).days

                if habit.name == "Drink 2.5L Water":
                    is_completed = True
                elif habit.name == "Morning Workout":
                    is_completed = days_from_today not in (6, 11)
                elif habit.name == "Read 20 Pages":
                    is_completed = days_from_today not in (7, 12)
                elif habit.name == "15-min Meditation":
                    is_completed = days_from_today not in (4, 10)
                elif habit.name == "Deep Work (2 hrs)":
                    is_completed = days_from_today not in (3, 8, 13)
                elif habit.name == "Healthy Meal / No Junk":
                    is_completed = days_from_today not in (5, 9)
                elif habit.name == "AWS & Tech Practice":
                    is_completed = days_from_today not in (6, 12)
                elif habit.name == "Sleep by 11:00 PM":
                    is_completed = days_from_today not in (0, 3, 7, 11)
                elif habit.name == "8,000 Steps Daily":
                    is_completed = days_from_today not in (8, 13)
                elif habit.name == "Gratitude & Reflection":
                    is_completed = days_from_today not in (10,)
                else:
                    is_completed = (d_offset % 3 != 0)

                note = notes_dict.get(log_date)

                existing_log = db.query(HabitLog).filter(
                    HabitLog.habit_id == habit.id,
                    HabitLog.date == log_date
                ).first()

                if existing_log:
                    existing_log.completed = is_completed
                    existing_log.value = 1 if is_completed else 0
                    if note:
                        existing_log.notes = note
                else:
                    log = HabitLog(
                        user_id=demo_user.id,
                        habit_id=habit.id,
                        date=log_date,
                        completed=is_completed,
                        value=1 if is_completed else 0,
                        notes=note
                    )
                    db.add(log)

        db.commit()
        print(f"Rich demo logs and streaks seeded for demo user {demo_user.email}!")

    return demo_user

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_habits(db, force=True, seed_sample_logs=True)
    finally:
        db.close()
