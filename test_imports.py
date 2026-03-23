#!/usr/bin/env python3
"""
Test script to check if all core modules can be imported successfully
"""

import sys
import traceback
from pathlib import Path

__test__ = False

def test_import(module_name, description):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✅ {description}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {description}: Import failed - {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False


test_import.__test__ = False

def main():
    """Run all import tests"""
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    print("🔍 Testing AgentForgeOS V2 Core Module Imports")
    print("=" * 60)
    
    test_results = []
    
    # Test core engine modules
    test_results.append(test_import("engine.server", "Engine Server"))
    test_results.append(test_import("engine.websocket_manager", "WebSocket Manager"))
    test_results.append(test_import("engine.websocket_routes", "WebSocket Routes"))
    
    # Test agent system
    test_results.append(test_import("agents.v2.base", "V2 Agent Base"))
    test_results.append(test_import("agents.v2.commander", "Commander Agent"))
    test_results.append(test_import("agents.v2.atlas", "Atlas Agent"))
    test_results.append(test_import("agents.v2.forge", "Forge Agent"))
    test_results.append(test_import("agents.v2.ai_engineer", "AI Engineer Agent"))
    
    # Test build system
    test_results.append(test_import("build_system.simulation_engine", "Build Simulation"))
    test_results.append(test_import("build_system.docker_sandbox", "Docker Sandbox"))
    
    # Test knowledge system
    test_results.append(test_import("knowledge.knowledge_graph", "Knowledge Graph"))
    test_results.append(test_import("research.pattern_extractor", "Pattern Extractor"))
    test_results.append(test_import("research.embedding_service", "Embedding Service"))
    
    # Test infrastructure
    test_results.append(test_import("infrastructure.model_router", "Model Router"))
    
    # Test bridge system
    test_results.append(test_import("bridge.bridge_server", "Bridge Server"))
    
    # Test monitoring
    test_results.append(test_import("monitoring.performance_monitor", "Performance Monitor"))
    
    # Test plugin system
    test_results.append(test_import("plugins.plugin_manager", "Plugin Manager"))
    
    # Test backend routes
    test_results.append(test_import("backend.routes.sandbox", "Sandbox Routes"))
    test_results.append(test_import("backend.routes.monitoring", "Monitoring Routes"))
    test_results.append(test_import("backend.routes.plugins", "Plugin Routes"))
    
    print("\n" + "=" * 60)
    print(f"📊 Import Test Results:")
    print(f"✅ Successful: {sum(test_results)}/{len(test_results)}")
    print(f"❌ Failed: {len(test_results) - sum(test_results)}/{len(test_results)}")
    
    if all(test_results):
        print("🎉 All core modules imported successfully!")
        return True
    else:
        print("⚠️  Some modules failed to import - check dependencies")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
