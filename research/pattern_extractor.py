"""
Advanced Pattern Extractor for Research System

Implements sophisticated pattern recognition and extraction from
projects, code repositories, and research sources to enhance
the AgentForgeOS knowledge graph with actionable insights.
"""

from __future__ import annotations

import ast
import re
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from knowledge.knowledge_graph import KnowledgeGraph
from knowledge.embedding_service import EmbeddingService


@dataclass
class CodePattern:
    """Represents a detected code pattern"""
    pattern_type: str
    pattern_name: str
    description: str
    code_snippet: str
    language: str
    complexity_score: float
    frequency: int
    contexts: List[str]
    tags: Set[str]


@dataclass
class ArchitecturePattern:
    """Represents an architectural pattern"""
    pattern_name: str
    category: str
    description: str
    components: List[str]
    relationships: List[Tuple[str, str]]
    benefits: List[str]
    use_cases: List[str]
    complexity: str
    examples: List[str]


@dataclass
class TechnologyPattern:
    """Represents a technology stack pattern"""
    tech_stack: List[str]
    compatibility_score: float
    use_case: str
    pros: List[str]
    cons: List[str]
    alternatives: List[str]
    learning_curve: str


@dataclass
class PerformancePattern:
    """Represents a performance optimization pattern"""
    optimization_type: str
    problem_solved: str
    solution: str
    impact_level: str
    implementation_complexity: str
    code_example: str
    benchmarks: Dict[str, float]


