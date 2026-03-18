from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from control.execution_monitor import execution_monitor, ExecutionEvent


def _to_ui_event(evt: ExecutionEvent) -> dict:
    """
    Normalize backend ExecutionEvent -> UI event shape expected by frontend hooks:
      { type, ts, source, data }
    """
    data = dict(evt.data or {})
    data.setdefault("pipeline_id", evt.pipeline_id)
    if evt.step_index is not None:
        data.setdefault("step_id", evt.step_index)  # UI treats step_id as identifier; index is acceptable
        data.setdefault("step_index", evt.step_index)
    if evt.agent_name:
        data.setdefault("agent_id", evt.agent_name)
        data.setdefault("agent_name", evt.agent_name)

    return {
        "schema": "agentforge.event.v1",
        "type": evt.event_type,
        "ts": evt.timestamp,
        "source": "execution_monitor",
        "data": data,
    }


async def execution_ws(websocket: WebSocket) -> None:
    """
    WebSocket endpoint at /ws.
    Streams ExecutionMonitor events to connected clients.
    """
    await websocket.accept()

    pipeline_id: Optional[str] = websocket.query_params.get("pipeline_id")
    cursor = 0

    try:
        while True:
            # Poll for new events (lightweight, in-memory).
            events = execution_monitor.get_events(pipeline_id=pipeline_id)
            if cursor < len(events):
                batch = events[cursor:]
                cursor = len(events)
                for evt in batch:
                    await websocket.send_json(_to_ui_event(evt))

            # Keep-alive without noise: a very infrequent heartbeat.
            await asyncio.sleep(0.25)
    except WebSocketDisconnect:
        return
    except Exception:
        # Best-effort: do not crash the server on stream issues
        try:
            await websocket.close()
        except Exception:
            pass

