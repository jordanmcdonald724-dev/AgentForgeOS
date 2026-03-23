from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .pattern_extractor import PatternExtractor


class AutopsyService:
    """Captures failure reports and lightweight pattern signals for analysis."""

    def __init__(
        self,
        pattern_extractor: Optional[PatternExtractor] = None,
        *,
        persist_path: Optional[Path] = None,
    ) -> None:
        self.pattern_extractor = pattern_extractor or PatternExtractor()
        self.persist_path = Path(persist_path) if persist_path else None
        self._reports: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self.persist_path:
            return
        try:
            if not self.persist_path.is_file():
                return
            raw = json.loads(self.persist_path.read_text(encoding="utf-8") or "[]")
            if isinstance(raw, list):
                self._reports = [r for r in raw if isinstance(r, dict)]
        except Exception:
            return

    def _save(self) -> None:
        if not self.persist_path:
            return
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            self.persist_path.write_text(json.dumps(self._reports, indent=2), encoding="utf-8")
        except Exception:
            return

    def record_failure(
        self,
        project: str,
        summary: str,
        *,
        root_cause: Optional[str] = None,
        remediation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Store a failure summary with extracted text patterns."""
        patterns = self.pattern_extractor.extract_patterns(summary)
        report = {
            "project": project,
            "summary": summary,
            "root_cause": root_cause,
            "remediation": remediation,
            "patterns": patterns,
        }
        self._reports.append(report)
        self._save()
        return report

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return recorded failure reports, optionally limited to the most recent items."""
        if limit is None:
            return self._reports
        return self._reports[-limit:]
