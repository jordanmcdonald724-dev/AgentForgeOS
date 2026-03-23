import asyncio
import logging
from typing import Awaitable, Callable, List

logger = logging.getLogger(__name__)

BackgroundTask = Callable[[], Awaitable[None]]


class WorkerSystem:
    """
    Minimal background worker registry. Tasks registered here will run when the
    engine starts and can be extended with additional workers in later phases.
    """

    def __init__(self) -> None:
        self._tasks: List[BackgroundTask] = []
        self._running_tasks: List[asyncio.Task] = []

    def register(self, task: BackgroundTask) -> None:
        task_name = getattr(task, "__name__", repr(task))
        logger.debug("Registering background task: %s", task_name)
        self._tasks.append(task)

    async def start(self) -> None:
        logger.info("Starting %d background task(s)", len(self._tasks))
        loop = asyncio.get_running_loop()
        self._running_tasks = []

        def _task_done_callback(task: asyncio.Task) -> None:
            if task.cancelled():
                return
            exception = task.exception()
            if exception:
                logger.exception(
                    "Background task error in %s", task.get_name(), exc_info=exception
                )
            else:
                logger.debug("Background task '%s' completed", task.get_name())

        for task_fn in self._tasks:
            task_name = getattr(task_fn, "__name__", repr(task_fn))
            task = loop.create_task(task_fn(), name=task_name)
            task.add_done_callback(_task_done_callback)
            self._running_tasks.append(task)

    async def shutdown(self) -> None:
        logger.info("Shutting down background tasks")
        for task in self._running_tasks:
            task.cancel()
        if self._running_tasks:
            results = await asyncio.gather(*self._running_tasks, return_exceptions=True)
            for task, result in zip(self._running_tasks, results):
                if isinstance(result, asyncio.CancelledError):
                    continue
                if isinstance(result, Exception):
                    logger.exception(
                        "Background task '%s' shut down with error",
                        task.get_name(),
                        exc_info=result,
                    )
        self._running_tasks.clear()

    def running_task_count(self) -> int:
        return len(self._running_tasks)


worker_system = WorkerSystem()
