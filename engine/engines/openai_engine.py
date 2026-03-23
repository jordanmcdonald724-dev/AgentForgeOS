from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    import httpx
except Exception:
    httpx = None


async def generate(model: str, prompt: str, engine_cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if httpx is None:
        raise RuntimeError("openai engine unavailable: missing optional dependency 'httpx'")
    cfg = engine_cfg or {}
    base_url = str(cfg.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    api_key = str(cfg.get("api_key") or os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("openai api_key missing")

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=float(cfg.get("timeout_sec") or 60)) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        try:
            choices = data.get("choices") if isinstance(data, dict) else None
            if isinstance(choices, list) and choices:
                msg = choices[0].get("message")
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str):
                        out: Dict[str, Any] = {"text": content}
                        usage = data.get("usage") if isinstance(data, dict) else None
                        if isinstance(usage, dict):
                            out["usage"] = {
                                "prompt_tokens": usage.get("prompt_tokens"),
                                "completion_tokens": usage.get("completion_tokens"),
                                "total_tokens": usage.get("total_tokens"),
                            }
                        return out
        except Exception:
            pass
        return {"text": str(data), "raw": None}
