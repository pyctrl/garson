import datetime
import logging

from garson.schedulers import interval
from garson.services import step


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class ExampleService(step.StepService):

    def _step(self, scheduler):
        dt = datetime.datetime.utcnow()
        LOG.info("My service >> step << %s", dt)
        delta = datetime.timedelta(seconds=3)
        scheduler.set_next_step_schedule(timestamp=(dt + delta))
        scheduler.set_next_step_schedule(delta=10.5)


def main():
    ExampleService(interval.IntervalScheduler(3)).serve()


if __name__ == "__main__":
    main()
