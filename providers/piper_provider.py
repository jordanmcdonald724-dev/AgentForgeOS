"""PiperTTSProvider — local text-to-speech via the Piper binary."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from providers.tts_provider import TTSProvider

logger = logging.getLogger(__name__)

_DEFAULT_PIPER_BIN = "piper"
_DEFAULT_MODEL = "en_US-lessac-medium"


class PiperTTSProvider(TTSProvider):
    """Converts text to speech using the local Piper TTS binary.

    Piper is a fast, local neural text-to-speech system.
    See https://github.com/rhasspy/piper for installation instructions.

    The binary is looked up via ``shutil.which``; set ``PIPER_BIN`` in
    ``config/.env`` if the binary is not on PATH.
    """

    def __init__(
        self,
        piper_bin: Optional[str] = None,
        model: Optional[str] = None,
        *,
        models_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.piper_bin = piper_bin or os.environ.get("PIPER_BIN", _DEFAULT_PIPER_BIN)
        self.model = model or os.environ.get("PIPER_MODEL", _DEFAULT_MODEL)
        self.models_dir = Path(
            models_dir or os.environ.get("PIPER_MODELS_DIR", "./models/piper")
        )
        self.output_dir = Path(
            output_dir or os.environ.get("PIPER_OUTPUT_DIR", "./workspace/audio")
        )

    async def speak(
        self,
        text: str,
        *,
        voice: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not shutil.which(self.piper_bin):
            return {
                "success": False,
                "data": None,
                "error": (
                    f"Piper binary '{self.piper_bin}' not found. "
                    "Install piper-tts and set PIPER_BIN in config/.env"
                ),
            }

        model_name = voice or self.model
        model_path = self.models_dir / f"{model_name}.onnx"
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                suffix=".wav", dir=self.output_dir, delete=False
            ) as tmp_file:
                output_path = tmp_file.name

            cmd = [
                self.piper_bin,
                "--model",
                str(model_path),
                "--output_file",
                output_path,
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate(input=text.encode("utf-8"))
            if proc.returncode != 0:
                return {
                    "success": False,
                    "data": None,
                    "error": (
                        f"Piper exited with code {proc.returncode}: "
                        + stderr.decode("utf-8", errors="replace")
                    ),
                }
            return {
                "success": True,
                "data": {"output_file": output_path},
                "error": None,
            }
        except Exception as exc:
            logger.warning("PiperTTSProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}
