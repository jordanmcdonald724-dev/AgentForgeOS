import os
import unittest


class AppsScaffoldTests(unittest.TestCase):
    def test_app_directories_exist(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps"))
        expected = ["studio", "builds", "research", "assets", "deployment"]
        for name in expected:
            path = os.path.join(base, name)
            with self.subTest(app=name):
                self.assertTrue(os.path.isdir(path), f"Expected scaffold directory missing: {path}")


if __name__ == "__main__":
    unittest.main()
