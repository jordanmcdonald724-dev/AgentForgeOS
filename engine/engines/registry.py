from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Protocol


class EngineAdapter(Protocol):
    async def generate(self, *, model: str, prompt: str, engine_cfg: Dict[str, Any]) -> Any: ...


_REGISTRY: dict[str, EngineAdapter] = {}


def register_engine(name: str, adapter: EngineAdapter) -> None:
    key = (name or "").strip().lower()
    if not key:
        raise ValueError("engine name required")
    _REGISTRY[key] = adapter


def get_engine(name: str) -> EngineAdapter:
    key = (name or "").strip().lower()
    if key in _REGISTRY:
        return _REGISTRY[key]

    if key == "fal":
        from engine.engines.fal_engine import generate

        return _FunctionAdapter(generate)
    if key == "openai":
        from engine.engines.openai_engine import generate

        return _FunctionAdapter(generate)
    if key == "anthropic":
        from engine.engines.anthropic_engine import generate

        return _FunctionAdapter(generate)
    if key == "local":
        from engine.engines.local_engine import generate

        return _FunctionAdapter(generate)

    raise RuntimeError(f"Unknown engine: {name}")


@dataclass(frozen=True)
class _FunctionAdapter:
    fn: Callable[..., Awaitable[Any]]

    async def generate(self, *, model: str, prompt: str, engine_cfg: Dict[str, Any]) -> Any:
        return await self.fn(model, prompt, engine_cfg=engine_cfg)

