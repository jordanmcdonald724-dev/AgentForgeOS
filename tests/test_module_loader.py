import json
import tempfile
import unittest
from pathlib import Path

from control.module_registry import ModuleRegistry
from engine.module_loader import load_modules


class ModuleLoaderManifestTests(unittest.TestCase):
    def _create_module(self, base: Path, name: str, manifest: dict, body: str = "class Module:\n    pass\n"):
        module_dir = base / name
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "manifest.json").write_text(json.dumps(manifest))
        entry = manifest.get("entry")
        if entry:
            (module_dir / entry).write_text(body)
        return module_dir

    def test_loads_module_with_valid_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            apps_path = Path(tmp)
            manifest = {
                "id": "valid-module",
                "name": "Valid",
                "version": "1.0.0",
                "entry": "module.py",
            }
            self._create_module(apps_path, "valid", manifest)

            registry = ModuleRegistry()
            loaded = load_modules(apps_path=apps_path, registry=registry)

            self.assertIn("valid-module", loaded)
            self.assertIs(registry.get_instance("valid-module"), loaded["valid-module"])
            self.assertEqual(registry.get_manifest("valid-module")["name"], "Valid")

    def test_skips_manifest_missing_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            apps_path = Path(tmp)

            valid_manifest = {
                "id": "valid-module",
                "name": "Valid",
                "version": "1.0.0",
                "entry": "module.py",
            }
            invalid_manifest = {
                "id": "incomplete-module",
                "name": "Incomplete",
                # version missing on purpose
                "entry": "module.py",
            }

            self._create_module(apps_path, "valid", valid_manifest)
            self._create_module(apps_path, "invalid", invalid_manifest, body="class Module:\n    pass\n")

            registry = ModuleRegistry()
            with self.assertLogs("engine.module_loader", level="WARNING") as logs:
                loaded = load_modules(apps_path=apps_path, registry=registry)

            self.assertIn("valid-module", loaded)
            self.assertNotIn("incomplete-module", loaded)
            self.assertTrue(
                any("manifest missing required fields" in message for message in logs.output),
                "Expected warning about missing manifest fields",
            )


if __name__ == "__main__":
    unittest.main()
