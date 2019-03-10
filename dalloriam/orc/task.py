from .client import ORCClient

import time


class Task:

    def __init__(self, name: str, orc_client: ORCClient = None) -> None:
        self._client = orc_client or ORCClient()
        self._name = name

    def start(self) -> None:
        self._client.do('task/start', {'name': self._name})

    def stop(self) -> None:
        self._client.do('task/stop', {'name': self._name})

    @property
    def running(self) -> bool:
        # TODO: Not super optimal, add way to check task status directly.
        return self._name in self._client.do('task/running')['tasks']


def requires(task_name: str, teardown: bool = False):
    def decorator(fn):
        def internal(*args, **kwargs):
            t = Task(task_name)
            if not t.running:
                t.start()
                time.sleep(2)  # TODO: Customize timeout

            x = fn(*args, **kwargs)

            if teardown:
                t.stop()

            return x

        return internal
    return decorator
