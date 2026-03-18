import os
import unittest


class AppsScaffoldTests(unittest.TestCase):
    def test_app_directories_exist(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps"))
        expected = [
            "studio",
            "builds",
            "research",
            "assets",
            "deployment",
            "sandbox",
            "game_dev",
            "saas_builder",
        ]
        for name in expected:
            path = os.path.join(base, name)
            with self.subTest(app=name):
                self.assertTrue(os.path.isdir(path), f"Expected scaffold directory missing: {path}")

    def test_new_modules_have_required_files(self):
        """sandbox, game_dev, saas_builder must have manifest, module, README, backend/routes."""
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps"))
        new_modules = ["sandbox", "game_dev", "saas_builder"]
        required_files = [
            "manifest.json",
            "module.py",
            "README.md",
            os.path.join("backend", "routes.py"),
        ]
        for mod in new_modules:
            for rel_path in required_files:
                full = os.path.join(base, mod, rel_path)
                with self.subTest(module=mod, file=rel_path):
                    self.assertTrue(os.path.isfile(full), f"Missing file: {full}")

    def test_new_module_manifests_valid(self):
        """manifest.json for each new module has required non-empty fields."""
        import json
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps"))
        new_modules = ["sandbox", "game_dev", "saas_builder"]
        required_fields = ["id", "name", "version", "entry", "class"]
        for mod in new_modules:
            manifest_path = os.path.join(base, mod, "manifest.json")
            with self.subTest(module=mod):
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                for field in required_fields:
                    self.assertIn(field, manifest, f"{mod}/manifest.json missing '{field}'")
                    self.assertTrue(str(manifest[field]).strip(), f"{mod}/manifest.json '{field}' is empty")


if __name__ == "__main__":
    unittest.main()

