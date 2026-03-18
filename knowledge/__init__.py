"""Knowledge system scaffold for Phase 7."""

from .knowledge_graph import KnowledgeGraph
from .vector_store import KnowledgeVectorStore
from .embedding_service import EmbeddingService
from .pattern_extractor import PatternExtractor
from .project_genome import ProjectGenome

__all__ = [
    "KnowledgeGraph",
    "KnowledgeVectorStore",
    "EmbeddingService",
    "PatternExtractor",
    "ProjectGenome",
    "V2_KNOWLEDGE_CATEGORIES",
]

# V2 knowledge categories (from BUILD_BIBLE_V2):
# - architecture_patterns
# - code_templates
# - bug_patterns
# - optimization_patterns
# - gameplay_systems
# - research_insights
# - project_genomes

V2_KNOWLEDGE_CATEGORIES = [
    "architecture_patterns",
    "code_templates",
    "bug_patterns",
    "optimization_patterns",
    "gameplay_systems",
    "research_insights",
    "project_genomes",
]
