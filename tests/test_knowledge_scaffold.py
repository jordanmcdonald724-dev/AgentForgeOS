import tempfile
import unittest
from pathlib import Path

from knowledge import (
    EmbeddingService,
    KnowledgeGraph,
    KnowledgeVectorStore,
    PatternExtractor,
    ProjectGenome,
)


class KnowledgeScaffoldTests(unittest.TestCase):
    def test_embedding_service_returns_vector(self):
        """embed() returns a length-8 stub vector when no corpus exists."""
        service = EmbeddingService()
        vec = service.embed("hello")
        self.assertEqual(len(vec), 8)
        self.assertTrue(all(isinstance(v, float) for v in vec))

    def test_embedding_service_tfidf_after_add(self):
        """After add_text() the TF-IDF vocabulary produces non-empty vectors."""
        service = EmbeddingService()
        service.add_text("d1", "the quick brown fox")
        service.add_text("d2", "lazy dog jumps over fence")
        vec = service.embed("quick fox")
        self.assertGreater(len(vec), 0)
        self.assertTrue(any(v > 0 for v in vec))

    def test_embedding_service_search_relevance(self):
        """Most relevant document ranks first in search results."""
        service = EmbeddingService()
        service.add_text("python", "python programming language")
        service.add_text("cooking", "recipe bake chicken oven")
        results = service.search("python code", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["doc_id"], "python")

    def test_embedding_service_document_count(self):
        service = EmbeddingService()
        service.add_text("a", "alpha")
        service.add_text("b", "beta")
        self.assertEqual(service.document_count(), 2)

    def test_vector_store_adds_and_counts(self):
        store = KnowledgeVectorStore()
        store.add("doc-1", {"title": "First"}, [0.1, 0.2])
        store.add("doc-2", {"title": "Second"}, [0.3, 0.4])
        self.assertEqual(store.count(), 2)
        results = store.query([0.0, 0.0], top_k=1)
        self.assertEqual(len(results), 1)

    def test_vector_store_cosine_similarity(self):
        """query() ranks documents by cosine similarity, not insertion order."""
        store = KnowledgeVectorStore()
        store.add("similar", {"title": "Close"}, [0.9, 0.1])
        store.add("distant", {"title": "Far"}, [0.0, 1.0])
        results = store.query([0.9, 0.1], top_k=1)
        self.assertEqual(results[0]["title"], "Close")

    def test_vector_store_json_persistence(self):
        """KnowledgeVectorStore round-trips data via a JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vs.json"
            s1 = KnowledgeVectorStore(persist_path=path)
            s1.add("x", {"label": "X"}, [1.0, 0.0])
            # Create a second instance loading from the same file
            s2 = KnowledgeVectorStore(persist_path=path)
            self.assertEqual(s2.count(), 1)
            self.assertEqual(s2.query([1.0, 0.0], top_k=1)[0]["label"], "X")

    def test_knowledge_graph_nodes_and_edges(self):
        graph = KnowledgeGraph()
        graph.add_node("a", {"label": "A"})
        graph.add_node("b", {"label": "B"})
        graph.add_edge("a", "b")
        self.assertEqual(graph.node_count(), 2)
        self.assertEqual(graph.edge_count(), 1)
        self.assertEqual(graph.neighbors("a"), ["b"])

    def test_knowledge_graph_json_persistence(self):
        """KnowledgeGraph round-trips nodes and edges via a JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kg.json"
            g1 = KnowledgeGraph(persist_path=path)
            g1.add_node("n1", {"type": "module"})
            g1.add_node("n2", {"type": "agent"})
            g1.add_edge("n1", "n2")
            g2 = KnowledgeGraph(persist_path=path)
            self.assertEqual(g2.node_count(), 2)
            self.assertEqual(g2.edge_count(), 1)
            self.assertIn("n2", g2.neighbors("n1"))

    def test_knowledge_graph_get_node(self):
        graph = KnowledgeGraph()
        graph.add_node("x", {"val": 42})
        self.assertEqual(graph.get_node("x")["val"], 42)
        self.assertEqual(graph.get_node("missing"), {})

    def test_pattern_extractor_records(self):
        extractor = PatternExtractor()
        extractor.record({"pattern": "bugfix"})
        self.assertEqual(len(extractor.list_patterns()), 1)

    def test_project_genome_summary(self):
        genome = ProjectGenome()
        genome.add_trait({"key": "resilience"})
        summary = genome.summarize()
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["traits"][0]["key"], "resilience")


if __name__ == "__main__":
    unittest.main()

