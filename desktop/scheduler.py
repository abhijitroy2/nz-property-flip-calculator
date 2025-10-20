from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .config import ScheduleConfig


class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.started = False

    def start(self) -> None:
        if not self.started:
            self.scheduler.start()
            self.started = True

    def schedule(self, schedule: ScheduleConfig, func: Callable[[], None]) -> None:
        self.scheduler.remove_all_jobs()
        if schedule.mode == "cron":
            trig = CronTrigger(
                minute=schedule.cron.get("minute", "0"),
                hour=schedule.cron.get("hour", "0"),
                day=schedule.cron.get("day", "*"),
                month=schedule.cron.get("month", "*"),
                day_of_week=schedule.cron.get("day_of_week", "*"),
            )
        else:
            trig = IntervalTrigger(minutes=max(1, int(schedule.minutes or 60)))
        self.scheduler.add_job(func, trig, id="batch-run")

    def shutdown(self) -> None:
        if self.started:
            self.scheduler.shutdown(wait=False)
            self.started = False


