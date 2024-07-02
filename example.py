import logging
import random

from garson.schedulers import interval
from garson.services import interval


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class FirstIteration(step.AbstractIteration):

    def _step(self):
        LOG.info("my_step_1 >> step  I. << %s", self._iteration)
        # while True:
        #     LOG.info(svc._steps.next())
        #     time.sleep(0.2)

        # dt = datetime.datetime.utcnow()
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


class SecondIteration(step.AbstractIteration):

    def _step(self):
        # dt = datetime.datetime.utcnow()
        LOG.info("my_step_2 >> step II. << %s", self._iteration)
        if random.randint(0, 10) % 2:
            raise ZeroDivisionError()
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


def main():
    step_1 = FirstIteration(interval.IntervalScheduler(interval=3))
    step_2 = SecondIteration(interval.IntervalScheduler(interval=1.2))
    step.IterationService(step_1, step_2).serve()


if __name__ == "__main__":
    main()
