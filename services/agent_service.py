from typing import Any, Dict, List, Optional

from providers import LLMProvider
from .memory_manager import MemoryManager


class AgentService:
    """Coordinates agent interactions using configured providers and memory."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        memory_manager: Optional[MemoryManager] = None,
    ):
        self.llm_provider = llm_provider
        self.memory = memory_manager or MemoryManager()

    async def run_agent(self, prompt: str, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a simple agent loop: append prompt to memory and query LLM provider."""
        self.memory.add_memory({"role": "user", "content": prompt})
        response = await self.llm_provider.chat(prompt, context=context)
        if response.get("success"):
            data = response.get("data")
            if data is not None:
                if isinstance(data, dict):
                    content = data.get("text", data)
                else:
                    content = data
                self.memory.add_memory({"role": "assistant", "content": str(content)})
        return response

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return recent memory entries."""
        return self.memory.get_recent(limit=limit)
