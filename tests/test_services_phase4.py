import unittest

from services.autopsy_service import AutopsyService
from services.embedding_service import EmbeddingService
from services.knowledge_graph import KnowledgeGraph
from services.pattern_extractor import PatternExtractor
from services.project_genome_service import ProjectGenomeService


class KnowledgeGraphTests(unittest.TestCase):
    def test_entities_and_relations_round_trip(self) -> None:
        graph = KnowledgeGraph()
        graph.add_entity("bug-123", {"type": "issue"})
        graph.add_entity("fix-1", {"type": "patch"})
        graph.add_relation("bug-123", "resolved_by", "fix-1", metadata={"confidence": 0.8})

        self.assertEqual(graph.get_entity("bug-123")["type"], "issue")
        relations = graph.relations_for("fix-1")
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["predicate"], "resolved_by")
        self.assertEqual(relations[0]["metadata"]["confidence"], 0.8)


class EmbeddingServiceTests(unittest.TestCase):
    def test_search_returns_inserted_document(self) -> None:
        service = EmbeddingService()
        service.add_text("doc-1", "Hello world", metadata={"tag": "greeting"})
        results = service.search("Hello")

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["tag"], "greeting")
        self.assertEqual(results[0]["text"], "Hello world")


class PatternExtractorTests(unittest.TestCase):
    def test_extracts_pattern_counts(self) -> None:
        extractor = PatternExtractor()
        frequencies = extractor.extract_patterns("Code code test!")
        self.assertEqual(frequencies["code"], 2)
        self.assertEqual(extractor.top_patterns("one two two three three three", limit=2), ["three", "two"])


class ProjectGenomeServiceTests(unittest.TestCase):
    def test_records_project_genome(self) -> None:
        service = ProjectGenomeService()
        genome = service.record_project("demo", "API client uses retries", artifacts=["diagram"])

        self.assertEqual(genome["artifacts"], ["diagram"])
        self.assertIn("api", genome["patterns"])
        self.assertEqual(service.list_projects(), ["demo"])
        self.assertIsNotNone(service.get_genome("demo"))


class AutopsyServiceTests(unittest.TestCase):
    def test_records_failure_with_patterns(self) -> None:
        service = AutopsyService()
        report = service.record_failure(
            "demo",
            "Build failed due to missing dependency",
            root_cause="missing library",
            remediation="install dependency",
        )

        self.assertEqual(report["project"], "demo")
        self.assertIn("missing", report["patterns"])
        self.assertEqual(service.history(limit=1)[0]["root_cause"], "missing library")


if __name__ == "__main__":
    unittest.main()
