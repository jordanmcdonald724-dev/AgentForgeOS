from __future__ import annotations

import unittest

from knowledge import V2_KNOWLEDGE_CATEGORIES, KnowledgeGraph
from research.ingestion import IngestedSource, ResearchIngestionService


class TestV2KnowledgeCompliance(unittest.TestCase):
    """Compliance checks for V2 knowledge and research ingestion rules."""

    def test_v2_knowledge_categories_match_build_bible(self) -> None:
        """The V2 knowledge categories list is stable and complete.

        Mirrors the categories enumerated in BUILD_BIBLE_V2.md.
        """

        expected = [
            "architecture_patterns",
            "code_templates",
            "bug_patterns",
            "optimization_patterns",
            "gameplay_systems",
            "research_insights",
            "project_genomes",
        ]
        self.assertEqual(V2_KNOWLEDGE_CATEGORIES, expected)

    def test_research_ingestion_projects_sources_into_all_categories(self) -> None:
        """ResearchIngestionService tags ingested sources with all V2 categories."""
        import asyncio

        graph = KnowledgeGraph()
        service = ResearchIngestionService(graph=graph)
        src = IngestedSource(source_id="s1", kind="github", path="https://example.com/repo")

        info = asyncio.run(service.ingest(src, meta={"label": "sample"}))
        node_id = info["node_id"]
        node = graph.get_node(node_id)

        categories = node.get("categories")
        self.assertIsInstance(categories, list)
        self.assertEqual(sorted(categories), sorted(V2_KNOWLEDGE_CATEGORIES))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
