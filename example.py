import datetime
import logging
import time

from garson.schedulers import interval
from garson.services import step


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


def my_step_1(svc: step.StepService, schedule):
    LOG.info("my_step_1 >> step  I. << %s", schedule.iteration)
    # while True:
    #     LOG.info(svc._steps.next())
    #     time.sleep(0.2)

    # dt = datetime.datetime.utcnow()
    # delta = datetime.timedelta(seconds=3)
    # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
    # schedule.scheduler.set_next_run_schedule(delay=0.5)


def my_step_2(svc, schedule):
    dt = datetime.datetime.utcnow()
    LOG.info("my_step_2 >> step II. << %s", schedule.iteration)
    # delta = datetime.timedelta(seconds=3)
    # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
    # schedule.scheduler.set_next_run_schedule(delay=0.5)


def main():
    sch_1 = interval.IntervalScheduler(name="single_step",
                                       target=my_step_1,
                                       interval=3)
    sch_2 = interval.IntervalScheduler(name="second_step",
                                       target=my_step_2,
                                       interval=1.2)
    step.StepService(sch_1, sch_2).serve()


if __name__ == "__main__":
    LOG.info("blah", a="A", b="B", c=42)
    main()
