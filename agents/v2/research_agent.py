from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, cast

from orchestration.task_model import Task
from .base import AgentResult


@dataclass
class ResearchAgent:
    """ARCHIVIST agent: research ingestion and synthesis.

    Now HOOKED UP to your AdvancedPatternExtractor to capture real insights.
    """

    name: str = "Archivist"

    def _resolve_project_root(self, task: Task) -> Path:
        raw = task.inputs.get("project_root")
        base = Path(raw).expanduser().resolve() if isinstance(raw, str) and raw.strip() else Path("projects") / "session_default"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def handle_task(self, task: Task) -> AgentResult:
        project_root = self._resolve_project_root(task)
        research_dir = project_root / "research"
        research_dir.mkdir(parents=True, exist_ok=True)

        brief_value = task.inputs.get("brief")
        brief_map: dict[str, Any] = cast(dict[str, Any], brief_value) if isinstance(brief_value, dict) else {}
        sources: list[Any] = []
        sources_raw = brief_map.get("sources")
        if isinstance(sources_raw, list):
            for item in cast(list[Any], sources_raw):
                if isinstance(item, dict):
                    sources.append(cast(dict[str, Any], item))
                elif isinstance(item, str) and item.strip():
                    sources.append(item.strip())

        # New capability: Web and Video Research
        web_query = task.inputs.get("web_search") if isinstance(task.inputs.get("web_search"), str) else None
        video_url = task.inputs.get("video_url") if isinstance(task.inputs.get("video_url"), str) else None

        logs: list[str] = []

        # 1. Handle Web Research
        if web_query:
            try:
                import importlib
                internet_scanner = importlib.import_module("research.internet_scanner")
                perform_web_search_any = getattr(internet_scanner, "perform_web_search")
                perform_web_search_fn = cast(Callable[[str], list[Any]], perform_web_search_any)
                web_results: list[Any] = perform_web_search_fn(web_query)
                sources.append({"kind": "web_search", "query": web_query, "results": web_results})
                logs.append(f"Archivist performed web search for: {web_query}")
            except Exception as e:
                logs.append(f"Web search failed: {str(e)}")

        # 2. Handle Video Research
        if video_url:
            try:
                import importlib
                video_mod = importlib.import_module("research.video_processor")
                process_video = getattr(video_mod, "process_video")
                transcription = process_video(video_url, str(research_dir))
                sources.append({"kind": "video", "url": video_url, "transcription_preview": transcription[:200]})
                logs.append(f"Archivist processed video: {video_url}")
            except Exception as e:
                logs.append(f"Video processing failed: {str(e)}")

        # 3. Pattern Extraction (Always run on project root to 'learn')
        from research.pattern_extractor import AdvancedPatternExtractor
        extractor: Any = AdvancedPatternExtractor()

        results: dict[str, Any] = {}
        research_insights: dict[str, Any] = {
            "sources": sources,
            "high_level_summary": "",
        }
        patterns: dict[str, list[Any]] = {"design_patterns": [], "architecture_patterns": []}

        try:
            # We run the extraction on the project root to 'learn' from it
            raw_results: Any = asyncio.run(extractor.extract_patterns_from_project(str(project_root)))
            results = cast(dict[str, Any], raw_results) if isinstance(raw_results, dict) else {}
            research_insights["high_level_summary"] = (
                f"System learned {len(results.get('code_patterns', []))} patterns from this environment."
            )
            try:
                research_insights["extraction_stats"] = extractor.get_extraction_statistics()
            except Exception as e:
                research_insights["extraction_stats_error"] = str(e)

            patterns["design_patterns"] = results.get("code_patterns", [])
            patterns["architecture_patterns"] = results.get("architecture_patterns", [])
        except Exception as e:
            # Fallback if extraction fails
            research_insights["error"] = str(e)
            research_insights["high_level_summary"] = "Learning failed."

        extracted_systems: dict[str, Any] = {
            "systems": results.get("architecture_patterns", []),
            "performance_patterns": results.get("performance_patterns", []),
            "anti_patterns": results.get("anti_patterns", []),
        }

        insights_path = research_dir / "research_insights.json"
        patterns_path = research_dir / "patterns.json"
        systems_path = research_dir / "extracted_systems.json"

        # Helper to handle non-serializable objects (like your Pattern dataclasses)
        def default_serializer(obj: Any) -> Any:
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            if isinstance(obj, set):
                return list(cast(set[Any], obj))
            return str(obj)

        insights_path.write_text(json.dumps(research_insights, indent=2, default=default_serializer), encoding="utf-8")
        patterns_path.write_text(json.dumps(patterns, indent=2, default=default_serializer), encoding="utf-8")
        systems_path.write_text(json.dumps(extracted_systems, indent=2, default=default_serializer), encoding="utf-8")

        return AgentResult(
            outputs={
                "research_insights_path": str(insights_path),
                "patterns_path": str(patterns_path),
                "extracted_systems_path": str(systems_path),
            },
            logs=logs + [f"Archivist successfully learned patterns and wrote to {research_dir}"],
        )
