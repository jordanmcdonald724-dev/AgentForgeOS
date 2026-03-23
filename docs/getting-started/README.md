# Getting Started with AgentForgeOS V2

Welcome to AgentForgeOS V2! This guide will help you get up and running with the multi-agent operating system that revolutionizes software development through intelligent agent collaboration.

## 🎯 What is AgentForgeOS?

AgentForgeOS is a **multi-agent operating system** that automates software development through specialized AI agents working together in deterministic task graphs. Unlike traditional development tools, AgentForgeOS provides:

- **12 Specialized Agents** - Each with specific roles and expertise
- **Deterministic Task Graphs** - Predictable, reproducible execution
- **Build Simulation** - Feasibility analysis before execution
- **Knowledge Graph** - Learning from every project
- **Real-time Monitoring** - Live updates on agent activity
- **Secure Sandboxing** - Isolated build environments

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.11+** - Core system runtime
- **Node.js 18+** - Frontend development
- **Docker** - Build sandboxing (optional but recommended)
- **Git** - Version control

### Installation

1. **Clone AgentForgeOS**
   ```bash
   git clone https://github.com/your-org/AgentForgeOS.git
   cd AgentForgeOS
   ```

2. **Install Python Dependencies**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies**
   ```bash
   npm install --prefix frontend
   ```

4. **Setup Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your configuration
   nano .env
   ```

### First Launch

1. **Start the Engine**
   ```bash
   python engine/server.py
   ```
   
2. **Start the Frontend** (in another terminal)
   ```bash
   npm run dev --prefix frontend
   ```

3. **Access AgentForgeOS**
   - **Frontend**: http://localhost:5173
   - **API Documentation**: http://localhost:8000/docs
   - **WebSocket Monitor**: http://localhost:5173/monitor

### Your First Project

1. **Open Command Center** - Navigate to http://localhost:5173
2. **Enter Your Command** - Type what you want to build
3. **Review Simulation** - Check feasibility and timeline
4. **Approve Build** - Let agents execute your vision
5. **Monitor Progress** - Watch real-time agent activity

## 📋 System Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 10GB free space
- **CPU**: 2 cores
- **Network**: Internet connection for AI models

### Recommended Requirements
- **RAM**: 16GB
- **Storage**: 50GB free space
- **CPU**: 4+ cores
- **GPU**: Optional for AI acceleration
- **Docker**: For secure build sandboxing

## 🏗️ Architecture Overview

### Core Components

```
AgentForgeOS V2
├── Desktop Layer          # Tauri desktop application
├── Engine Layer           # FastAPI runtime and orchestration
├── Control Layer          # Security and governance
├── Orchestration Layer    # Task graph execution
├── Agent System          # 12 specialized AI agents
├── Knowledge Graph        # Neo4j + Qdrant integration
├── Build System          # Simulation + Docker sandboxing
└── Frontend              # React 3-page interface
```

### The 12 Agents

| Agent | Role | Responsibility |
|-------|------|---------------|
| **Origin** | Commander | Command interpretation and task graph generation |
| **Architect** | Atlas | System architecture and module design |
| **Builder** | Forge | Code generation and scaffolding |
| **Frontend** | Surface | UI/UX implementation |
| **Backend** | Core | Backend systems and APIs |
| **Game Engine** | Fabricator | Unity/Unreal integration |
| **AI Engineer** | Synapse | Model routing and AI integration |
| **Security** | Guardian | Security validation and controls |
| **Testing** | Analyst | Quality assurance and testing |
| **DevOps** | Launcher | Deployment and operations |
| **Research** | Archivist | Knowledge extraction and storage |
| **Simulation** | Simulator | Build feasibility analysis |

## 🎮 User Interface

AgentForgeOS follows the **3-page architecture** principle:

### 1. Command Center
- **Purpose**: Project initiation and command input
- **Features**: Command parsing, simulation preview, project management
- **Access**: Main dashboard

### 2. Project Workspace
- **Purpose**: Active project monitoring and interaction
- **Features**: Real-time task status, agent activity, file explorer
- **Access**: During active builds

### 3. Research & Knowledge Lab
- **Purpose**: Knowledge exploration and research
- **Features**: Pattern search, project history, knowledge graph
- **Access**: Research and analysis

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Core System
ENGINE_HOST=localhost
ENGINE_PORT=8000
FRONTEND_URL=http://localhost:5173

# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=agentforge_v2

# AI Models
FAL_API_KEY=your_fal_api_key
OPENAI_API_KEY=your_openai_key

# Knowledge Graph
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Game Engines
UNITY_EDITOR_PATH=/path/to/Unity/Editor/Unity.exe
UNREAL_EDITOR_PATH=/path/to/Unreal/Engine/Binaries/Win64/UnrealEditor.exe

# Docker Sandbox
DOCKER_ENABLED=true
SANDBOX_IMAGE=agentforge/build-sandbox:latest
```

