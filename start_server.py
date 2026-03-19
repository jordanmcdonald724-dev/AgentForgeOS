#!/usr/bin/env python3
"""
Simple server startup script for AgentForgeOS V2
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONPATH'] = str(project_root)

if __name__ == "__main__":
    print("🚀 Starting AgentForgeOS V2 Backend Server")
    print("=" * 50)
    
    try:
        # Start the backend server
        import backend.server
        print("✅ Server module imported successfully")
        
        # Check if we can create the app
        app = backend.server.app
        print(f"✅ FastAPI app created with {len(app.routes)} routes")
        
        # Show some key routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        api_routes = [r for r in routes if r.startswith('/api')]
        print(f"🔗 Found {len(api_routes)} API routes")
        
        if api_routes:
            print("📋 Sample routes:")
            for route in api_routes[:10]:
                print(f"   {route}")
        
        print("\n🎉 Server is ready to start!")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs available at http://localhost:8000/docs")
        
        # Start the server
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
        sys.exit(1)
