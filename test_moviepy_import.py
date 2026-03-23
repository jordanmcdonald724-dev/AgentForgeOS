import importlib
import unittest


class TestMoviePyImport(unittest.TestCase):
    def test_moviepy_import(self) -> None:
        module = importlib.import_module("moviepy.video.io.VideoFileClip")
        self.assertTrue(hasattr(module, "VideoFileClip"))
