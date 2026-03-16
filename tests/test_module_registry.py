import unittest

from control.module_registry import ModuleRegistry, module_registry


class ModuleRegistrySingletonTests(unittest.TestCase):
    def setUp(self):
        # Ensure clean state for each test since registry is a singleton
        ModuleRegistry().clear()

    def tearDown(self):
        ModuleRegistry().clear()

    def test_module_registry_is_singleton(self):
        first = ModuleRegistry()
        second = ModuleRegistry()
        self.assertIs(first, second)
        self.assertIs(first, module_registry)

    def test_register_and_retrieve_modules(self):
        registry = ModuleRegistry()
        manifest = {"id": "demo", "name": "Demo", "version": "1.0.0", "entry": "module.py"}
        instance = object()

        registry.register_module("demo", instance, manifest)

        module_entry = registry.get_module("demo")
        self.assertIsNotNone(module_entry)
        self.assertIs(module_entry["instance"], instance)
        self.assertEqual(module_entry["manifest"], manifest)
        self.assertIn("demo", registry.get_all_modules())
        self.assertEqual(registry.get_instance("demo"), instance)
        self.assertEqual(registry.get_manifest("demo"), manifest)

    def test_clear_removes_all_modules(self):
        registry = ModuleRegistry()
        registry.register_module("demo", object(), {"id": "demo"})
        self.assertIn("demo", registry.get_all_modules())

        registry.clear()
        self.assertEqual(dict(registry.get_all_modules()), {})


if __name__ == "__main__":
    unittest.main()
