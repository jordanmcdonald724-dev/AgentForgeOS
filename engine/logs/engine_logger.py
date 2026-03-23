from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.router.config_loader import ensure_engine_config_exists


class EngineLogger:
    def __init__(self, log_path: Optional[Path] = None) -> None:
        paths = ensure_engine_config_exists()
        self.log_path = log_path or paths.engine_logs_path
        self._lock = threading.Lock()

    def write_event(self, event: Dict[str, Any], *, max_entries: int = 5000) -> None:
        payload = dict(event)
        payload.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            existing: List[Dict[str, Any]] = []
            try:
                if self.log_path.is_file():
                    raw = json.loads(self.log_path.read_text(encoding="utf-8") or "[]")
                    if isinstance(raw, list):
                        existing = [e for e in raw if isinstance(e, dict)]
            except Exception:
                existing = []
            existing.append(payload)
            if max_entries and len(existing) > max_entries:
                existing = existing[-max_entries:]
            self.log_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

