# Scheduler File for Reminder Functionality

import asyncio
import logging

from backend.db.crud import DatabaseService
from backend.db.database import SessionLocal

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 5

# Function to process due reminders and mark them as triggered
def process_due_reminders(db, now=None) -> list:
    service = DatabaseService(db)
    due = service.get_due_reminders(now=now)
    for reminder in due:
        service.mark_triggered(reminder.id)
        logger.info("Reminder triggered: %s", reminder.message)
    return due

# Function to check for due reminders once and return the count of due reminders
def _check_once() -> int:
    db = SessionLocal()
    try:
        due = process_due_reminders(db)
        return len(due)
    finally:
        db.close()

# Asynchronous loop to continuously check for due reminders at regular intervals
async def reminder_loop():
    while True:
        try:
            await asyncio.to_thread(_check_once)
        except Exception:
            logger.exception("Error checking reminders")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)