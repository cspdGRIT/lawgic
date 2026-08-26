"""Daily deadline-reminder sweep. APScheduler (open source, MIT) running in-process —
no Redis/Celery broker needed, which matters for a single free-tier Render instance.
Started/stopped from main.py's lifespan."""

import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.database import async_session
from app.models.case import Case
from app.models.user import User
from app.services.notifications import send_deadline_reminder

logger = logging.getLogger("lawgic.scheduler")

REMIND_WITHIN_DAYS = 3
_scheduler: AsyncIOScheduler | None = None


async def _send_due_reminders() -> None:
    today = date.today()
    horizon = today + timedelta(days=REMIND_WITHIN_DAYS)

    async with async_session() as db:
        result = await db.execute(
            select(Case, User)
            .join(User, Case.user_id == User.id)
            .where(
                Case.deadline_date.is_not(None),
                Case.deadline_date >= today,
                Case.deadline_date <= horizon,
                Case.deadline_reminder_sent.is_(False),
            )
        )
        rows = result.all()

        for case, user in rows:
            # OTP-created accounts get a placeholder @phone.lawgic.local address —
            # nothing to send to until they add a real email.
            if not user.email or user.email.endswith("@phone.lawgic.local"):
                continue

            days_left = (case.deadline_date - today).days
            subject = f"Lawgic: {days_left} day{'s' if days_left != 1 else ''} left on \"{case.title}\""
            body = (
                f"Hi {user.full_name},\n\n"
                f"Your case \"{case.title}\" has a deadline on {case.deadline_date.isoformat()} "
                f"({days_left} day{'s' if days_left != 1 else ''} from now).\n\n"
                f"Log in to Lawgic to review it: https://lawgic-dusky.vercel.app/cases\n\n"
                f"— Lawgic"
            )
            try:
                await send_deadline_reminder(user.email, subject, body)
                case.deadline_reminder_sent = True
            except Exception as e:
                logger.warning("reminder send failed for case %s: %s", case.id, e)

        await db.commit()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(_send_due_reminders, "cron", hour=8, minute=0, id="deadline_reminders")
    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
