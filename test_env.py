#!/usr/bin/env python3
"""
Test script to start AgentForgeOS server with environment setup
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set minimal environment variables for testing
os.environ.update({
    'MONGO_URL': 'mongodb://localhost:27017',
    'DB_NAME': 'agentforge_test',
    'CORS_ORIGINS': '*',
    'DOCKER_ENABLED': 'false',
    'TELEMETRY_ENABLED': 'false',
    'LOG_LEVEL': 'INFO'
})

def main():
    print("🚀 Starting AgentForgeOS V2 Server with Test Environment")
    print("=" * 60)
    
    try:
        # Test imports first
        print("📦 Testing imports...")
        import backend.server
        print("✅ Backend server imported successfully")
        
        # Create app
        app = backend.server.app
        print(f"✅ FastAPI app created with {len(app.routes)} routes")
        
        # Show routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"🔗 Found {len(routes)} routes")
        
        # Show some key routes
        api_routes = [r for r in routes if r.startswith('/api')]
        if api_routes:
            print("📋 Sample API routes:")
            for route in api_routes[:10]:
                print(f"   {route}")
        
        print("\n🎉 Server is ready!")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/api/")
        
        # Start server
        import uvicorn
        uvicorn.run(
            backend.server.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
