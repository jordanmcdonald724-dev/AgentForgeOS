import json
import textwrap
import tempfile
import unittest
from pathlib import Path

from control.module_registry import ModuleRegistry
from engine.module_loader import load_modules


class ModuleLoaderManifestTests(unittest.TestCase):
    def setUp(self):
        ModuleRegistry().clear()

    def tearDown(self):
        ModuleRegistry().clear()

    def _create_module(
        self,
        base: Path,
        name: str,
        manifest: dict,
        body: str | None = None,
    ):
        if body is None:
            body = textwrap.dedent(
                """\
                class Module:
                    pass
                """
            )
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
                "class": "Module",
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
                "class": "Module",
            }
            invalid_manifest = {
                "id": "incomplete-module",
                "name": "Incomplete",
                "version": "1.0.0",
                "entry": "module.py",
                # class missing on purpose
            }

            self._create_module(apps_path, "valid", valid_manifest)
            self._create_module(apps_path, "invalid", invalid_manifest)

            registry = ModuleRegistry()
            with self.assertLogs("engine.module_loader", level="WARNING") as logs:
                loaded = load_modules(apps_path=apps_path, registry=registry)

            self.assertIn("valid-module", loaded)
            self.assertNotIn("incomplete-module", loaded)
            self.assertTrue(
                any("manifest missing or invalid required fields" in message for message in logs.output),
                "Expected warning about missing or invalid manifest fields",
            )

    def test_skips_when_manifest_not_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            apps_path = Path(tmp)
            valid_manifest = {
                "id": "valid-module",
                "name": "Valid",
                "version": "1.0.0",
                "entry": "module.py",
                "class": "Module",
            }
            self._create_module(apps_path, "valid", valid_manifest)

            invalid_dir = apps_path / "invalid"
            invalid_dir.mkdir(parents=True, exist_ok=True)
            (invalid_dir / "manifest.json").write_text(json.dumps(["not-a-dict"]))

            registry = ModuleRegistry()
            with self.assertLogs("engine.module_loader", level="WARNING") as logs:
                loaded = load_modules(apps_path=apps_path, registry=registry)

            self.assertIn("valid-module", loaded)
            self.assertNotIn("invalid", loaded)
            self.assertTrue(
                any("manifest is not a JSON object" in message for message in logs.output),
                "Expected warning about invalid manifest structure",
            )


if __name__ == "__main__":
    unittest.main()
