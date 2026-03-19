#!/usr/bin/env python3
"""
Comprehensive Compliance Test Report for AgentForgeOS V2
Tests alignment with Build Bible V2 and Master Blueprint specifications
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ComplianceTestSuite:
    """Comprehensive compliance testing for AgentForgeOS V2"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        self.compliance_score = 0
        self.total_checks = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive compliance tests"""
        print("🔍 Starting AgentForgeOS V2 Compliance Testing...")
        print("=" * 60)
        
        # Test repository structure
        self.test_repository_structure()
        
        # Test agent system
        self.test_agent_system()
        
        # Test frontend architecture
        self.test_frontend_architecture()
        
        # Test orchestration engine
        self.test_orchestration_engine()
        
        # Test build simulation
        self.test_build_simulation()
        
        # Test knowledge graph
        self.test_knowledge_graph()
        
        # Test model routing
        self.test_model_routing()
        
        # Test bridge integration
        self.test_bridge_integration()
        
        # Calculate final score
        self.calculate_compliance_score()
        
        return self.generate_report()
    
    def test_repository_structure(self):
        """Test repository structure compliance"""
        print("\n📁 Testing Repository Structure...")
        
        required_dirs = [
            "frontend", "backend", "agents", "orchestration", "build_system",
            "knowledge", "research", "infrastructure", "models", "memory",
            "projects", "tests", "scripts", "docs", "bridge", "control",
            "providers", "services", "engine", "desktop", "apps"
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.add_test_result(f"Directory {dir_name}", True, "Required directory exists")
            else:
                missing_dirs.append(dir_name)
                self.add_test_result(f"Directory {dir_name}", False, "Required directory missing")
        
        if not missing_dirs:
            print("✅ All required directories present")
        else:
            print(f"❌ Missing directories: {missing_dirs}")
    
    def test_agent_system(self):
        """Test 12-agent system compliance"""
        print("\n🤖 Testing Agent System...")
        
        v2_agents_dir = self.project_root / "agents" / "v2"
        if not v2_agents_dir.exists():
            self.add_test_result("V2 Agents Directory", False, "agents/v2 directory missing")
            return
        
        required_agents = [
            "commander.py", "atlas.py", "forge.py", "frontend_engineer.py",
            "backend_engineer.py", "game_engine_engineer.py", "ai_engineer.py",
            "prism.py", "sentinel.py", "probe.py", "devops_engineer.py", "research_agent.py"
        ]
        
        missing_agents = []
        for agent_file in required_agents:
            agent_path = v2_agents_dir / agent_file
            if agent_path.exists():
                self.add_test_result(f"Agent {agent_file}", True, "Agent implementation exists")
            else:
                missing_agents.append(agent_file)
                self.add_test_result(f"Agent {agent_file}", False, "Agent implementation missing")
        
        if not missing_agents:
            print("✅ All 12 agents implemented")
        else:
            print(f"❌ Missing agents: {missing_agents}")
    
    def test_frontend_architecture(self):
        """Test 3-page frontend architecture"""
        print("\n🎨 Testing Frontend Architecture...")
        
        pages_dir = self.project_root / "frontend" / "src" / "ui" / "pages"
        if not pages_dir.exists():
            self.add_test_result("Frontend Pages Directory", False, "frontend/src/ui/pages missing")
            return
        
        required_pages = [
            "CommandCenterPage.tsx", "ProjectWorkspacePage.tsx", "ResearchLabPage.tsx"
        ]
        
        missing_pages = []
        for page_file in required_pages:
            page_path = pages_dir / page_file
            if page_path.exists():
                self.add_test_result(f"Page {page_file}", True, "Required page exists")
            else:
                missing_pages.append(page_file)
                self.add_test_result(f"Page {page_file}", False, "Required page missing")
        
        # Check for extra pages (should not exist according to Build Bible)
        all_pages = list(pages_dir.glob("*.tsx"))
        extra_pages = [p.name for p in all_pages if p.name not in required_pages and not p.name.startswith("_")]
        
        if extra_pages:
            for extra_page in extra_pages:
                self.add_test_result(f"Extra Page {extra_page}", False, "Additional page violates 3-page rule")
        
        if not missing_pages and not extra_pages:
            print("✅ Exactly 3 pages implemented")
        else:
            print(f"❌ Issues found - Missing: {missing_pages}, Extra: {extra_pages}")
    
    def test_orchestration_engine(self):
        """Test orchestration engine compliance"""
        print("\n⚙️ Testing Orchestration Engine...")
        
        orchestration_dir = self.project_root / "orchestration"
        if not orchestration_dir.exists():
            self.add_test_result("Orchestration Directory", False, "orchestration directory missing")
            return
        
        required_files = ["engine.py", "task_model.py", "runtime.py"]
        for file_name in required_files:
            file_path = orchestration_dir / file_name
            if file_path.exists():
                self.add_test_result(f"Orchestration {file_name}", True, "Core orchestration file exists")
            else:
                self.add_test_result(f"Orchestration {file_name}", False, "Core orchestration file missing")
        
        # Test task model structure
        task_model_path = orchestration_dir / "task_model.py"
        if task_model_path.exists():
            try:
                content = task_model_path.read_text(encoding='utf-8')
                if 'class Task' in content and 'TaskStatus' in content:
                    self.add_test_result("Task Model Structure", True, "Task model properly defined")
                else:
                    self.add_test_result("Task Model Structure", False, "Task model incomplete")
            except Exception:
                self.add_test_result("Task Model Structure", False, "Could not read task model")
    
    def test_build_simulation(self):
        """Test build simulation engine"""
        print("\n🔬 Testing Build Simulation...")
        
        simulation_path = self.project_root / "build_system" / "simulation_engine.py"
        if not simulation_path.exists():
            self.add_test_result("Build Simulation Engine", False, "simulation_engine.py missing")
            return
        
        try:
            content = simulation_path.read_text(encoding='utf-8')
            
            # Check for advanced features
            advanced_features = [
                "_analyze_command_complexity",
                "_estimate_duration", 
                "_generate_architecture_preview",
                "_assess_feasibility",
                "find_similar_projects"
            ]
            
            implemented_features = []
            for feature in advanced_features:
                if feature in content:
                    implemented_features.append(feature)
                    self.add_test_result(f"Simulation Feature {feature}", True, "Advanced feature implemented")
                else:
                    self.add_test_result(f"Simulation Feature {feature}", False, "Advanced feature missing")
            
            if len(implemented_features) >= 4:
                print("✅ Advanced build simulation implemented")
            else:
                print(f"⚠️  Partial simulation implementation: {len(implemented_features)}/{len(advanced_features)} features")
                
        except Exception as e:
            self.add_test_result("Build Simulation Engine", False, f"Error reading file: {e}")
    
    def test_knowledge_graph(self):
        """Test knowledge graph integration"""
        print("\n🧠 Testing Knowledge Graph...")
        
        kg_path = self.project_root / "knowledge" / "knowledge_graph.py"
        if not kg_path.exists():
            self.add_test_result("Knowledge Graph", False, "knowledge_graph.py missing")
            return
        
        try:
            content = kg_path.read_text(encoding='utf-8')
            
            # Check for database integration features
            db_features = [
                "_init_neo4j",
                "_init_qdrant", 
                "find_similar_projects",
                "_add_vector_qdrant",
                "_add_node_neo4j"
            ]
            
            implemented_features = []
            for feature in db_features:
                if feature in content:
                    implemented_features.append(feature)
                    self.add_test_result(f"KG Feature {feature}", True, "Database integration feature implemented")
                else:
                    self.add_test_result(f"KG Feature {feature}", False, "Database integration feature missing")
            
            if len(implemented_features) >= 3:
                print("✅ Advanced knowledge graph with database integration")
            else:
                print(f"⚠️  Basic knowledge graph: {len(implemented_features)}/{len(db_features)} features")
                
        except Exception as e:
            self.add_test_result("Knowledge Graph", False, f"Error reading file: {e}")
    
    def test_model_routing(self):
        """Test fal.ai model routing"""
        print("\n🔄 Testing Model Routing...")
        
        router_path = self.project_root / "infrastructure" / "model_router.py"
        if not router_path.exists():
            self.add_test_result("Model Router", False, "model_router.py missing")
            return
        
        try:
            content = router_path.read_text(encoding='utf-8')
            
            # Check for fal.ai integration
            fal_features = [
                "FalAIConfig",
                "async def call_model",
                "get_usage_stats",
                "deepseek-coder",
                "flux-schnell",
                "shape-e"
            ]
            
            implemented_features = []
            for feature in fal_features:
                if feature in content:
                    implemented_features.append(feature)
                    self.add_test_result(f"Model Routing {feature}", True, "fal.ai feature implemented")
                else:
                    self.add_test_result(f"Model Routing {feature}", False, "fal.ai feature missing")
            
            if len(implemented_features) >= 5:
                print("✅ Full fal.ai model routing implemented")
            else:
                print(f"⚠️  Partial model routing: {len(implemented_features)}/{len(fal_features)} features")
                
        except Exception as e:
            self.add_test_result("Model Router", False, f"Error reading file: {e}")
    
    def test_bridge_integration(self):
        """Test Unity/Unreal bridge integration"""
        print("\n🌉 Testing Bridge Integration...")
        
        bridge_path = self.project_root / "bridge" / "bridge_server.py"
        if not bridge_path.exists():
            self.add_test_result("Bridge Server", False, "bridge_server.py missing")
            return
        
        try:
            content = bridge_path.read_text(encoding='utf-8')
            
            # Check for game engine integration
            engine_features = [
                "launch_unity_editor",
                "launch_unreal_editor",
                "build_unity_project", 
                "build_unreal_project",
                "_is_unity_project",
                "_is_unreal_project"
            ]
            
            implemented_features = []
            for feature in engine_features:
                if feature in content:
                    implemented_features.append(feature)
                    self.add_test_result(f"Bridge Feature {feature}", True, "Game engine feature implemented")
                else:
                    self.add_test_result(f"Bridge Feature {feature}", False, "Game engine feature missing")
            
            if len(implemented_features) >= 4:
                print("✅ Unity/Unreal bridge integration complete")
            else:
                print(f"⚠️  Partial bridge integration: {len(implemented_features)}/{len(engine_features)} features")
                
        except Exception as e:
            self.add_test_result("Bridge Server", False, f"Error reading file: {e}")
    
    def add_test_result(self, test_name: str, passed: bool, message: str):
        """Add a test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.total_checks += 1
        if passed:
            self.compliance_score += 1
    
    def calculate_compliance_score(self):
        """Calculate final compliance score"""
        if self.total_checks > 0:
            self.compliance_score = (self.compliance_score / self.total_checks) * 100
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        report = {
            "compliance_score": round(self.compliance_score, 1),
            "total_checks": self.total_checks,
            "passed_checks": len(passed_tests),
            "failed_checks": len(failed_tests),
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": self._generate_summary(),
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(failed_tests)
        }
        
        return report
    
    def _generate_summary(self) -> str:
        """Generate test summary"""
        if self.compliance_score >= 95:
            return "EXCELLENT - AgentForgeOS demonstrates exceptional compliance with V2 specifications"
        elif self.compliance_score >= 85:
            return "VERY GOOD - AgentForgeOS shows strong compliance with minor gaps"
        elif self.compliance_score >= 70:
            return "GOOD - AgentForgeOS meets most requirements with some areas needing attention"
        elif self.compliance_score >= 50:
            return "FAIR - AgentForgeOS partially complies with significant gaps"
        else:
            return "POOR - AgentForgeOS requires substantial improvement to meet V2 standards"
    
    def _generate_recommendations(self, failed_tests: List[Dict]) -> List[str]:
        """Generate recommendations based on failed tests"""
        recommendations = []
        
        # Group failures by category
        categories = {}
        for test in failed_tests:
            category = test["test"].split()[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        for category, tests in categories.items():
            if category == "Directory":
                recommendations.append("Create missing directory structure to comply with V2 repository layout")
            elif category == "Agent":
                recommendations.append("Implement missing agent files to complete the 12-agent system")
            elif category == "Page":
                recommendations.append("Ensure exactly 3 frontend pages as specified in Build Bible")
            elif category == "Simulation":
                recommendations.append("Enhance build simulation with advanced heuristics and knowledge graph integration")
            elif category == "KG":
                recommendations.append("Complete Neo4j/Qdrant integration for advanced knowledge management")
            elif category == "Model":
                recommendations.append("Implement full fal.ai model routing with cost optimization")
            elif category == "Bridge":
                recommendations.append("Complete Unity/Unreal integration for local game engine support")
        
        return recommendations

def main():
    """Run compliance tests and generate report"""
    suite = ComplianceTestSuite()
    report = suite.run_all_tests()
    
    print("\n" + "=" * 60)
    print("📊 COMPLIANCE TEST REPORT")
    print("=" * 60)
    print(f"🎯 Overall Compliance Score: {report['compliance_score']}%")
    print(f"✅ Passed: {report['passed_checks']}/{report['total_checks']}")
    print(f"❌ Failed: {report['failed_checks']}/{report['total_checks']}")
    print(f"📝 Summary: {report['summary']}")
    
    if report['recommendations']:
        print("\n🔧 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Save detailed report
    report_path = Path(__file__).parent / "compliance_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"\n💾 Detailed report saved to: {report_path}")
    
    return report

if __name__ == "__main__":
    main()
