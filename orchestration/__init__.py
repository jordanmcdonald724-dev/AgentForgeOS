"""V2 orchestration engine package.

Defines the central task graph model and orchestration controller
as described in BUILD_BIBLE_V2.
"""

from .task_model import Task, TaskStatus
from .engine import OrchestrationEngine
