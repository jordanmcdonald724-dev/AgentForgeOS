from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Dict, Optional

from orchestration.task_model import Task
from .base import AgentResult
from infrastructure.model_router import ModelRouter, RouteKind, ModelRoute


@dataclass
class AIEngineerAgent:
    """SYNAPSE (AI Engineer) agent.

    Implements the role defined in V2_AGENT_ROLES:
    - selects correct model routes with fal.ai integration
    - manages embeddings and inference logs
    - provides cost optimization and provider fallback
    Outputs model_routes.json and inference_logs.json under the
    project root for downstream agents to consume.
    """

    name: str = "Synapse"
    router: Optional[ModelRouter] = None

    def __post_init__(self):
        if self.router is None:
            self.router = ModelRouter()

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw) if raw else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _determine_route_kind(self, use_case: str, task_inputs: Dict[str, Any]) -> RouteKind:
        """Determine the appropriate route kind based on use case and inputs."""
        use_case_lower = use_case.lower()
        
        # Check for specific indicators in task inputs
        if 'image' in use_case_lower or 'visual' in use_case_lower:
            return RouteKind.IMAGE
        elif 'audio' in use_case_lower or 'sound' in use_case_lower or 'voice' in use_case_lower:
            return RouteKind.AUDIO
        elif '3d' in use_case_lower or 'model' in use_case_lower or 'mesh' in use_case_lower:
            return RouteKind.THREE_D
        elif 'code' in use_case_lower or 'programming' in use_case_lower or 'backend' in use_case_lower:
            return RouteKind.CODE
        else:
            return RouteKind.GENERIC

    async def handle_task(self, task: Task) -> AgentResult:
        """Handle AI engineering task with advanced model routing."""
        project_root = self._resolve_project_root(task)
        use_case = task.inputs.get("use_case", "generic")
        task.inputs
        
        # Determine route kind
        kind = self._determine_route_kind(use_case, task.inputs)
        
        # Select optimal route
        requirements = {
            'max_tokens': task.inputs.get('max_tokens'),
            'temperature': task.inputs.get('temperature'),
            'quality': task.inputs.get('quality', 'standard')
        }
        
        selected_route = self.router.select_route(kind, requirements)
        
        # Prepare route configuration
        routes_config = {
            "use_case": use_case,
            "kind": kind.name,
            "selected_route": {
                "name": selected_route.name,
                "provider": selected_route.provider,
                "model_id": selected_route.model_id,
                "max_tokens": selected_route.max_tokens,
                "temperature": selected_route.temperature,
                "cost_per_1k_tokens": selected_route.cost_per_1k_tokens
            },
            "requirements": requirements,
            "alternative_routes": [route.name for route in self.router.routes.get(kind, []) if route.name != selected_route.name]
        }
        
        # Generate inference logs
        logs = [
            {
                "timestamp": "2024-01-01T00:00:00Z",  # Would use real timestamp
                "message": f"Synapse selected route {selected_route.name} for use_case={use_case}",
                "route_kind": kind.name,
                "provider": selected_route.provider,
                "model_id": selected_route.model_id,
                "cost_estimate": selected_route.cost_per_1k_tokens
            }
        ]
        
        # Get usage statistics
        usage_stats = self.router.get_usage_stats()
        logs.append({
            "timestamp": "2024-01-01T00:00:00Z",
            "message": f"Current usage stats: {usage_stats['total_calls']} calls, ${usage_stats['total_cost']:.4f} total cost",
            "stats": usage_stats
        })

        # Write artifacts
        routes_path = project_root / "model_routes.json"
        logs_path = project_root / "inference_logs.json"

        routes_path.write_text(json.dumps(routes_config, indent=2), encoding="utf-8")
        logs_path.write_text(json.dumps(logs, indent=2), encoding="utf-8")

        return AgentResult(
            outputs={
                "model_routes_path": str(routes_path),
                "inference_logs_path": str(logs_path),
                "selected_route": selected_route.name,
                "provider": selected_route.provider,
                "estimated_cost_per_1k_tokens": selected_route.cost_per_1k_tokens
            },
            logs=[
                f"Synapse wrote model routing artifacts under {project_root}",
                f"Selected {selected_route.name} via {selected_route.provider}",
                f"Route kind: {kind.name}",
                f"Cost: ${selected_route.cost_per_1k_tokens}/1k tokens"
            ],
        )

    def handle_task_sync(self, task: Task) -> AgentResult:
        """Synchronous wrapper for handle_task."""
        return asyncio.run(self.handle_task(task))
