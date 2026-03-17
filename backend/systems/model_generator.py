from __future__ import annotations

from typing import Dict


class ModelGenerator:
    """
    Deterministic placeholder for 3D model generation.
    """

    def generate(self, plan: Dict[str, object], references: Dict[str, object]) -> Dict[str, object]:
        constraints = plan.get("constraints", {}) if isinstance(plan, dict) else {}
        constraint_poly = constraints.get("polycount") if isinstance(constraints, dict) else None
        safe_constraint = int(constraint_poly) if isinstance(constraint_poly, int) else 8000

        # Deliberately sit near the constraint; slightly above for possible refinement.
        if safe_constraint <= 0:
            polycount = 0
        elif safe_constraint <= 10_000:
            polycount = safe_constraint + 1000
        else:
            polycount = safe_constraint

        return {
            "mesh": "mock_mesh_data",
            "polycount": polycount,
            "status": "generated",
        }
