from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    display_name = Column(String(100), nullable=True)
    profession = Column(String(100), nullable=True)
    bio = Column(String(255), nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    tracking_start_date = Column(Date, nullable=True)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "display_name": self.display_name or self.full_name or self.email.split("@")[0],
            "profession": self.profession,
            "bio": self.bio,
            "onboarding_completed": bool(self.onboarding_completed),
            "tracking_start_date": self.tracking_start_date.isoformat() if self.tracking_start_date else None,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, default="General")
    description = Column(String(255), nullable=True)
    subtopics = Column(Text, nullable=True)
    icon = Column(String(20), default="🎯")
    color = Column(String(20), default="#10b981")  # Emerald accent
    daily_target = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    activation_date = Column(Date, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan", order_by="HabitLog.date")

    def get_subtopics_list(self):
        if self.subtopics:
            return [s.strip() for s in self.subtopics.split(",") if s.strip()]
        if self.description:
            return [t.strip() for t in self.description.split(",") if t.strip()]
        return [self.category]

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "subtopics": self.get_subtopics_list(),
            "icon": self.icon,
            "color": self.color,
            "daily_target": self.daily_target,
            "is_active": self.is_active,
            "display_order": self.display_order,
            "activation_date": self.activation_date.isoformat() if self.activation_date else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=False, nullable=False)
    value = Column(Integer, default=1)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    habit = relationship("Habit", back_populates="logs")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "habit_id": self.habit_id,
            "date": self.date.isoformat() if self.date else None,
            "completed": self.completed,
            "value": self.value,
            "notes": self.notes
        }
