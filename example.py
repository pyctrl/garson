import logging

from garson.schedulers import interval
from garson.services import step


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class FirstStep(step.AbstractStep):

    def _step(self):
        LOG.info("my_step_1 >> step  I. << %s", self._iteration)
        # while True:
        #     LOG.info(svc._steps.next())
        #     time.sleep(0.2)

        # dt = datetime.datetime.utcnow()
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


class SecondStep(step.AbstractStep):

    def _step(self):
        # dt = datetime.datetime.utcnow()
        LOG.info("my_step_2 >> step II. << %s", self._iteration)
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


def main():
    step_1 = FirstStep(interval.IntervalScheduler(interval=3))
    step_2 = SecondStep(interval.IntervalScheduler(interval=1.2))
    step.StepService(step_1, step_2).serve()


if __name__ == "__main__":
    main()
