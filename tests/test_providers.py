"""Tests for all concrete provider implementations."""

import asyncio
import unittest


class NoOpProviderTests(unittest.TestCase):
    """NoOpLLMProvider should return a clear misconfiguration error."""

    def test_chat_returns_failure(self):
        from providers.noop_provider import NoOpLLMProvider

        provider = NoOpLLMProvider()
        result = asyncio.run(provider.chat("hello"))
        self.assertFalse(result["success"])
        self.assertIsNone(result["data"])
        self.assertIn("provider", result["error"].lower())


class OllamaProviderTests(unittest.TestCase):
    """OllamaProvider is importable and its constructor accepts custom args."""

    def test_importable_and_instantiable(self):
        from providers.ollama_provider import OllamaProvider

        p = OllamaProvider(base_url="http://localhost:11434", model="llama3")
        self.assertEqual(p.model, "llama3")
        self.assertEqual(p.base_url, "http://localhost:11434")

    def test_system_prompt_option(self):
        from providers.ollama_provider import OllamaProvider

        p = OllamaProvider(system_prompt="Be concise.")
        self.assertEqual(p.system_prompt, "Be concise.")

    def test_network_failure_returns_error(self):
        from providers.ollama_provider import OllamaProvider

        # Point at an unreachable port — should return an error dict, not raise.
        p = OllamaProvider(base_url="http://127.0.0.1:19999")
        result = asyncio.run(p.chat("test"))
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])


class OpenAIProviderTests(unittest.TestCase):
    """OpenAIProvider fails gracefully without an API key."""

    def test_importable(self):
        from providers.openai_provider import OpenAIProvider

        p = OpenAIProvider()
        self.assertIsNotNone(p)

    def test_missing_api_key_returns_error(self):
        import os
        from providers.openai_provider import OpenAIProvider

        # Unset the env var to guarantee no key is present.
        old = os.environ.pop("OPENAI_API_KEY", None)
        try:
            p = OpenAIProvider(api_key="")
            result = asyncio.run(p.chat("hi"))
            self.assertFalse(result["success"])
            self.assertIn("key", result["error"].lower())
        finally:
            if old is not None:
                os.environ["OPENAI_API_KEY"] = old


class FalImageProviderTests(unittest.TestCase):
    """FalImageProvider fails gracefully without an API key."""

    def test_importable(self):
        from providers.fal_provider import FalImageProvider

        p = FalImageProvider()
        self.assertIsNotNone(p)

    def test_missing_api_key_returns_error(self):
        import os
        from providers.fal_provider import FalImageProvider

        old = os.environ.pop("FAL_API_KEY", None)
        try:
            p = FalImageProvider(api_key="")
            result = asyncio.run(p.generate("a cat"))
            self.assertFalse(result["success"])
            self.assertIn("key", result["error"].lower())
        finally:
            if old is not None:
                os.environ["FAL_API_KEY"] = old


class ComfyUIProviderTests(unittest.TestCase):
    """ComfyUIImageProvider builds a valid workflow and fails gracefully."""

    def test_importable(self):
        from providers.comfyui_provider import ComfyUIImageProvider

        p = ComfyUIImageProvider()
        self.assertIsNotNone(p)

    def test_build_workflow_structure(self):
        from providers.comfyui_provider import ComfyUIImageProvider

        wf = ComfyUIImageProvider._build_workflow("a dog", {"steps": 10, "cfg": 5.0})
        self.assertIn("3", wf)  # KSampler
        self.assertIn("6", wf)  # CLIPTextEncode (positive)
        self.assertEqual(wf["3"]["inputs"]["steps"], 10)
        self.assertEqual(wf["3"]["inputs"]["cfg"], 5.0)
        self.assertEqual(wf["6"]["inputs"]["text"], "a dog")

    def test_network_failure_returns_error(self):
        from providers.comfyui_provider import ComfyUIImageProvider

        p = ComfyUIImageProvider(base_url="http://127.0.0.1:19998")
        result = asyncio.run(p.generate("a sunset"))
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])


class PiperTTSProviderTests(unittest.TestCase):
    """PiperTTSProvider fails gracefully when the binary is not installed."""

    def test_importable(self):
        from providers.piper_provider import PiperTTSProvider

        p = PiperTTSProvider()
        self.assertIsNotNone(p)

    def test_missing_binary_returns_error(self):
        from providers.piper_provider import PiperTTSProvider

        # Use a binary name that will never be on PATH.
        p = PiperTTSProvider(piper_bin="piper-not-installed-xyz")
        result = asyncio.run(p.speak("hello world"))
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])


class ProvidersInitTests(unittest.TestCase):
    """All providers are exported from the providers package."""

    def test_all_providers_importable_from_package(self):
        import providers

        for name in [
            "LLMProvider",
            "ImageProvider",
            "TTSProvider",
            "NoOpLLMProvider",
            "OllamaProvider",
            "OpenAIProvider",
            "FalImageProvider",
            "ComfyUIImageProvider",
            "PiperTTSProvider",
        ]:
            self.assertTrue(
                hasattr(providers, name),
                f"providers.{name} not found in package __init__",
            )


if __name__ == "__main__":
    unittest.main()
