from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore[assignment]
from enum import Enum, auto
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class RouteKind(Enum):
    CODE = auto()
    IMAGE = auto()
    AUDIO = auto()
    THREE_D = auto()
    GENERIC = auto()


@dataclass
class ModelRoute:
    """Model route configuration."""
    name: str
    provider: str
    model_id: str
    endpoint: str
    api_key_env: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.001


@dataclass
class FalAIConfig:
    """fal.ai configuration."""
    base_url: str = "https://fal.run"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


class ModelRouter:
    """Advanced model router with fal.ai integration and provider abstraction.
    
    Provides intelligent routing based on task requirements, cost optimization,
    and provider availability. Supports multiple providers with fallback logic.
    """

    def __init__(self):
        self.fal_config = FalAIConfig(
            api_key=os.getenv('FAL_API_KEY')
        )
        
        # Define route mappings per Build Bible specification
        self.routes: Dict[RouteKind, List[ModelRoute]] = {
            RouteKind.CODE: [
                ModelRoute(
                    name="deepseek-like-code-backend",
                    provider="fal",
                    model_id="deepseek-ai/deepseek-coder-6.7b-base",
                    endpoint="/deepseek-ai/deepseek-coder-6.7b-base",
                    api_key_env="FAL_API_KEY",
                    max_tokens=8192,
                    temperature=0.1,
                    cost_per_1k_tokens=0.00014
                ),
                ModelRoute(
                    name="codellama",
                    provider="fal",
                    model_id="meta-llama/codellama-7b-instruct",
                    endpoint="/meta-llama/codellama-7b-instruct",
                    api_key_env="FAL_API_KEY",
                    max_tokens=4096,
                    temperature=0.1,
                    cost_per_1k_tokens=0.00010
                )
            ],
            RouteKind.IMAGE: [
                ModelRoute(
                    name="flux-like-image-backend",
                    provider="fal",
                    model_id="flux-ai/flux-image-3.5b",
                    endpoint="/black-forest-labs/flux-schnell",
                    api_key_env="FAL_API_KEY",
                    cost_per_1k_tokens=0.0025
                ),
                ModelRoute(
                    name="flux-dev",
                    provider="fal",
                    model_id="black-forest-labs/flux-dev",
                    endpoint="/black-forest-labs/flux-dev", 
                    api_key_env="FAL_API_KEY",
                    cost_per_1k_tokens=0.003
                )
            ],
            RouteKind.THREE_D: [
                ModelRoute(
                    name="shape-e-like-3d-backend",
                    provider="fal",
                    model_id="shape-e/shape-e-3d-2.0",
                    endpoint="/lewdragon/shape-e",
                    api_key_env="FAL_API_KEY",
                    cost_per_1k_tokens=0.005
                )
            ],
            RouteKind.AUDIO: [
                ModelRoute(
                    name="bark",
                    provider="fal",
                    model_id="suno-ai/bark",
                    endpoint="/suno-ai/bark",
                    api_key_env="FAL_API_KEY",
                    cost_per_1k_tokens=0.0015
                ),
                ModelRoute(
                    name="audiocraft-like-audio-backend",
                    provider="fal",
                    model_id="audiocraft/audiocraft-2.0",
                    endpoint="/meta-audiocraft/audiocraft-medium",
                    api_key_env="FAL_API_KEY",
                    cost_per_1k_tokens=0.002
                )
            ],
            RouteKind.GENERIC: [
                ModelRoute(
                    name="generic-llm-backend",
                    provider="fal",
                    model_id="generic-llm/generic-llm-1.0",
                    endpoint="/meta-llama/llama-3-8b-instruct",
                    api_key_env="FAL_API_KEY",
                    max_tokens=4096,
                    temperature=0.7,
                    cost_per_1k_tokens=0.00005
                ),
                ModelRoute(
                    name="mixtral-8x7b",
                    provider="fal",
                    model_id="mistralai/mixtral-8x7b-instruct",
                    endpoint="/mistralai/mixtral-8x7b-instruct",
                    api_key_env="FAL_API_KEY",
                    max_tokens=4096,
                    temperature=0.7,
                    cost_per_1k_tokens=0.00024
                )
            ]
        }
        
        # Route selection history for optimization
        self.usage_history: List[Dict[str, Any]] = []

    def select_route(self, kind: RouteKind, requirements: Optional[Dict[str, Any]] = None) -> ModelRoute:
        """Select optimal route based on kind and requirements."""
        available_routes = self.routes.get(kind, [])
        
        if not available_routes:
            # Fallback to generic routes
            available_routes = self.routes.get(RouteKind.GENERIC, [])
        
        if not available_routes:
            raise ValueError(f"No routes available for kind: {kind}")
        
        # Select route based on requirements
        best_route = self._select_best_route(available_routes, requirements or {})
        
        # Log usage
        self._log_route_usage(best_route, kind, requirements or {})
        
        return best_route

    def _select_best_route(self, routes: List[ModelRoute], requirements: Dict[str, Any]) -> ModelRoute:
        """Select best route based on cost, availability, and requirements."""
        # Simple selection: choose lowest cost route
        # In production, consider availability, latency, success rate, etc.
        return min(routes, key=lambda r: r.cost_per_1k_tokens)

    def _log_route_usage(self, route: ModelRoute, kind: RouteKind, requirements: Dict[str, Any]) -> None:
        """Log route usage for optimization."""
        usage_record: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'route_name': route.name,
            'provider': route.provider,
            'kind': kind.name,
            'requirements': requirements,
            'cost_per_1k_tokens': route.cost_per_1k_tokens
        }
        self.usage_history.append(usage_record)
        
        # Keep only last 1000 records
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

    async def call_model(self, route: ModelRoute, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute model call via fal.ai."""
        if not self.fal_config.api_key:
            raise ValueError("FAL_API_KEY not configured")
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "max_tokens": kwargs.get('max_tokens', route.max_tokens),
            "temperature": kwargs.get('temperature', route.temperature),
            **{k: v for k, v in kwargs.items() if k not in ['max_tokens', 'temperature']}
        }
        
        headers = {
            "Authorization": f"Key {self.fal_config.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.fal_config.base_url}{route.endpoint}"
        
        if aiohttp is None:
            raise RuntimeError(
                "aiohttp is required for provider calls. Install dependencies with: python -m pip install -r requirements.txt"
            )

        async with aiohttp.ClientSession() as session:
            for attempt in range(self.fal_config.max_retries):
                try:
                    async with session.post(
                        url, 
                        json=payload, 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.fal_config.timeout)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {
                                'success': True,
                                'data': result,
                                'route_used': route.name,
                                'tokens_used': result.get('tokens_used', 0),
                                'cost': result.get('tokens_used', 0) * route.cost_per_1k_tokens / 1000
                            }
                        else:
                            error_text = await response.text()
                            if attempt == self.fal_config.max_retries - 1:
                                return {
                                    'success': False,
                                    'error': f"HTTP {response.status}: {error_text}",
                                    'route_used': route.name
                                }
                except asyncio.TimeoutError:
                    if attempt == self.fal_config.max_retries - 1:
                        return {
                            'success': False,
                            'error': f"Timeout after {self.fal_config.timeout}s",
                            'route_used': route.name
                        }
                except Exception as e:
                    if attempt == self.fal_config.max_retries - 1:
                        return {
                            'success': False,
                            'error': str(e),
                            'route_used': route.name
                        }
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
        return {'success': False, 'error': 'Max retries exceeded', 'route_used': route.name}

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for optimization."""
        if not self.usage_history:
            return {'total_calls': 0, 'total_cost': 0.0, 'routes_used': {}}
        
        total_cost = sum(record.get('cost', 0) for record in self.usage_history)
        routes_used = {}
        
        for record in self.usage_history:
            route_name = record['route_name']
            routes_used[route_name] = routes_used.get(route_name, 0) + 1
        
        return {
            'total_calls': len(self.usage_history),
            'total_cost': total_cost,
            'routes_used': routes_used,
            'avg_cost_per_call': total_cost / len(self.usage_history)
        }

    def get_route_info(self, kind: RouteKind) -> List[Dict[str, Any]]:
        """Get information about available routes for a kind."""
        routes = self.routes.get(kind, [])
        return [
            {
                'name': route.name,
                'provider': route.provider,
                'model_id': route.model_id,
                'max_tokens': route.max_tokens,
                'temperature': route.temperature,
                'cost_per_1k_tokens': route.cost_per_1k_tokens
            }
            for route in routes
        ]
