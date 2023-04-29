import datetime
import logging

from garson.schedulers import interval
from garson.services import step


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


def my_step(svc, schedule):
    dt = datetime.datetime.utcnow()
    LOG.info("[%s] My service >> step << %s :: %s", svc, dt, schedule)
    # delta = datetime.timedelta(seconds=3)
    # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
    schedule.scheduler.set_next_run_schedule(delay=0.5)


def main():
    sch = interval.IntervalScheduler(name="single_step",
                                     target=my_step,
                                     interval=3)
    step.StepService(sch).serve()


if __name__ == "__main__":
    main()
