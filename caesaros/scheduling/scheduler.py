from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from caesaros.state.models import RunRequest


class Scheduler:
    """A single-process scheduler; definitions are persisted and restored on startup."""
    def __init__(self, runtime):
        self.runtime = runtime
        self.engine = AsyncIOScheduler(timezone=runtime.settings.timezone)

    def start(self):
        self.engine.start()
        for item in self.runtime.store.schedules():
            self.configure(item)

    def configure(self, item):
        if self.engine.get_job(item['id']):
            self.engine.remove_job(item['id'])
        if item['enabled']:
            self.engine.add_job(self.trigger, CronTrigger(hour=item['hour'], minute=item['minute'],
                                timezone=self.runtime.settings.timezone), id=item['id'],
                                args=[item['id']], max_instances=1, coalesce=True, misfire_grace_time=300)

    async def trigger(self, name):
        item = next(s for s in self.runtime.store.schedules() if s['id'] == name)
        state = self.runtime.submit(RunRequest(user_input=item['prompt'], workflow=name))
        item['last_run_id'] = state['id']
        self.runtime.store.save_schedule(item)
        return state

    def list(self):
        items = self.runtime.store.schedules()
        for item in items:
            job = self.engine.get_job(item['id'])
            item['next_run'] = job.next_run_time.isoformat() if job and job.next_run_time else None
            item['timezone'] = self.runtime.settings.timezone
        return items

    def close(self):
        self.engine.shutdown(wait=False)
