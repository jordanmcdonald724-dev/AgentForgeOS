"""AI Router that classifies tasks into control categories."""

from typing import Optional


class AIRouter:
    """Classify tasks into predefined categories."""

    KEYWORDS = {
        "bug_fix": ["fix", "bug", "error", "fault"],
        "code_generation": ["generate", "build", "implement", "create"],
        "deployment": ["deploy", "release", "ship"],
        "research": ["research", "investigate", "explore"],
        "refactor": ["refactor", "cleanup", "clean up"],
    }

    def classify(self, task: str) -> Optional[str]:
        """Return the first matching category for the task description."""
        lowered = task.lower()
        for category, keywords in self.KEYWORDS.items():
            if any(word in lowered for word in keywords):
                return category
        return None
