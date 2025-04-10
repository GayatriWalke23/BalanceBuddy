"""Database models for BalanceBuddy."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    preferences = Column(JSON)  # Store user preferences as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plans = relationship("DailyPlan", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

class DailyPlan(Base):
    __tablename__ = 'daily_plans'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime, nullable=False)
    meals = Column(JSON)  # Store meal plan as JSON
    workout = Column(JSON)  # Store workout plan as JSON
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="plans")

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)  # meal, workout, water, etc.
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reminders")
