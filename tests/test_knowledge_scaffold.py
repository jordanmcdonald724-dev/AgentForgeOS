import unittest

from knowledge import (
    EmbeddingService,
    KnowledgeGraph,
    KnowledgeVectorStore,
    PatternExtractor,
    ProjectGenome,
)


class KnowledgeScaffoldTests(unittest.TestCase):
    def test_embedding_service_returns_vector(self):
        service = EmbeddingService()
        vec = service.embed("hello")
        self.assertEqual(len(vec), 8)
        self.assertTrue(all(isinstance(v, float) for v in vec))

    def test_vector_store_adds_and_counts(self):
        store = KnowledgeVectorStore()
        store.add("doc-1", {"title": "First"}, [0.1, 0.2])
        store.add("doc-2", {"title": "Second"}, [0.3, 0.4])
        self.assertEqual(store.count(), 2)
        results = store.query([0.0], top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "First")

    def test_knowledge_graph_nodes_and_edges(self):
        graph = KnowledgeGraph()
        graph.add_node("a", {"label": "A"})
        graph.add_node("b", {"label": "B"})
        graph.add_edge("a", "b")
        self.assertEqual(graph.node_count(), 2)
        self.assertEqual(graph.edge_count(), 1)
        self.assertEqual(graph.neighbors("a"), ["b"])

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
