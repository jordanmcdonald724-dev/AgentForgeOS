"""Tests for module backend routes and engine route registration."""

import asyncio
import importlib.util
import os
import unittest
from types import ModuleType
from typing import cast


def _load_module(module_name: str, file_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Failed to load module spec for {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    loader = cast(object, spec.loader)
    exec_module = getattr(loader, "exec_module", None)
    if exec_module is None:
        raise AssertionError(f"Module loader missing exec_module for {module_name} from {file_path}")
    exec_module(mod)
    return mod


class ModuleBackendRouteTests(unittest.TestCase):
    """Each app module should have a backend/routes.py with a FastAPI router."""

    MODULES = ["studio", "builds", "research", "assets", "deployment"]

    def test_routes_files_exist(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for module_name in self.MODULES:
            path = os.path.join(repo_root, "apps", module_name, "backend", "routes.py")
            self.assertTrue(
                os.path.isfile(path),
                f"apps/{module_name}/backend/routes.py missing",
            )

    def test_routes_export_router(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for module_name in self.MODULES:
            path = os.path.join(repo_root, "apps", module_name, "backend", "routes.py")
            mod = _load_module(f"apps.{module_name}.backend.routes", path)
            self.assertTrue(
                hasattr(mod, "router"),
                f"apps/{module_name}/backend/routes.py has no 'router' attribute",
            )

    def test_studio_status_endpoint(self):
        from fastapi.testclient import TestClient

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "studio", "backend", "routes.py")
        mod = _load_module("apps.studio.backend.routes", path)

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            resp = client.get("/studio/status")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["data"]["module"], "studio")

    def test_studio_workspace_default_path(self):
        """GET /studio/workspace (no path param) returns success response."""
        from fastapi.testclient import TestClient

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "studio", "backend", "routes.py")
        mod = _load_module("apps.studio.backend.routes_default_path_test", path)

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            resp = client.get("/studio/workspace")
            # Returns either success (bridge root exists) or a structured error — never a 500.
            self.assertIn(resp.status_code, (200,))
            data = resp.json()
            self.assertIn("success", data)

    def test_studio_workspace_with_path_param(self):
        """GET /studio/workspace?path=. is accepted (path query param wired)."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "studio", "backend", "routes.py")
        mod = _load_module("apps.studio.backend.routes_explicit_path_test", path)

        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            resp = client.get("/studio/workspace?path=.")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("success", data)

    def test_builds_trigger_and_list(self):
        from fastapi.testclient import TestClient

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "builds", "backend", "routes.py")
        mod = _load_module("apps.builds.backend.routes", path)

        # Reset internal state for isolation
        mod._build_log.clear()

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            # Trigger a build
            resp = client.post("/builds/trigger", json={"project": "test-project"})
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.json()["success"])

            # List runs
            resp = client.get("/builds/runs")
            self.assertEqual(resp.status_code, 200)
            runs = resp.json()["data"]
            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0]["project"], "test-project")

    def test_assets_generate_endpoint(self):
        from fastapi.testclient import TestClient

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "assets", "backend", "routes.py")
        mod = _load_module("apps.assets.backend.routes", path)

        mod._asset_registry.clear()

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            resp = client.post("/assets/generate", json={"type": "image", "prompt": "test"})
            self.assertEqual(resp.status_code, 200)
            payload = resp.json()
            self.assertTrue(payload["success"])
            self.assertIn("id", payload["data"])
            self.assertIn("path", payload["data"])

    def test_deployment_launch_endpoint(self):
        from fastapi.testclient import TestClient

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(repo_root, "apps", "deployment", "backend", "routes.py")
        mod = _load_module("apps.deployment.backend.routes", path)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(mod.router)
        with TestClient(app) as client:
            resp = client.post("/deployment/launch", json={"engine": "web"})
            self.assertEqual(resp.status_code, 200)
            payload = resp.json()
            self.assertTrue(payload["success"])
            self.assertEqual(payload["data"]["engine"], "web")


class CollectModuleRoutersTests(unittest.TestCase):
    """collect_module_routers() should return a list of FastAPI routers."""

    def test_returns_list(self):
        from engine.module_loader import collect_module_routers
        from fastapi.routing import APIRouter

        routers = collect_module_routers()
        self.assertIsInstance(routers, list)
        for r in routers:
            self.assertIsInstance(r, APIRouter)

    def test_returns_all_five_module_routers(self):
        from engine.module_loader import collect_module_routers

        routers = collect_module_routers()
        self.assertGreaterEqual(
            len(routers), 5, "Expected at least 5 module routers (one per app)"
        )


class EngineAgentRouteTests(unittest.TestCase):
    """The /api/agent/run route must be registered on the engine app."""

    def test_agent_route_registered(self):
        from fastapi.routing import APIRoute
        from engine.server import create_app

        app = create_app()
        paths = [r.path for r in app.router.routes if isinstance(r, APIRoute)]
        self.assertIn("/api/agent/run", paths)


class MongoMemoryManagerTests(unittest.TestCase):
    """MongoMemoryManager works in-memory when no DB is provided."""

    def test_save_and_load_without_db(self):
        from services.mongo_memory import MongoMemoryManager

        mgr = MongoMemoryManager(db=None, session_id="sess-1")
        asyncio.run(mgr.save_memory({"role": "user", "content": "hi"}))
        asyncio.run(mgr.save_memory({"role": "assistant", "content": "hello"}))
        history = asyncio.run(mgr.load_memories())
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")

    def test_clear_without_db(self):
        from services.mongo_memory import MongoMemoryManager

        mgr = MongoMemoryManager(db=None, session_id="sess-2")
        asyncio.run(mgr.save_memory({"role": "user", "content": "test"}))
        asyncio.run(mgr.clear())
        history = asyncio.run(mgr.load_memories())
        self.assertEqual(len(history), 0)

    def test_session_isolation(self):
        from services.mongo_memory import MongoMemoryManager

        mgr1 = MongoMemoryManager(db=None, session_id="a")
        mgr2 = MongoMemoryManager(db=None, session_id="b")
        asyncio.run(mgr1.save_memory({"role": "user", "content": "for a"}))
        asyncio.run(mgr2.save_memory({"role": "user", "content": "for b"}))

        hist1 = asyncio.run(mgr1.load_memories())
        hist2 = asyncio.run(mgr2.load_memories())
        self.assertEqual(len(hist1), 1)
        self.assertEqual(hist1[0]["content"], "for a")
        self.assertEqual(len(hist2), 1)
        self.assertEqual(hist2[0]["content"], "for b")

    def test_limit_parameter(self):
        from services.mongo_memory import MongoMemoryManager

        mgr = MongoMemoryManager(db=None, session_id="sess-3")
        for i in range(5):
            asyncio.run(mgr.save_memory({"role": "user", "content": str(i)}))
        history = asyncio.run(mgr.load_memories(limit=3))
        self.assertEqual(len(history), 3)

    def test_exported_from_services_package(self):
        from services import MongoMemoryManager

        self.assertIsNotNone(MongoMemoryManager)


if __name__ == "__main__":
    unittest.main()
