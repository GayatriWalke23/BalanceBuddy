"""Database module for BalanceBuddy using SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional, Dict

from .models import Base, User, DailyPlan, Reminder

class Database:
    def __init__(self, db_url: str = "sqlite:///balancebuddy.db"):
        """Initialize database connection."""
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_db()

    def _init_db(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def create_user(self, username: str, preferences: Dict = None) -> Optional[User]:
        """Create a new user."""
        with self.get_session() as session:
            try:
                user = User(username=username, preferences=preferences or {})
                session.add(user)
                session.commit()
                return user
            except SQLAlchemyError:
                session.rollback()
                return None

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()

    def create_daily_plan(self, user_id: int, date: datetime, meals: Dict, workout: List[str]) -> Optional[DailyPlan]:
        """Create a new daily plan."""
        with self.get_session() as session:
            try:
                plan = DailyPlan(
                    user_id=user_id,
                    date=date,
                    meals=meals,
                    workout=workout
                )
                session.add(plan)
                session.commit()
                return plan
            except SQLAlchemyError:
                session.rollback()
                return None

    def get_daily_plan(self, user_id: int, date: datetime) -> Optional[DailyPlan]:
        """Get daily plan for a specific date."""
        with self.get_session() as session:
            return session.query(DailyPlan).filter(
                DailyPlan.user_id == user_id,
                DailyPlan.date == date
            ).first()

    def create_reminder(self, user_id: int, time: datetime, message: str, type: str) -> Optional[Reminder]:
        """Create a new reminder."""
        with self.get_session() as session:
            try:
                reminder = Reminder(
                    user_id=user_id,
                    time=time,
                    message=message,
                    type=type
                )
                session.add(reminder)
                session.commit()
                return reminder
            except SQLAlchemyError:
                session.rollback()
                return None

    def get_due_reminders(self, user_id: int) -> List[Reminder]:
        """Get all uncompleted reminders that are due."""
        with self.get_session() as session:
            return session.query(Reminder).filter(
                Reminder.user_id == user_id,
                Reminder.time <= datetime.utcnow(),
                Reminder.completed == False
            ).all()

    def mark_reminder_completed(self, reminder_id: int) -> bool:
        """Mark a reminder as completed."""
        with self.get_session() as session:
            try:
                reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
                if reminder:
                    reminder.completed = True
                    session.commit()
                    return True
                return False
            except SQLAlchemyError:
                session.rollback()
                return False
