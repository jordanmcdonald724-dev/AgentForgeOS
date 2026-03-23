"""
Sandbox API Routes

Provides REST API endpoints for Docker sandbox build execution
and sandbox management.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from build_system.docker_sandbox import docker_sandbox, BuildRequest, SandboxConfig

logger = logging.getLogger(__name__)

# Create router
sandbox_router = APIRouter(prefix="/sandbox", tags=["sandbox"])


# Request/Response Models
class BuildRequestModel(BaseModel):
    """Model for build requests"""
    project_id: str = Field(..., description="Project identifier")
    command: str = Field(..., description="Build command to execute")
    working_dir: str = Field(default=".", description="Working directory in container")
    files: Dict[str, str] = Field(default_factory=dict, description="Files to create (filename -> content)")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    requirements: list[str] = Field(default_factory=list, description="Python requirements to install")


class SandboxConfigModel(BaseModel):
    """Model for sandbox configuration"""
    image: str = Field(default="agentforge/build-sandbox:latest", description="Docker image")
    memory_limit: str = Field(default="2g", description="Memory limit (e.g., '2g', '512m')")
    cpu_limit: str = Field(default="1.0", description="CPU limit (e.g., '1.0', '0.5')")
    timeout: int = Field(default=300, description="Timeout in seconds")
    network_mode: str = Field(default="none", description="Network mode")
    read_only: bool = Field(default=False, description="Read-only filesystem")
    environment: Dict[str, str] = Field(default_factory=dict, description="Default environment variables")


class BuildResultModel(BaseModel):
    """Model for build results"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    container_id: str
    artifacts: Dict[str, str] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# In-memory build results store (in production, use database)
build_results: Dict[str, BuildResultModel] = {}


@sandbox_router.get("/info")
async def get_sandbox_info() -> Dict[str, Any]:
    """Get sandbox system information and status."""
    try:
        info = await docker_sandbox.get_sandbox_info()
        return {
            "success": True,
            "data": info,
            "error": None
        }
    except Exception as e:
        logger.error(f"Failed to get sandbox info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@sandbox_router.post("/build")
async def execute_build(
    request: BuildRequestModel,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Execute a build in the Docker sandbox.
    
    Args:
        request: Build request with command and files
        background_tasks: FastAPI background tasks
        
    Returns:
        Build result information
    """
    try:
        # Convert Pydantic model to internal format
        build_request = BuildRequest(
            project_id=request.project_id,
            command=request.command,
            working_dir=request.working_dir,
            files=request.files,
            environment=request.environment,
            requirements=request.requirements
        )
        
        # Execute build
        result = await docker_sandbox.execute_build(build_request)
        
        # Convert to response model
        result_model = BuildResultModel(
            success=result.success,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time=result.execution_time,
            container_id=result.container_id,
            artifacts=result.artifacts,
            error=result.error
        )
        
        # Store result
        build_results[result.container_id] = result_model
        
        # Schedule cleanup in background
        background_tasks.add_task(cleanup_build_result, result.container_id)
        
        return {
            "success": True,
            "data": result_model.dict(),
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Failed to execute build: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@sandbox_router.get("/build/{container_id}")
async def get_build_result(container_id: str) -> Dict[str, Any]:
    """Get the result of a previous build execution."""
    if container_id not in build_results:
        raise HTTPException(status_code=404, detail="Build result not found")
    
    return {
        "success": True,
        "data": build_results[container_id].dict(),
        "error": None
    }


@sandbox_router.post("/image/build")
async def build_sandbox_image() -> Dict[str, Any]:
    """Build the sandbox Docker image."""
    try:
        success = await docker_sandbox.build_sandbox_image()
        
        return {
            "success": success,
            "data": {
                "image_built": success,
                "image_name": docker_sandbox.config.image
            },
            "error": None if success else "Failed to build sandbox image"
        }
        
    except Exception as e:
        logger.error(f"Failed to build sandbox image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@sandbox_router.post("/config")
async def update_sandbox_config(config: SandboxConfigModel) -> Dict[str, Any]:
    """Update sandbox configuration."""
    try:
        # Create new sandbox instance with updated config
        new_config = SandboxConfig(
            image=config.image,
            memory_limit=config.memory_limit,
            cpu_limit=config.cpu_limit,
            timeout=config.timeout,
            network_mode=config.network_mode,
            read_only=config.read_only,
            environment=config.environment
        )
        
        # Update global sandbox instance
        global docker_sandbox
        docker_sandbox = docker_sandbox.__class__(new_config)
        
        return {
            "success": True,
            "data": {
                "config": new_config.__dict__,
                "message": "Sandbox configuration updated"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Failed to update sandbox config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@sandbox_router.get("/results")
async def list_build_results() -> Dict[str, Any]:
    """List all build results."""
    return {
        "success": True,
        "data": {
            "results": [result.dict() for result in build_results.values()],
            "total": len(build_results)
        },
        "error": None
    }


@sandbox_router.delete("/results/{container_id}")
async def delete_build_result(container_id: str) -> Dict[str, Any]:
    """Delete a build result."""
    if container_id not in build_results:
        raise HTTPException(status_code=404, detail="Build result not found")
    
    del build_results[container_id]
    
    return {
        "success": True,
        "data": {"message": f"Build result {container_id} deleted"},
        "error": None
    }


@sandbox_router.delete("/results")
async def clear_all_build_results() -> Dict[str, Any]:
    """Clear all build results."""
    cleared_count = len(build_results)
    build_results.clear()
    
    return {
        "success": True,
        "data": {
            "message": f"Cleared {cleared_count} build results"
        },
        "error": None
    }


async def cleanup_build_result(container_id: str, delay: int = 3600) -> None:
    """
    Background task to cleanup build results after a delay.
    
    Args:
        container_id: Container ID to cleanup
        delay: Delay in seconds (default: 1 hour)
    """
    await asyncio.sleep(delay)
    
    if container_id in build_results:
        del build_results[container_id]
        logger.info(f"Cleaned up build result for container {container_id}")


# Health check endpoint
@sandbox_router.get("/health")
async def sandbox_health() -> Dict[str, Any]:
    """Check sandbox system health."""
    try:
        info = await docker_sandbox.get_sandbox_info()
        
        return {
            "success": True,
            "data": {
                "healthy": info.get("docker_available", False),
                "image_exists": info.get("image_exists", False),
                "active_results": len(build_results),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Sandbox health check failed: {e}")
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }
