"""
Plugin Management API Routes

Provides REST API endpoints for plugin management,
installation, configuration, and monitoring.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from plugins.plugin_manager import plugin_manager, PluginType, PluginStatus


# Create router
plugins_router = APIRouter(prefix="/plugins", tags=["plugins"])


# Request/Response Models
class PluginListResponse(BaseModel):
    """Plugin list response model"""
    plugins: Dict[str, Dict[str, Any]]
    total_count: int
    active_count: int


class PluginInfoResponse(BaseModel):
    """Plugin information response model"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    status: str
    installed_at: str
    last_updated: str
    config: Dict[str, Any]
    usage_stats: Dict[str, Any]
    error_message: Optional[str] = None


class PluginConfigUpdateRequest(BaseModel):
    """Plugin configuration update request model"""
    config: Dict[str, Any]


class PluginInstallResponse(BaseModel):
    """Plugin installation response model"""
    success: bool
    message: str
    plugin_name: Optional[str] = None


class PluginUsageStatsResponse(BaseModel):
    """Plugin usage statistics response model"""
    global_stats: Dict[str, Any]
    plugins: Dict[str, Dict[str, Any]]


@plugins_router.get("/", response_model=PluginListResponse)
async def list_plugins() -> PluginListResponse:
    """List all installed plugins."""
    try:
        plugins = plugin_manager.list_plugins()
        
        # Convert to response format
        plugin_data = {}
        for name, info in plugins.items():
            plugin_data[name] = {
                'metadata': {
                    'name': info.metadata.name,
                    'version': info.metadata.version,
                    'description': info.metadata.description,
                    'author': info.metadata.author,
                    'plugin_type': info.metadata.plugin_type.value,
                    'dependencies': info.metadata.dependencies,
                    'permissions': info.metadata.permissions,
                    'tags': info.metadata.tags
                },
                'status': info.status.value,
                'installed_at': info.installed_at,
                'last_updated': info.last_updated,
                'error_message': info.error_message
            }
        
        active_plugins = plugin_manager.get_active_plugins()
        
        return PluginListResponse(
            plugins=plugin_data,
            total_count=len(plugins),
            active_count=len(active_plugins)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/{plugin_name}", response_model=PluginInfoResponse)
async def get_plugin_info(plugin_name: str) -> PluginInfoResponse:
    """Get detailed information about a specific plugin."""
    try:
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return PluginInfoResponse(
            name=plugin_info.metadata.name,
            version=plugin_info.metadata.version,
            description=plugin_info.metadata.description,
            author=plugin_info.metadata.author,
            plugin_type=plugin_info.metadata.plugin_type.value,
            status=plugin_info.status.value,
            installed_at=plugin_info.installed_at,
            last_updated=plugin_info.last_updated,
            config=plugin_info.config,
            usage_stats=plugin_info.usage_stats,
            error_message=plugin_info.error_message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/install", response_model=PluginInstallResponse)
async def install_plugin(
    file: UploadFile = File(...),
    overwrite: bool = Form(False)
) -> PluginInstallResponse:
    """Install a plugin from uploaded file."""
    try:
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Install plugin
            from pathlib import Path
            success = await plugin_manager.install_plugin(Path(temp_file_path))
            
            if success:
                return PluginInstallResponse(
                    success=True,
                    message="Plugin installed successfully",
                    plugin_name=file.filename.replace('.zip', '')
                )
            else:
                return PluginInstallResponse(
                    success=False,
                    message="Plugin installation failed"
                )
        finally:
            # Cleanup temporary file
            import os
            os.unlink(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/load")
async def load_plugin(plugin_name: str) -> Dict[str, Any]:
    """Load a plugin."""
    try:
        success = await plugin_manager.load_plugin(plugin_name)
        
        return {
            "success": success,
            "message": f"Plugin {plugin_name} loaded successfully" if success else f"Failed to load plugin {plugin_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/unload")
async def unload_plugin(plugin_name: str) -> Dict[str, Any]:
    """Unload a plugin."""
    try:
        success = await plugin_manager.unload_plugin(plugin_name)
        
        return {
            "success": success,
            "message": f"Plugin {plugin_name} unloaded successfully" if success else f"Failed to unload plugin {plugin_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/enable")
async def enable_plugin(plugin_name: str) -> Dict[str, Any]:
    """Enable a plugin."""
    try:
        success = await plugin_manager.enable_plugin(plugin_name)
        
        return {
            "success": success,
            "message": f"Plugin {plugin_name} enabled successfully" if success else f"Failed to enable plugin {plugin_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/disable")
async def disable_plugin(plugin_name: str) -> Dict[str, Any]:
    """Disable a plugin."""
    try:
        success = await plugin_manager.disable_plugin(plugin_name)
        
        return {
            "success": success,
            "message": f"Plugin {plugin_name} disabled successfully" if success else f"Failed to disable plugin {plugin_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.delete("/{plugin_name}")
async def uninstall_plugin(plugin_name: str) -> Dict[str, Any]:
    """Uninstall a plugin."""
    try:
        success = await plugin_manager.uninstall_plugin(plugin_name)
        
        return {
            "success": success,
            "message": f"Plugin {plugin_name} uninstalled successfully" if success else f"Failed to uninstall plugin {plugin_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.put("/{plugin_name}/config")
async def update_plugin_config(
    plugin_name: str, 
    request: PluginConfigUpdateRequest
) -> Dict[str, Any]:
    """Update plugin configuration."""
    try:
        success = await plugin_manager.update_plugin_config(plugin_name, request.config)
        
        return {
            "success": success,
            "message": f"Plugin configuration updated successfully" if success else f"Failed to update plugin configuration"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/{plugin_name}/config")
async def get_plugin_config(plugin_name: str) -> Dict[str, Any]:
    """Get plugin configuration."""
    try:
        plugin_info = plugin_manager.get_plugin_info(plugin_name)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return {
            "config": plugin_info.config,
            "schema": plugin_info.metadata.config_schema
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/types/{plugin_type}")
async def get_plugins_by_type(plugin_type: str) -> Dict[str, Any]:
    """Get plugins by type."""
    try:
        # Validate plugin type
        try:
            plugin_type_enum = PluginType(plugin_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid plugin type: {plugin_type}")
        
        plugins = plugin_manager.get_plugins_by_type(plugin_type_enum)
        
        plugin_details = {}
        for plugin_name in plugins:
            info = plugin_manager.get_plugin_info(plugin_name)
            if info:
                plugin_details[plugin_name] = {
                    'name': info.metadata.name,
                    'version': info.metadata.version,
                    'description': info.metadata.description,
                    'status': info.status.value,
                    'author': info.metadata.author,
                    'tags': info.metadata.tags
                }
        
        return {
            "plugin_type": plugin_type,
            "plugins": plugin_details,
            "count": len(plugins)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/active")
async def get_active_plugins() -> Dict[str, Any]:
    """Get list of active plugins."""
    try:
        active_plugins = plugin_manager.get_active_plugins()
        
        plugin_details = {}
        for plugin_name in active_plugins:
            info = plugin_manager.get_plugin_info(plugin_name)
            if info:
                plugin_details[plugin_name] = {
                    'name': info.metadata.name,
                    'version': info.metadata.version,
                    'plugin_type': info.metadata.plugin_type.value,
                    'description': info.metadata.description,
                    'last_used': info.usage_stats.get('last_used')
                }
        
        return {
            "active_plugins": plugin_details,
            "count": len(active_plugins)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/usage/stats", response_model=PluginUsageStatsResponse)
async def get_usage_statistics() -> PluginUsageStatsResponse:
    """Get plugin usage statistics."""
    try:
        stats = plugin_manager.get_usage_statistics()
        return PluginUsageStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/discover")
async def discover_plugins() -> Dict[str, Any]:
    """Discover plugins in the plugins directory."""
    try:
        await plugin_manager.discover_plugins()
        
        plugins = plugin_manager.list_plugins()
        
        return {
            "success": True,
            "message": "Plugin discovery completed",
            "plugins_found": len(plugins),
            "plugins": list(plugins.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/categories")
async def get_plugin_categories() -> Dict[str, Any]:
    """Get plugin categories and counts."""
    try:
        plugins = plugin_manager.list_plugins()
        
        categories = {}
        for plugin_type in PluginType:
            type_plugins = [
                name for name, info in plugins.items()
                if info.metadata.plugin_type == plugin_type
            ]
            categories[plugin_type.value] = {
                'count': len(type_plugins),
                'plugins': type_plugins
            }
        
        return {
            "categories": categories,
            "total_plugins": len(plugins)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/execute")
async def execute_tool_plugin(
    plugin_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a tool plugin."""
    try:
        result = await plugin_manager.execute_tool_plugin(plugin_name, parameters)
        
        return {
            "success": True,
            "result": result,
            "plugin_name": plugin_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/agent-task")
async def execute_agent_plugin(
    plugin_name: str,
    task: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute an agent plugin."""
    try:
        result = await plugin_manager.execute_agent_plugin(plugin_name, task)
        
        return {
            "success": True,
            "result": result,
            "plugin_name": plugin_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.post("/{plugin_name}/model-call")
async def call_model_provider(
    plugin_name: str,
    model_name: str,
    prompt: str,
    **kwargs
) -> Dict[str, Any]:
    """Call a model provider plugin."""
    try:
        result = await plugin_manager.call_model_provider(plugin_name, model_name, prompt, **kwargs)
        
        return {
            "success": True,
            "result": result,
            "plugin_name": plugin_name,
            "model_name": model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plugins_router.get("/system/info")
async def get_plugin_system_info() -> Dict[str, Any]:
    """Get plugin system information."""
    try:
        plugins = plugin_manager.list_plugins()
        active_plugins = plugin_manager.get_active_plugins()
        
        # Count by type
        type_counts = {}
        for plugin_type in PluginType:
            type_counts[plugin_type.value] = len(plugin_manager.get_plugins_by_type(plugin_type))
        
        return {
            "total_plugins": len(plugins),
            "active_plugins": len(active_plugins),
            "inactive_plugins": len(plugins) - len(active_plugins),
            "plugins_directory": str(plugin_manager.plugins_dir),
            "supported_types": [t.value for t in PluginType],
            "type_distribution": type_counts,
            "global_stats": plugin_manager.global_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
