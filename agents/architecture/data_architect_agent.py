"""Data Architect agent — designs data models, schemas, and storage strategy."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class DataArchitectAgent(BaseAgent):
    """Designs the data layer: schemas, collections, indexes, and migrations."""

    role = "Data Architect"
    system_prompt = (
        "You are a data architecture specialist. "
        "Given the module and API specifications, design the data layer: "
        "define document/record schemas, collection or table structures, "
        "index strategy, relationships, and any migration requirements. "
        "Consider read/write patterns and propose caching strategies where appropriate. "
        "Do not write code — schemas and strategy only."
    )

    async def run(
        self, prompt: str, *, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._run_with_service(prompt, context=context)
