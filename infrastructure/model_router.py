from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class RouteKind(Enum):
    CODE = auto()
    IMAGE = auto()
    AUDIO = auto()
    THREE_D = auto()
    GENERIC = auto()


@dataclass
class ModelRouter:
    """Simple model routing stub.

    This does not call any real models yet; it only encodes
    routing intent as described in BUILD_BIBLE_V2.
    """

    def select_route(self, kind: RouteKind) -> str:
        if kind is RouteKind.CODE:
            return "deepseek-like-code-backend"
        if kind is RouteKind.IMAGE:
            return "flux-like-image-backend"
        if kind is RouteKind.THREE_D:
            return "shape-e-like-3d-backend"
        if kind is RouteKind.AUDIO:
            return "audiocraft-like-audio-backend"
        return "generic-llm-backend"
