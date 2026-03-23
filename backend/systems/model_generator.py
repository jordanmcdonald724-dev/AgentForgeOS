from __future__ import annotations

from typing import Dict


DEFAULT_POLYCOUNT_CONSTRAINT = 8_000
LOW_POLY_THRESHOLD = 10_000
POLYCOUNT_INFLATION = 1_000


class ModelGenerator:
    """
    Deterministic placeholder for 3D model generation.
    """

    def generate(self, plan: Dict[str, object], references: Dict[str, object]) -> Dict[str, object]:
        constraints = plan.get("constraints", {}) if isinstance(plan, dict) else {}
        constraint_poly = constraints.get("polycount") if isinstance(constraints, dict) else None
        safe_constraint = int(constraint_poly) if isinstance(constraint_poly, int) else DEFAULT_POLYCOUNT_CONSTRAINT

        # Deliberately sit near the constraint; slightly above for possible refinement.
        if safe_constraint <= 0:
            polycount = 0
        elif safe_constraint <= LOW_POLY_THRESHOLD:
            polycount = safe_constraint + POLYCOUNT_INFLATION
        else:
            polycount = safe_constraint

        return {
            "mesh": "mock_mesh_data",
            "polycount": polycount,
            "status": "generated",
        }
