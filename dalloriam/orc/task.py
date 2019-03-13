from .client import ORCClient

import time


class Task:

    """ Tasks wraps around the task ORC module. """

    def __init__(self, name: str, orc_client: ORCClient = None) -> None:
        """
        Task constructor.
        Args:
            name (str): The name of the task, as defined in the taskdef loaded by ORC.
            orc_client (Optional[ORCClient]): The ORC client instance to use.
        """
        self._client = orc_client or ORCClient()
        self._name = name

    def start(self) -> None:
        """
        Starts the task.
        """
        self._client.do('task/start', name=self._name)

    def stop(self) -> None:
        """
        Stops the task.
        """
        self._client.do('task/stop', name=self._name)

    @property
    def running(self) -> bool:
        """
        Gets the current status of the task.
        Returns:
            Whether the task is running.
        """
        # TODO: Not super optimal, add way to check task status directly.
        return self._name in self._client.do('task/running')['tasks']


def requires(task_name: str, teardown: bool = False):
    """
    The requires decorator starts the specified task before invoking the wrapped method,
    with the option of terminating it afterwards.
    Args:
        task_name (str): The name of the required task.
        teardown (bool): Whether to tear the task down on wrapped method exit.
    """
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
