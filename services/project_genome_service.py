from typing import Any, Dict, List, Optional

from .pattern_extractor import PatternExtractor


class ProjectGenomeService:
    """Tracks lightweight project profiles and extracted development patterns."""

    def __init__(self, pattern_extractor: Optional[PatternExtractor] = None) -> None:
        self.pattern_extractor = pattern_extractor or PatternExtractor()
        self._genomes: Dict[str, Dict[str, Any]] = {}

    def record_project(
        self, project_name: str, description: str, *, artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Capture a project description and derived patterns."""
        patterns = self.pattern_extractor.extract_patterns(description)
        genome = {"description": description, "patterns": patterns, "artifacts": artifacts or []}
        self._genomes[project_name] = genome
        return genome

    def get_genome(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Return the stored profile for a project."""
        return self._genomes.get(project_name)

    def list_projects(self) -> List[str]:
        """List all recorded project identifiers."""
        return list(self._genomes.keys())
