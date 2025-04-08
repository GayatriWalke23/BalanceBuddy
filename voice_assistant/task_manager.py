"""Task manager module for handling tasks and reminders."""
import os
from datetime import datetime
import threading
import time
from typing import Optional

from plyer import notification
from voice_assistant.db.database import Database

class TaskManager:
    def __init__(self, db_path: str = "tasks.db"):
        """Initialize task manager."""
        self.db = Database(db_path)
        self._stop_event = threading.Event()
        self._reminder_thread = None

    def start_reminder_checker(self):
        """Start the reminder checking thread."""
        if self._reminder_thread is None:
            self._stop_event.clear()
            self._reminder_thread = threading.Thread(target=self._check_reminders)
            self._reminder_thread.daemon = True
            self._reminder_thread.start()

    def stop_reminder_checker(self):
        """Stop the reminder checking thread."""
        if self._reminder_thread is not None:
            self._stop_event.set()
            self._reminder_thread.join()
            self._reminder_thread = None

    def _check_reminders(self):
        """Check for due reminders periodically."""
        while not self._stop_event.is_set():
            due_reminders = self.db.get_due_reminders()
            
            for reminder in due_reminders:
                self._show_notification(
                    title="Task Reminder",
                    message=f"Don't forget: {reminder['title']}"
                )
                self.db.mark_reminder_triggered(reminder['id'])
            
            # Sleep for 30 seconds before next check
            time.sleep(30)

    def _show_notification(self, title: str, message: str):
        """Show a system notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                timeout=10,  # seconds
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")

    def add_task(self, title: str, reminder_time: Optional[datetime] = None) -> int:
        """Add a new task with optional reminder."""
        task_id = self.db.add_task(title, reminder_time)
        print(f"✅ Added task: {title}")
        if reminder_time:
            print(f"⏰ Reminder set for: {reminder_time}")
        return task_id

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        if self.db.complete_task(task_id):
            print(f"✅ Marked task {task_id} as completed")
            return True
        print(f"❌ Task {task_id} not found")
        return False

    def list_tasks(self, include_completed: bool = False):
        """List all tasks."""
        tasks = self.db.get_tasks(include_completed)
        if not tasks:
            print("📝 No tasks found")
            return []
        
        print("\n📋 Tasks:")
        for task in tasks:
            status = "✅" if task['is_completed'] else "⭕"
            reminder = f" ⏰ {task['reminder_time']}" if task['reminder_time'] else ""
            print(f"{status} [{task['id']}] {task['title']}{reminder}")
        
        return tasks