class AdvancedPatternExtractor:
    """
    Advanced pattern extraction system for AgentForgeOS research.
    
    Extracts and analyzes patterns from:
    - Code repositories and files
    - Project architectures
    - Technology stacks
    - Performance optimizations
    - Best practices and anti-patterns
    """
    
    def __init__(self, knowledge_graph: Optional[KnowledgeGraph] = None):
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        self.embedding_service = EmbeddingService()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Pattern recognition rules
        self.code_patterns = self._load_code_patterns()
        self.architecture_patterns = self._load_architecture_patterns()
        self.technology_patterns = self._load_technology_patterns()
        
        # Pattern statistics
        self.extraction_stats = {
            'files_processed': 0,
            'patterns_found': 0,
            'patterns_by_type': defaultdict(int),
            'last_extraction': None
        }
    
    def _load_code_patterns(self) -> Dict[str, Dict]:
        """Load code pattern recognition rules."""
        return {
            'design_patterns': {
                'singleton': {
                    'indicators': [r'class\s+\w+\s*:', r'instance\s*=\s*None', r'def\s+__new__'],
                    'description': 'Singleton pattern implementation',
                    'complexity': 0.3
                },
                'factory': {
                    'indicators': [r'def\s+create_\w+', r'class\s+\w*Factory', r'return\s+\w+\('],
                    'description': 'Factory pattern implementation',
                    'complexity': 0.4
                },
                'observer': {
                    'indicators': [r'def\s+notify', r'def\s+attach', r'def\s+detach'],
                    'description': 'Observer pattern implementation',
                    'complexity': 0.5
                },
                'decorator': {
                    'indicators': [r'@\w+', r'def\s+wrapper', r'def\s+__call__'],
                    'description': 'Decorator pattern implementation',
                    'complexity': 0.4
                }
            },
            'architectural_patterns': {
                'mvc': {
                    'indicators': [r'class.*Controller', r'class.*View', r'class.*Model'],
                    'description': 'Model-View-Controller architecture',
                    'complexity': 0.6
                },
                'microservices': {
                    'indicators': [r'app\.route', r'flask', r'fastapi', r'redis'],
                    'description': 'Microservices architecture',
                    'complexity': 0.8
                },
                'repository': {
                    'indicators': [r'class.*Repository', r'def\s+find', r'def\s+save'],
                    'description': 'Repository pattern',
                    'complexity': 0.4
                }
            },
            'async_patterns': {
                'async_await': {
                    'indicators': [r'async\s+def', r'await\s+', r'asyncio'],
                    'description': 'Async/await pattern',
                    'complexity': 0.6
                },
                'producer_consumer': {
                    'indicators': [r'queue\.put', r'queue\.get', r'threading'],
                    'description': 'Producer-consumer pattern',
                    'complexity': 0.7
                }
            }
        }
    
    def _load_architecture_patterns(self) -> Dict[str, Dict]:
        """Load architectural pattern definitions."""
        return {
            'layered_architecture': {
                'description': 'Traditional layered architecture with clear separation',
                'components': ['presentation', 'business', 'data'],
                'complexity': 'medium'
            },
            'hexagonal_architecture': {
                'description': 'Hexagonal (ports and adapters) architecture',
                'components': ['domain', 'application', 'infrastructure'],
                'complexity': 'high'
            },
            'event_driven': {
                'description': 'Event-driven architecture with loose coupling',
                'components': ['events', 'handlers', 'dispatchers'],
                'complexity': 'high'
            },
            'serverless': {
                'description': 'Serverless architecture with cloud functions',
                'components': ['functions', 'triggers', 'bindings'],
                'complexity': 'medium'
            }
        }
    
    def _load_technology_patterns(self) -> Dict[str, Dict]:
        """Load technology stack patterns."""
        return {
            'web_full_stack': {
                'frontend': ['react', 'vue', 'angular'],
                'backend': ['nodejs', 'python', 'java'],
                'database': ['postgresql', 'mongodb', 'mysql'],
                'deployment': ['docker', 'kubernetes', 'aws']
            },
            'mobile_app': {
                'frameworks': ['react-native', 'flutter', 'swift', 'kotlin'],
                'backend': ['firebase', 'aws', 'azure'],
                'database': ['sqlite', 'firebase', 'realm']
            },
            'machine_learning': {
                'libraries': ['tensorflow', 'pytorch', 'scikit-learn'],
                'frameworks': ['jupyter', 'mlflow', 'kubeflow'],
                'deployment': ['docker', 'sagemaker', 'azure-ml']
            },
            'game_development': {
                'engines': ['unity', 'unreal', 'godot'],
                'languages': ['csharp', 'cpp', 'blueprint'],
                'tools': ['blender', 'substance', 'photoshop']
            }
        }
    
    async def extract_patterns_from_project(self, project_path: str) -> Dict[str, List]:
        """
        Extract all patterns from a project directory.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dictionary of patterns by type
        """
        project_path = Path(project_path)
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        results = {
            'code_patterns': [],
            'architecture_patterns': [],
            'technology_patterns': [],
            'performance_patterns': [],
            'anti_patterns': []
        }
        
        # Process all code files
        code_files = self._find_code_files(project_path)
        
        # Use parallel processing for large projects
        if len(code_files) > 10:
            tasks = []
            for file_chunk in self._chunk_list(code_files, 5):
                task = asyncio.create_task(
                    self._process_file_chunk(file_chunk, project_path)
                )
                tasks.append(task)
            
            chunk_results = await asyncio.gather(*tasks)
            for chunk_result in chunk_results:
                for pattern_type, patterns in chunk_result.items():
                    results[pattern_type].extend(patterns)
        else:
            # Process sequentially for small projects
            for file_path in code_files:
                file_patterns = await self._extract_patterns_from_file(file_path, project_path)
                for pattern_type, patterns in file_patterns.items():
                    results[pattern_type].extend(patterns)
        
        # Extract project-level patterns
        arch_patterns = await self._extract_architecture_patterns(project_path)
        results['architecture_patterns'].extend(arch_patterns)
        
        tech_patterns = await self._extract_technology_patterns(project_path)
        results['technology_patterns'].extend(tech_patterns)
        
        # Update statistics
        self.extraction_stats['files_processed'] = len(code_files)
        self.extraction_stats['patterns_found'] = sum(len(patterns) for patterns in results.values())
        self.extraction_stats['last_extraction'] = datetime.now(timezone.utc).isoformat()
        
        # Store patterns in knowledge graph
        await self._store_patterns_in_knowledge_graph(results, str(project_path))
        
        return results
    
    def _find_code_files(self, project_path: Path) -> List[Path]:
        """Find all code files in the project."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt'
        }
        
        code_files = []
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip common directories to ignore
                if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__', 'venv']):
                    continue
                code_files.append(file_path)
        
        return code_files
    
    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """Split list into chunks for parallel processing."""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    async def _process_file_chunk(self, file_chunk: List[Path], project_path: Path) -> Dict[str, List]:
        """Process a chunk of files in parallel."""
        results = {
            'code_patterns': [],
            'architecture_patterns': [],
            'technology_patterns': [],
            'performance_patterns': [],
            'anti_patterns': []
        }
        
        loop = asyncio.get_event_loop()
        tasks = []
        
        for file_path in file_chunk:
            task = loop.run_in_executor(
                self.executor,
                self._extract_patterns_from_file_sync,
                file_path,
                project_path
            )
            tasks.append(task)
        
        file_results = await asyncio.gather(*tasks)
        
        for file_result in file_results:
            for pattern_type, patterns in file_result.items():
                results[pattern_type].extend(patterns)
        
        return results
    
    def _extract_patterns_from_file_sync(self, file_path: Path, project_path: Path) -> Dict[str, List]:
        """Synchronous pattern extraction from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._analyze_code_content(content, file_path, project_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return {key: [] for key in ['code_patterns', 'architecture_patterns', 'technology_patterns', 'performance_patterns', 'anti_patterns']}
    
    async def _extract_patterns_from_file(self, file_path: Path, project_path: Path) -> Dict[str, List]:
        """Extract patterns from a single file."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._extract_patterns_from_file_sync,
            file_path,
            project_path
        )
    
    def _analyze_code_content(self, content: str, file_path: Path, project_path: Path) -> Dict[str, List]:
        """Analyze code content for patterns."""
        results = {
            'code_patterns': [],
            'architecture_patterns': [],
            'technology_patterns': [],
            'performance_patterns': [],
            'anti_patterns': []
        }
        
        language = self._detect_language(file_path)
        
        # Extract code patterns
        code_patterns = self._extract_code_patterns(content, language, file_path)
        results['code_patterns'] = code_patterns
        
        # Extract performance patterns
        perf_patterns = self._extract_performance_patterns(content, language, file_path)
        results['performance_patterns'] = perf_patterns
        
        # Extract anti-patterns
        anti_patterns = self._extract_anti_patterns(content, language, file_path)
        results['anti_patterns'] = anti_patterns
        
        return results
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        return extension_map.get(file_path.suffix, 'unknown')
    
    def _extract_code_patterns(self, content: str, language: str, file_path: Path) -> List[CodePattern]:
        """Extract design and implementation patterns."""
        patterns = []
        
        for pattern_category, pattern_rules in self.code_patterns.items():
            for pattern_name, rule in pattern_rules.items():
                matches = 0
                contexts = []
                
                for indicator in rule['indicators']:
                    found_matches = re.findall(indicator, content, re.IGNORECASE)
                    matches += len(found_matches)
                    
                    # Extract context around matches
                    for match in found_matches:
                        context = self._extract_context(content, match, 100)
                        contexts.append(context)
                
                if matches > 0:
                    pattern = CodePattern(
                        pattern_type=pattern_category,
                        pattern_name=pattern_name,
                        description=rule['description'],
                        code_snippet=self._extract_code_snippet(content, pattern_name),
                        language=language,
                        complexity_score=rule['complexity'],
                        frequency=matches,
                        contexts=contexts[:3],  # Limit contexts
                        tags=self._generate_tags(pattern_name, language)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _extract_performance_patterns(self, content: str, language: str, file_path: Path) -> List[PerformancePattern]:
        """Extract performance optimization patterns."""
        patterns = []
        
        # Common performance patterns
        perf_indicators = {
            'caching': {
                'indicators': [r'cache', r'memoize', r'remember'],
                'description': 'Caching implementation',
                'impact': 'medium'
            },
            'lazy_loading': {
                'indicators': [r'lazy', r'deferred', r'load.*on.*demand'],
                'description': 'Lazy loading pattern',
                'impact': 'medium'
            },
            'batching': {
                'indicators': [r'batch', r'bulk', r'chunk'],
                'description': 'Batch processing',
                'impact': 'high'
            },
            'connection_pooling': {
                'indicators': [r'pool', r'connection.*pool'],
                'description': 'Database connection pooling',
                'impact': 'high'
            }
        }
        
        for pattern_name, rule in perf_indicators.items():
            matches = 0
            for indicator in rule['indicators']:
                matches += len(re.findall(indicator, content, re.IGNORECASE))
            
            if matches > 0:
                pattern = PerformancePattern(
                    optimization_type=pattern_name,
                    problem_solved=f"Performance issue addressed by {rule['description']}",
                    solution=self._extract_code_snippet(content, pattern_name),
                    impact_level=rule['impact'],
                    implementation_complexity='medium',
                    code_example=self._extract_code_snippet(content, pattern_name),
                    benchmarks={'improvement': 0.0}  # Would be calculated from actual metrics
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_anti_patterns(self, content: str, language: str, file_path: Path) -> List[Dict]:
        """Extract anti-patterns and code smells."""
        anti_patterns = []
        
        # Common anti-patterns
        anti_indicators = {
            'god_object': {
                'indicators': [r'class.*\{.*\n.*\n.*\n.*\n.*\}', r'def.*\n.*def.*\n.*def.*\n.*def.*'],
                'description': 'God object - too many responsibilities'
            },
            'long_method': {
                'indicators': [r'def\s+\w+.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n'],
                'description': 'Long method - too complex'
            },
            'magic_numbers': {
                'indicators': [r'\b\d{2,}\b'],
                'description': 'Magic numbers - unnamed constants'
            },
            'deep_nesting': {
                'indicators': [r'if.*\n.*if.*\n.*if'],
                'description': 'Deep nesting - complex control flow'
            }
        }
        
        for anti_name, rule in anti_indicators.items():
            matches = 0
            for indicator in rule['indicators']:
                matches += len(re.findall(indicator, content, re.IGNORECASE))
            
            if matches > 0:
                anti_patterns.append({
                    'anti_pattern': anti_name,
                    'description': rule['description'],
                    'frequency': matches,
                    'severity': 'medium' if matches < 3 else 'high',
                    'file': str(file_path),
                    'language': language
                })
        
        return anti_patterns
    
    def _extract_context(self, content: str, match: str, context_size: int) -> str:
        """Extract context around a pattern match."""
        index = content.find(match)
        if index == -1:
            return match
        
        start = max(0, index - context_size)
        end = min(len(content), index + len(match) + context_size)
        
        return content[start:end].strip()
    
    def _extract_code_snippet(self, content: str, pattern_name: str) -> str:
        """Extract a representative code snippet for the pattern."""
        lines = content.split('\n')
        
        # Find lines containing pattern indicators
        pattern_lines = []
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in pattern_name.split('_')):
                # Include some context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                snippet = '\n'.join(lines[start:end])
                pattern_lines.append(snippet)
        
        # Return the most representative snippet
        if pattern_lines:
            return max(pattern_lines, key=len)
        
        return "No specific code snippet found"
    
    def _generate_tags(self, pattern_name: str, language: str) -> Set[str]:
        """Generate tags for a pattern."""
        tags = {language, pattern_name}
        
        # Add category tags
        if 'singleton' in pattern_name:
            tags.add('creational')
        elif 'factory' in pattern_name:
            tags.add('creational')
        elif 'observer' in pattern_name:
            tags.add('behavioral')
        elif 'decorator' in pattern_name:
            tags.add('structural')
        
        return tags
    
    async def _extract_architecture_patterns(self, project_path: Path) -> List[ArchitecturePattern]:
        """Extract architectural patterns from project structure."""
        patterns = []
        
        # Analyze directory structure
        structure_patterns = self._analyze_directory_structure(project_path)
        
        # Analyze configuration files
        config_patterns = self._analyze_configuration_files(project_path)
        
        # Analyze dependencies
        dependency_patterns = self._analyze_dependencies(project_path)
        
        patterns.extend(structure_patterns)
        patterns.extend(config_patterns)
        patterns.extend(dependency_patterns)
        
        return patterns
    
    def _analyze_directory_structure(self, project_path: Path) -> List[ArchitecturePattern]:
        """Analyze project directory structure for architectural patterns."""
        patterns = []
        
        # Check for common architectural indicators
        dirs = [d.name.lower() for d in project_path.iterdir() if d.is_dir()]
        
        # MVC pattern
        if any(indicator in dirs for indicator in ['models', 'views', 'controllers']):
            patterns.append(ArchitecturePattern(
                pattern_name='mvc',
                category='architectural',
                description='Model-View-Controller architecture detected',
                components=['models', 'views', 'controllers'],
                relationships=[('models', 'views'), ('controllers', 'models')],
                benefits=['separation of concerns', 'maintainability'],
                use_cases=['web applications', 'enterprise systems'],
                complexity='medium',
                examples=[str(project_path)]
            ))
        
        # Microservices pattern
        if len([d for d in dirs if 'service' in d]) >= 2:
            patterns.append(ArchitecturePattern(
                pattern_name='microservices',
                category='architectural',
                description='Microservices architecture detected',
                components=[d for d in dirs if 'service' in d],
                relationships=[('api_gateway', 'services')],
                benefits=['scalability', 'independent deployment'],
                use_cases=['large applications', 'distributed systems'],
                complexity='high',
                examples=[str(project_path)]
            ))
        
        return patterns
    
    def _analyze_configuration_files(self, project_path: Path) -> List[ArchitecturePattern]:
        """Analyze configuration files for architectural insights."""
        patterns = []
        
        # Look for common config files
        config_files = [
            'docker-compose.yml', 'Dockerfile', 'package.json', 'requirements.txt',
            'pom.xml', 'build.gradle', 'webpack.config.js', 'vite.config.js'
        ]
        
        found_configs = []
        for config_file in config_files:
            if (project_path / config_file).exists():
                found_configs.append(config_file)
        
        if 'docker-compose.yml' in found_configs or 'Dockerfile' in found_configs:
            patterns.append(ArchitecturePattern(
                pattern_name='containerized',
                category='deployment',
                description='Containerized architecture with Docker',
                components=['containers', 'volumes', 'networks'],
                relationships=[('app', 'database'), ('app', 'cache')],
                benefits=['portability', 'consistency'],
                use_cases=['deployment', 'development'],
                complexity='medium',
                examples=[str(project_path)]
            ))
        
        return patterns
    
    def _analyze_dependencies(self, project_path: Path) -> List[ArchitecturePattern]:
        """Analyze project dependencies for architectural patterns."""
        patterns = []
        
        # Check package.json for Node.js patterns
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                dependencies = list(package_data.get('dependencies', {}).keys())
                
                # React pattern
                if 'react' in dependencies:
                    patterns.append(ArchitecturePattern(
                        pattern_name='react_spa',
                        category='frontend',
                        description='React Single Page Application',
                        components=['components', 'hooks', 'state'],
                        relationships=[('components', 'state'), ('hooks', 'components')],
                        benefits=['component reusability', 'state management'],
                        use_cases=['web applications', 'interactive UIs'],
                        complexity='medium',
                        examples=[str(project_path)]
                    ))
                
            except Exception:
                pass
        
        return patterns
    
    async def _extract_technology_patterns(self, project_path: Path) -> List[TechnologyPattern]:
        """Extract technology stack patterns."""
        patterns = []
        
        # Analyze technology stack
        tech_stack = self._identify_technology_stack(project_path)
        
        if len(tech_stack) >= 2:
            # Determine use case based on technologies
            use_case = self._determine_use_case(tech_stack)
            
            patterns.append(TechnologyPattern(
                tech_stack=tech_stack,
                compatibility_score=self._calculate_compatibility(tech_stack),
                use_case=use_case,
                pros=self._get_tech_pros(tech_stack),
                cons=self._get_tech_cons(tech_stack),
                alternatives=self._get_alternatives(tech_stack),
                learning_curve=self._estimate_learning_curve(tech_stack)
            ))
        
        return patterns
    
    def _identify_technology_stack(self, project_path: Path) -> List[str]:
        """Identify technologies used in the project."""
        technologies = []
        
        # Check for various technology indicators
        tech_indicators = {
            'package.json': ['nodejs', 'npm'],
            'requirements.txt': ['python', 'pip'],
            'pom.xml': ['java', 'maven'],
            'build.gradle': ['java', 'gradle'],
            'Cargo.toml': ['rust', 'cargo'],
            'go.mod': ['go'],
            'Gemfile': ['ruby'],
            'composer.json': ['php'],
            'Dockerfile': ['docker'],
            'docker-compose.yml': ['docker-compose'],
        }
        
        for file_name, techs in tech_indicators.items():
            if (project_path / file_name).exists():
                technologies.extend(techs)
        
        # Check for framework indicators in code
        for file_path in self._find_code_files(project_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                if 'react' in content:
                    technologies.append('react')
                if 'vue' in content:
                    technologies.append('vue')
                if 'angular' in content:
                    technologies.append('angular')
                if 'flask' in content:
                    technologies.append('flask')
                if 'django' in content:
                    technologies.append('django')
                if 'fastapi' in content:
                    technologies.append('fastapi')
                if 'express' in content:
                    technologies.append('express')
                    
            except Exception:
                continue
        
        return list(set(technologies))
    
    def _determine_use_case(self, tech_stack: List[str]) -> str:
        """Determine the primary use case based on technology stack."""
        if any(tech in tech_stack for tech in ['react', 'vue', 'angular']):
            return 'web_application'
        elif any(tech in tech_stack for tech in ['tensorflow', 'pytorch', 'scikit-learn']):
            return 'machine_learning'
        elif any(tech in tech_stack for tech in ['unity', 'unreal']):
            return 'game_development'
        elif any(tech in tech_stack for tech in ['react-native', 'flutter']):
            return 'mobile_application'
        elif 'docker' in tech_stack:
            return 'containerized_application'
        else:
            return 'general_application'
    
    def _calculate_compatibility(self, tech_stack: List[str]) -> float:
        """Calculate compatibility score for technology stack."""
        # Simple compatibility scoring based on common combinations
        compatible_combinations = {
            ('react', 'nodejs'): 0.9,
            ('python', 'django'): 0.9,
            ('python', 'fastapi'): 0.9,
            ('java', 'spring'): 0.9,
            ('docker', 'any'): 0.8,
        }
        
        max_score = 0.5  # Base score
        
        for combo, score in compatible_combinations.items():
            if all(tech in tech_stack for tech in combo if tech != 'any'):
                max_score = max(max_score, score)
        
        return max_score
    
    def _get_tech_pros(self, tech_stack: List[str]) -> List[str]:
        """Get pros for the technology stack."""
        pros = []
        
        if 'react' in tech_stack:
            pros.append('Rich ecosystem and community support')
        if 'python' in tech_stack:
            pros.append('Rapid development and readability')
        if 'docker' in tech_stack:
            pros.append('Consistent deployment environment')
        if 'nodejs' in tech_stack:
            pros.append('JavaScript ecosystem and npm')
        
        return pros
    
    def _get_tech_cons(self, tech_stack: List[str]) -> List[str]:
        """Get cons for the technology stack."""
        cons = []
        
        if len(tech_stack) > 5:
            cons.append('Complex technology stack')
        if 'nodejs' in tech_stack and 'python' in tech_stack:
            cons.append('Mixed language complexity')
        if 'docker' in tech_stack:
            cons.append('Container management overhead')
        
        return cons
    
    def _get_alternatives(self, tech_stack: List[str]) -> List[str]:
        """Get alternative technology stacks."""
        alternatives = []
        
        if 'react' in tech_stack:
            alternatives.append('Vue.js or Angular for frontend')
        if 'python' in tech_stack:
            alternatives.append('Node.js or Java for backend')
        if 'mongodb' in tech_stack:
            alternatives.append('PostgreSQL or MySQL for database')
        
        return alternatives
    
    def _estimate_learning_curve(self, tech_stack: List[str]) -> str:
        """Estimate learning curve for the technology stack."""
        complexity_score = 0
        
        # Add complexity for each technology
        tech_complexity = {
            'react': 2, 'vue': 1, 'angular': 3,
            'python': 1, 'java': 3, 'rust': 4,
            'docker': 2, 'kubernetes': 4,
            'tensorflow': 4, 'pytorch': 3
        }
        
        for tech in tech_stack:
            complexity_score += tech_complexity.get(tech, 2)
        
        if complexity_score <= 3:
            return 'easy'
        elif complexity_score <= 6:
            return 'medium'
        else:
            return 'hard'
    
    async def _store_patterns_in_knowledge_graph(self, patterns: Dict[str, List], project_path: str) -> None:
        """Store extracted patterns in the knowledge graph."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Store project node
        project_id = hashlib.md5(project_path.encode()).hexdigest()
        self.knowledge_graph.add_node(project_id, {
            'type': 'project',
            'path': project_path,
            'patterns_extracted': timestamp,
            'pattern_counts': {k: len(v) for k, v in patterns.items()}
        })
        
        # Store pattern nodes and relationships
        for pattern_type, pattern_list in patterns.items():
            for i, pattern in enumerate(pattern_list):
                pattern_id = f"{project_id}_{pattern_type}_{i}"
                
                # Convert pattern to dict for storage
                if hasattr(pattern, '__dict__'):
                    pattern_data = pattern.__dict__
                else:
                    pattern_data = pattern
                
                pattern_data['type'] = 'pattern'
                pattern_data['pattern_type'] = pattern_type
                pattern_data['project_id'] = project_id
                pattern_data['extracted_at'] = timestamp
                
                self.knowledge_graph.add_node(pattern_id, pattern_data)
                self.knowledge_graph.add_edge(project_id, pattern_id)
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get pattern extraction statistics."""
        return {
            **self.extraction_stats,
            'supported_languages': list(set(
                pattern['language'] for patterns in self.code_patterns.values()
                for pattern in patterns.values()
            )),
            'pattern_types_count': len(self.code_patterns),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def search_similar_patterns(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar patterns using vector similarity."""
        try:
            # Generate embedding for query
            query_embedding = self.embedding_service.get_embedding(query)
            
            # Search knowledge graph for similar patterns
            similar_projects = self.knowledge_graph.find_similar_projects(query, [])
            
            results = []
            for project in similar_projects[:limit]:
                results.append({
                    'project_id': project['project_id'],
                    'similarity_score': project['similarity_score'],
                    'patterns': project['project_data'].get('patterns', {}),
                    'path': project['project_data'].get('path', '')
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching similar patterns: {e}")
            return []


# Global pattern extractor instance
pattern_extractor = AdvancedPatternExtractor()
