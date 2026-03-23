from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional, Tuple

from engine.logs.engine_logger import EngineLogger
from engine.engines.registry import get_engine


class EngineManager:
    def __init__(self) -> None:
        self._logger = EngineLogger()
        self._locks: Dict[str, asyncio.Semaphore] = {}
        self._health: Dict[str, Dict[str, Any]] = {}

    def _get_semaphore(self, engine_name: str, concurrency: int) -> asyncio.Semaphore:
        sem = self._locks.get(engine_name)
        if sem is None:
            sem = asyncio.Semaphore(max(1, int(concurrency or 1)))
            self._locks[engine_name] = sem
        return sem

    async def generate(
        self,
        engine_name: str,
        model: str,
        prompt: str,
        engine_cfg: Dict[str, Any],
        *,
        task_type: str,
    ) -> Tuple[bool, str, Optional[str], float, Dict[str, Any]]:
        retries = int(engine_cfg.get("retries") or 0)
        timeout_sec = float(engine_cfg.get("timeout_sec") or 60)
        concurrency = int(engine_cfg.get("concurrency") or 3)

        sem = self._get_semaphore(engine_name, concurrency)
        start = time.perf_counter()
        ok = False
        text = ""
        error: Optional[str] = None
        meta: Dict[str, Any] = {}

        name_key = (engine_name or "").strip().lower()
        cooldown_until = float((self._health.get(name_key) or {}).get("cooldown_until") or 0.0)
        now = time.time()
        if cooldown_until and cooldown_until > now:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return False, "", "engine cooling down", elapsed_ms, {"error_class": "cooldown", "cooldown_remaining_ms": (cooldown_until - now) * 1000.0}

        async with sem:
            for attempt in range(retries + 1):
                try:
                    result = await asyncio.wait_for(
                        self._dispatch(engine_name, model, prompt, engine_cfg),
                        timeout=timeout_sec,
                    )
                    ok = True
                    meta = {}
                    if isinstance(result, dict):
                        text = str(result.get("text") or "")
                        usage = result.get("usage")
                        if isinstance(usage, dict):
                            meta["usage"] = usage
                        cost = None
                        if isinstance(result.get("cost_usd"), (int, float)):
                            cost = float(result["cost_usd"])
                        else:
                            cost = _estimate_cost_usd(meta.get("usage"), engine_cfg)
                        if isinstance(cost, (int, float)):
                            meta["cost_usd"] = float(cost)
                        if result.get("raw") is not None:
                            meta["raw"] = result.get("raw")
                    else:
                        text = str(result or "")
                    error = None
                    meta["error_class"] = None
                    meta["attempt"] = attempt + 1
                    self._update_health(name_key, ok=True, error_class=None)
                    break
                except Exception as exc:
                    error = str(exc)
                    error_class = _classify_error(error)
                    meta = {"error_class": error_class, "attempt": attempt + 1}
                    self._update_health(name_key, ok=False, error_class=error_class)
                    if attempt < retries:
                        await asyncio.sleep(min(2.0, 0.2 * (attempt + 1)))
                        continue
                    break

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return ok, text, error, elapsed_ms, meta

    async def _dispatch(self, engine_name: str, model: str, prompt: str, engine_cfg: Dict[str, Any]) -> Any:
        impl = get_engine(engine_name)
        return await impl.generate(model=model, prompt=prompt, engine_cfg=engine_cfg)

    def log_call(
        self,
        *,
        task_type: str,
        engine: str,
        model: str,
        elapsed_ms: float,
        success: bool,
        error: Optional[str],
        max_entries: int,
        usage: Optional[Dict[str, Any]] = None,
        cost_usd: Optional[float] = None,
        error_class: Optional[str] = None,
        attempt: Optional[int] = None,
    ) -> None:
        event = {
            "task_type": task_type,
            "engine": engine,
            "model": model,
            "elapsed_ms": round(elapsed_ms, 3),
            "success": bool(success),
            "error": error if not success else None,
            "error_class": error_class if not success else None,
            "usage": usage,
            "cost_usd": cost_usd,
            "attempt": attempt,
        }
        self._logger.write_event(event, max_entries=max_entries)
        try:
            from engine.websocket_manager import websocket_manager  # type: ignore
            loop = asyncio.get_event_loop()
            loop.create_task(
                websocket_manager.broadcast_system_event(
                    "engine_telemetry",
                    {"event": event},
                    severity="info" if success else "error",
                )
            )
        except Exception:
            pass

    def _update_health(self, engine_name: str, *, ok: bool, error_class: Optional[str]) -> None:
        h = self._health.get(engine_name)
        if not isinstance(h, dict):
            h = {"failures": 0, "cooldown_until": 0.0, "last_error_class": None}
        if ok:
            h["failures"] = 0
            h["cooldown_until"] = 0.0
            h["last_error_class"] = None
        else:
            failures = int(h.get("failures") or 0) + 1
            h["failures"] = failures
            h["last_error_class"] = error_class
            cooldown_s = 0.0
            if error_class in {"auth", "config"}:
                cooldown_s = 300.0
            elif error_class in {"rate_limit"}:
                cooldown_s = min(120.0, 2.0 * failures)
            elif error_class in {"timeout"}:
                cooldown_s = min(60.0, 1.0 * failures)
            elif failures >= 3:
                cooldown_s = min(30.0, 1.0 * failures)
            if cooldown_s:
                h["cooldown_until"] = float(time.time() + cooldown_s)
        self._health[engine_name] = h


def _classify_error(msg: str) -> str:
    m = (msg or "").lower()
    if "api key" in m or "unauthorized" in m or "forbidden" in m or "401" in m or "403" in m:
        return "auth"
    if "rate limit" in m or "429" in m or "too many requests" in m:
        return "rate_limit"
    if "timeout" in m or "timed out" in m:
        return "timeout"
    if "not configured" in m or "missing" in m:
        return "config"
    if "500" in m or "502" in m or "503" in m or "504" in m:
        return "upstream"
    return "unknown"


def _estimate_cost_usd(usage: Any, engine_cfg: Dict[str, Any]) -> Optional[float]:
    if not isinstance(usage, dict):
        return None
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    if prompt_tokens is None and completion_tokens is None:
        return None
    try:
        pt = float(prompt_tokens or 0)
        ct = float(completion_tokens or 0)
    except Exception:
        return None
    try:
        pp = float(engine_cfg.get("price_per_1k_prompt_usd") or 0)
        pc = float(engine_cfg.get("price_per_1k_completion_usd") or 0)
    except Exception:
        return None
    if pp <= 0 and pc <= 0:
        return None
    return (pt / 1000.0) * pp + (ct / 1000.0) * pc
