"""FastAPI server for BalanceBuddy."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="BalanceBuddy API")

class DailyPlan(BaseModel):
    date: datetime
    meals: dict
    workout: List[str]
    completed: bool = False

class Reminder(BaseModel):
    time: datetime
    message: str
    type: str  # meal, workout, water, etc.
    completed: bool = False

# In-memory storage (replace with database later)
daily_plans = {}
reminders = []

@app.get("/")
async def root():
    return {"message": "Welcome to BalanceBuddy API"}

@app.post("/plans/")
async def create_plan(plan: DailyPlan):
    daily_plans[plan.date.date()] = plan
    return plan

@app.get("/plans/{date}")
async def get_plan(date: str):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    plan = daily_plans.get(date_obj)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.post("/reminders/")
async def create_reminder(reminder: Reminder):
    reminders.append(reminder)
    return reminder

@app.get("/reminders/")
async def get_reminders(completed: Optional[bool] = None):
    if completed is None:
        return reminders
    return [r for r in reminders if r.completed == completed]
