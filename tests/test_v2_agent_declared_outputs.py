from pathlib import Path
import unittest

from orchestration.engine import DEFAULT_PROJECT_ROOT, get_default_declared_outputs
from orchestration.runtime import default_agent_registry


class TestV2AgentDeclaredOutputs(unittest.TestCase):
    """Ensure every V2 agent has a declared_outputs contract.

    This keeps the artifact responsibilities for each role encoded in
    one place and in sync with the AgentRegistry.
    """

    def test_all_agents_have_declared_outputs_mapping(self) -> None:
        registry = default_agent_registry()
        root = DEFAULT_PROJECT_ROOT

        for name in sorted(registry.agents.keys()):
            with self.subTest(agent=name):
                outputs = get_default_declared_outputs(name, root)
                # Some agents may not be wired into a specific task yet,
                # but they should still have a non-empty contract.
                self.assertTrue(outputs, msg=f"No declared_outputs mapping for agent {name}")
                for raw in outputs:
                    # Paths should be under the project root
                    self.assertTrue(str(raw).startswith(str(root)), raw)


if __name__ == "__main__":
    unittest.main()