### First-Time Setup

1. **Run Setup Wizard**
   ```bash
   python scripts/setup_wizard.py
   ```

2. **Verify Dependencies**
   ```bash
   python scripts/check_dependencies.py
   ```

3. **Initialize Knowledge Graph**
   ```bash
   python scripts/init_knowledge_graph.py
   ```

## 🎯 Common Use Cases

### 1. Web Application Development
```
Command: "Build a modern e-commerce website with React, Node.js, and MongoDB"
Expected Timeline: 2-4 weeks
Agents Involved: Origin, Atlas, Forge, Surface, Core, Synapse
```

### 2. Mobile App Development
```
Command: "Create a cross-platform mobile app for task management"
Expected Timeline: 3-6 weeks
Agents Involved: Origin, Atlas, Forge, Surface, Synapse, Analyst
```

### 3. Game Development
```
Command: "Develop a 3D puzzle game using Unity"
Expected Timeline: 8-12 weeks
Agents Involved: Origin, Atlas, Forge, Fabricator, Analyst, Launcher
```

### 4. API Service
```
Command: "Build a RESTful API service for user authentication"
Expected Timeline: 1-2 weeks
Agents Involved: Origin, Atlas, Forge, Core, Synapse, Guardian
```

## 🔍 Monitoring and Debugging

### Real-time Monitoring
- **WebSocket Updates**: Live task and agent status
- **Build Progress**: Real-time build stage tracking
- **System Health**: Resource usage and performance

### Debugging Tools
- **Task Graph Visualization**: See execution flow
- **Agent Logs**: Detailed agent activity logs
- **Error Tracking**: Comprehensive error reporting

### Performance Metrics
- **Execution Time**: Task and build duration
- **Agent Efficiency**: Success rates and performance
- **Resource Usage**: Memory, CPU, and storage consumption

## 🆘 Troubleshooting

### Common Issues

**Problem**: Docker not available
```bash
# Solution: Install Docker or disable sandboxing
export DOCKER_ENABLED=false
```

**Problem**: AI model API errors
```bash
# Solution: Check API keys and network connectivity
python scripts/test_api_connections.py
```

**Problem**: Frontend not loading
```bash
# Solution: Check port availability and rebuild
npm run build --prefix frontend
npm run dev --prefix frontend
```

### Getting Help

1. **Check Logs**: `logs/agentforge.log`
2. **Run Diagnostics**: `python scripts/diagnostics.py`
3. **Consult FAQ**: [FAQ Documentation](../faq/)
4. **Community Support**: GitHub Discussions

## 📚 Next Steps

Now that you're set up, explore these guides:

- [**User Guide**](../user-guide/) - Detailed usage instructions
- [**Architecture Guide**](../architecture/) - Deep dive into system design
- [**Developer Guide**](../developer-guide/) - Extension and customization
- [**API Reference**](../api/) - Complete API documentation

## 🎉 Congratulations!

You've successfully set up AgentForgeOS V2! You're ready to experience the future of software development through intelligent agent collaboration.

**Next Steps**:
1. Try a simple project to understand the workflow
2. Explore the 3-page interface
3. Monitor real-time agent activity
4. Build your knowledge base with project history

Welcome to the future of software development! 🚀
