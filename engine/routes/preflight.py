from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request

from engine.security.preflight import run_preflight

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/preflight")
async def get_preflight(request: Request) -> Dict[str, Any]:
    result = await run_preflight(request, scope="system")
    return {"success": True, "data": result, "error": None}

