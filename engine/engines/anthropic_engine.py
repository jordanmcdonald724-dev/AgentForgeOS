from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import httpx
except Exception:
    httpx = None


async def generate(model: str, prompt: str, engine_cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if httpx is None:
        raise RuntimeError("anthropic engine unavailable: missing optional dependency 'httpx'")
    cfg = engine_cfg or {}
    base_url = str(cfg.get("base_url") or "https://api.anthropic.com").rstrip("/")
    api_key = str(cfg.get("api_key") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("anthropic api_key missing")

    url = f"{base_url}/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": int(cfg.get("max_tokens") or 1024),
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=float(cfg.get("timeout_sec") or 60)) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            content = data.get("content") if isinstance(data, dict) else None
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict):
                    text = first.get("text")
                    if isinstance(text, str):
                        out: Dict[str, Any] = {"text": text}
                        usage = data.get("usage") if isinstance(data, dict) else None
                        if isinstance(usage, dict):
                            out["usage"] = {
                                "input_tokens": usage.get("input_tokens"),
                                "output_tokens": usage.get("output_tokens"),
                            }
                        return out
        except Exception:
            pass
        return {"text": str(data), "raw": None}
