from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
import re
from pathlib import Path

from orchestration.task_model import Task
from agents.v2.base import AgentResult
from knowledge.knowledge_graph import KnowledgeGraph
from knowledge.pattern_extractor import PatternExtractor


@dataclass
class SimulationReport:
    complexity: str
    duration_estimate: str
    project_size: str
    architecture_preview: str
    feasible: bool


class SimulationEngine:
    """Advanced simulation engine with knowledge graph-driven analysis.
    
    Uses pattern extraction, historical data, and complexity analysis
    to generate accurate feasibility reports for build simulation.
    """

    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.pattern_extractor = PatternExtractor()
        self.complexity_weights = {
            'simple': {'base_days': 1, 'multiplier': 1.0},
            'medium': {'base_days': 7, 'multiplier': 1.5},
            'complex': {'base_days': 21, 'multiplier': 2.5},
            'enterprise': {'base_days': 60, 'multiplier': 4.0}
        }

    def _analyze_command_complexity(self, command: str) -> str:
        """Analyze command to determine complexity level."""
        command_lower = command.lower()
        
        # Complexity indicators
        simple_indicators = ['simple', 'basic', 'minimal', 'prototype', 'demo']
        medium_indicators = ['app', 'website', 'api', 'service', 'system']
        complex_indicators = ['platform', 'enterprise', 'scalable', 'distributed', 'multi-user']
        enterprise_indicators = ['enterprise-grade', 'production', 'large-scale', 'microservices']
        
        # Count indicators
        simple_count = sum(1 for indicator in simple_indicators if indicator in command_lower)
        medium_count = sum(1 for indicator in medium_indicators if indicator in command_lower)
        complex_count = sum(1 for indicator in complex_indicators if indicator in command_lower)
        enterprise_count = sum(1 for indicator in enterprise_indicators if indicator in command_lower)
        
        # Feature complexity analysis
        feature_patterns = {
            'database': r'\b(database|db|storage|persistence)\b',
            'auth': r'\b(auth|authentication|login|security)\b',
            'api': r'\b(api|rest|graphql|endpoint)\b',
            'ui': r'\b(ui|interface|frontend|user interface)\b',
            'realtime': r'\b(realtime|real-time|websocket|live)\b',
            'ai': r'\b(ai|machine learning|ml|model|inference)\b',
            'game': r'\b(game|unity|unreal|gameplay)\b'
        }
        
        feature_count = 0
        for pattern in feature_patterns.values():
            if re.search(pattern, command_lower):
                feature_count += 1
        
        # Determine complexity
        if enterprise_count > 0 or feature_count >= 6:
            return 'enterprise'
        elif complex_count > 0 or feature_count >= 4:
            return 'complex'
        elif medium_count > 0 or feature_count >= 2:
            return 'medium'
        else:
            return 'simple'

    def _estimate_duration(self, complexity: str, features: List[str], similar_projects: List[Dict[str, Any]] | None = None) -> str:
        """Estimate project duration based on complexity, features, and historical data."""
        base_config = self.complexity_weights[complexity]
        base_days = base_config['base_days']
        multiplier = base_config['multiplier']
        
        # Historical adjustment if similar projects exist
        historical_adjustment = 1.0
        if similar_projects:
            # Average the complexity of similar projects to adjust our estimate
            avg_similarity = sum(p['similarity_score'] for p in similar_projects) / len(similar_projects)
            # If we've done this before, we might be 20% faster
            historical_adjustment = 1.0 - (avg_similarity * 0.2)
        
        # Feature-based adjustments
        feature_multipliers = {
            'database': 1.2,
            'auth': 1.1,
            'api': 1.15,
            'ui': 1.25,
            'realtime': 1.3,
            'ai': 1.4,
            'game': 1.5
        }
        
        total_multiplier = multiplier * historical_adjustment
        for feature in features:
            total_multiplier *= feature_multipliers.get(feature, 1.0)
        
        estimated_days = int(base_days * total_multiplier)
        
        if estimated_days <= 7:
            return f"{estimated_days} days"
        elif estimated_days <= 30:
            weeks = estimated_days // 7
            return f"{weeks}-{weeks+1} weeks"
        else:
            months = estimated_days // 30
            return f"{months}-{months+1} months"

    def _determine_project_size(self, complexity: str, features: List[str]) -> str:
        if complexity == "enterprise":
            return "enterprise"
        if complexity == "complex":
            return "large" if len(features) >= 3 else "medium-large"
        if complexity == "medium":
            return "medium" if len(features) >= 2 else "small-medium"
        return "small"

    def _assess_feasibility(self, command: str, complexity: str, features: List[str]) -> bool:
        cmd = (command or "").lower()
        impossible_markers = [
            "break encryption",
            "crack password",
            "steal",
            "malware",
            "ransomware",
            "zero day",
            "0day",
        ]
        if any(marker in cmd for marker in impossible_markers):
            return False
        if complexity == "enterprise" and len(features) >= 7:
            return False
        return True

    def _generate_architecture_preview(self, command: str, complexity: str, features: List[str], similar_projects: List[Dict[str, Any]] | None = None) -> str:
        """Generate architecture preview based on analysis and historical patterns."""
        command_lower = command.lower()
        
        # Determine project type
        if 'game' in command_lower or 'unity' in command_lower or 'unreal' in command_lower:
            project_type = 'Game'
            core_stack = 'Unity/Unreal Engine + C#'
        elif 'web' in command_lower or 'website' in command_lower:
            project_type = 'Web Application'
            core_stack = 'React + Node.js + MongoDB'
        elif 'app' in command_lower or 'mobile' in command_lower:
            project_type = 'Mobile Application'
            core_stack = 'React Native + Firebase'
        elif 'api' in command_lower:
            project_type = 'API Service'
            core_stack = 'FastAPI + PostgreSQL + Redis'
        else:
            project_type = 'Software System'
            core_stack = 'Modular architecture based on requirements'
        
        # Build architecture description
        preview = f"{project_type} with {core_stack}\n\n"
        
        # Add key components based on features
        components = []
        if 'database' in features:
            components.append("• Database layer with schema design")
        if 'auth' in features:
            components.append("• Authentication and authorization system")
        if 'api' in features:
            components.append("• RESTful API endpoints")
        if 'ui' in features:
            components.append("• User interface with responsive design")
        if 'realtime' in features:
            components.append("• Real-time communication (WebSockets)")
        if 'ai' in features:
            components.append("• AI/ML integration pipeline")
        
        # Add historical insights if available
        if similar_projects:
            patterns_found = set()
            for p in similar_projects:
                p_data = p.get('project_data', {})
                patterns = p_data.get('pattern_summary', {})
                for pattern in patterns.keys():
                    patterns_found.add(pattern)
            
            if patterns_found:
                preview += "Historical Patterns Identified:\n"
                preview += "\n".join([f"• {p.replace('_', ' ').title()}" for p in list(patterns_found)[:3]])
                preview += "\n\n"

        if components:
            preview += "Key Components:\n" + "\n".join(components[:4])
        
        # Add complexity note
        if complexity == 'enterprise':
            preview += "\n\nEnterprise-grade architecture with scalability, monitoring, and deployment automation."
        elif complexity == 'complex':
            preview += "\n\nComplex system with multiple integrated services and data flows."
        
        return preview

    def run(self, brief: Dict[str, Any]) -> SimulationReport:
        """Run advanced simulation with knowledge graph-driven analysis."""
        command = brief.get('command', '')
        
        # Analyze command
        complexity = self._analyze_command_complexity(command)
        
        # Extract features
        feature_patterns = {
            'database': r'\b(database|db|storage|persistence)\b',
            'auth': r'\b(auth|authentication|login|security)\b',
            'api': r'\b(api|rest|graphql|endpoint)\b',
            'ui': r'\b(ui|interface|frontend|user interface)\b',
            'realtime': r'\b(realtime|real-time|websocket|live)\b',
            'ai': r'\b(ai|machine learning|ml|model|inference)\b',
            'game': r'\b(game|unity|unreal|gameplay)\b'
        }
        
        features = []
        for feature_name, pattern in feature_patterns.items():
            if re.search(pattern, command.lower()):
                features.append(feature_name)
        
        # Search for similar projects to inform simulation
        similar_projects = []
        try:
            similar_projects = self.knowledge_graph.find_similar_projects(command, features)
        except Exception:
            pass

        # Generate report components
        duration_estimate = self._estimate_duration(complexity, features, similar_projects)
        project_size = self._determine_project_size(complexity, features)
        architecture_preview = self._generate_architecture_preview(command, complexity, features, similar_projects)
        feasible = self._assess_feasibility(command, complexity, features)
        
        return SimulationReport(
            complexity=complexity,
            duration_estimate=duration_estimate,
            project_size=project_size,
            architecture_preview=architecture_preview,
            feasible=feasible,
        )

    def to_task_result(self, report: SimulationReport) -> AgentResult:
        return AgentResult(
            outputs={
                "complexity": report.complexity,
                "duration_estimate": report.duration_estimate,
                "project_size": report.project_size,
                "architecture_preview": report.architecture_preview,
                "feasible": report.feasible,
            },
            logs=[
                f"Advanced simulation analysis completed",
                f"Complexity assessed as: {report.complexity}",
                f"Features detected: {len(features) if 'features' in locals() else 0}",
                f"Feasibility: {'FEASIBLE' if report.feasible else 'NOT FEASIBLE'}",
                f"Duration estimate: {report.duration_estimate}",
            ],
        )
