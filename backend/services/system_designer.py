from __future__ import annotations

from typing import Dict, List


class SystemDesigner:
    """
    Deterministic classifier that converts a raw request into a structured system
    specification for Gate 8 builds.
    """

    def design_system(self, request: str) -> Dict[str, object]:
        safe_request = (request or "").strip().lower()

        system_type = self._detect_type(safe_request)
        platform = self._detect_platform(safe_request)
        complexity = self._detect_complexity(safe_request)
        features = self._extract_features(safe_request)

        return {
            "type": system_type,
            "platform": platform,
            "complexity": complexity,
            "features": features,
        }

    def _detect_type(self, text: str) -> str:
        if any(word in text for word in ["unity", "unreal", "game", "level", "inventory"]):
            return "game_system"
        if any(word in text for word in ["backend", "api", "service"]):
            return "backend"
        if any(word in text for word in ["os", "firmware", "driver"]):
            return "os"
        return "app"

    def _detect_platform(self, text: str) -> str:
        if "unity" in text:
            return "unity"
        if "unreal" in text:
            return "unreal"
        if any(word in text for word in ["web", "browser", "frontend"]):
            return "web"
        if any(word in text for word in ["desktop", "electron"]):
            return "desktop"
        return "unknown"

    def _detect_complexity(self, text: str) -> str:
        if any(word in text for word in ["enterprise", "distributed", "scalable", "multiplayer", "advanced"]):
            return "high"
        if any(word in text for word in ["simple", "basic", "prototype", "demo"]):
            return "low"
        return "medium"

    def _extract_features(self, text: str) -> List[str]:
        features: List[str] = []
        feature_keywords = [
            ("inventory", ["inventory", "items"]),
            ("ui", ["ui", "interface", "menu", "hud"]),
            ("auth", ["login", "auth", "authentication", "signin", "signup"]),
            ("data", ["data", "database", "persist", "save"]),
            ("api", ["api", "endpoint", "rest", "graphql"]),
            ("multiplayer", ["multiplayer", "coop", "pvp"]),
        ]

        for feature_name, keywords in feature_keywords:
            if any(keyword in text for keyword in keywords):
                features.append(feature_name)

        return features
