from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import httpx
except Exception:
    httpx = None


async def generate(model: str, prompt: str, engine_cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if httpx is None:
        raise RuntimeError("fal engine unavailable: missing optional dependency 'httpx'")
    cfg = engine_cfg or {}
    api_key = str(cfg.get("api_key") or os.environ.get("FAL_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("fal api_key missing")
    timeout = float(cfg.get("timeout_sec") or 120)

    from providers.fal_llm_provider import FalLLMProvider

    provider = FalLLMProvider(api_key=api_key, model=model, timeout=timeout)
    resp = await provider.chat(prompt, context=None)
    if not isinstance(resp, dict):
        raise RuntimeError("fal engine returned invalid response")
    if not resp.get("success"):
        err = resp.get("error")
        raise RuntimeError(str(err) if err else "fal request failed")
    data = resp.get("data")
    if isinstance(data, dict):
        text = data.get("text")
        if isinstance(text, str):
            return {"text": text, "raw": data}
    return {"text": str(data), "raw": data}
