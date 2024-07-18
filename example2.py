import os
import time

import garson.run_controls.daemon
from garson.services import base
from garson.run_controls.daemon import sig_hooks
from garson.run_controls import daemon


class MyService(base.BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(
            contexts=[
                daemon.DaemonizeRc(
                    self,
                    hooks=(
                        garson.run_controls.daemon.TouchSignalHook("/Users/a.gruk/git/garson/heh"),
                    ),
                ),
            ],
        )

    def _serve(self):
        while 1:
            print("ahahah")
            time.sleep(1)

    def _stop(self):
        print("I am stopped")

    def _check_alive(self) -> None:
        print("Are you alive, son?")


my_service = MyService()
print(os.getpid())
my_service.serve()
