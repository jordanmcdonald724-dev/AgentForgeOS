#!/usr/bin/env python3
"""
AgentForgeOS V2 Setup Wizard

5-step guided setup process for new users to configure
AgentForgeOS with optimal settings based on their use case.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class SetupConfiguration:
    """Configuration collected during setup wizard."""
    # Step 1: Use Case
    primary_use_case: str
    project_types: List[str]
    experience_level: str
    
    # Step 2: AI Models
    preferred_ai_provider: str
    api_keys: Dict[str, str]
    model_preferences: Dict[str, Any]
    
    # Step 3: Databases
    database_preferences: Dict[str, Any]
    knowledge_graph_enabled: bool
    
    # Step 4: Development Tools
    game_engines: Dict[str, str]
    docker_enabled: bool
    development_tools: List[str]
    
    # Step 5: System Settings
    performance_settings: Dict[str, Any]
    security_settings: Dict[str, Any]
    monitoring_enabled: bool
    
    # Metadata
    setup_completed_at: str
    wizard_version: str = "2.0"


class SetupWizard:
    """
    5-step setup wizard for AgentForgeOS V2 configuration.
    
    Steps:
    1. Use Case Selection
    2. AI Model Configuration  
    3. Database Setup
    4. Development Tools
    5. System Settings
    """
    
    def __init__(self):
        self.config = SetupConfiguration(
            primary_use_case="",
            project_types=[],
            experience_level="",
            preferred_ai_provider="",
            api_keys={},
            model_preferences={},
            database_preferences={},
            knowledge_graph_enabled=True,
            game_engines={},
            docker_enabled=True,
            development_tools=[],
            performance_settings={},
            security_settings={},
            monitoring_enabled=True,
            setup_completed_at=""
        )
        
        self.current_step = 0
        self.total_steps = 5
        
        # Use case definitions
        self.use_cases = {
            'web_development': {
                'name': 'Web Development',
                'description': 'Build modern web applications and APIs',
                'recommended_tools': ['react', 'nodejs', 'docker'],
                'ai_models': ['code_completion', 'code_generation']
            },
            'mobile_development': {
                'name': 'Mobile Development',
                'description': 'Create cross-platform mobile applications',
                'recommended_tools': ['react-native', 'flutter'],
                'ai_models': ['code_generation', 'ui_generation']
            },
            'game_development': {
                'name': 'Game Development',
                'description': 'Develop games with Unity or Unreal Engine',
                'recommended_tools': ['unity', 'unreal', 'blender'],
                'ai_models': ['asset_generation', 'code_generation']
            },
            'machine_learning': {
                'name': 'Machine Learning',
                'description': 'Build ML models and data pipelines',
                'recommended_tools': ['jupyter', 'mlflow', 'docker'],
                'ai_models': ['model_training', 'data_analysis']
            },
            'enterprise_software': {
                'name': 'Enterprise Software',
                'description': 'Build scalable enterprise applications',
                'recommended_tools': ['kubernetes', 'microservices', 'docker'],
                'ai_models': ['code_generation', 'architecture_design']
            },
            'research_prototyping': {
                'name': 'Research & Prototyping',
                'description': 'Rapid prototyping and research projects',
                'recommended_tools': ['jupyter', 'docker', 'git'],
                'ai_models': ['research_analysis', 'code_generation']
            }
        }
        
        print("🚀 Welcome to AgentForgeOS V2 Setup Wizard!")
        print("=" * 60)
    
    async def run_setup(self) -> SetupConfiguration:
        """Run the complete 5-step setup process."""
        try:
            for step in range(self.total_steps):
                self.current_step = step + 1
                await self._run_step(step)
            
            # Complete setup
            self.config.setup_completed_at = datetime.now(timezone.utc).isoformat()
            await self._save_configuration()
            await self._apply_configuration()
            
            print("\n🎉 Setup completed successfully!")
            print(f"Configuration saved to: {self._get_config_file_path()}")
            
            return self.config
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Setup failed: {e}")
            sys.exit(1)
    
    async def _run_step(self, step: int) -> None:
        """Run a specific setup step."""
        print(f"\n📍 Step {step + 1}/{self.total_steps}")
        print("-" * 40)
        
        if step == 0:
            await self._step_1_use_case()
        elif step == 1:
            await self._step_2_ai_models()
        elif step == 2:
            await self._step_3_databases()
        elif step == 3:
            await self._step_4_development_tools()
        elif step == 4:
            await self._step_5_system_settings()
    
    async def _step_1_use_case(self) -> None:
        """Step 1: Use Case Selection"""
        print("🎯 Let's configure your primary use case")
        print("This helps us optimize AgentForgeOS for your specific needs.\n")
        
        # Display use cases
        for i, (key, use_case) in enumerate(self.use_cases.items(), 1):
            print(f"{i}. {use_case['name']}")
            print(f"   {use_case['description']}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect your primary use case (1-{len(self.use_cases)}): ")
                choice_idx = int(choice) - 1
                use_case_keys = list(self.use_cases.keys())
                
                if 0 <= choice_idx < len(use_case_keys):
                    selected_key = use_case_keys[choice_idx]
                    selected_use_case = self.use_cases[selected_key]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a number.")
        
        self.config.primary_use_case = selected_key
        print(f"\n✅ Selected: {selected_use_case['name']}")
        
        # Experience level
        print("\nWhat's your experience level with software development?")
        print("1. Beginner - Just starting out")
        print("2. Intermediate - Some experience")
        print("3. Advanced - Experienced developer")
        print("4. Expert - Senior/Lead level")
        
        while True:
            try:
                exp_choice = input("Select your experience level (1-4): ")
                exp_idx = int(exp_choice) - 1
                exp_levels = ['beginner', 'intermediate', 'advanced', 'expert']
                
                if 0 <= exp_idx < len(exp_levels):
                    self.config.experience_level = exp_levels[exp_idx]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a number.")
        
        print(f"✅ Experience level: {self.config.experience_level}")
        
        # Project types
        print(f"\nBased on {selected_use_case['name']}, what project types will you work on?")
        print("Select all that apply (comma-separated numbers):")
        
        project_types = self._get_project_types_for_use_case(selected_key)
        for i, project_type in enumerate(project_types, 1):
            print(f"{i}. {project_type}")
        
        while True:
            try:
                proj_choices = input("Enter project types: ")
                proj_indices = [int(x.strip()) - 1 for x in proj_choices.split(',')]
                
                if all(0 <= idx < len(project_types) for idx in proj_indices):
                    self.config.project_types = [project_types[idx] for idx in proj_indices]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter comma-separated numbers.")
        
        print(f"✅ Project types: {', '.join(self.config.project_types)}")
    
    async def _step_2_ai_models(self) -> None:
        """Step 2: AI Model Configuration"""
        print("🤖 Configure AI Model Settings")
        print("AgentForgeOS uses AI models to power the 12 specialized agents.\n")
        
        # AI Provider selection
        print("Choose your preferred AI provider:")
        print("1. fal.ai - Fast, affordable, good for code generation")
        print("2. OpenAI - High quality, more expensive")
        print("3. Local models - Privacy-focused, requires hardware")
        print("4. Hybrid - Use multiple providers")
        
        while True:
            try:
                provider_choice = input("Select AI provider (1-4): ")
                provider_idx = int(provider_choice) - 1
                providers = ['fal', 'openai', 'local', 'hybrid']
                
                if 0 <= provider_idx < len(providers):
                    self.config.preferred_ai_provider = providers[provider_idx]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a number.")
        
        print(f"✅ AI Provider: {self.config.preferred_ai_provider}")
        
        # API Keys
        if self.config.preferred_ai_provider in ['fal', 'openai', 'hybrid']:
            print("\n🔑 Enter your API keys (leave empty to skip):")
            
            if self.config.preferred_ai_provider in ['fal', 'hybrid']:
                fal_key = input("fal.ai API key: ").strip()
                if fal_key:
                    self.config.api_keys['fal'] = fal_key
                    print("✅ fal.ai API key saved")
            
            if self.config.preferred_ai_provider in ['openai', 'hybrid']:
                openai_key = input("OpenAI API key: ").strip()
                if openai_key:
                    self.config.api_keys['openai'] = openai_key
                    print("✅ OpenAI API key saved")
        
        # Model preferences
        print("\n⚙️ Model Preferences:")
        
        # Temperature setting
        temp_input = input("Model creativity (0.1-1.0, default 0.7): ").strip()
        try:
            temp = float(temp_input) if temp_input else 0.7
            if 0.1 <= temp <= 1.0:
                self.config.model_preferences['temperature'] = temp
                print(f"✅ Temperature: {temp}")
            else:
                print("⚠️ Using default temperature: 0.7")
                self.config.model_preferences['temperature'] = 0.7
        except ValueError:
            print("⚠️ Using default temperature: 0.7")
            self.config.model_preferences['temperature'] = 0.7
        
        # Max tokens
        tokens_input = input("Max response tokens (1000-8000, default 4096): ").strip()
        try:
            tokens = int(tokens_input) if tokens_input else 4096
            if 1000 <= tokens <= 8000:
                self.config.model_preferences['max_tokens'] = tokens
                print(f"✅ Max tokens: {tokens}")
            else:
                print("⚠️ Using default max tokens: 4096")
                self.config.model_preferences['max_tokens'] = 4096
        except ValueError:
            print("⚠️ Using default max tokens: 4096")
            self.config.model_preferences['max_tokens'] = 4096
    
    async def _step_3_databases(self) -> None:
        """Step 3: Database Setup"""
        print("🗄️ Database Configuration")
        print("AgentForgeOS uses databases for knowledge storage and project data.\n")
        
        # MongoDB setup
        print("MongoDB is used for project data and agent outputs.")
        mongo_choice = input("Use local MongoDB? (Y/n): ").strip().lower()
        
        if mongo_choice in ['', 'y', 'yes']:
            self.config.database_preferences['mongodb'] = {
                'type': 'local',
                'url': 'mongodb://localhost:27017',
                'database': 'agentforge_v2'
            }
            print("✅ Local MongoDB configured")
        else:
            mongo_url = input("MongoDB connection string: ").strip()
            if mongo_url:
                self.config.database_preferences['mongodb'] = {
                    'type': 'remote',
                    'url': mongo_url,
                    'database': 'agentforge_v2'
                }
                print("✅ Remote MongoDB configured")
        
        # Knowledge Graph
        kg_choice = input("Enable advanced knowledge graph? (Y/n): ").strip().lower()
        self.config.knowledge_graph_enabled = kg_choice in ['', 'y', 'yes']
        
        if self.config.knowledge_graph_enabled:
            print("✅ Knowledge graph enabled")
            
            # Neo4j setup
            neo4j_choice = input("Use local Neo4j? (Y/n): ").strip().lower()
            if neo4j_choice in ['', 'y', 'yes']:
                self.config.database_preferences['neo4j'] = {
                    'type': 'local',
                    'uri': 'bolt://localhost:7687',
                    'user': 'neo4j',
                    'password': ''
                }
                print("✅ Local Neo4j configured")
            else:
                neo4j_uri = input("Neo4j URI: ").strip()
                if neo4j_uri:
                    self.config.database_preferences['neo4j'] = {
                        'type': 'remote',
                        'uri': neo4j_uri,
                        'user': input("Neo4j username: ").strip(),
                        'password': input("Neo4j password: ").strip()
                    }
                    print("✅ Remote Neo4j configured")
            
            # Qdrant setup
            qdrant_choice = input("Use local Qdrant? (Y/n): ").strip().lower()
            if qdrant_choice in ['', 'y', 'yes']:
                self.config.database_preferences['qdrant'] = {
                    'type': 'local',
                    'host': 'localhost',
                    'port': '6333'
                }
                print("✅ Local Qdrant configured")
            else:
                qdrant_host = input("Qdrant host: ").strip()
                qdrant_port = input("Qdrant port: ").strip()
                if qdrant_host:
                    self.config.database_preferences['qdrant'] = {
                        'type': 'remote',
                        'host': qdrant_host,
                        'port': qdrant_port or '6333'
                    }
                    print("✅ Remote Qdrant configured")
        else:
            print("⚠️ Knowledge graph disabled - limited functionality")
    
    async def _step_4_development_tools(self) -> None:
        """Step 4: Development Tools"""
        print("🛠️ Development Tools Configuration")
        print("Configure external development tools and engines.\n")
        
        # Game Engines
        if 'game_development' in self.config.project_types:
            print("🎮 Game Engine Setup:")
            
            unity_choice = input("Install Unity support? (Y/n): ").strip().lower()
            if unity_choice in ['', 'y', 'yes']:
                unity_path = input("Unity Editor path (press Enter for default): ").strip()
                if not unity_path:
                    unity_path = "C:/Program Files/Unity/Editor/Unity.exe"
                self.config.game_engines['unity'] = unity_path
                print(f"✅ Unity configured: {unity_path}")
            
            unreal_choice = input("Install Unreal Engine support? (Y/n): ").strip().lower()
            if unreal_choice in ['', 'y', 'yes']:
                unreal_path = input("Unreal Editor path (press Enter for default): ").strip()
                if not unreal_path:
                    unreal_path = "C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/Win64/UnrealEditor.exe"
                self.config.game_engines['unreal'] = unreal_path
                print(f"✅ Unreal Engine configured: {unreal_path}")
        
        # Docker
        docker_choice = input("Enable Docker sandboxing? (Y/n): ").strip().lower()
        self.config.docker_enabled = docker_choice in ['', 'y', 'yes']
        
        if self.config.docker_enabled:
            print("✅ Docker sandboxing enabled")
            
            # Docker settings
            memory_input = input("Docker memory limit (default 2g): ").strip()
            self.config.performance_settings['docker_memory'] = memory_input or '2g'
            
            cpu_input = input("Docker CPU limit (default 1.0): ").strip()
            self.config.performance_settings['docker_cpu'] = cpu_input or '1.0'
        else:
            print("⚠️ Docker disabled - build sandboxing unavailable")
        
        # Additional tools
        print("\n🔧 Additional Development Tools:")
        tools = [
            'git', 'vscode', 'postman', 'docker-desktop', 
            'nodejs', 'python', 'unity-hub', 'unreal-engine'
        ]
        
        print("Select tools you want to integrate (comma-separated numbers):")
        for i, tool in enumerate(tools, 1):
            print(f"{i}. {tool}")
        
        tools_input = input("Enter tools: ").strip()
        if tools_input:
            try:
                tool_indices = [int(x.strip()) - 1 for x in tools_input.split(',')]
                if all(0 <= idx < len(tools) for idx in tool_indices):
                    self.config.development_tools = [tools[idx] for idx in tool_indices]
                    print(f"✅ Tools selected: {', '.join(self.config.development_tools)}")
            except ValueError:
                print("⚠️ Invalid tool selection")
    
    async def _step_5_system_settings(self) -> None:
        """Step 5: System Settings"""
        print("⚙️ System Settings")
        print("Final configuration for performance and security.\n")
        
        # Performance settings
        print("🚀 Performance Settings:")
        
        concurrent_input = input("Max concurrent tasks (1-10, default 5): ").strip()
        try:
            concurrent = int(concurrent_input) if concurrent_input else 5
            if 1 <= concurrent <= 10:
                self.config.performance_settings['max_concurrent_tasks'] = concurrent
                print(f"✅ Max concurrent tasks: {concurrent}")
            else:
                print("⚠️ Using default: 5 concurrent tasks")
                self.config.performance_settings['max_concurrent_tasks'] = 5
        except ValueError:
            print("⚠️ Using default: 5 concurrent tasks")
            self.config.performance_settings['max_concurrent_tasks'] = 5
        
        # Logging level
        print("\n📝 Logging level:")
        print("1. DEBUG - Detailed debugging information")
        print("2. INFO - General information (recommended)")
        print("3. WARNING - Warnings and errors only")
        print("4. ERROR - Errors only")
        
        while True:
            try:
                log_choice = input("Select logging level (1-4): ").strip()
                log_idx = int(log_choice) - 1
                log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
                
                if 0 <= log_idx < len(log_levels):
                    self.config.performance_settings['log_level'] = log_levels[log_idx]
                    print(f"✅ Logging level: {log_levels[log_idx]}")
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a number.")
        
        # Security settings
        print("\n🔒 Security Settings:")
        
        telemetry_choice = input("Enable anonymous telemetry? (y/N): ").strip().lower()
        self.config.security_settings['telemetry_enabled'] = telemetry_choice == 'y'
        
        if self.config.security_settings['telemetry_enabled']:
            print("✅ Telemetry enabled - helps improve AgentForgeOS")
        else:
            print("✅ Telemetry disabled - maximum privacy")
        
        # Monitoring
        monitor_choice = input("Enable performance monitoring? (Y/n): ").strip().lower()
        self.config.monitoring_enabled = monitor_choice in ['', 'y', 'yes']
        
        if self.config.monitoring_enabled:
            print("✅ Performance monitoring enabled")
        else:
            print("⚠️ Performance monitoring disabled")
        
        # Auto-updates
        update_choice = input("Enable automatic updates? (y/N): ").strip().lower()
        self.config.security_settings['auto_updates'] = update_choice == 'y'
        
        if self.config.security_settings['auto_updates']:
            print("✅ Auto-updates enabled")
        else:
            print("✅ Auto-updates disabled - manual updates only")
    
    def _get_project_types_for_use_case(self, use_case: str) -> List[str]:
        """Get project types relevant to a use case."""
        project_type_mapping = {
            'web_development': ['websites', 'web-apps', 'apis', 'e-commerce', 'dashboards'],
            'mobile_development': ['ios-apps', 'android-apps', 'cross-platform', 'mobile-games'],
            'game_development': ['2d-games', '3d-games', 'mobile-games', 'vr-games', 'ar-games'],
            'machine_learning': ['data-analysis', 'ml-models', 'data-pipelines', 'research'],
            'enterprise_software': ['business-apps', 'microservices', 'enterprise-apis', 'internal-tools'],
            'research_prototyping': ['proofs-of-concept', 'experiments', 'prototypes', 'academic-projects']
        }
        
        return project_type_mapping.get(use_case, ['general-projects'])
    
    def _get_config_file_path(self) -> Path:
        """Get the configuration file path."""
        config_dir = project_root / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "setup_config.json"
    
    async def _save_configuration(self) -> None:
        """Save configuration to file."""
        config_path = self._get_config_file_path()
        
        # Convert config to dict and save
        config_dict = asdict(self.config)
        
        # Remove sensitive data for display
        display_config = config_dict.copy()
        if 'api_keys' in display_config:
            display_config['api_keys'] = {k: "***" if v else "" for k, v in display_config['api_keys'].items()}
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"\n📄 Configuration saved to: {config_path}")
    
    async def _apply_configuration(self) -> None:
        """Apply the configuration to the system."""
        print("\n🔧 Applying configuration...")
        
        # Create .env file
        env_path = project_root / ".env"
        env_content = []
        
        # Database settings
        if 'mongodb' in self.config.database_preferences:
            mongo_config = self.config.database_preferences['mongodb']
            env_content.append(f"MONGO_URL={mongo_config['url']}")
            env_content.append(f"DB_NAME={mongo_config['database']}")
        
        # AI settings
        if 'fal' in self.config.api_keys:
            env_content.append(f"FAL_API_KEY={self.config.api_keys['fal']}")
        if 'openai' in self.config.api_keys:
            env_content.append(f"OPENAI_API_KEY={self.config.api_keys['openai']}")
        
        # Neo4j settings
        if self.config.knowledge_graph_enabled and 'neo4j' in self.config.database_preferences:
            neo4j_config = self.config.database_preferences['neo4j']
            env_content.append(f"NEO4J_URI={neo4j_config['uri']}")
            env_content.append(f"NEO4J_USER={neo4j_config['user']}")
            env_content.append(f"NEO4J_PASSWORD={neo4j_config['password']}")
            env_content.append("NEO4J_ENABLED=true")
        
        # Qdrant settings
        if self.config.knowledge_graph_enabled and 'qdrant' in self.config.database_preferences:
            qdrant_config = self.config.database_preferences['qdrant']
            env_content.append(f"QDRANT_HOST={qdrant_config['host']}")
            env_content.append(f"QDRANT_PORT={qdrant_config['port']}")
            env_content.append("QDRANT_ENABLED=true")
        
        # Game engine settings
        if 'unity' in self.config.game_engines:
            env_content.append(f"UNITY_EDITOR_PATH={self.config.game_engines['unity']}")
        if 'unreal' in self.config.game_engines:
            env_content.append(f"UNREAL_EDITOR_PATH={self.config.game_engines['unreal']}")
        
        # Docker settings
        if self.config.docker_enabled:
            env_content.append("DOCKER_ENABLED=true")
            if 'docker_memory' in self.config.performance_settings:
                env_content.append(f"DOCKER_MEMORY_LIMIT={self.config.performance_settings['docker_memory']}")
            if 'docker_cpu' in self.config.performance_settings:
                env_content.append(f"DOCKER_CPU_LIMIT={self.config.performance_settings['docker_cpu']}")
        
        # System settings
        if 'max_concurrent_tasks' in self.config.performance_settings:
            env_content.append(f"MAX_CONCURRENT_TASKS={self.config.performance_settings['max_concurrent_tasks']}")
        if 'log_level' in self.config.performance_settings:
            env_content.append(f"LOG_LEVEL={self.config.performance_settings['log_level']}")
        
        env_content.append(f"TELEMETRY_ENABLED={'true' if self.config.security_settings.get('telemetry_enabled', False) else 'false'}")
        env_content.append(f"AUTO_UPDATES={'true' if self.config.security_settings.get('auto_updates', False) else 'false'}")
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(env_content))
        
        print(f"✅ Environment file created: {env_path}")
        
        # Create directories if needed
        dirs_to_create = [
            "projects",
            "logs", 
            "data/knowledge",
            "data/vectors"
        ]
        
        for dir_path in dirs_to_create:
            full_path = project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directory structure created")


async def main():
    """Main setup wizard entry point."""
    wizard = SetupWizard()
    config = await wizard.run_setup()
    
    # Show summary
    print("\n📋 Setup Summary:")
    print(f"Use Case: {config.primary_use_case}")
    print(f"Experience Level: {config.experience_level}")
    print(f"AI Provider: {config.preferred_ai_provider}")
    print(f"Knowledge Graph: {'Enabled' if config.knowledge_graph_enabled else 'Disabled'}")
    print(f"Docker: {'Enabled' if config.docker_enabled else 'Disabled'}")
    print(f"Monitoring: {'Enabled' if config.monitoring_enabled else 'Disabled'}")
    
    print("\n🚀 AgentForgeOS V2 is ready to use!")
    print("Run 'python engine/server.py' to start the system.")


if __name__ == "__main__":
    asyncio.run(main())
