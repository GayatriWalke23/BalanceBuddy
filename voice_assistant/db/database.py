"""Database module for storing tasks and reminders."""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

class Database:
    def __init__(self, db_path: str = "tasks.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    is_completed BOOLEAN DEFAULT 0
                )
            """)
            
            # Create reminders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    reminder_time TIMESTAMP NOT NULL,
                    is_triggered BOOLEAN DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)
            
            conn.commit()

    def add_task(self, title: str, reminder_time: Optional[datetime] = None) -> int:
        """Add a new task and optional reminder."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add task
            cursor.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,)
            )
            task_id = cursor.lastrowid
            
            # Add reminder if specified
            if reminder_time:
                cursor.execute(
                    "INSERT INTO reminders (task_id, reminder_time) VALUES (?, ?)",
                    (task_id, reminder_time)
                )
            
            conn.commit()
            return task_id

    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        """Get all tasks."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT t.id, t.title, t.created_at, t.completed_at, 
                       t.is_completed, r.reminder_time
                FROM tasks t
                LEFT JOIN reminders r ON t.id = r.task_id
            """
            
            if not include_completed:
                query += " WHERE t.is_completed = 0"
                
            cursor.execute(query)
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                tasks.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'completed_at': row[3],
                    'is_completed': bool(row[4]),
                    'reminder_time': row[5]
                })
            
            return tasks

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE tasks 
                SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due but not triggered."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT r.id, t.title, r.reminder_time
                FROM reminders r
                JOIN tasks t ON r.task_id = t.id
                WHERE r.is_triggered = 0 
                AND r.reminder_time <= CURRENT_TIMESTAMP
                AND t.is_completed = 0
                """
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row[0],
                    'title': row[1],
                    'reminder_time': row[2]
                })
            
            return reminders

    def mark_reminder_triggered(self, reminder_id: int):
        """Mark a reminder as triggered."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reminders SET is_triggered = 1 WHERE id = ?",
                (reminder_id,)
            )
            conn.commit()
