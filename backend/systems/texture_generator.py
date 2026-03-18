from __future__ import annotations

from typing import Dict


class TextureGenerator:
    """
    Deterministic placeholder for texture/material generation.
    """

    def generate(self, plan: Dict[str, object], references: Dict[str, object]) -> Dict[str, object]:
        asset_type = plan.get("asset_type") if isinstance(plan, dict) else ""
        textures = ["albedo", "normal", "roughness"] if asset_type != "material" else ["albedo", "normal", "roughness", "metallic"]

        return {
            "textures": textures,
            "status": "generated",
        }
