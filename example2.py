import os
import time

from garson.services import base
from garson.middlewares.daemon import mws, sig_hooks


class MyService(base.BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(
            contexts=[
                mws.DaemonizeMiddleware(
                    self,
                    hooks=(
                        sig_hooks.TouchSignalHook("/Users/a.gruk/git/garson/heh"),
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
