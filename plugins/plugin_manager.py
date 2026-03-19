"""
Plugin Architecture Framework

Provides a comprehensive plugin system for extending AgentForgeOS V2
with custom agents, tools, and functionality while maintaining
system integrity and security.
"""

from __future__ import annotations

import asyncio
import json
import importlib
import inspect
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib
import zipfile
import tempfile

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Plugin type enumeration."""
    AGENT = "agent"
    TOOL = "tool"
    MODEL_PROVIDER = "model_provider"
    BUILD_STEP = "build_step"
    MONITORING = "monitoring"
    AUTHENTICATION = "authentication"
    STORAGE = "storage"
    NOTIFICATION = "notification"


class PluginStatus(Enum):
    """Plugin status enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    LOADING = "loading"


@dataclass
class PluginMetadata:
    """Plugin metadata structure."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    min_agentforge_version: str
    max_agentforge_version: Optional[str]
    permissions: List[str]
    entry_point: str
    config_schema: Optional[Dict[str, Any]] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PluginInfo:
    """Plugin information structure."""
    metadata: PluginMetadata
    status: PluginStatus
    installed_at: str
    last_updated: str
    error_message: Optional[str] = None
    config: Dict[str, Any] = None
    usage_stats: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.usage_stats is None:
            self.usage_stats = {
                'calls': 0,
                'errors': 0,
                'last_used': None,
                'total_execution_time': 0.0
            }


class BasePlugin(ABC):
    """Base class for all AgentForgeOS plugins."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self._initialized = False
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if not self.get_metadata().config_schema:
            return True
        
        # Simple validation - in production, use jsonschema
        schema = self.get_metadata().config_schema
        for key, value_type in schema.items():
            if key in config and not isinstance(config[key], value_type):
                return False
        
        return True
    
    def record_usage(self, execution_time: float, success: bool = True) -> None:
        """Record plugin usage statistics."""
        plugin_manager.record_plugin_usage(self.get_metadata().name, execution_time, success)


class AgentPlugin(BasePlugin):
    """Base class for agent plugins."""
    
    @abstractmethod
    async def handle_task(self, task: Any) -> Any:
        """Handle a task assigned to this agent."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        pass


class ToolPlugin(BasePlugin):
    """Base class for tool plugins."""
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_tool_schema(self) -> Dict[str, Any]:
        """Get tool parameter schema."""
        pass


class ModelProviderPlugin(BasePlugin):
    """Base class for model provider plugins."""
    
    @abstractmethod
    async def call_model(self, model_name: str, prompt: str, **kwargs) -> str:
        """Call a model with the given prompt."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        pass


