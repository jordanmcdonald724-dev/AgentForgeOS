from __future__ import annotations

from typing import Dict, List


class ReferenceAnalyzer:
    """
    Lightweight, deterministic analyzer for reference inputs.
    """

    def analyze(self, references: List[object]) -> Dict[str, List[str]]:
        style_features: List[str] = []
        color_palette: List[str] = []
        shape_language: List[str] = []

        for ref in references or []:
            text = str(ref).lower()
            if "realistic" in text:
                style_features.append("realistic")
            if "stylized" in text or "stylised" in text:
                style_features.append("stylized")
            if "grunge" in text:
                style_features.append("grunge")
            if "dark" in text:
                color_palette.append("dark")
            if "bright" in text or "vibrant" in text:
                color_palette.append("vibrant")
            if "organic" in text:
                shape_language.append("organic")
            if "hard surface" in text or "hardsurface" in text:
                shape_language.append("hard_surface")

        return {
            "style_features": style_features or ["unspecified"],
            "color_palette": color_palette or ["neutral"],
            "shape_language": shape_language or ["mixed"],
        }
