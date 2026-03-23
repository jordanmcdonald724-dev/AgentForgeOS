import unittest
import os


class TasksApiTests(unittest.TestCase):
    def test_tasks_lifecycle_and_limits(self):
        try:
            from fastapi.testclient import TestClient
        except Exception as exc:
            self.skipTest(str(exc))
            return

        from engine.server import create_app

        os.environ["AGENTFORGE_BRIDGE_TOKEN"] = "testtoken"
        with TestClient(create_app()) as client:
            r = client.post("/api/tasks/create", json={"type": "backend", "description": "Create status endpoint", "planned_files": 3, "planned_loc": 120})
            self.assertEqual(r.status_code, 200)
            payload = r.json()
            self.assertTrue(payload["success"])
            task_id = payload["data"]["task"]["task_id"]

            r = client.post("/api/tasks/run", json={"task_id": task_id})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])

            r = client.post("/api/tasks/complete", json={"task_id": task_id, "actual_files": 4, "actual_loc": 120, "validation_passed": True})
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.json()["success"])

            r = client.post("/api/tasks/complete", json={"task_id": task_id, "actual_files": 3, "actual_loc": 121, "validation_passed": True})
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.json()["success"])

            r = client.post("/api/tasks/complete", json={"task_id": task_id, "actual_files": 3, "actual_loc": 120, "validation_passed": True})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            task = r.json()["data"]["task"]
            self.assertTrue(task.get("validation", {}).get("passed"))

            r = client.post("/api/tasks/create", json={"type": "backend", "description": "Too many files", "planned_files": 6})
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.json()["success"])

            r = client.post("/api/tasks/create", json={"type": "backend", "description": "Parent task", "planned_files": 1, "planned_loc": 1})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            parent_id = r.json()["data"]["task"]["task_id"]

            r = client.post("/api/tasks/create", json={"type": "backend", "description": "Child task", "depends_on": [parent_id]})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            child_id = r.json()["data"]["task"]["task_id"]

            r = client.post("/api/tasks/run", json={"task_id": parent_id})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])

            r = client.post("/api/tasks/fail", json={"task_id": parent_id, "error": "boom"})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            self.assertEqual(r.json()["data"]["action"], "retry")

            r = client.post("/api/tasks/run", json={"task_id": parent_id})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])

            r = client.post("/api/tasks/fail", json={"task_id": parent_id, "error": "boom again"})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            self.assertEqual(r.json()["data"]["action"], "escalate")
            self.assertTrue(r.json()["data"]["task"].get("escalated"))

            r = client.get("/api/tasks/status", params={"task_id": child_id})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json()["success"])
            self.assertEqual(r.json()["data"]["task"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
