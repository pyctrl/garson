import logging
import random

from garson.rcs import daemon
from garson.schedulers import interval as isched
from garson.services import interval as isvc


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class FirstIteration(isvc.AbstractIteration):

    def _iterate(self):
        LOG.info("my_step_1 >> step  I. << %s", self._iteration)
        # while True:
        #     LOG.info(svc._steps.next())
        #     time.sleep(0.2)

        # dt = datetime.datetime.utcnow()
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


class SecondIteration(isvc.AbstractIteration):

    def _iterate(self):
        # dt = datetime.datetime.utcnow()
        LOG.info("my_step_2 >> step II. << %s", self._iteration)
        if random.randint(0, 10) % 2:
            raise ZeroDivisionError()
        # delta = datetime.timedelta(seconds=3)
        # schedule.scheduler.set_next_run_schedule(timestamp=(dt + delta))
        # schedule.scheduler.set_next_run_schedule(delay=0.5)


def main():
    svc = isvc.IterationService()
    svc.register_rc(daemon.DaemonizeRc.pack())
    svc.register_iteration(
        scheduler_pack=isched.IntervalScheduler.pack(interval=3),
        iteration_pack=FirstIteration.pack(),
    )
    svc.register_iteration(
        scheduler_pack=isched.IntervalScheduler.pack(interval=1.2),
        iteration_pack=SecondIteration.pack(),
    )
    svc.serve()


if __name__ == "__main__":
    main()
