import React, { useState, useEffect, useRef, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { 
  ResizableHandle, 
  ResizablePanel, 
  ResizablePanelGroup 
} from "./components/ui/resizable";
import { 
  Layout, Layers, FlaskConical, ImageIcon, Rocket, 
  Box, Gamepad2, Building2, FolderOpen, ChevronRight,
  Send, Settings, User, Cpu, FileText, FileCode, File,
  Plus, Search, Upload, Database, Globe, Zap, Play, Square,
  Circle, GitBranch, Link2, Trash2, Eye, Code, Terminal
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const LOGO_URL = "https://customer-assets.emergentagent.com/job_agent-builder-os/artifacts/nc1ky769_Flux_Dev_Design_a_premium_technology_platform_logo_for_an_AI_d_0.jpg";

// Module definitions
const MODULES = [
  { id: "studio", name: "Studio", icon: Layout, description: "Project workspace and file management" },
  { id: "builds", name: "Build Pipelines", icon: Layers, description: "Manage and trigger build pipelines" },
  { id: "research", name: "Research", icon: FlaskConical, description: "Knowledge search and research notes" },
  { id: "assets", name: "Assets", icon: ImageIcon, description: "Generated assets registry" },
  { id: "deployment", name: "Deployment", icon: Rocket, description: "Deploy projects to targets" },
  { id: "sandbox", name: "Sandbox", icon: Box, description: "Agent experimentation environment" },
  { id: "game_dev", name: "Game Dev", icon: Gamepad2, description: "Game development assistant" },
  { id: "saas_builder", name: "SaaS Builder", icon: Building2, description: "End-to-end SaaS scaffolding" },
];

// Pipeline stages
const PIPELINE_STAGES = [
  "Project Planner", "System Architect", "Task Router",
  "Module Builder", "API Architect", "Data Architect",
  "Backend Engineer", "Frontend Engineer", "AI Integration Engineer",
  "Integration Tester", "Security Auditor", "System Stabilizer"
];

// Utility functions
const formatBytes = (bytes) => {
  if (bytes == null) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const formatTime = () => {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
};

// Components
const NavBar = () => (
  <header className="nav-bar">
    <div className="nav-logo">
      <div className="logo-hexagon">
        <span className="logo-letters">AF</span>
      </div>
      <span className="nav-logo-text">AgentForgeOS</span>
    </div>
    <div className="nav-pills">
      <button className="nav-pill">Project</button>
      <button className="nav-pill">Workspace</button>
      <button className="nav-pill">Providers</button>
      <button className="nav-pill">
        <Cpu size={14} style={{ marginRight: 6, display: 'inline' }} />
        System
      </button>
      <button className="nav-pill">
        <Settings size={14} style={{ marginRight: 6, display: 'inline' }} />
        Settings
      </button>
      <button className="nav-pill">
        <User size={14} style={{ marginRight: 6, display: 'inline' }} />
        Profile
      </button>
    </div>
  </header>
);

const Sidebar = ({ activeModule, setActiveModule }) => (
  <aside className="sidebar">
    <div className="sidebar-title">Modules</div>
    <nav className="sidebar-nav">
      {MODULES.map((mod) => {
        const Icon = mod.icon;
        return (
          <button
            key={mod.id}
            className={`sidebar-item ${activeModule?.id === mod.id ? "active" : ""}`}
            onClick={() => setActiveModule(mod)}
            data-testid={`sidebar-${mod.id}`}
          >
            <span className="sidebar-item-icon">
              <Icon size={18} />
            </span>
            {mod.name}
          </button>
        );
      })}
    </nav>
  </aside>
);

// Module Panels
const StudioPanel = ({ addLog }) => {
  const [path, setPath] = useState(".");
  const [entries, setEntries] = useState([
    { name: "backend", type: "directory" },
    { name: "frontend", type: "directory" },
    { name: "tests", type: "directory" },
    { name: "README.md", type: "file", size: 1024 },
    { name: "package.json", type: "file", size: 2048 },
  ]);
  const [loading, setLoading] = useState(false);

  const loadFiles = async (newPath) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/bridge/list?path=${encodeURIComponent(newPath)}`);
      const data = await res.json();
      if (data?.data?.entries) {
        setEntries(data.data.entries);
      }
      setPath(newPath);
      addLog("info", `Loaded workspace: ${newPath}`);
    } catch (err) {
      addLog("warn", `Using mock data - API unavailable`);
    }
    setLoading(false);
  };

  useEffect(() => { 
    addLog("info", "Studio workspace initialized");
    // eslint-disable-next-line
  }, []);

  const pathParts = path === "." ? [] : path.split("/").filter(Boolean);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Project Files</div>
      <div className="breadcrumb">
        <span className="breadcrumb-item" onClick={() => loadFiles(".")}>workspace</span>
        {pathParts.map((part, i) => (
          <React.Fragment key={i}>
            <span className="breadcrumb-sep"><ChevronRight size={12} /></span>
            <span className="breadcrumb-item" onClick={() => loadFiles(pathParts.slice(0, i + 1).join("/"))}>
              {part}
            </span>
          </React.Fragment>
        ))}
      </div>
      <div className="file-browser">
        {loading ? (
          <div className="item-empty">Loading...</div>
        ) : entries.length === 0 ? (
          <div className="item-empty">Empty directory</div>
        ) : (
          entries.map((entry, i) => {
            const getIcon = () => {
              if (entry.type === "directory") return <FolderOpen size={16} />;
              if (entry.name.endsWith(".md")) return <FileText size={16} />;
              if (entry.name.endsWith(".json") || entry.name.endsWith(".js") || entry.name.endsWith(".py")) return <FileCode size={16} />;
              return <File size={16} />;
            };
            return (
              <div
                key={i}
                className={`file-entry ${entry.type}`}
                onClick={() => entry.type === "directory" && loadFiles(path === "." ? entry.name : `${path}/${entry.name}`)}
              >
                <span className="file-entry-icon">{getIcon()}</span>
                <span className="file-entry-name">{entry.name}</span>
                {entry.size != null && <span className="file-entry-size">{formatBytes(entry.size)}</span>}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

const BuildsPanel = ({ addLog }) => {
  const [runs, setRuns] = useState([
    { id: "build_001", project: "AgentForgeOS", status: "success", triggered_at: new Date().toISOString() },
    { id: "build_002", project: "Studio Module", status: "running", triggered_at: new Date().toISOString() },
  ]);
  const [project, setProject] = useState("");

  const loadRuns = async () => {
    try {
      const res = await fetch(`${API}/modules/builds/runs`);
      const data = await res.json();
      if (data?.data?.length) setRuns(data.data);
    } catch (err) {
      // Use mock data
    }
  };

  const triggerBuild = async () => {
    const newBuild = { 
      id: `build_${Date.now()}`, 
      project: project || "default", 
      status: "queued", 
      triggered_at: new Date().toISOString() 
    };
    setRuns(prev => [...prev, newBuild]);
    addLog("info", `Build triggered: ${newBuild.id}`);
    setProject("");
  };

  useEffect(() => { 
    loadRuns(); 
    addLog("info", "Build pipelines loaded");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Build Pipelines</div>
      <div className="panel-actions">
        <input className="input" placeholder="Project name" value={project} onChange={(e) => setProject(e.target.value)} style={{ flex: 1 }} />
        <button className="btn btn-primary" onClick={triggerBuild} data-testid="trigger-build-btn">Trigger Build</button>
      </div>
      <div className="item-list">
        {runs.length === 0 ? (
          <div className="item-empty">No builds yet. Trigger one above.</div>
        ) : (
          runs.slice().reverse().map((run, i) => (
            <div className="item-row" key={i}>
              <span className={`item-badge ${run.status}`}>{run.status}</span>
              <span className="item-name">{run.project}</span>
              <span className="item-meta">#{run.id}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// NODULAR RESEARCH PANEL
const ResearchPanel = ({ addLog }) => {
  const [nodes, setNodes] = useState([
    { id: 1, type: "document", title: "Architecture Patterns", x: 50, y: 50, connections: [2] },
    { id: 2, type: "api", title: "API Design Notes", x: 300, y: 80, connections: [3] },
    { id: 3, type: "database", title: "Schema Definitions", x: 200, y: 200, connections: [] },
  ]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [draggedNode, setDraggedNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // File drop handling
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const rect = canvasRef.current?.getBoundingClientRect();
    const x = e.clientX - (rect?.left || 0) - 60;
    const y = e.clientY - (rect?.top || 0) - 30;
    
    files.forEach((file, idx) => {
      const type = file.type.includes("image") ? "image" : 
                   file.type.includes("audio") ? "audio" :
                   file.name.endsWith(".json") ? "api" :
                   file.name.endsWith(".sql") ? "database" : "document";
      
      const newNode = {
        id: Date.now() + idx,
        type,
        title: file.name,
        x: x + (idx * 30),
        y: y + (idx * 30),
        connections: [],
      };
      setNodes(prev => [...prev, newNode]);
      addLog("info", `Added node: ${file.name}`);
    });
  }, [addLog]);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  };

  const handleNodeMouseDown = (e, node) => {
    e.stopPropagation();
    const rect = canvasRef.current?.getBoundingClientRect();
    setDraggedNode(node.id);
    setDragOffset({
      x: e.clientX - (rect?.left || 0) - node.x,
      y: e.clientY - (rect?.top || 0) - node.y
    });
    setIsDragging(true);
    setSelectedNode(node.id);
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || draggedNode === null) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    const newX = Math.max(0, Math.min(e.clientX - (rect?.left || 0) - dragOffset.x, (rect?.width || 500) - 120));
    const newY = Math.max(0, Math.min(e.clientY - (rect?.top || 0) - dragOffset.y, (rect?.height || 300) - 60));
    
    setNodes(prev => prev.map(n => 
      n.id === draggedNode ? { ...n, x: newX, y: newY } : n
    ));
  }, [isDragging, draggedNode, dragOffset]);

  const handleMouseUp = () => {
    setIsDragging(false);
    setDraggedNode(null);
  };

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove]);

  const addNewNode = (type) => {
    const newNode = {
      id: Date.now(),
      type,
      title: `New ${type}`,
      x: 100 + Math.random() * 200,
      y: 100 + Math.random() * 100,
      connections: [],
    };
    setNodes(prev => [...prev, newNode]);
    addLog("info", `Created new ${type} node`);
  };

  const deleteNode = (id) => {
    setNodes(prev => prev.filter(n => n.id !== id).map(n => ({
      ...n,
      connections: n.connections.filter(c => c !== id)
    })));
    setSelectedNode(null);
    addLog("info", "Node deleted");
  };

  const getNodeIcon = (type) => {
    switch (type) {
      case "document": return <FileText size={18} />;
      case "api": return <Globe size={18} />;
      case "database": return <Database size={18} />;
      case "image": return <ImageIcon size={18} />;
      case "audio": return <Zap size={18} />;
      default: return <Circle size={18} />;
    }
  };

  useEffect(() => { 
    addLog("info", "Research graph initialized");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card research-panel">
      <div className="workspace-card-title">Knowledge Graph</div>
      
      {/* Node Type Toolbar */}
      <div className="node-toolbar">
        <button className="node-add-btn" onClick={() => addNewNode("document")} title="Add Document">
          <FileText size={14} /> Doc
        </button>
        <button className="node-add-btn" onClick={() => addNewNode("api")} title="Add API">
          <Globe size={14} /> API
        </button>
        <button className="node-add-btn" onClick={() => addNewNode("database")} title="Add Database">
          <Database size={14} /> DB
        </button>
        <div className="toolbar-divider" />
        <div className="dropzone-hint">
          <Upload size={14} /> Drop files to add nodes
        </div>
      </div>

      {/* Canvas */}
      <div 
        ref={canvasRef}
        className="node-canvas"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {/* Connection Lines */}
        <svg className="connection-lines">
          {nodes.map(node => 
            node.connections.map(targetId => {
              const target = nodes.find(n => n.id === targetId);
              if (!target) return null;
              return (
                <line
                  key={`${node.id}-${targetId}`}
                  x1={node.x + 60}
                  y1={node.y + 30}
                  x2={target.x + 60}
                  y2={target.y + 30}
                  className="connection-line"
                />
              );
            })
          )}
        </svg>

        {/* Nodes */}
        {nodes.map(node => (
          <div
            key={node.id}
            className={`graph-node ${node.type} ${selectedNode === node.id ? 'selected' : ''}`}
            style={{ left: node.x, top: node.y }}
            onMouseDown={(e) => handleNodeMouseDown(e, node)}
          >
            <div className="node-icon">{getNodeIcon(node.type)}</div>
            <div className="node-title">{node.title}</div>
            {selectedNode === node.id && (
              <button className="node-delete" onClick={() => deleteNode(node.id)}>
                <Trash2 size={12} />
              </button>
            )}
          </div>
        ))}

        {nodes.length === 0 && (
          <div className="canvas-empty">
            <Upload size={32} />
            <p>Drop files here or use the toolbar to add nodes</p>
          </div>
        )}
      </div>
    </div>
  );
};

const AssetsPanel = ({ addLog }) => {
  const [assets, setAssets] = useState([
    { type: "image", path: "/assets/logo.png", source: "Generated" },
    { type: "audio", path: "/assets/notification.mp3", source: "TTS Provider" },
    { type: "image", path: "/assets/icon_set.svg", source: "Generated" },
  ]);

  useEffect(() => { 
    addLog("info", "Asset registry loaded");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Generated Assets</div>
      <div className="item-list">
        {assets.length === 0 ? (
          <div className="item-empty">No assets registered yet.</div>
        ) : (
          assets.slice().reverse().map((a, i) => (
            <div className="item-row" key={i}>
              <span className={`item-badge ${a.type}`}>{a.type}</span>
              <span className="item-name">{a.path || "—"}</span>
              <span className="item-meta">{a.source || ""}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const DeploymentPanel = ({ addLog }) => {
  const [deployments, setDeployments] = useState([
    { id: "dep_001", project: "AgentForgeOS", version: "1.0.0", target: "staging", status: "done", initiated_at: new Date().toISOString() },
  ]);
  const [project, setProject] = useState("");
  const [version, setVersion] = useState("");
  const [target, setTarget] = useState("local");

  const deploy = () => {
    const newDep = { 
      id: `dep_${Date.now()}`, 
      project: project || "default", 
      version: version || "0.0.1", 
      target, 
      status: "pending", 
      initiated_at: new Date().toISOString() 
    };
    setDeployments(prev => [...prev, newDep]);
    addLog("info", `Deployment initiated: ${newDep.project} → ${newDep.target}`);
    setProject(""); setVersion("");
  };

  useEffect(() => { 
    addLog("info", "Deployment manager loaded");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Deployments</div>
      <div className="panel-actions">
        <input className="input" placeholder="Project" value={project} onChange={(e) => setProject(e.target.value)} />
        <input className="input" placeholder="Version" value={version} onChange={(e) => setVersion(e.target.value)} />
        <select className="select" value={target} onChange={(e) => setTarget(e.target.value)}>
          <option value="local">local</option>
          <option value="staging">staging</option>
          <option value="production">production</option>
        </select>
        <button className="btn btn-danger" onClick={deploy} data-testid="deploy-btn">Deploy</button>
      </div>
      <div className="item-list">
        {deployments.length === 0 ? (
          <div className="item-empty">No deployments yet.</div>
        ) : (
          deployments.slice().reverse().map((d, i) => (
            <div className="item-row" key={i}>
              <span className={`item-badge ${d.status}`}>{d.status}</span>
              <span className="item-name">{d.project} → {d.target}</span>
              <span className="item-meta">v{d.version}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// EMERGENT-INSPIRED SANDBOX PANEL
const SandboxPanel = ({ addLog }) => {
  const [prompt, setPrompt] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [buildSteps, setBuildSteps] = useState([
    { id: 1, name: "Initialize", status: "done", output: "Environment ready" },
    { id: 2, name: "Parse Request", status: "done", output: "Request parsed successfully" },
    { id: 3, name: "Generate", status: "idle", output: "" },
    { id: 4, name: "Validate", status: "idle", output: "" },
    { id: 5, name: "Deploy", status: "idle", output: "" },
  ]);
  const [preview, setPreview] = useState(null);
  const [consoleOutput, setConsoleOutput] = useState([
    { type: "system", text: "Sandbox initialized. Ready for experimentation." },
  ]);

  const runExperiment = () => {
    if (!prompt.trim() || isRunning) return;
    
    setIsRunning(true);
    setConsoleOutput(prev => [...prev, { type: "user", text: `> ${prompt}` }]);
    addLog("info", "Sandbox experiment started");
    
    // Simulate build process
    let stepIndex = 2;
    const runStep = () => {
      if (stepIndex >= buildSteps.length) {
        setIsRunning(false);
        setPreview({ type: "component", content: prompt });
        setConsoleOutput(prev => [...prev, 
          { type: "success", text: "Build complete! Preview ready." }
        ]);
        addLog("success", "Sandbox build complete");
        return;
      }
      
      setBuildSteps(prev => prev.map((s, i) => 
        i === stepIndex ? { ...s, status: "running" } : s
      ));
      
      setTimeout(() => {
        setBuildSteps(prev => {
          const stepName = prev[stepIndex]?.name || `Step ${stepIndex + 1}`;
          setConsoleOutput(c => [...c, 
            { type: "info", text: `[${stepName}] Completed` }
          ]);
          return prev.map((s, i) => 
            i === stepIndex ? { ...s, status: "done", output: `Step ${i + 1} completed` } : s
          );
        });
        stepIndex++;
        runStep();
      }, 800 + Math.random() * 400);
    };
    
    setBuildSteps(prev => prev.map((s, i) => i >= 2 ? { ...s, status: "idle", output: "" } : s));
    setTimeout(runStep, 500);
    setPrompt("");
  };

  const resetSandbox = () => {
    setBuildSteps(prev => prev.map((s, i) => 
      i < 2 ? s : { ...s, status: "idle", output: "" }
    ));
    setPreview(null);
    setConsoleOutput([{ type: "system", text: "Sandbox reset. Ready for new experiment." }]);
    addLog("info", "Sandbox reset");
  };

  useEffect(() => { 
    addLog("info", "Sandbox environment ready");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card sandbox-panel">
      <div className="workspace-card-title">Agent Sandbox</div>
      
      <div className="sandbox-layout">
        {/* Left: Build Pipeline */}
        <div className="sandbox-pipeline">
          <div className="pipeline-header">
            <Terminal size={14} /> Build Pipeline
          </div>
          <div className="pipeline-steps">
            {buildSteps.map((step, i) => (
              <div key={step.id} className={`pipeline-step ${step.status}`}>
                <div className="step-indicator">
                  {step.status === "running" ? (
                    <div className="step-spinner" />
                  ) : step.status === "done" ? (
                    <Circle size={12} fill="currentColor" />
                  ) : (
                    <Circle size={12} />
                  )}
                </div>
                <div className="step-info">
                  <span className="step-name">{step.name}</span>
                  {step.output && <span className="step-output">{step.output}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center: Preview */}
        <div className="sandbox-preview">
          <div className="preview-header">
            <Eye size={14} /> Live Preview
          </div>
          <div className="preview-canvas">
            {preview ? (
              <div className="preview-content">
                <div className="preview-mock-component">
                  <div className="mock-header">Generated Component</div>
                  <div className="mock-body">
                    <Code size={24} />
                    <p>"{preview.content.slice(0, 100)}..."</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="preview-empty">
                <Box size={32} />
                <p>Run an experiment to see the preview</p>
              </div>
            )}
          </div>
        </div>

        {/* Right: Console */}
        <div className="sandbox-console">
          <div className="console-header">
            <Code size={14} /> Output Console
          </div>
          <div className="console-output">
            {consoleOutput.map((line, i) => (
              <div key={i} className={`console-line ${line.type}`}>
                {line.text}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="sandbox-input-area">
        <textarea 
          className="sandbox-input"
          placeholder="Describe what you want to build... (e.g., 'Create a user authentication form with email and password')"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={2}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); runExperiment(); } }}
        />
        <div className="sandbox-controls">
          <button className="btn btn-secondary" onClick={resetSandbox} disabled={isRunning}>
            <Square size={14} /> Reset
          </button>
          <button className="btn btn-primary" onClick={runExperiment} disabled={isRunning || !prompt.trim()}>
            {isRunning ? <div className="btn-spinner" /> : <Play size={14} />}
            {isRunning ? "Building..." : "Run Experiment"}
          </button>
        </div>
      </div>
    </div>
  );
};

const GameDevPanel = ({ addLog }) => {
  const [projects, setProjects] = useState([
    { id: "game_001", title: "Cyber Runner", genre: "platformer", platform: "cross-platform", status: "done", created_at: new Date().toISOString() },
  ]);
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("");
  const [platform, setPlatform] = useState("cross-platform");

  const createDesign = () => {
    const newProject = { 
      id: `game_${Date.now()}`, 
      title: title || "Untitled Game", 
      genre: genre || "unknown", 
      platform, 
      status: "pending", 
      created_at: new Date().toISOString() 
    };
    setProjects(prev => [...prev, newProject]);
    addLog("info", `Game design created: ${newProject.title}`);
    setTitle(""); setGenre("");
  };

  useEffect(() => { 
    addLog("info", "Game development module loaded");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Game Development</div>
      <div className="panel-actions">
        <input className="input" placeholder="Game title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input className="input" placeholder="Genre" value={genre} onChange={(e) => setGenre(e.target.value)} />
        <select className="select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="cross-platform">cross-platform</option>
          <option value="pc">PC</option>
          <option value="mobile">mobile</option>
          <option value="web">web</option>
        </select>
        <button className="btn btn-primary" onClick={createDesign}>Create Design Doc</button>
      </div>
      <div className="item-list">
        {projects.length === 0 ? (
          <div className="item-empty">No projects yet.</div>
        ) : (
          projects.slice().reverse().map((p, i) => (
            <div className="item-row" key={i}>
              <span className={`item-badge ${p.status}`}>{p.status}</span>
              <span className="item-name">{p.title}</span>
              <span className="item-meta">{p.genre} · {p.platform}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const SaasBuilderPanel = ({ addLog }) => {
  const [projects, setProjects] = useState([
    { id: "saas_001", name: "TaskFlow Pro", stack: { frontend: "react", backend: "fastapi" }, status: "done", created_at: new Date().toISOString() },
  ]);
  const [name, setName] = useState("");
  const [frontend, setFrontend] = useState("react");
  const [backend, setBackend] = useState("fastapi");

  const scaffold = () => {
    const newProject = { 
      id: `saas_${Date.now()}`, 
      name: name || "Untitled SaaS", 
      stack: { frontend, backend, db: "postgres" }, 
      status: "pending", 
      created_at: new Date().toISOString() 
    };
    setProjects(prev => [...prev, newProject]);
    addLog("info", `SaaS scaffolded: ${newProject.name}`);
    setName("");
  };

  useEffect(() => { 
    addLog("info", "SaaS Builder ready");
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">SaaS Builder</div>
      <div className="panel-actions">
        <input className="input" placeholder="Project name" value={name} onChange={(e) => setName(e.target.value)} style={{ flex: 1 }} />
        <select className="select" value={frontend} onChange={(e) => setFrontend(e.target.value)}>
          <option value="react">React</option>
          <option value="vue">Vue</option>
          <option value="svelte">Svelte</option>
        </select>
        <select className="select" value={backend} onChange={(e) => setBackend(e.target.value)}>
          <option value="fastapi">FastAPI</option>
          <option value="express">Express</option>
          <option value="django">Django</option>
        </select>
        <button className="btn btn-primary" onClick={scaffold}>Scaffold Project</button>
      </div>
      <div className="item-list">
        {projects.length === 0 ? (
          <div className="item-empty">No projects yet.</div>
        ) : (
          projects.slice().reverse().map((p, i) => (
            <div className="item-row" key={i}>
              <span className={`item-badge ${p.status}`}>{p.status}</span>
              <span className="item-name">{p.name}</span>
              <span className="item-meta">{p.stack?.frontend} + {p.stack?.backend}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Main Workspace
const Workspace = ({ module, addLog }) => {
  const panels = {
    studio: StudioPanel,
    builds: BuildsPanel,
    research: ResearchPanel,
    assets: AssetsPanel,
    deployment: DeploymentPanel,
    sandbox: SandboxPanel,
    game_dev: GameDevPanel,
    saas_builder: SaasBuilderPanel,
  };

  const Panel = panels[module?.id];

  return (
    <section className="workspace">
      <div className="workspace-header">
        <h1 className="workspace-title">{module?.name || "Select Module"}</h1>
        {module && <span className="workspace-version">v1.0</span>}
      </div>
      <p className="workspace-desc">{module?.description || "Select a module from the sidebar to begin."}</p>
      {Panel ? <Panel addLog={addLog} /> : (
        <div className="workspace-card">
          <div className="item-empty">Select a module from the sidebar.</div>
        </div>
      )}
    </section>
  );
};

// Agent Console - 12 Core Agents with Avatars
const AGENTS = [
  { id: "planner", name: "Project Planner", shortName: "Planner", avatar: "https://images.unsplash.com/photo-1605504836193-e77d3d9ede8a?w=100&h=100&fit=crop" },
  { id: "architect", name: "System Architect", shortName: "Architect", avatar: "https://images.unsplash.com/photo-1749133218238-f90d8a742c3a?w=100&h=100&fit=crop" },
  { id: "router", name: "Task Router", shortName: "Router", avatar: "https://images.unsplash.com/photo-1745441888183-c217893cfe48?w=100&h=100&fit=crop" },
  { id: "builder", name: "Module Builder", shortName: "Builder", avatar: "https://images.unsplash.com/photo-1697759042426-848c5f3b68b3?w=100&h=100&fit=crop" },
  { id: "api", name: "API Architect", shortName: "API", avatar: "https://images.unsplash.com/photo-1737574994780-e31827afaed7?w=100&h=100&fit=crop" },
  { id: "data", name: "Data Architect", shortName: "Data", avatar: "https://images.unsplash.com/photo-1593524843106-11f37c8bf6e0?w=100&h=100&fit=crop" },
  { id: "backend", name: "Backend Engineer", shortName: "Backend", avatar: "https://images.unsplash.com/photo-1743116591535-06e9c9aca4a4?w=100&h=100&fit=crop" },
  { id: "frontend", name: "Frontend Engineer", shortName: "Frontend", avatar: "https://images.unsplash.com/photo-1731419223715-aec6664f9011?w=100&h=100&fit=crop" },
  { id: "ai", name: "AI Integration Engineer", shortName: "AI Eng", avatar: "https://images.unsplash.com/photo-1565687981296-535f09db714e?w=100&h=100&fit=crop" },
  { id: "tester", name: "Integration Tester", shortName: "Tester", avatar: "https://images.unsplash.com/photo-1762709117664-985ffc56bc7f?w=100&h=100&fit=crop" },
  { id: "auditor", name: "Security Auditor", shortName: "Auditor", avatar: "https://images.unsplash.com/photo-1650075990015-af095f1659e3?w=100&h=100&fit=crop" },
  { id: "stabilizer", name: "System Stabilizer", shortName: "Stabilizer", avatar: "https://images.unsplash.com/photo-1608662867938-f50663c033f0?w=100&h=100&fit=crop" },
];

const AgentConsole = ({ addLog }) => {
  const [messages, setMessages] = useState([
    { role: "agent", agentId: "planner", text: "Hey! AgentForgeOS is ready. What are we building today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState(AGENTS[0]);
  const messagesRef = useRef(null);

  const getAgent = (id) => AGENTS.find(a => a.id === id) || AGENTS[0];

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const prompt = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: prompt }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      const text = data?.data?.data?.text || data?.data?.error || data?.error || "Processing your request...";
      setMessages((prev) => [...prev, { role: "agent", agentId: activeAgent.id, text }]);
      addLog("info", `${activeAgent.name} responded`);
    } catch (err) {
      // Mock response - rotate through agents for realistic feel
      const responses = [
        { agentId: "planner", text: `Got it! Planning out "${prompt.slice(0, 30)}..." — routing to the team.` },
        { agentId: "architect", text: `I'll design the architecture for this. Looks like we need a modular approach.` },
        { agentId: "backend", text: `Setting up the backend infrastructure now. APIs coming up.` },
        { agentId: "frontend", text: `On it! Building out the UI components for this feature.` },
      ];
      const response = responses[Math.floor(Math.random() * responses.length)];
      setMessages((prev) => [...prev, { role: "agent", ...response }]);
      setActiveAgent(getAgent(response.agentId));
      addLog("info", `${getAgent(response.agentId).name} processing request`);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="panel-content">
      <div className="panel-title-row">
        <span className="panel-title">Agent Console</span>
        <div className="agent-selector">
          {AGENTS.slice(0, 6).map(agent => (
            <button
              key={agent.id}
              className={`agent-chip ${activeAgent.id === agent.id ? 'active' : ''}`}
              onClick={() => setActiveAgent(agent)}
              title={agent.name}
            >
              <img src={agent.avatar} alt={agent.name} className="agent-chip-avatar" />
            </button>
          ))}
          <span className="agent-more">+6</span>
        </div>
      </div>
      <div className="console-messages" ref={messagesRef}>
        {messages.map((msg, i) => {
          const agent = msg.agentId ? getAgent(msg.agentId) : AGENTS[0];
          return (
            <div key={i} className={`console-msg ${msg.role}`}>
              {msg.role === "agent" && (
                <img src={agent.avatar} alt={agent.name} className="console-avatar" />
              )}
              <div className="console-msg-content">
                <span className="console-msg-role">{msg.role === "user" ? "You" : agent.shortName}</span>
                <p className="console-msg-text">{msg.text}</p>
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="console-msg agent">
            <img src={activeAgent.avatar} alt={activeAgent.name} className="console-avatar" />
            <div className="console-msg-content">
              <span className="console-msg-role">{activeAgent.shortName}</span>
              <p className="console-msg-text typing">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </p>
            </div>
          </div>
        )}
      </div>
      <form className="console-form" onSubmit={sendMessage}>
        <textarea
          className="console-input"
          placeholder="Type a prompt..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={1}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(e); } }}
          data-testid="console-input"
        />
        <button type="submit" className="console-send" disabled={loading} data-testid="console-send">
          {loading ? "..." : <Send size={16} />}
        </button>
      </form>
    </div>
  );
};

// Pipeline Monitor
const PipelineMonitor = ({ logs }) => {
  const [activeStage, setActiveStage] = useState(null);
  const logsRef = useRef(null);

  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="panel-content">
      <div className="panel-title">Pipeline Monitor</div>
      <div className="pipeline-stages">
        {PIPELINE_STAGES.map((stage, i) => (
          <span key={i} className={`pipeline-chip ${stage === activeStage ? "active" : ""}`}>
            {stage}
          </span>
        ))}
      </div>
    </div>
  );
};

// Output Log Panel (New 3rd bottom panel)
const OutputLog = ({ logs }) => {
  const logsRef = useRef(null);

  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="panel-content">
      <div className="panel-title">Output Log</div>
      <div className="output-log" ref={logsRef}>
        {logs.map((log, i) => (
          <div key={i} className="log-entry">
            <span className="log-ts">{log.time}</span>
            <span className={`log-lvl ${log.level}`}>[{log.level.toUpperCase()}]</span>
            <span className="log-msg">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main App with Resizable Panels
const Studio = () => {
  const [activeModule, setActiveModule] = useState(MODULES[0]);
  const [logs, setLogs] = useState([{ time: formatTime(), level: "info", message: "AgentForgeOS initialized" }]);

  const addLog = (level, message) => {
    setLogs((prev) => [...prev.slice(-50), { time: formatTime(), level, message }]);
  };

  return (
    <div className="studio-layout" data-testid="studio-layout">
      <NavBar />
      <ResizablePanelGroup direction="vertical" className="studio-resizable-main">
        {/* Top: Sidebar + Workspace */}
        <ResizablePanel defaultSize={70} minSize={40}>
          <ResizablePanelGroup direction="horizontal">
            <ResizablePanel defaultSize={15} minSize={10} maxSize={25}>
              <Sidebar activeModule={activeModule} setActiveModule={setActiveModule} />
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel defaultSize={85}>
              <Workspace module={activeModule} addLog={addLog} />
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
        
        <ResizableHandle className="resize-handle-vertical" />
        
        {/* Bottom: 3-way split */}
        <ResizablePanel defaultSize={30} minSize={15} maxSize={50}>
          <ResizablePanelGroup direction="horizontal" className="studio-bottom-panels">
            <ResizablePanel defaultSize={33} minSize={20}>
              <div className="panel">
                <AgentConsole addLog={addLog} />
              </div>
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel defaultSize={34} minSize={20}>
              <div className="panel">
                <PipelineMonitor logs={logs} />
              </div>
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel defaultSize={33} minSize={20}>
              <div className="panel">
                <OutputLog logs={logs} />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Studio />} />
          <Route path="*" element={<Studio />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
