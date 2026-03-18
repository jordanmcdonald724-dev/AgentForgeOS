from __future__ import annotations

from typing import Dict, List


class AssetValidator:
    """
    Deterministic asset validation.
    """

    def validate(self, asset: Dict[str, object], plan: Dict[str, object]) -> Dict[str, object]:
        issues: List[str] = []
        valid = True

        if not isinstance(asset, dict):
            return {"valid": False, "issues": ["asset_not_dict"]}

        constraints = plan.get("constraints", {}) if isinstance(plan, dict) else {}
        max_poly = constraints.get("polycount") if isinstance(constraints, dict) else None

        mesh = asset.get("mesh")
        if mesh is None and (plan.get("asset_type") == "3d_model"):
            issues.append("missing_mesh")

        polycount = asset.get("polycount")
        if isinstance(polycount, int) and isinstance(max_poly, int) and max_poly > 0 and polycount > max_poly:
            issues.append("polycount_exceeds_constraint")

        textures = asset.get("textures")
        if plan.get("asset_type") in ("texture", "material") and not textures:
            issues.append("missing_textures")

        valid = not issues
        return {"valid": valid, "issues": issues}
