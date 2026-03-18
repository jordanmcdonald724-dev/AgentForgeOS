from __future__ import annotations

from typing import Dict, List, Optional


class AssetPlanner:
    """
    Deterministic planner that translates asset requests into a structured plan.
    """

    def plan_asset(self, request: str, references: Optional[List[object]] = None) -> Dict[str, object]:
        text = (request or "").lower()
        asset_type = self._detect_type(text)
        target_engine = self._detect_engine(text)
        style = self._detect_style(text, references or [])

        constraints = self._default_constraints(asset_type, text)

        plan = {
            "asset_type": asset_type,
            "style": style,
            "target_engine": target_engine,
            "constraints": constraints,
            "stages": ["blockout", "refine", "texture", "optimize", "validate"],
        }
        return plan

    def _detect_type(self, text: str) -> str:
        if "material" in text:
            return "material"
        if any(keyword in text for keyword in ["texture", "albedo", "roughness", "normal"]):
            return "texture"
        return "3d_model"

    def _detect_engine(self, text: str) -> str:
        if "unity" in text:
            return "unity"
        if "unreal" in text:
            return "unreal"
        return "generic"

    def _detect_style(self, text: str, references: List[object]) -> str:
        if "realistic" in text:
            return "realistic"
        if "stylized" in text or "stylised" in text:
            return "stylized"
        if references:
            return "referenced"
        return "unspecified"

    def _default_constraints(self, asset_type: str, text: str) -> Dict[str, object]:
        polycount = 8000
        if "lowpoly" in text or "low poly" in text:
            polycount = 2000
        if "highpoly" in text or "high poly" in text:
            polycount = 20000

        lods = "lod" in text or "lods" in text

        if asset_type != "3d_model":
            polycount = 0
            lods = False

        return {
            "polycount": int(polycount),
            "lods": bool(lods),
        }
