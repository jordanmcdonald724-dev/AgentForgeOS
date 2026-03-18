from __future__ import annotations

from pathlib import Path

import unittest

from orchestration.engine import OrchestrationEngine
from orchestration.runtime import default_agent_registry


class TestV2BuildBibleCompliance(unittest.TestCase):
    """Structural checks that enforce critical Build Bible rules.

    These tests intentionally focus on *architecture-level* invariants that
    should not drift without an explicit decision to update the Build Bible
    and the corresponding checks.
    """

    def setUp(self) -> None:
        # Project root is one level above tests/ directory
        self.root = Path(__file__).resolve().parents[1]

    def test_repository_root_layout_matches_build_bible(self) -> None:
        """Required top-level directories from BUILD_BIBLE_V2.md exist.

        This encodes the "REPOSITORY STRUCTURE (MANDATORY)" section.
        """

        required_dirs = [
            "frontend",
            "backend",
            "agents",
            "orchestration",
            "build_system",
            "knowledge",
            "research",
            "infrastructure",
            "models",
            "memory",
            "projects",
            "tests",
            "scripts",
            "docs",
        ]

        missing = [name for name in required_dirs if not (self.root / name).is_dir()]
        self.assertFalse(
            missing,
            msg=f"Missing required root directories from BUILD_BIBLE_V2.md: {missing}",
        )

    def test_v2_agent_registry_has_all_12_roles(self) -> None:
        """The default AgentRegistry exposes all 12 V2 agents.

        This encodes the rule: "Do NOT remove the 12-agent system." The
        role names here are treated as canonical identifiers, matching
        V2_AGENT_ROLES.md.
        """

        registry = default_agent_registry()
        names = set(registry.agents.keys())

        required_agents = {
            "Origin",
            "Architect",
            "Builder",
            "Surface",
            "Core",
            "Simulator",
            "Synapse",
            "Fabricator",
            "Guardian",
            "Analyst",
            "Launcher",
            "Archivist",
        }

        missing = required_agents - names
        self.assertFalse(
            missing,
            msg=f"Missing agents from V2 registry (BUILD_BIBLE_V2): {missing}",
        )

    def test_simulation_task_gates_build_task(self) -> None:
        """Simulation is required before build, as per Build Bible.

        For a new command graph, the build task must transitively depend on
        the simulation task and be blocked when simulation is not approved.
        """

        engine = OrchestrationEngine()
        engine.create_command_task_graph("test command")

        # Basic shape of the graph
        ids = set(engine.tasks.keys())
        self.assertIn("cmd:root", ids)
        self.assertIn("cmd:simulate", ids)
        self.assertIn("cmd:plan", ids)
        self.assertIn("cmd:build", ids)

        simulate = engine.get_task("cmd:simulate")
        plan = engine.get_task("cmd:plan")
        build = engine.get_task("cmd:build")

        # Direct dependency chain: root -> simulate -> plan -> build
        self.assertIn("cmd:root", simulate.dependencies)
        self.assertIn("cmd:simulate", plan.dependencies)
        self.assertIn("cmd:plan", build.dependencies)

        # When simulation fails, build must be marked BLOCKED.
        engine.mark_simulation_result(task_id="cmd:simulate", approved=False, details={})
        self.assertEqual(build.status.value, "blocked")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
