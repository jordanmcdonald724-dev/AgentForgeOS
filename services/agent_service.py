from typing import Any, Dict, List, Optional

from providers.llm_provider import LLMProvider
from providers.noop_provider import NoOpLLMProvider
from .memory_manager import MemoryManager


class AgentService:
    """Coordinates agent interactions using configured providers and memory."""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        memory_manager: Optional[MemoryManager] = None,
    ):
        self.llm_provider: LLMProvider = llm_provider if llm_provider is not None else NoOpLLMProvider()
        self.memory = memory_manager or MemoryManager()

    async def run_agent(self, prompt: str, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a simple agent loop: append prompt to memory and query LLM provider."""
        self.memory.add_memory({"role": "user", "content": prompt})
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
                self.memory.add_memory({"role": "assistant", "content": str(content)})
        return response

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return recent memory entries."""
        return self.memory.get_recent(limit=limit)
