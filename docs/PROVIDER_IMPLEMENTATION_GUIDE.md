# AgentForgeOS — Provider Implementation Guide

Purpose:

Explain how AI providers integrate with the system.

Providers must follow standardized interfaces.

---

# Provider Directory

providers/

Example:

llm_provider.py
image_provider.py
tts_provider.py

---

# LLM Provider Interface

Example:

```python
class LLMProvider:
    async def chat(self, prompt: str):
        pass
```

---

# Image Provider Interface

```python
class ImageProvider:
    async def generate(self, prompt: str):
        pass
```

---

# TTS Provider Interface

```python
class TTSProvider:
    async def speak(self, text: str):
        pass
```

---

# Example Provider Implementations

FalProvider
OpenAIProvider
OllamaProvider
ComfyUIProvider
PiperProvider

---

# Provider Rules

Providers must:

• implement interface methods
• return standardized responses
• never expose API keys

Providers must not:

• modify system services
• bypass provider interface

---

# Provider Configuration

API keys stored in:

config/.env

Example:

FAL_API_KEY=xxxxx
OPENAI_API_KEY=xxxxx

---

# End of Provider Guide
