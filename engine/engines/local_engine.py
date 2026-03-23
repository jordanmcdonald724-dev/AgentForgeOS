from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import httpx
except Exception:
    httpx = None


async def generate(model: str, prompt: str, engine_cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = engine_cfg or {}
    provider = str(cfg.get("provider") or "ollama").strip().lower()
    if provider != "ollama":
        raise RuntimeError(f"local engine provider not supported: {provider}")
    if httpx is None:
        raise RuntimeError("local engine unavailable: missing optional dependency 'httpx'")

    base_url = str(cfg.get("base_url") or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
    url = f"{base_url}/api/chat"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=float(cfg.get("timeout_sec") or 120)) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            message = data.get("message") if isinstance(data, dict) else None
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    out: Dict[str, Any] = {"text": content}
                    if isinstance(data, dict):
                        usage: Dict[str, Any] = {}
                        if "prompt_eval_count" in data:
                            usage["prompt_eval_count"] = data.get("prompt_eval_count")
                        if "eval_count" in data:
                            usage["eval_count"] = data.get("eval_count")
                        if usage:
                            out["usage"] = usage
                    return out
        except Exception:
            pass
        return {"text": str(data), "raw": None}
