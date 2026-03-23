from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from engine.engines.engine_manager import EngineManager
from engine.router import config_loader
from services.agent_behavior import load_agent_system_prompt, normalize_pipeline_role


@dataclass(frozen=True)
class RouteTarget:
    engine: str
    model: str


class ModelRouter:
    def __init__(self) -> None:
        self._engine_manager = EngineManager()

    async def generate(self, task_type: str, prompt: str, *, agent_role: str | None = None) -> str:
        cfg = config_loader.load_engine_config()
        enabled = cfg.get("enabled_engines")
        enabled_engines: List[str] = [e for e in enabled if isinstance(e, str)] if isinstance(enabled, list) else []

        if not enabled_engines:
            enabled_engines = ["local"]

        selected_provider = os.environ.get("PROVIDER_LLM", "").strip().lower()
        selected_engine = ""
        if selected_provider in {"ollama", "local"}:
            selected_engine = "local"
        elif selected_provider in {"fal", "openai", "anthropic"}:
            selected_engine = selected_provider
        if selected_engine:
            enabled_engines = [e for e in enabled_engines if e != selected_engine]
            enabled_engines.insert(0, selected_engine)

        task_routing = cfg.get("task_routing") if isinstance(cfg.get("task_routing"), dict) else {}
        route = task_routing.get(task_type) if isinstance(task_routing, dict) else None
        targets = self._build_targets(task_type, route, enabled_engines, cfg)
        if selected_engine:
            engines_cfg = cfg.get("engines") if isinstance(cfg.get("engines"), dict) else {}
            selected_model = ""
            if selected_engine == "fal":
                selected_model = os.environ.get("FAL_LLM_MODEL", "").strip()
            elif selected_engine == "openai":
                selected_model = os.environ.get("OPENAI_MODEL", "").strip()
            elif selected_engine == "anthropic":
                selected_model = os.environ.get("ANTHROPIC_MODEL", "").strip()
            elif selected_engine == "local":
                selected_model = os.environ.get("OLLAMA_MODEL", "").strip()
            if isinstance(engines_cfg, dict):
                selected_model = str(engines_cfg.get(selected_engine, {}).get("model") or selected_model or "llama3")
            if selected_model and (not targets or targets[0][0] != selected_engine):
                targets = [(selected_engine, selected_model)] + targets
                dedup: List[Tuple[str, str]] = []
                seen = set()
                for e, m in targets:
                    key = f"{e}:{m}"
                    if key in seen:
                        continue
                    seen.add(key)
                    dedup.append((e, m))
                targets = dedup

        max_entries = 5000
        cost_controls = cfg.get("cost_controls")
        if isinstance(cost_controls, dict):
            try:
                max_entries = int(cost_controls.get("max_log_entries") or max_entries)
            except Exception:
                max_entries = 5000

        system_prompt = ""
        if agent_role and isinstance(agent_role, str) and agent_role.strip():
            normalized = normalize_pipeline_role(agent_role.strip())
            system_prompt = load_agent_system_prompt(normalized)
        final_prompt = self._assemble_prompt(task_type, prompt, system_prompt)

        last_error: Optional[str] = None
        for engine, model in targets:
            engine_cfg = self._engine_config_for(engine, cfg)
            ok, text, err, elapsed_ms, meta = await self._engine_manager.generate(
                engine, model, final_prompt, engine_cfg, task_type=task_type
            )
            self._engine_manager.log_call(
                task_type=task_type,
                engine=engine,
                model=model,
                elapsed_ms=elapsed_ms,
                success=ok,
                error=err,
                max_entries=max_entries,
                usage=(meta.get("usage") if isinstance(meta, dict) else None),
                cost_usd=(meta.get("cost_usd") if isinstance(meta, dict) else None),
                error_class=(meta.get("error_class") if isinstance(meta, dict) else None),
                attempt=(meta.get("attempt") if isinstance(meta, dict) else None),
            )
            if ok:
                return text
            last_error = err or "unknown error"

        raise RuntimeError(last_error or "All engines failed")

    def _assemble_prompt(self, task_type: str, user_prompt: str, system_prompt: str) -> str:
        if system_prompt:
            return f"[task_type:{task_type}]\n{system_prompt}\n\nTask: {user_prompt}"
        return user_prompt

    def _engine_config_for(self, engine_name: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
        engines = cfg.get("engines")
        engine_cfg = engines.get(engine_name) if isinstance(engines, dict) else None
        out: Dict[str, Any] = dict(engine_cfg) if isinstance(engine_cfg, dict) else {}
        api_keys = cfg.get("api_keys")
        if isinstance(api_keys, dict):
            key = api_keys.get(engine_name)
            if isinstance(key, str) and key.strip():
                out["api_key"] = key.strip()
        return out

    def _build_targets(
        self,
        task_type: str,
        route: Any,
        enabled_engines: List[str],
        cfg: Dict[str, Any],
    ) -> List[Tuple[str, str]]:
        engines_cfg = cfg.get("engines") if isinstance(cfg.get("engines"), dict) else {}
        default_engine = enabled_engines[0]
        default_model = "llama3"
        if isinstance(engines_cfg, dict):
            default_model = str(engines_cfg.get(default_engine, {}).get("model") or default_model)

        if not isinstance(route, dict):
            return [(default_engine, default_model)]

        primary_engine = str(route.get("engine") or default_engine).strip()
        primary_model = str(route.get("model") or default_model).strip()

        targets: List[Tuple[str, str]] = []
        if primary_engine in enabled_engines:
            targets.append((primary_engine, primary_model))

        fallback = route.get("fallback")
        if isinstance(fallback, list):
            for item in fallback:
                if not isinstance(item, dict):
                    continue
                e = str(item.get("engine") or "").strip()
                m = str(item.get("model") or "").strip()
                if not e or not m:
                    continue
                if e not in enabled_engines:
                    continue
                targets.append((e, m))

        if not targets:
            targets.append((default_engine, default_model))
        dedup: List[Tuple[str, str]] = []
        seen = set()
        for e, m in targets:
            key = f"{e}:{m}"
            if key in seen:
                continue
            seen.add(key)
            dedup.append((e, m))
        return dedup
