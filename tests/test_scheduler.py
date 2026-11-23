# Tests for Scheduler Module
# Uses pytest.

from datetime import datetime, timedelta, timezone
from multiprocessing import process
from backend.scheduler import process_due_reminders

# Helper function to get the current UTC time without timezone information
def utc_in(hours: float = 0) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=hours)

# Tests for the process_due_reminders function
class TestProcessDueReminders:

    # Tests that due reminders are marked as triggered and returned
    def test_marks_due_reminders_as_triggered(self, db, service):
        due = service.create_reminder("due", utc_in(hours=-1))
        future = service.create_reminder("future", utc_in(hours=5))

        processed = process_due_reminders(db, now=utc_in(hours=2))

        assert [r.message for r in processed] == ["due"]
        assert due.is_triggered is True
        assert future.is_triggered is False

    # Tests that no reminders are returned if none are due
    def test_returns_empty_list_when_nothing_is_due(self, db, service):
        service.create_reminder("future", utc_in(hours=5))

        processed = process_due_reminders(db, now=utc_in(hours=1))

        assert processed == []

    # Tests that the same reminder is not triggered twice
    def test_does_not_trigger_the_same_reminder_twice(self, db, service):
        service.create_reminder("once", utc_in(hours=1))

        first = process_due_reminders(db, now=utc_in(hours=2))
        second = process_due_reminders(db, now=utc_in(hours=2))

        assert len(first) == 1
        assert second == []