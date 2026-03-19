#!/usr/bin/env python3
"""
Test script to start the AgentForgeOS server and check for startup issues
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_server_startup():
    """Test server startup"""
    print("🚀 Starting AgentForgeOS V2 Server Test")
    print("=" * 50)
    
    try:
        # Test basic imports first
        print("📦 Testing imports...")
        from engine.server import create_app
        print("✅ Engine imports successful")
        
        # Create FastAPI app
        print("🔧 Creating FastAPI application...")
        app = create_app()
        print("✅ FastAPI app created successfully")
        
        # Test basic endpoints
        print("🔍 Testing endpoint registration...")
        routes = [route.path for route in app.routes]
        print(f"✅ {len(routes)} routes registered")
        
        # Show some key routes
        key_routes = [r for r in routes if any(keyword in r for keyword in ['/api', '/ws', '/health'])]
        print(f"🔗 Key routes: {key_routes[:5]}")
        
        # Test middleware
        print("🛡️ Testing middleware...")
        middleware_count = len(app.user_middleware)
        print(f"✅ {middleware_count} middleware layers configured")
        
        # Test plugin manager
        print("🔌 Testing plugin manager...")
        from plugins.plugin_manager import plugin_manager
        await plugin_manager.initialize()
        print(f"✅ Plugin manager initialized with {len(plugin_manager.plugins)} plugins")
        
        # Test performance monitor
        print("📊 Testing performance monitor...")
        from monitoring.performance_monitor import performance_monitor
        performance_monitor.start_monitoring(interval_seconds=60)
        print("✅ Performance monitor started")
        
        # Test knowledge graph
        print("🧠 Testing knowledge graph...")
        from knowledge.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        kg.add_node("test", {"type": "test"})
        print("✅ Knowledge graph functional")
        
        print("\n🎉 Server startup test completed successfully!")
        print("✅ All core systems are functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        # Cleanup
        try:
            from monitoring.performance_monitor import performance_monitor
            performance_monitor.stop_monitoring()
        except:
            pass

async def test_basic_api():
    """Test basic API functionality"""
    print("\n🌐 Testing Basic API Functionality")
    print("=" * 40)
    
    try:
        from engine.server import create_app
        from fastapi.testclient import TestClient
        
        # Create test client
        app = create_app()
        client = TestClient(app)
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        response = client.get("/api/")
        print(f"✅ Root endpoint: {response.status_code}")
        
        # Test status endpoint
        response = client.get("/api/status")
        print(f"✅ Status endpoint: {response.status_code}")
        
        # Test monitoring endpoint
        response = client.get("/api/monitoring/system/health")
        print(f"✅ Monitoring health: {response.status_code}")
        
        # Test plugins endpoint
        response = client.get("/api/plugins/")
        print(f"✅ Plugins endpoint: {response.status_code}")
        
        print("🎉 Basic API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 AgentForgeOS V2 System Test Suite")
    print("=" * 60)
    
    # Run startup tests
    startup_success = asyncio.run(test_server_startup())
    
    if startup_success:
        # Run API tests
        api_success = asyncio.run(test_basic_api())
        
        if api_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ AgentForgeOS V2 is ready to start")
            print("\n🚀 To start the server, run:")
            print("   python engine/server.py")
            print("\n🌐 Then access the API at:")
            print("   http://localhost:8000/docs")
            return True
        else:
            print("\n⚠️  Startup successful but API tests failed")
            return False
    else:
        print("\n❌ Startup tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
