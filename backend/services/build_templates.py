from __future__ import annotations

# Predefined agent sequences for common build scenarios.
BUILD_TEMPLATES = {
    "unity_system": [
        "planner_agent",
        "unity_planner_agent",
    ],
    "unreal_system": [
        "planner_agent",
        "unreal_planner_agent",
    ],
    "web_app": [
        "planner_agent",
    ],
    "backend": [
        "planner_agent",
    ],
}