class PluginManager:
    """
    Plugin management system for AgentForgeOS V2.
    
    Manages:
    - Plugin discovery and installation
    - Plugin lifecycle (load/unload/enable/disable)
    - Plugin security and permissions
    - Plugin dependencies
    - Plugin configuration
    - Plugin usage tracking
    """
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or Path(__file__).parent
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Plugin registry
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_instances: Dict[str, BasePlugin] = {}
        
        # Security and permissions
        self.allowed_permissions = {
            'file_read', 'file_write', 'network_access', 'system_info',
            'database_access', 'model_access', 'agent_control'
        }
        
        # Plugin statistics
        self.global_stats = {
            'total_plugins': 0,
            'active_plugins': 0,
            'total_calls': 0,
            'total_errors': 0,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"PluginManager initialized with directory: {self.plugins_dir}")
    
    async def initialize(self) -> None:
        """Initialize the plugin manager."""
        # Discover existing plugins
        await self.discover_plugins()
        
        # Load enabled plugins
        await self.load_enabled_plugins()
        
        logger.info(f"PluginManager initialized with {len(self.plugins)} plugins")
    
    async def discover_plugins(self) -> None:
        """Discover plugins in the plugins directory."""
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('.'):
                await self._discover_plugin_in_directory(plugin_dir)
    
    async def _discover_plugin_in_directory(self, plugin_dir: Path) -> None:
        """Discover a plugin in a specific directory."""
        metadata_file = plugin_dir / "plugin.json"
        
        if not metadata_file.exists():
            logger.warning(f"No plugin.json found in {plugin_dir}")
            return
        
        try:
            with open(metadata_file, 'r') as f:
                metadata_dict = json.load(f)
            
            # Convert to PluginMetadata
            metadata = PluginMetadata(
                name=metadata_dict['name'],
                version=metadata_dict['version'],
                description=metadata_dict['description'],
                author=metadata_dict['author'],
                plugin_type=PluginType(metadata_dict['plugin_type']),
                dependencies=metadata_dict.get('dependencies', []),
                min_agentforge_version=metadata_dict['min_agentforge_version'],
                max_agentforge_version=metadata_dict.get('max_agentforge_version'),
                permissions=metadata_dict.get('permissions', []),
                entry_point=metadata_dict['entry_point'],
                config_schema=metadata_dict.get('config_schema'),
                tags=metadata_dict.get('tags', [])
            )
            
            # Check if plugin already exists
            if metadata.name in self.plugins:
                existing = self.plugins[metadata.name]
                existing.metadata = metadata
                existing.last_updated = datetime.now(timezone.utc).isoformat()
            else:
                # Create new plugin info
                plugin_info = PluginInfo(
                    metadata=metadata,
                    status=PluginStatus.INACTIVE,
                    installed_at=datetime.now(timezone.utc).isoformat(),
                    last_updated=datetime.now(timezone.utc).isoformat()
                )
                self.plugins[metadata.name] = plugin_info
            
            logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")
            
        except Exception as e:
            logger.error(f"Failed to discover plugin in {plugin_dir}: {e}")
    
    async def load_enabled_plugins(self) -> None:
        """Load plugins that are marked as enabled."""
        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.status == PluginStatus.ACTIVE:
                await self.load_plugin(plugin_name)
    
    async def install_plugin(self, plugin_package: Union[str, Path]) -> bool:
        """Install a plugin from a package file."""
        try:
            # Handle different package types
            if isinstance(plugin_package, str) and plugin_package.startswith('http'):
                # Download from URL
                return await self._install_plugin_from_url(plugin_package)
            elif Path(plugin_package).suffix == '.zip':
                # Install from ZIP file
                return await self._install_plugin_from_zip(Path(plugin_package))
            elif Path(plugin_package).is_dir():
                # Install from directory
                return await self._install_plugin_from_directory(Path(plugin_package))
            else:
                logger.error(f"Unsupported plugin package: {plugin_package}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install plugin {plugin_package}: {e}")
            return False
    
    async def _install_plugin_from_zip(self, zip_path: Path) -> bool:
        """Install plugin from ZIP file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find plugin directory
            plugin_dir = None
            for item in Path(temp_dir).iterdir():
                if item.is_dir() and (item / "plugin.json").exists():
                    plugin_dir = item
                    break
            
            if not plugin_dir:
                logger.error("No valid plugin found in ZIP file")
                return False
            
            # Copy to plugins directory
            target_dir = self.plugins_dir / plugin_dir.name
            if target_dir.exists():
                logger.error(f"Plugin directory already exists: {plugin_dir.name}")
                return False
            
            import shutil
            shutil.copytree(plugin_dir, target_dir)
            
            # Discover the new plugin
            await self._discover_plugin_in_directory(target_dir)
            
            logger.info(f"Plugin installed from ZIP: {plugin_dir.name}")
            return True
    
    async def _install_plugin_from_directory(self, plugin_dir: Path) -> bool:
        """Install plugin from directory."""
        if not (plugin_dir / "plugin.json").exists():
            logger.error("No plugin.json found in directory")
            return False
        
        # Copy to plugins directory
        target_dir = self.plugins_dir / plugin_dir.name
        if target_dir.exists():
            logger.error(f"Plugin directory already exists: {plugin_dir.name}")
            return False
        
        import shutil
        shutil.copytree(plugin_dir, target_dir)
        
        # Discover the new plugin
        await self._discover_plugin_in_directory(target_dir)
        
        logger.info(f"Plugin installed from directory: {plugin_dir.name}")
        return True
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status == PluginStatus.ACTIVE:
            logger.warning(f"Plugin already active: {plugin_name}")
            return True
        
        try:
            plugin_info.status = PluginStatus.LOADING
            
            # Validate dependencies
            if not await self._validate_dependencies(plugin_info.metadata):
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = "Dependencies not satisfied"
                return False
            
            # Load plugin module
            plugin_instance = await self._load_plugin_instance(plugin_info)
            
            if not plugin_instance:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = "Failed to load plugin instance"
                return False
            
            # Initialize plugin
            if await plugin_instance.initialize():
                self.plugin_instances[plugin_name] = plugin_instance
                plugin_info.status = PluginStatus.ACTIVE
                plugin_info.error_message = None
                
                logger.info(f"Plugin loaded successfully: {plugin_name}")
                return True
            else:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = "Plugin initialization failed"
                return False
                
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    async def _validate_dependencies(self, metadata: PluginMetadata) -> bool:
        """Validate plugin dependencies."""
        for dependency in metadata.dependencies:
            if dependency not in self.plugins:
                logger.error(f"Missing dependency: {dependency}")
                return False
            
            dep_info = self.plugins[dependency]
            if dep_info.status != PluginStatus.ACTIVE:
                logger.error(f"Dependency not active: {dependency}")
                return False
        
        return True
    
    async def _load_plugin_instance(self, plugin_info: PluginInfo) -> Optional[BasePlugin]:
        """Load plugin instance from entry point."""
        try:
            # Get plugin directory
            plugin_dir = self.plugins_dir / plugin_info.metadata.name
            
            # Add plugin directory to Python path
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            # Import module
            module_name, class_name = plugin_info.metadata.entry_point.rsplit('.', 1)
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            
            # Validate plugin class
            if not issubclass(plugin_class, BasePlugin):
                logger.error(f"Plugin class must inherit from BasePlugin: {class_name}")
                return None
            
            # Create instance
            instance = plugin_class(plugin_info.config)
            
            # Validate configuration
            if not await instance.validate_config(plugin_info.config):
                logger.error(f"Invalid plugin configuration: {plugin_info.metadata.name}")
                return None
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load plugin instance: {e}")
            return None
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status != PluginStatus.ACTIVE:
            logger.warning(f"Plugin not active: {plugin_name}")
            return True
        
        try:
            # Get plugin instance
            plugin_instance = self.plugin_instances.get(plugin_name)
            
            if plugin_instance:
                # Cleanup plugin
                await plugin_instance.cleanup()
                del self.plugin_instances[plugin_name]
            
            plugin_info.status = PluginStatus.INACTIVE
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status == PluginStatus.DISABLED:
            plugin_info.status = PluginStatus.INACTIVE
            return await self.load_plugin(plugin_name)
        
        return True
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status == PluginStatus.ACTIVE:
            await self.unload_plugin(plugin_name)
        
        plugin_info.status = PluginStatus.DISABLED
        logger.info(f"Plugin disabled: {plugin_name}")
        return True
    
    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            # Unload plugin if active
            if self.plugins[plugin_name].status == PluginStatus.ACTIVE:
                await self.unload_plugin(plugin_name)
            
            # Remove plugin directory
            plugin_dir = self.plugins_dir / plugin_name
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
            
            # Remove from registry
            del self.plugins[plugin_name]
            
            logger.info(f"Plugin uninstalled: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin instance."""
        return self.plugin_instances.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """Get plugins by type."""
        return [
            name for name, info in self.plugins.items()
            if info.metadata.plugin_type == plugin_type
        ]
    
    def get_active_plugins(self) -> List[str]:
        """Get list of active plugins."""
        return [
            name for name, info in self.plugins.items()
            if info.status == PluginStatus.ACTIVE
        ]
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> Dict[str, PluginInfo]:
        """List all plugins."""
        return self.plugins.copy()
    
    async def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Update plugin configuration."""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        # Validate configuration
        plugin_instance = self.plugin_instances.get(plugin_name)
        if plugin_instance and not await plugin_instance.validate_config(config):
            logger.error(f"Invalid configuration for plugin: {plugin_name}")
            return False
        
        # Update configuration
        plugin_info.config = config
        
        # Save configuration
        await self._save_plugin_config(plugin_name, config)
        
        # Reload plugin if active
        if plugin_info.status == PluginStatus.ACTIVE:
            await self.unload_plugin(plugin_name)
            await self.load_plugin(plugin_name)
        
        logger.info(f"Plugin configuration updated: {plugin_name}")
        return True
    
    async def _save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """Save plugin configuration to file."""
        config_file = self.plugins_dir / plugin_name / "config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")
    
    async def _load_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Load plugin configuration from file."""
        config_file = self.plugins_dir / plugin_name / "config.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load plugin config: {e}")
            return {}
    
    def record_plugin_usage(self, plugin_name: str, execution_time: float, success: bool) -> None:
        """Record plugin usage statistics."""
        if plugin_name not in self.plugins:
            return
        
        plugin_info = self.plugins[plugin_name]
        stats = plugin_info.usage_stats
        
        stats['calls'] += 1
        stats['total_execution_time'] += execution_time
        if not success:
            stats['errors'] += 1
        stats['last_used'] = datetime.now(timezone.utc).isoformat()
        
        # Update global stats
        self.global_stats['total_calls'] += 1
        if not success:
            self.global_stats['total_errors'] += 1
        self.global_stats['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get plugin usage statistics."""
        plugin_stats = {}
        
        for name, info in self.plugins.items():
            plugin_stats[name] = {
                'status': info.status.value,
                'calls': info.usage_stats['calls'],
                'errors': info.usage_stats['errors'],
                'success_rate': (
                    (info.usage_stats['calls'] - info.usage_stats['errors']) / 
                    max(1, info.usage_stats['calls'])
                ),
                'avg_execution_time': (
                    info.usage_stats['total_execution_time'] / 
                    max(1, info.usage_stats['calls'])
                ),
                'last_used': info.usage_stats['last_used']
            }
        
        return {
            'global': self.global_stats,
            'plugins': plugin_stats
        }
    
    async def execute_agent_plugin(self, plugin_name: str, task: Any) -> Any:
        """Execute an agent plugin."""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            raise ValueError(f"Plugin not found or not active: {plugin_name}")
        
        if not isinstance(plugin, AgentPlugin):
            raise ValueError(f"Plugin is not an agent plugin: {plugin_name}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = await plugin.handle_task(task)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            plugin.record_usage(execution_time, success=True)
            return result
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            plugin.record_usage(execution_time, success=False)
            raise
    
    async def execute_tool_plugin(self, plugin_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool plugin."""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            raise ValueError(f"Plugin not found or not active: {plugin_name}")
        
        if not isinstance(plugin, ToolPlugin):
            raise ValueError(f"Plugin is not a tool plugin: {plugin_name}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = await plugin.execute(parameters)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            plugin.record_usage(execution_time, success=True)
            return result
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            plugin.record_usage(execution_time, success=False)
            raise
    
    async def call_model_provider(self, plugin_name: str, model_name: str, prompt: str, **kwargs) -> str:
        """Call a model provider plugin."""
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            raise ValueError(f"Plugin not found or not active: {plugin_name}")
        
        if not isinstance(plugin, ModelProviderPlugin):
            raise ValueError(f"Plugin is not a model provider: {plugin_name}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = await plugin.call_model(model_name, prompt, **kwargs)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            plugin.record_usage(execution_time, success=True)
            return result
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            plugin.record_usage(execution_time, success=False)
            raise


# Global plugin manager instance
plugin_manager = PluginManager()
