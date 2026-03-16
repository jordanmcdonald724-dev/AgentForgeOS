"""ComfyUIImageProvider — local image generation via the ComfyUI HTTP API."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

import httpx

from providers.image_provider import ImageProvider

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:8188"
_REQUEST_TIMEOUT = 300.0


class ComfyUIImageProvider(ImageProvider):
    """Queues a prompt on a locally running ComfyUI instance.

    ComfyUI must be running (``python main.py``).
    The workflow submitted uses a minimal KSampler pipeline; supply
    ``options["checkpoint"]`` to choose a specific model checkpoint.
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        *,
        timeout: float = _REQUEST_TIMEOUT,
        client_id: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = client_id or str(uuid.uuid4())

    async def generate(
        self, prompt: str, *, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Queue a text-to-image workflow on ComfyUI.

        Returns the queue entry data dict from ComfyUI, which includes
        the ``prompt_id`` that can be used to poll for results.
        """
        workflow = self._build_workflow(prompt, options or {})
        payload = {"prompt": workflow, "client_id": self.client_id}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/prompt", json=payload
                )
                response.raise_for_status()
                data = response.json()
                return {"success": True, "data": data, "error": None}
        except httpx.HTTPStatusError as exc:
            logger.warning("ComfyUIImageProvider HTTP error: %s", exc)
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
            }
        except Exception as exc:
            logger.warning("ComfyUIImageProvider error: %s", exc)
            return {"success": False, "data": None, "error": str(exc)}

    @staticmethod
    def _build_workflow(prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Return a minimal ComfyUI workflow dict for text-to-image generation."""
        steps = int(options.get("steps", 20))
        cfg = float(options.get("cfg", 7.0))
        width = int(options.get("width", 512))
        height = int(options.get("height", 512))
        checkpoint = options.get(
            "checkpoint", "v1-5-pruned-emaonly.safetensors"
        )
        return {
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]},
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "", "clip": ["4", 1]},
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                    "seed": int(options.get("seed", 0)),
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": options.get("sampler", "euler"),
                    "scheduler": options.get("scheduler", "normal"),
                    "denoise": 1.0,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["8", 0],
                    "filename_prefix": "agentforge",
                },
            },
        }
