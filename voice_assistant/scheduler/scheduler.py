"""Scheduler for BalanceBuddy notifications."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from plyer import notification
from datetime import datetime, time
import pytz

class NotificationScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.timezone = pytz.timezone('America/New_York')
        
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            
    def schedule_meal_reminder(self, meal_type: str, time_str: str):
        """Schedule a meal reminder.
        
        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            time_str: Time in 24-hour format (HH:MM)
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=self.timezone
            )
            
            self.scheduler.add_job(
                self._show_meal_notification,
                trigger=trigger,
                args=[meal_type],
                id=f"meal_{meal_type}_{time_str}"
            )
            
        except ValueError:
            print(f"Invalid time format: {time_str}. Use HH:MM format.")
            
    def schedule_workout_reminder(self, days: list, time_str: str):
        """Schedule a workout reminder.
        
        Args:
            days: List of days (mon, tue, wed, thu, fri, sat, sun)
            time_str: Time in 24-hour format (HH:MM)
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            trigger = CronTrigger(
                day_of_week=','.join(days),
                hour=hour,
                minute=minute,
                timezone=self.timezone
            )
            
            self.scheduler.add_job(
                self._show_workout_notification,
                trigger=trigger,
                id=f"workout_{'_'.join(days)}_{time_str}"
            )
            
        except ValueError:
            print(f"Invalid time format: {time_str}. Use HH:MM format.")
            
    def _show_meal_notification(self, meal_type: str):
        """Show a meal reminder notification."""
        notification.notify(
            title='BalanceBuddy Meal Reminder',
            message=f"Time for {meal_type}! Check your meal plan.",
            app_icon=None,
            timeout=10
        )
        
    def _show_workout_notification(self):
        """Show a workout reminder notification."""
        notification.notify(
            title='BalanceBuddy Workout Reminder',
            message="Time to work out! Check your exercise plan.",
            app_icon=None,
            timeout=10
        )
