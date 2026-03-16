from typing import Any, Dict, List, Optional

from .pattern_extractor import PatternExtractor


class AutopsyService:
    """Captures failure reports and lightweight pattern signals for analysis."""

    def __init__(self, pattern_extractor: Optional[PatternExtractor] = None) -> None:
        self.pattern_extractor = pattern_extractor or PatternExtractor()
        self._reports: List[Dict[str, Any]] = []

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
        return report

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return recorded failure reports, optionally limited to the most recent items."""
        if limit is None:
            return self._reports
        return self._reports[-limit:]
