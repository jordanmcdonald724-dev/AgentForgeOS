"""File guard enforcing repository modification rules."""

from pathlib import Path
from typing import Dict, Iterable, Optional, Set


PROTECTED_DIRS: Set[str] = {"engine", "services", "providers", "control"}


class FileGuard:
    """Checks whether a path may be modified for a given category."""

    def __init__(self, permission_matrix_path: Optional[Path] = None):
        base = Path(__file__).resolve().parent
        self.permission_matrix_path = permission_matrix_path or base / "permission_matrix.yaml"
        self.permissions = self._load_permissions()

    def _load_permissions(self) -> Dict[str, list]:
        if not self.permission_matrix_path.exists():
            return {}
        permissions: Dict[str, list] = {}
        current_key: Optional[str] = None
        for raw_line in self.permission_matrix_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith("-") and ":" in line:
                key = line.split(":", 1)[0].strip()
                permissions[key] = []
                current_key = key
                continue
            if line.startswith("-") and current_key:
                permissions[current_key].append(line.lstrip("-").strip())
        return permissions

    def _is_protected(self, path: Path) -> bool:
        parts = path.parts
        return any(part in PROTECTED_DIRS for part in parts)

    def _allowed_prefixes(self, category: str) -> Iterable[Path]:
        entries = self.permissions.get(category, [])
        return [Path(p) for p in entries]

    def is_allowed(self, path: str, category: Optional[str]) -> bool:
        """Return True if the given path can be modified for the category."""
        p = Path(path)
        if self._is_protected(p):
            return False
        if category is None:
            return False
        for prefix in self._allowed_prefixes(category):
            try:
                p.relative_to(prefix)
                return True
            except ValueError:
                continue
        return False
