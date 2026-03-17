from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ContextEntry:
    request_signature: str
    pipeline_agents: List[str]
    success: bool
    score: float
    metadata: Dict[str, object] = field(default_factory=dict)


class ContextIndex:
    """
    Lightweight in-memory index for past executions.
    Provides simple keyword/containment based similarity lookups.
    """

    def __init__(self) -> None:
        self._entries: List[ContextEntry] = []

    def add_entry(self, entry: ContextEntry) -> None:
        try:
            if not isinstance(entry, ContextEntry):
                return
            self._entries.append(entry)
        except Exception:
            return

    def query_similar(self, request: str, top_k: int = 3) -> List[ContextEntry]:
        try:
            if not isinstance(request, str) or not request.strip():
                return []
            clean = request.strip().lower()
            tokens = set(clean.split())
            scored: List[tuple[int, float, ContextEntry]] = []

            for entry in self._entries:
                signature = entry.request_signature.strip().lower() if isinstance(entry.request_signature, str) else ""
                if not signature:
                    continue
                entry_tokens = set(signature.split())
                overlap = len(tokens & entry_tokens)
                containment_bonus = 1 if signature in clean or clean in signature else 0
                similarity = overlap + containment_bonus
                if similarity <= 0:
                    continue
                scored.append((similarity, float(entry.score), entry))

            scored.sort(key=lambda item: (-item[0], -item[1]))
            return [entry for _, _, entry in scored[: max(1, int(top_k))]]
        except Exception:
            return []
