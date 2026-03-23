from typing import Any, Dict, List, Optional, Union

from providers.llm_provider import LLMProvider
from providers.noop_provider import NoOpLLMProvider
from .memory_manager import MemoryManager
from .mongo_memory import MongoMemoryManager
from engine.router.model_router import ModelRouter


class AgentService:
    """Coordinates agent interactions using configured providers and memory.

    Accepts either the lightweight in-memory :class:`MemoryManager` (default)
    or the async MongoDB-backed :class:`MongoMemoryManager`.  When a
    ``MongoMemoryManager`` is provided, conversation turns are persisted to the
    database; in both cases a local in-memory cache is kept so that
    :meth:`history` can be called synchronously without a DB round-trip.
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        memory_manager: Optional[Union[MemoryManager, MongoMemoryManager]] = None,
    ):
        self.llm_provider: LLMProvider = llm_provider if llm_provider is not None else NoOpLLMProvider()
        self.memory: Union[MemoryManager, MongoMemoryManager] = memory_manager or MemoryManager()
        self.model_router: Optional[ModelRouter] = None

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    async def _save_memory(self, entry: Dict[str, Any]) -> None:
        """Save one memory entry via whichever backend is configured."""
        if isinstance(self.memory, MongoMemoryManager):
            await self.memory.save_memory(entry)
        else:
            self.memory.add_memory(entry)

    def _local_history(self) -> List[Dict[str, Any]]:
        """Return the in-memory history list regardless of backend type."""
        if isinstance(self.memory, MongoMemoryManager):
            return self.memory.get_local_cache()
        return self.memory.get_recent()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def run_agent(
        self,
        prompt: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        task_type: str = "conversation",
    ) -> Dict[str, Any]:
        """Run a simple agent loop: append prompt to memory and query LLM provider."""
        effective_task_type = task_type
        agent_role = None
        if isinstance(context, dict):
            ctx_task = context.get("task_type")
            if isinstance(ctx_task, str) and ctx_task.strip():
                effective_task_type = ctx_task.strip()
            ctx_role = context.get("agent_id")
            if isinstance(ctx_role, str) and ctx_role.strip():
                agent_role = ctx_role.strip()
        await self._save_memory({"role": "user", "content": prompt})
        if self.model_router is not None:
            try:
                text = await self.model_router.generate(effective_task_type, prompt, agent_role=agent_role)
                response = {"success": True, "data": {"text": text}, "error": None}
            except Exception as e:
                response = {"success": False, "data": None, "error": str(e)}
        else:
            response = await self.llm_provider.chat(prompt, context=context)
        if response.get("success"):
            data = response.get("data")
            if data is not None:
                if isinstance(data, dict):
                    content = data.get("text")
                    if content is None:
                        content = data
                else:
                    content = data
                await self._save_memory({"role": "assistant", "content": str(content)})
        return response

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return recent memory entries from the local cache.

        Reads synchronously from the in-memory cache so callers do not need to
        await.  When using ``MongoMemoryManager`` the cache is always kept in
        sync with MongoDB writes, so this is safe and accurate.
        """
        entries = self._local_history()
        if limit is None:
            return entries
        return entries[-limit:]
