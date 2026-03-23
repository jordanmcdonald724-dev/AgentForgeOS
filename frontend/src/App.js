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
  Circle, GitBranch, Link2, Trash2, Eye, Code, Terminal,
  X, Clock, Star, Folder, Check, AlertTriangle, Activity,
  Server, HardDrive, Wifi, WifiOff, Key, Palette, Bell,
  Keyboard, Monitor, Moon, Sun, Volume2, Shield, Lock,
  Mail, Calendar, BarChart3, TrendingUp, Award, Target,
  ChevronLeft, Sparkles, Download, ExternalLink, CheckCircle2,
  XCircle, ArrowRight, Radio, Mic, Bot, Cog
} from "lucide-react";
import { useSystemEvents } from "./hooks/useWebSocket";

const resolveBackendBase = () => {
  try {
    const stored = localStorage.getItem("agentforge_backend_url");
    if (stored && typeof stored === "string" && stored.trim()) return stored.trim();
  } catch (e) {
  }
  const viteUrl = typeof import.meta !== "undefined" ? import.meta.env?.VITE_BACKEND_URL : "";
  if (viteUrl) return viteUrl;
  if (typeof process !== "undefined" && process.env?.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  try {
    if (typeof window !== "undefined") {
      const proto = window.location?.protocol || "";
      const port = window.location?.port || "";
      const isVite = port === "5173" || port === "5174" || port === "5175";
      if ((proto === "http:" || proto === "https:") && !isVite) {
        return window.location.origin;
      }
    }
  } catch (e) {
  }
  return "http://127.0.0.1:8000";
};

const BACKEND_URL = (resolveBackendBase() || "").replace(/\/$/, "");
const API = BACKEND_URL ? `${BACKEND_URL}/api` : "/api";
const LOGO_URL = "https://customer-assets.emergentagent.com/job_agent-builder-os/artifacts/nc1ky769_Flux_Dev_Design_a_premium_technology_platform_logo_for_an_AI_d_0.jpg";

const apiFetch = (path, init = {}) => {
  const url = typeof path === "string" && path.startsWith("http")
    ? path
    : `${API}${String(path).startsWith("/") ? String(path) : `/${String(path)}`}`;
  return fetch(url, { credentials: "include", ...init });
};

const getAgentRunDefaultProvider = () => {
  try {
    const v = localStorage.getItem("agentforge_agent_run_provider");
    return typeof v === "string" ? v : "";
  } catch (e) {
    return "";
  }
};

const setAgentRunDefaultProvider = (provider) => {
  try {
    if (!provider) {
      localStorage.removeItem("agentforge_agent_run_provider");
      return;
    }
    localStorage.setItem("agentforge_agent_run_provider", String(provider));
  } catch (e) {
  }
};

const getAgentRunProviderPayload = () => {
  const p = (getAgentRunDefaultProvider() || "").trim().toLowerCase();
  if (p === "router") return { provider: "router" };
  return {};
};

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

const localGet = (key, fallback = null) => {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch (e) {
    return fallback;
  }
};

const localSet = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
  }
};

// ===============================================
// MODAL PAGES FOR TOP NAVIGATION
// ===============================================

// Modal Container
const Modal = ({ isOpen, onClose, title, size = "md", children }) => {
  const containerRef = useRef(null);
  const previouslyFocusedElementRef = useRef(null);
  const titleIdRef = useRef(`modal-title-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const container = containerRef.current;
    if (!container) {
      return;
    }

    // Save the element that was focused before opening the modal
    previouslyFocusedElementRef.current = document.activeElement;

    const focusableSelectors =
      'a[href], area[href], input:not([disabled]):not([type="hidden"]), select:not([disabled]), ' +
      'textarea:not([disabled]), button:not([disabled]), iframe, object, embed, ' +
      '*[tabindex]:not([tabindex="-1"]), *[contenteditable=true]';

    const getFocusableElements = () => {
      return Array.from(container.querySelectorAll(focusableSelectors)).filter(
        (el) => !el.hasAttribute("disabled") && el.getAttribute("aria-hidden") !== "true"
      );
    };

    const focusableElements = getFocusableElements();
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    } else {
      container.focus();
    }

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
        return;
      }

      if (event.key === "Tab") {
        const elements = getFocusableElements();
        if (elements.length === 0) {
          event.preventDefault();
          return;
        }

        const firstElement = elements[0];
        const lastElement = elements[elements.length - 1];
        const isShift = event.shiftKey;
        const current = document.activeElement;

        if (!isShift && current === lastElement) {
          event.preventDefault();
          firstElement.focus();
        } else if (isShift && current === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      }
    };

    container.addEventListener("keydown", handleKeyDown);

    return () => {
      container.removeEventListener("keydown", handleKeyDown);
      const previouslyFocused = previouslyFocusedElementRef.current;
      if (
        previouslyFocused &&
        typeof previouslyFocused.focus === "function"
      ) {
        previouslyFocused.focus();
      }
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={`modal-container modal-size-${size}`}
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleIdRef.current}
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 className="modal-title" id={titleIdRef.current}>
            {title}
          </h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>
  );
};

// 1. PROJECT PAGE
const ProjectPage = ({ isOpen, onClose, addLog }) => {
  const [projects, setProjects] = useState([
    { id: 1, name: "AgentForgeOS", path: "/projects/agentforge", lastOpened: "2 hours ago", starred: true },
    { id: 2, name: "GameEngine Module", path: "/projects/game-engine", lastOpened: "Yesterday", starred: false },
    { id: 3, name: "SaaS Template", path: "/projects/saas-template", lastOpened: "3 days ago", starred: true },
  ]);
  const [newProjectName, setNewProjectName] = useState("");
  const [activeTab, setActiveTab] = useState("recent");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isOpen) return;
    const s = localGet("agentforge_project_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.activeTab === "string") setActiveTab(s.activeTab);
      if (typeof s.newProjectName === "string") setNewProjectName(s.newProjectName);
      if (Array.isArray(s.starredNames)) {
        setProjects((prev) =>
          prev.map((p) => ({
            ...p,
            starred: s.starredNames.includes(p.name),
          }))
        );
      }
    } catch (e) {}
  }, [isOpen]);

  useEffect(() => {
    const starredNames = projects.filter((p) => p.starred).map((p) => p.name);
    localSet("agentforge_project_state", { activeTab, newProjectName, starredNames });
  }, [activeTab, newProjectName, projects]);

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await apiFetch("/projects");
        const data = await res.json();
        const names = data?.data?.projects;
        if (!cancelled && data?.success && Array.isArray(names)) {
          setProjects((prev) => {
            const starredByName = new Map(prev.map((p) => [p.name, !!p.starred]));
            return names.map((name, idx) => ({
              id: idx + 1,
              name,
              path: `/projects/${name}`,
              lastOpened: "",
              starred: starredByName.get(name) || false,
            }));
          });
        }
      } catch (e) {
        if (!cancelled) setError("Failed to load projects");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  const createProject = async () => {
    if (!newProjectName.trim()) return;
    setError("");
    try {
      const res = await apiFetch("/projects/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newProjectName.trim() }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Create failed");
      setProjects((prev) => [
        { id: Date.now(), name: data?.data?.id || newProjectName.trim(), path: data?.data?.path || "", lastOpened: "Just now", starred: false },
        ...prev,
      ]);
      addLog("info", `Project created: ${newProjectName.trim()}`);
      setNewProjectName("");
      setActiveTab("recent");
    } catch (e) {
      setError(e.message || "Create failed");
      const newProject = {
        id: Date.now(),
        name: newProjectName,
        path: `/projects/${newProjectName.toLowerCase().replace(/\s+/g, '-')}`,
        lastOpened: "Just now",
        starred: false
      };
      setProjects([newProject, ...projects]);
      setNewProjectName("");
      addLog("info", `Project created: ${newProjectName}`);
    }
  };

  const toggleStar = (id) => {
    setProjects(projects.map(p => p.id === id ? { ...p, starred: !p.starred } : p));
  };

  const openProject = (project) => {
    addLog("info", `Opened project: ${project.name}`);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Project Manager" size="sm">
      <div className="page-tabs">
        <button className={`page-tab ${activeTab === 'recent' ? 'active' : ''}`} onClick={() => setActiveTab('recent')}>
          <Clock size={14} /> Recent
        </button>
        <button className={`page-tab ${activeTab === 'starred' ? 'active' : ''}`} onClick={() => setActiveTab('starred')}>
          <Star size={14} /> Starred
        </button>
        <button className={`page-tab ${activeTab === 'new' ? 'active' : ''}`} onClick={() => setActiveTab('new')}>
          <Plus size={14} /> New Project
        </button>
      </div>

      {activeTab === 'new' && (
        <div className="page-section">
          {error && <div className="item-empty">{error}</div>}
          <div className="form-group">
            <label>Project Name</label>
            <input 
              className="input" 
              placeholder="My Awesome Project" 
              value={newProjectName} 
              onChange={(e) => setNewProjectName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Template</label>
            <div className="template-grid">
              <div className="template-card active">
                <Layout size={24} />
                <span>Blank Project</span>
              </div>
              <div className="template-card">
                <Gamepad2 size={24} />
                <span>Game Dev</span>
              </div>
              <div className="template-card">
                <Building2 size={24} />
                <span>SaaS Starter</span>
              </div>
              <div className="template-card">
                <Globe size={24} />
                <span>API Service</span>
              </div>
            </div>
          </div>
          <button className="btn btn-primary" onClick={createProject} style={{ width: '100%' }}>
            <Plus size={14} /> Create Project
          </button>
        </div>
      )}

      {(activeTab === 'recent' || activeTab === 'starred') && (
        <div className="project-list">
          {loading && <div className="item-empty">Loading...</div>}
          {!loading && error && <div className="item-empty">{error}</div>}
          {projects
            .filter(p => activeTab === 'recent' || p.starred)
            .map(project => (
              <div key={project.id} className="project-card" onClick={() => openProject(project)}>
                <div className="project-icon">
                  <Folder size={20} />
                </div>
                <div className="project-info">
                  <span className="project-name">{project.name}</span>
                  <span className="project-path">{project.path}</span>
                </div>
                <span className="project-time">{project.lastOpened}</span>
                <button 
                  className={`star-btn ${project.starred ? 'starred' : ''}`}
                  onClick={(e) => { e.stopPropagation(); toggleStar(project.id); }}
                >
                  <Star size={16} fill={project.starred ? "currentColor" : "none"} />
                </button>
              </div>
            ))}
        </div>
      )}
    </Modal>
  );
};

// 2. WORKSPACE PAGE
const WorkspacePage = ({ isOpen, onClose, addLog }) => {
  const [layout, setLayout] = useState("default");
  const [activeModules, setActiveModules] = useState(["studio", "builds", "research", "sandbox"]);
  const [workspaceStatus, setWorkspaceStatus] = useState(null);
  const [workspacePath, setWorkspacePath] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const layouts = [
    { id: "default", name: "Default", desc: "Sidebar + Workspace + 3-Panel Bottom" },
    { id: "focused", name: "Focused", desc: "Maximized workspace, minimal UI" },
    { id: "split", name: "Split View", desc: "Side-by-side workspaces" },
    { id: "compact", name: "Compact", desc: "Condensed layout for smaller screens" },
  ];

  const toggleModule = (id) => {
    setActiveModules(prev => 
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const applyLayout = (layoutId) => {
    setLayout(layoutId);
    addLog("info", `Layout changed to: ${layouts.find(l => l.id === layoutId)?.name}`);
  };

  useEffect(() => {
    if (!isOpen) return;
    const savedLayout = localStorage.getItem("agentforge_workspace_layout");
    const savedModules = localStorage.getItem("agentforge_workspace_modules");
    if (savedLayout) setLayout(savedLayout);
    if (savedModules) {
      try {
        const parsed = JSON.parse(savedModules);
        if (Array.isArray(parsed)) setActiveModules(parsed);
      } catch (e) {
      }
    }
    const draftPath = localGet("agentforge_workspace_path_draft", "");
    if (typeof draftPath === "string" && draftPath) setWorkspacePath(draftPath);
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await apiFetch("/workspace/status");
        const data = await res.json();
        if (!data?.success) throw new Error(data?.error || "Failed to load workspace");
        if (cancelled) return;
        setWorkspaceStatus(data.data);
        setWorkspacePath(data.data?.workspace_path || "");
      } catch (e) {
        if (!cancelled) setError(e.message || "Failed to load workspace");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  useEffect(() => {
    localStorage.setItem("agentforge_workspace_layout", layout);
    localStorage.setItem("agentforge_workspace_modules", JSON.stringify(activeModules));
  }, [activeModules, layout]);

  useEffect(() => {
    localSet("agentforge_workspace_path_draft", workspacePath);
  }, [workspacePath]);

  const saveWorkspace = async () => {
    if (!workspacePath.trim() || saving) return;
    setSaving(true);
    setError("");
    try {
      const res = await apiFetch("/workspace/set", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_path: workspacePath.trim() }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Save failed");
      addLog("success", "Workspace path saved");
      const statusRes = await apiFetch("/workspace/status");
      const statusData = await statusRes.json();
      if (statusData?.success) setWorkspaceStatus(statusData.data);
      onClose();
    } catch (e) {
      setError(e.message || "Save failed");
      addLog("error", "Workspace save failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Workspace Configuration">
      <div className="page-section">
        <h3 className="section-title">Layout Presets</h3>
        <div className="layout-grid">
          {layouts.map(l => (
            <div 
              key={l.id} 
              className={`layout-card ${layout === l.id ? 'active' : ''}`}
              onClick={() => applyLayout(l.id)}
            >
              <div className="layout-preview">
                <Monitor size={32} />
              </div>
              <span className="layout-name">{l.name}</span>
              <span className="layout-desc">{l.desc}</span>
              {layout === l.id && <Check size={16} className="layout-check" />}
            </div>
          ))}
        </div>
      </div>

      <div className="page-section">
        <h3 className="section-title">Active Modules</h3>
        <p className="section-desc">Toggle which modules appear in the sidebar</p>
        <div className="module-toggles">
          {MODULES.map(mod => {
            const Icon = mod.icon;
            return (
              <div 
                key={mod.id} 
                className={`module-toggle ${activeModules.includes(mod.id) ? 'active' : ''}`}
                onClick={() => toggleModule(mod.id)}
              >
                <Icon size={18} />
                <span>{mod.name}</span>
                <div className="toggle-switch">
                  <div className="toggle-knob" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <details className="advanced-details">
        <summary className="advanced-summary">Advanced</summary>
        <div className="page-section">
          <h3 className="section-title">Workspace</h3>
          {loading && <div className="item-empty">Loading...</div>}
          {!loading && error && <div className="item-empty">{error}</div>}
          <div className="form-row">
            <label>Workspace path</label>
            <input className="input" value={workspacePath} onChange={(e) => setWorkspacePath(e.target.value)} />
            <button className="btn btn-primary" onClick={saveWorkspace} disabled={saving || !workspacePath.trim()}>
              {saving ? "Saving..." : "Save"}
            </button>
          </div>
          {workspaceStatus?.projects?.length ? (
            <div className="item-empty">{workspaceStatus.projects.length} projects detected</div>
          ) : null}
        </div>
        <div className="page-section">
          <h3 className="section-title">Quick Actions</h3>
          <div className="quick-actions">
            <button className="btn btn-secondary">
              <Upload size={14} /> Export Layout
            </button>
            <button className="btn btn-secondary">
              <FolderOpen size={14} /> Import Layout
            </button>
            <button className="btn btn-danger">
              Reset to Default
            </button>
          </div>
        </div>
      </details>
    </Modal>
  );
};

// 3. PROVIDERS PAGE
const ProvidersPage = ({ isOpen, onClose, addLog }) => {
  const [providers, setProviders] = useState({
    llm: { provider: "ollama", apiKey: "", model: "llama3", status: "disconnected" },
    image: { provider: "comfyui", apiKey: "", endpoint: "http://localhost:8188", status: "disconnected" },
    tts: { provider: "piper", apiKey: "", voice: "", status: "disconnected" },
    embedding: { provider: "ollama", apiKey: "", model: "nomic-embed-text", status: "disconnected" },
  });
  const [useRouterForAgentRuns, setUseRouterForAgentRuns] = useState(false);
  const [saving, setSaving] = useState(false);

  const providerOptions = {
    llm: ["ollama", "openai", "fal", "anthropic", "local"],
    image: ["comfyui", "fal", "replicate", "local"],
    tts: ["piper", "elevenlabs", "openai-tts", "local"],
    embedding: ["ollama", "openai", "local"],
  };

  const updateProvider = (type, field, value) => {
    setProviders(prev => ({
      ...prev,
      [type]: { ...prev[type], [field]: value }
    }));
  };

  const testConnection = (type) => {
    const provider = providers[type];
    addLog("info", `Testing ${type.toUpperCase()} connection to ${provider.provider}...`);
    const key = type === "embedding" ? "llm" : type;
    apiFetch(`/providers/test?type=${encodeURIComponent(key)}`)
      .then((r) => r.json())
      .then((data) => {
        const result = data?.data?.results?.[key];
        const ok = !!result?.ok;
        const newStatus = ok ? "connected" : "error";
        updateProvider(type, "status", newStatus);
        addLog(ok ? "success" : "error", `${type.toUpperCase()} ${ok ? "connected" : "failed"}${result?.detail ? ` (${result.detail})` : ""}`);
      })
      .catch(() => {
        updateProvider(type, "status", "error");
        addLog("error", `${type.toUpperCase()} failed`);
      });
  };

  useEffect(() => {
    if (!isOpen) return;
    setUseRouterForAgentRuns((getAgentRunDefaultProvider() || "").trim().toLowerCase() === "router");
    const localDraft = localGet("agentforge_providers_draft", null);
    if (localDraft && typeof localDraft === "object") {
      try {
        if (typeof localDraft.useRouterForAgentRuns === "boolean") setUseRouterForAgentRuns(localDraft.useRouterForAgentRuns);
        if (localDraft.providers && typeof localDraft.providers === "object") {
          setProviders((prev) => ({
            llm: { ...prev.llm, ...(localDraft.providers.llm || {}) },
            image: { ...prev.image, ...(localDraft.providers.image || {}) },
            tts: { ...prev.tts, ...(localDraft.providers.tts || {}) },
            embedding: { ...prev.embedding, ...(localDraft.providers.embedding || {}) },
          }));
        }
      } catch (e) {}
    }
    Promise.all([apiFetch("/system/status").then((r) => r.json()).catch(() => null), apiFetch("/providers").then((r) => r.json()).catch(() => null), apiFetch("/providers/test").then((r) => r.json()).catch(() => null)])
      .then(([status, prov, test]) => {
        const cfg = status?.data?.config || {};
        const selected = cfg?.providers || {};
        const ollama = cfg?.ollama || {};
        const comfyui = cfg?.comfyui || {};
        const piper = cfg?.piper || {};
        const openai = prov?.data?.providers?.openai || {};
        const fal = prov?.data?.providers?.fal || {};
        const llmSelected = (selected?.llm || "ollama").toString();
        const imageSelected = (selected?.image || "comfyui").toString();
        const ttsSelected = (selected?.tts || "piper").toString();
        const t = test?.data?.results || {};
        setProviders((prev) => ({
          ...prev,
          llm: {
            ...prev.llm,
            provider: llmSelected,
            model: (ollama?.model || openai?.model || fal?.model || prev.llm.model).toString(),
            status: t?.llm?.ok ? "connected" : "disconnected",
          },
          image: {
            ...prev.image,
            provider: imageSelected,
            endpoint: (comfyui?.base_url || prev.image.endpoint).toString(),
            status: t?.image?.ok ? "connected" : "disconnected",
          },
          tts: {
            ...prev.tts,
            provider: ttsSelected,
            voice: (piper?.model_path || prev.tts.voice).toString(),
            status: t?.tts?.ok ? "connected" : "disconnected",
          },
        }));
      })
      .catch(() => {});
  }, [isOpen]);

  useEffect(() => {
    localSet("agentforge_providers_draft", { providers, useRouterForAgentRuns });
  }, [providers, useRouterForAgentRuns]);

  const saveProviders = async () => {
    if (saving) return;
    setSaving(true);
    try {
      const cfg = {};
      if (providers.llm.provider === "openai") {
        cfg.PROVIDER_LLM = "openai";
        if (providers.llm.apiKey) cfg.OPENAI_API_KEY = providers.llm.apiKey;
        if (providers.llm.model) cfg.OPENAI_MODEL = providers.llm.model;
      } else if (providers.llm.provider === "fal") {
        cfg.PROVIDER_LLM = "fal";
        if (providers.llm.apiKey) cfg.FAL_API_KEY = providers.llm.apiKey;
        if (providers.llm.model) cfg.FAL_LLM_MODEL = providers.llm.model;
      } else if (providers.llm.provider === "ollama") {
        cfg.PROVIDER_LLM = "ollama";
        if (providers.llm.model) cfg.OLLAMA_MODEL = providers.llm.model;
      } else if (providers.llm.provider) {
        cfg.PROVIDER_LLM = providers.llm.provider;
      }

      if (providers.image.provider === "fal") {
        cfg.PROVIDER_IMAGE = "fal";
        if (providers.image.apiKey) cfg.FAL_API_KEY = providers.image.apiKey;
      } else if (providers.image.provider === "comfyui") {
        cfg.PROVIDER_IMAGE = "comfyui";
        if (providers.image.endpoint) cfg.COMFYUI_BASE_URL = providers.image.endpoint;
      } else if (providers.image.provider) {
        cfg.PROVIDER_IMAGE = providers.image.provider;
      }

      if (providers.tts.provider === "piper") {
        cfg.PROVIDER_TTS = "piper";
        if (providers.tts.voice) cfg.PIPER_MODEL_PATH = providers.tts.voice;
      } else if (providers.tts.provider) {
        cfg.PROVIDER_TTS = providers.tts.provider;
      }

      const res = await apiFetch("/setup/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config: cfg,
        }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Save failed");
      setAgentRunDefaultProvider(useRouterForAgentRuns ? "router" : "");
      addLog("success", "Providers saved");
      onClose();
    } catch (e) {
      addLog("error", "Providers save failed");
    } finally {
      setSaving(false);
    }
  };

  const ProviderCard = ({ type, title, icon: Icon }) => {
    const p = providers[type];
    return (
      <div className="provider-card">
        <div className="provider-header">
          <Icon size={20} />
          <span className="provider-title">{title}</span>
          <span className={`provider-status ${p.status}`}>
            {p.status === 'connected' ? <Wifi size={14} /> : <WifiOff size={14} />}
            {p.status}
          </span>
        </div>
        <div className="provider-body">
          <div className="form-row">
            <label>Provider</label>
            <select 
              className="select" 
              value={p.provider} 
              onChange={(e) => updateProvider(type, 'provider', e.target.value)}
            >
              {providerOptions[type].map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          {p.provider !== 'local' && p.provider !== 'ollama' && p.provider !== 'piper' && p.provider !== 'comfyui' && (
            <div className="form-row">
              <label>API Key</label>
              <div className="input-with-icon">
                <Key size={14} />
                <input 
                  type="password" 
                  className="input" 
                  placeholder="sk-..." 
                  value={p.apiKey}
                  onChange={(e) => updateProvider(type, 'apiKey', e.target.value)}
                />
              </div>
            </div>
          )}
          <div className="form-row">
            <label>Model / Voice</label>
            <input 
              className="input" 
              value={p.model || p.voice || p.endpoint || ''} 
              onChange={(e) => updateProvider(type, p.model ? 'model' : p.voice ? 'voice' : 'endpoint', e.target.value)}
            />
          </div>
          <button className="btn btn-secondary" onClick={() => testConnection(type)}>
            <Activity size={14} /> Test Connection
          </button>
        </div>
      </div>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="AI Providers">
      <div className="providers-grid">
        <ProviderCard type="llm" title="LLM Provider" icon={Cpu} />
        <ProviderCard type="image" title="Image Generation" icon={ImageIcon} />
        <ProviderCard type="tts" title="Text-to-Speech" icon={Volume2} />
        <ProviderCard type="embedding" title="Embeddings" icon={Database} />
      </div>
      <div className="page-section">
        <div className="provider-note">
          <AlertTriangle size={16} />
          <span>Local providers (Ollama, ComfyUI, Piper) must be running on your machine. No API keys required.</span>
        </div>
      </div>
      <div className="page-section">
        <h3 className="section-title">Agent Run Default</h3>
        <div
          className={`module-toggle ${useRouterForAgentRuns ? "active" : ""}`}
          onClick={() => {
            const next = !useRouterForAgentRuns;
            setUseRouterForAgentRuns(next);
            setAgentRunDefaultProvider(next ? "router" : "");
          }}
        >
          <span className="module-name">Use Model Router for agent runs</span>
          <div className={`toggle-switch ${useRouterForAgentRuns ? "active" : ""}`}>
            <div className="toggle-knob" />
          </div>
        </div>
        <p className="section-desc">When enabled, /api/agent/run uses provider=router automatically.</p>
      </div>
      <div className="page-section">
        <button className="btn btn-primary" onClick={saveProviders} disabled={saving} style={{ width: "100%" }}>
          {saving ? "Saving..." : "Save Providers"}
        </button>
      </div>
    </Modal>
  );
};

// 4. SYSTEM PAGE
const SystemPage = ({ isOpen, onClose, addLog }) => {
  const [services, setServices] = useState([
    { name: "Engine Server", status: "running", port: 8001, uptime: "2h 34m", cpu: "2.3%", memory: "128MB" },
    { name: "Database", status: "running", port: 27017, uptime: "2h 34m", cpu: "0.8%", memory: "256MB" },
    { name: "Bridge Server", status: "running", port: 8080, uptime: "2h 34m", cpu: "0.2%", memory: "64MB" },
    { name: "Worker System", status: "running", port: null, uptime: "2h 34m", cpu: "5.1%", memory: "512MB" },
    { name: "Vector Store", status: "stopped", port: 6333, uptime: "-", cpu: "-", memory: "-" },
  ]);

  const [systemStats, setSystemStats] = useState({
    totalCpu: "8.4%",
    totalMemory: "1.2GB / 16GB",
    activeAgents: 3,
    queuedTasks: 12,
    completedToday: 47,
  });
  const [backendStatus, setBackendStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tasksLoading, setTasksLoading] = useState(false);
  const [tasksError, setTasksError] = useState("");
  const [tasks, setTasks] = useState([]);
  const [newTaskType, setNewTaskType] = useState("feature");
  const [newTaskDesc, setNewTaskDesc] = useState("");
  const [taskFailMessage, setTaskFailMessage] = useState("");
  const [monitoringLoading, setMonitoringLoading] = useState(false);
  const [monitoringError, setMonitoringError] = useState("");
  const [monitoringData, setMonitoringData] = useState(null);
  const [engineLogsLoading, setEngineLogsLoading] = useState(false);
  const [engineLogsError, setEngineLogsError] = useState("");
  const [engineLogsData, setEngineLogsData] = useState(null);
  const [engineFilter, setEngineFilter] = useState("");
  const [taskTypeFilter, setTaskTypeFilter] = useState("");
  const [successFilter, setSuccessFilter] = useState("");
  const [engineLiveEntries, setEngineLiveEntries] = useState([]);
  const systemEventsHook = useSystemEvents({});
  const [debugSource, setDebugSource] = useState("system");
  const [debugLevel, setDebugLevel] = useState("");
  const [debugEntries, setDebugEntries] = useState([]);
  const [problems, setProblems] = useState([]);
  const [debugAuto, setDebugAuto] = useState(false);
  const [problemsAuto, setProblemsAuto] = useState(false);
  const [debugIntervalMs, setDebugIntervalMs] = useState(5000);
  const [problemsIntervalMs, setProblemsIntervalMs] = useState(5000);
  const [debugPaused, setDebugPaused] = useState(false);
  const [problemsPaused, setProblemsPaused] = useState(false);
  useEffect(() => {
    const items = Array.isArray(systemEventsHook.systemEvents) ? systemEventsHook.systemEvents : [];
    const telemetry = items.filter((m) => m && m.type === "system_event" && m.data && m.data.event_type === "engine_telemetry");
    const mapped = telemetry.map((m) => (m.data && m.data.event) ? m.data.event : {});
    if (mapped.length > 0) {
      setEngineLiveEntries((prev) => [...prev, ...mapped].slice(-50));
    }
  }, [systemEventsHook.systemEvents]);
  const [moduleActionLoading, setModuleActionLoading] = useState(false);
  const [moduleActionError, setModuleActionError] = useState("");
  const [moduleIdInput, setModuleIdInput] = useState("");
  const [bridgeBusy, setBridgeBusy] = useState(false);
  const [bridgeError, setBridgeError] = useState("");
  const [bridgeRole, setBridgeRole] = useState("user");
  const [bridgeCwd, setBridgeCwd] = useState(".");
  const [bridgeCmdText, setBridgeCmdText] = useState("python -m unittest -q");
  const [bridgeStdout, setBridgeStdout] = useState("");
  const [bridgeStderr, setBridgeStderr] = useState("");
  const [bridgeFilePath, setBridgeFilePath] = useState("");
  const [bridgeFileContent, setBridgeFileContent] = useState("");
  const [bridgeListPath, setBridgeListPath] = useState(".");
  const [bridgeListOutput, setBridgeListOutput] = useState("");
  const [kbBusy, setKbBusy] = useState(false);
  const [kbError, setKbError] = useState("");
  const [kbOutput, setKbOutput] = useState("");
  const [kbStoreId, setKbStoreId] = useState("");
  const [kbStoreContent, setKbStoreContent] = useState("");
  const [kbStoreMeta, setKbStoreMeta] = useState("");
  const [kbSearchQuery, setKbSearchQuery] = useState("");
  const [kbSearchK, setKbSearchK] = useState("5");
  const [kbEdgeSource, setKbEdgeSource] = useState("");
  const [kbEdgeTarget, setKbEdgeTarget] = useState("");
  const [kbNodeId, setKbNodeId] = useState("");
  const [loopBusy, setLoopBusy] = useState(false);
  const [loopError, setLoopError] = useState("");
  const [loopId, setLoopId] = useState("");
  const [loopPrompt, setLoopPrompt] = useState("");
  const [loopProject, setLoopProject] = useState("");
  const [loopIterations, setLoopIterations] = useState("1");
  const [loopStatus, setLoopStatus] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    const s = localGet("agentforge_system_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.engineFilter === "string") setEngineFilter(s.engineFilter);
      if (typeof s.taskTypeFilter === "string") setTaskTypeFilter(s.taskTypeFilter);
      if (typeof s.successFilter === "string") setSuccessFilter(s.successFilter);
      if (typeof s.debugSource === "string") setDebugSource(s.debugSource);
      if (typeof s.debugLevel === "string") setDebugLevel(s.debugLevel);
      if (typeof s.debugAuto === "boolean") setDebugAuto(s.debugAuto);
      if (typeof s.debugIntervalMs === "number") setDebugIntervalMs(s.debugIntervalMs);
      if (typeof s.problemsAuto === "boolean") setProblemsAuto(s.problemsAuto);
      if (typeof s.problemsIntervalMs === "number") setProblemsIntervalMs(s.problemsIntervalMs);
      if (typeof s.bridgeRole === "string") setBridgeRole(s.bridgeRole);
      if (typeof s.bridgeCwd === "string") setBridgeCwd(s.bridgeCwd);
      if (typeof s.bridgeCmdText === "string") setBridgeCmdText(s.bridgeCmdText);
      if (typeof s.bridgeFilePath === "string") setBridgeFilePath(s.bridgeFilePath);
      if (typeof s.bridgeFileContent === "string") setBridgeFileContent(s.bridgeFileContent);
      if (typeof s.bridgeListPath === "string") setBridgeListPath(s.bridgeListPath);
      if (typeof s.kbStoreId === "string") setKbStoreId(s.kbStoreId);
      if (typeof s.kbStoreContent === "string") setKbStoreContent(s.kbStoreContent);
      if (typeof s.kbStoreMeta === "string") setKbStoreMeta(s.kbStoreMeta);
      if (typeof s.kbSearchQuery === "string") setKbSearchQuery(s.kbSearchQuery);
      if (typeof s.kbSearchK === "string") setKbSearchK(s.kbSearchK);
      if (typeof s.kbEdgeSource === "string") setKbEdgeSource(s.kbEdgeSource);
      if (typeof s.kbEdgeTarget === "string") setKbEdgeTarget(s.kbEdgeTarget);
      if (typeof s.kbNodeId === "string") setKbNodeId(s.kbNodeId);
      if (typeof s.loopProject === "string") setLoopProject(s.loopProject);
      if (typeof s.loopIterations === "string") setLoopIterations(s.loopIterations);
      if (typeof s.loopPrompt === "string") setLoopPrompt(s.loopPrompt);
      if (typeof s.moduleIdInput === "string") setModuleIdInput(s.moduleIdInput);
    } catch (e) {}
  }, [isOpen]);

  useEffect(() => {
    const payload = {
      engineFilter,
      taskTypeFilter,
      successFilter,
      debugSource,
      debugLevel,
      debugAuto,
      debugIntervalMs,
      problemsAuto,
      problemsIntervalMs,
      bridgeRole,
      bridgeCwd,
      bridgeCmdText,
      bridgeFilePath,
      bridgeFileContent,
      bridgeListPath,
      kbStoreId,
      kbStoreContent,
      kbStoreMeta,
      kbSearchQuery,
      kbSearchK,
      kbEdgeSource,
      kbEdgeTarget,
      kbNodeId,
      loopProject,
      loopIterations,
      loopPrompt,
      moduleIdInput,
    };
    localSet("agentforge_system_state", payload);
  }, [
    engineFilter,
    taskTypeFilter,
    successFilter,
    debugSource,
    debugLevel,
    debugAuto,
    debugIntervalMs,
    problemsAuto,
    problemsIntervalMs,
    bridgeRole,
    bridgeCwd,
    bridgeCmdText,
    bridgeFilePath,
    bridgeFileContent,
    bridgeListPath,
    kbStoreId,
    kbStoreContent,
    kbStoreMeta,
    kbSearchQuery,
    kbSearchK,
    kbEdgeSource,
    kbEdgeTarget,
    kbNodeId,
    loopProject,
    loopIterations,
    loopPrompt,
    moduleIdInput,
  ]);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [statusRes, bridgeRes, wsRes] = await Promise.all([
        apiFetch("/system/status"),
        apiFetch("/bridge/health"),
        apiFetch("/workspace/status"),
      ]);
      const data = await statusRes.json();
      const bridge = await bridgeRes.json();
      const ws = await wsRes.json();
      if (!data?.success) throw new Error(data?.error || "Status fetch failed");
      setBackendStatus(data.data);
      const modules = Array.isArray(data.data?.modules_loaded) ? data.data.modules_loaded.length : 0;
      setSystemStats((prev) => ({
        ...prev,
        activeAgents: modules,
        queuedTasks: 0,
      }));
      const port = (() => {
        try {
          const url = new URL(BACKEND_URL || "http://127.0.0.1:8000");
          return url.port ? Number(url.port) : 8000;
        } catch (e) {
          return 8000;
        }
      })();
      setServices([
        { name: "Engine Server", status: "running", port, uptime: "-", cpu: "-", memory: "-" },
        { name: "Bridge Server", status: bridge?.data?.root_exists ? "running" : "stopped", port: null, uptime: "-", cpu: "-", memory: "-" },
        { name: "Workspace", status: ws?.success ? "running" : "stopped", port: null, uptime: "-", cpu: "-", memory: "-" },
        { name: "Modules", status: "running", port: null, uptime: "-", cpu: "-", memory: `${modules}` },
      ]);
    } catch (e) {
      setError(e.message || "Status fetch failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isOpen) return;
    refresh();
  }, [isOpen, refresh]);

  const refreshTasks = useCallback(async () => {
    if (tasksLoading) return;
    setTasksLoading(true);
    setTasksError("");
    try {
      const res = await apiFetch("/tasks");
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Task fetch failed");
      const list = Array.isArray(data?.data?.tasks) ? data.data.tasks : [];
      setTasks(list);
    } catch (e) {
      setTasksError(e?.message || "Task fetch failed");
    } finally {
      setTasksLoading(false);
    }
  }, [tasksLoading]);

  const createTask = useCallback(async () => {
    if (tasksLoading) return;
    const type = String(newTaskType || "").trim();
    const description = String(newTaskDesc || "").trim();
    if (!type || !description) return;
    setTasksLoading(true);
    setTasksError("");
    try {
      const res = await apiFetch("/tasks/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, description }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Task create failed");
      addLog("success", "Task created");
      setNewTaskDesc("");
      await refreshTasks();
    } catch (e) {
      setTasksError(e?.message || "Task create failed");
    } finally {
      setTasksLoading(false);
    }
  }, [addLog, newTaskDesc, newTaskType, refreshTasks, tasksLoading]);

  const runTask = useCallback(async (taskId) => {
    if (!taskId || tasksLoading) return;
    setTasksLoading(true);
    setTasksError("");
    try {
      const res = await apiFetch("/tasks/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Task run failed");
      addLog("info", `Task started: ${taskId}`);
      await refreshTasks();
    } catch (e) {
      setTasksError(e?.message || "Task run failed");
    } finally {
      setTasksLoading(false);
    }
  }, [addLog, refreshTasks, tasksLoading]);

  const completeTask = useCallback(async (taskId) => {
    if (!taskId || tasksLoading) return;
    setTasksLoading(true);
    setTasksError("");
    try {
      const res = await apiFetch("/tasks/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId, actual_files: 0, actual_loc: 0, validation_passed: true }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Task complete failed");
      addLog("success", `Task completed: ${taskId}`);
      await refreshTasks();
    } catch (e) {
      setTasksError(e?.message || "Task complete failed");
    } finally {
      setTasksLoading(false);
    }
  }, [addLog, refreshTasks, tasksLoading]);

  const failTask = useCallback(async (taskId) => {
    if (!taskId || tasksLoading) return;
    const err = String(taskFailMessage || "").trim() || "failed";
    setTasksLoading(true);
    setTasksError("");
    try {
      const res = await apiFetch("/tasks/fail", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId, error: err }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Task fail failed");
      addLog("warn", `Task failed: ${taskId}`);
      await refreshTasks();
    } catch (e) {
      setTasksError(e?.message || "Task fail failed");
    } finally {
      setTasksLoading(false);
    }
  }, [addLog, refreshTasks, taskFailMessage, tasksLoading]);

  const refreshMonitoring = useCallback(async () => {
    if (monitoringLoading) return;
    setMonitoringLoading(true);
    setMonitoringError("");
    try {
      const [dashRes, alertsRes] = await Promise.all([
        apiFetch("/monitoring/dashboard"),
        apiFetch("/monitoring/alerts"),
      ]);
      const dash = await dashRes.json();
      const alerts = await alertsRes.json();
      if (!dash?.success) throw new Error(dash?.error || "Monitoring fetch failed");
      setMonitoringData({ dashboard: dash?.data || null, alerts: alerts?.data || null });
    } catch (e) {
      setMonitoringError(e?.message || "Monitoring fetch failed");
    } finally {
      setMonitoringLoading(false);
    }
  }, [monitoringLoading]);

  const refreshEngineLogs = useCallback(async () => {
    if (engineLogsLoading) return;
    setEngineLogsLoading(true);
    setEngineLogsError("");
    try {
      const params = new URLSearchParams();
      params.set("limit", "200");
      if (taskTypeFilter && String(taskTypeFilter).trim()) params.set("task_type", String(taskTypeFilter).trim());
      if (engineFilter && String(engineFilter).trim()) params.set("engine", String(engineFilter).trim());
      if (successFilter === "true" || successFilter === "false") params.set("success", successFilter === "true" ? "true" : "false");
      const res = await apiFetch(`/engine_logs?${params.toString()}`);
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Engine logs fetch failed");
      setEngineLogsData(data?.data || null);
    } catch (e) {
      setEngineLogsError(e?.message || "Engine logs fetch failed");
    } finally {
      setEngineLogsLoading(false);
    }
  }, [engineLogsLoading, taskTypeFilter, engineFilter, successFilter]);

  const refreshDebugConsole = useCallback(async () => {
    try {
      const res = await apiFetch(`/logs?source=${encodeURIComponent(debugSource)}&limit=200`);
      const payload = await res.json();
      const entries = Array.isArray(payload?.data?.entries) ? payload.data.entries : [];
      const filtered = entries.filter((e) => {
        if (!debugLevel) return true;
        return String(e.level || "").toLowerCase() === debugLevel.toLowerCase();
      });
      setDebugEntries(filtered.slice(-200));
    } catch (e) {
      setDebugEntries([]);
    }
  }, [debugSource, debugLevel]);

  const refreshProblems = useCallback(async () => {
    try {
      const res = await apiFetch("/logs?source=errors&limit=200");
      const payload = await res.json();
      const errorEntries = Array.isArray(payload?.data?.entries) ? payload.data.entries : [];
      const telemetryErrors = (Array.isArray(engineLiveEntries) ? engineLiveEntries : []).filter((e) => !e.success);
      const items = [
        ...errorEntries.map((e) => ({ source: "backend", time: e.time, level: e.level || "error", message: e.message })),
        ...telemetryErrors.map((e) => ({
          source: "engine",
          time: new Date().toLocaleTimeString(),
          level: "error",
          message: `${String(e.engine || "")}/${String(e.model || "")}: ${String(e.error || "failed")} (${typeof e.elapsed_ms === "number" ? `${Math.round(e.elapsed_ms)}ms` : ""})`,
        })),
      ];
      setProblems(items.slice(-200));
    } catch (e) {
      setProblems([]);
    }
  }, [engineLiveEntries]);

  useEffect(() => {
    if (!isOpen) return;
    if (!debugAuto) return;
    if (debugPaused) return;
    const id = setInterval(() => {
      refreshDebugConsole();
    }, Math.max(1000, Number(debugIntervalMs) || 5000));
    return () => clearInterval(id);
  }, [isOpen, debugAuto, debugPaused, debugIntervalMs, refreshDebugConsole]);

  useEffect(() => {
    if (!isOpen) return;
    if (!problemsAuto) return;
    if (problemsPaused) return;
    const id = setInterval(() => {
      refreshProblems();
    }, Math.max(1000, Number(problemsIntervalMs) || 5000));
    return () => clearInterval(id);
  }, [isOpen, problemsAuto, problemsPaused, problemsIntervalMs, refreshProblems]);

  const refreshLoopStatus = useCallback(async () => {
    const id = String(loopId || "").trim();
    if (!id || loopBusy) return;
    setLoopBusy(true);
    setLoopError("");
    try {
      const res = await apiFetch(`/v2/loop/status?loop_id=${encodeURIComponent(id)}`);
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Loop status failed");
      setLoopStatus(data?.data || null);
    } catch (e) {
      setLoopError(e?.message || "Loop status failed");
    } finally {
      setLoopBusy(false);
    }
  }, [loopBusy, loopId]);

  const startLoop = useCallback(async () => {
    if (loopBusy) return;
    const prompt = String(loopPrompt || "").trim();
    if (!prompt) return;
    setLoopBusy(true);
    setLoopError("");
    setLoopStatus(null);
    try {
      const iters = Math.max(1, Math.min(parseInt(String(loopIterations || "1"), 10) || 1, 10));
      const res = await apiFetch("/v2/loop/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, project: String(loopProject || "").trim() || null, max_iterations: iters }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Loop start failed");
      const id = data?.data?.loop_id;
      if (id) setLoopId(id);
      addLog("info", `Recursive loop started: ${id}`);
    } catch (e) {
      setLoopError(e?.message || "Loop start failed");
    } finally {
      setLoopBusy(false);
    }
  }, [addLog, loopBusy, loopIterations, loopProject, loopPrompt]);

  const pauseLoop = useCallback(async () => {
    const id = String(loopId || "").trim();
    if (!id || loopBusy) return;
    setLoopBusy(true);
    setLoopError("");
    try {
      const res = await apiFetch("/v2/loop/pause", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ loop_id: id }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Pause failed");
      addLog("warn", `Loop paused: ${id}`);
      await refreshLoopStatus();
    } catch (e) {
      setLoopError(e?.message || "Pause failed");
    } finally {
      setLoopBusy(false);
    }
  }, [addLog, loopBusy, loopId, refreshLoopStatus]);

  const resumeLoop = useCallback(async () => {
    const id = String(loopId || "").trim();
    if (!id || loopBusy) return;
    setLoopBusy(true);
    setLoopError("");
    try {
      const res = await apiFetch("/v2/loop/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ loop_id: id }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Resume failed");
      addLog("info", `Loop resumed: ${id}`);
      await refreshLoopStatus();
    } catch (e) {
      setLoopError(e?.message || "Resume failed");
    } finally {
      setLoopBusy(false);
    }
  }, [addLog, loopBusy, loopId, refreshLoopStatus]);

  const stopLoop = useCallback(async () => {
    const id = String(loopId || "").trim();
    if (!id || loopBusy) return;
    setLoopBusy(true);
    setLoopError("");
    try {
      const res = await apiFetch("/v2/loop/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ loop_id: id }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Stop failed");
      addLog("warn", `Loop stop requested: ${id}`);
      await refreshLoopStatus();
    } catch (e) {
      setLoopError(e?.message || "Stop failed");
    } finally {
      setLoopBusy(false);
    }
  }, [addLog, loopBusy, loopId, refreshLoopStatus]);

  const parseCommandLine = useCallback((text) => {
    const src = String(text || "").trim();
    if (!src) return [];
    const argv = [];
    let cur = "";
    let quote = "";
    for (let i = 0; i < src.length; i += 1) {
      const ch = src[i];
      if (quote) {
        if (ch === quote) {
          quote = "";
          continue;
        }
        cur += ch;
        continue;
      }
      if (ch === "'" || ch === '"') {
        quote = ch;
        continue;
      }
      if (ch === " " || ch === "\t") {
        if (cur) {
          argv.push(cur);
          cur = "";
        }
        continue;
      }
      cur += ch;
    }
    if (cur) argv.push(cur);
    return argv;
  }, []);

  const runBridgeCommand = useCallback(async (cmdOverride) => {
    if (bridgeBusy) return;
    setBridgeBusy(true);
    setBridgeError("");
    setBridgeStdout("");
    setBridgeStderr("");
    try {
      const argv = parseCommandLine(cmdOverride != null ? cmdOverride : bridgeCmdText);
      const cwd = String(bridgeCwd || ".").trim() || ".";
      const res = await apiFetch("/bridge/run_command", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-AgentForge-Role": String(bridgeRole || "user") },
        body: JSON.stringify({ command: argv, cwd }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Bridge command failed");
      setBridgeStdout(String(data?.data?.stdout || ""));
      setBridgeStderr(String(data?.data?.stderr || ""));
      addLog("info", `Bridge command finished (${data?.data?.returncode ?? "?"})`);
    } catch (e) {
      setBridgeError(e?.message || "Bridge command failed");
      addLog("warn", `Bridge command failed${e?.message ? `: ${e.message}` : ""}`);
    } finally {
      setBridgeBusy(false);
    }
  }, [addLog, bridgeBusy, bridgeCmdText, bridgeCwd, parseCommandLine]);

  const bridgeReadFile = useCallback(async () => {
    if (bridgeBusy) return;
    const path = String(bridgeFilePath || "").trim();
    if (!path) return;
    setBridgeBusy(true);
    setBridgeError("");
    try {
      const res = await apiFetch("/bridge/read_file", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-AgentForge-Role": String(bridgeRole || "user") },
        body: JSON.stringify({ path }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Read failed");
      const content = data?.data?.content;
      setBridgeFileContent(typeof content === "string" ? content : JSON.stringify(content, null, 2));
      addLog("info", `Read file: ${path}`);
    } catch (e) {
      setBridgeError(e?.message || "Read failed");
    } finally {
      setBridgeBusy(false);
    }
  }, [addLog, bridgeBusy, bridgeFilePath]);

  const bridgeWriteFile = useCallback(async () => {
    if (bridgeBusy) return;
    const path = String(bridgeFilePath || "").trim();
    if (!path) return;
    setBridgeBusy(true);
    setBridgeError("");
    try {
      const res = await apiFetch("/bridge/write_file", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-AgentForge-Role": String(bridgeRole || "user") },
        body: JSON.stringify({ path, content: String(bridgeFileContent || "") }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Write failed");
      addLog("success", `Wrote file: ${path}`);
    } catch (e) {
      setBridgeError(e?.message || "Write failed");
    } finally {
      setBridgeBusy(false);
    }
  }, [addLog, bridgeBusy, bridgeFileContent, bridgeFilePath]);

  const bridgeDeleteFile = useCallback(async () => {
    if (bridgeBusy) return;
    const path = String(bridgeFilePath || "").trim();
    if (!path) return;
    setBridgeBusy(true);
    setBridgeError("");
    try {
      const res = await apiFetch("/bridge/delete_file", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-AgentForge-Role": String(bridgeRole || "user") },
        body: JSON.stringify({ path }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Delete failed");
      addLog("warn", `Deleted: ${path}`);
      setBridgeFileContent("");
    } catch (e) {
      setBridgeError(e?.message || "Delete failed");
    } finally {
      setBridgeBusy(false);
    }
  }, [addLog, bridgeBusy, bridgeFilePath]);

  const bridgeListDir = useCallback(async () => {
    if (bridgeBusy) return;
    const path = String(bridgeListPath || ".").trim() || ".";
    setBridgeBusy(true);
    setBridgeError("");
    setBridgeListOutput("");
    try {
      const res = await apiFetch(`/bridge/list?path=${encodeURIComponent(path)}`, {
        headers: { "X-AgentForge-Role": String(bridgeRole || "user") },
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "List failed");
      setBridgeListOutput(JSON.stringify(data?.data || null, null, 2));
    } catch (e) {
      setBridgeError(e?.message || "List failed");
    } finally {
      setBridgeBusy(false);
    }
  }, [bridgeBusy, bridgeListPath, bridgeRole]);

  const kbStore = useCallback(async () => {
    if (kbBusy) return;
    const content = String(kbStoreContent || "").trim();
    if (!content) return;
    setKbBusy(true);
    setKbError("");
    setKbOutput("");
    try {
      let meta = {};
      const rawMeta = String(kbStoreMeta || "").trim();
      if (rawMeta) {
        meta = JSON.parse(rawMeta);
      }
      const body = {
        id: String(kbStoreId || "").trim() || undefined,
        content,
        metadata: meta,
      };
      const res = await apiFetch("/knowledge/store", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Store failed");
      setKbOutput(JSON.stringify(data?.data || null, null, 2));
      addLog("success", "Knowledge stored");
    } catch (e) {
      setKbError(e?.message || "Store failed");
    } finally {
      setKbBusy(false);
    }
  }, [addLog, kbBusy, kbStoreContent, kbStoreId, kbStoreMeta]);

  const kbSearch = useCallback(async () => {
    if (kbBusy) return;
    const query = String(kbSearchQuery || "").trim();
    if (!query) return;
    setKbBusy(true);
    setKbError("");
    setKbOutput("");
    try {
      const k = Math.max(1, Math.min(parseInt(String(kbSearchK || "5"), 10) || 5, 10));
      const res = await apiFetch("/knowledge/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: k }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Search failed");
      setKbOutput(JSON.stringify(data?.data || null, null, 2));
    } catch (e) {
      setKbError(e?.message || "Search failed");
    } finally {
      setKbBusy(false);
    }
  }, [kbBusy, kbSearchK, kbSearchQuery]);

  const kbAddEdge = useCallback(async () => {
    if (kbBusy) return;
    const source = String(kbEdgeSource || "").trim();
    const target = String(kbEdgeTarget || "").trim();
    if (!source || !target) return;
    setKbBusy(true);
    setKbError("");
    setKbOutput("");
    try {
      const res = await apiFetch("/knowledge/graph/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, target }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Add edge failed");
      setKbOutput(JSON.stringify(data?.data || null, null, 2));
    } catch (e) {
      setKbError(e?.message || "Add edge failed");
    } finally {
      setKbBusy(false);
    }
  }, [kbBusy, kbEdgeSource, kbEdgeTarget]);

  const kbGetNode = useCallback(async () => {
    if (kbBusy) return;
    const nodeId = String(kbNodeId || "").trim();
    if (!nodeId) return;
    setKbBusy(true);
    setKbError("");
    setKbOutput("");
    try {
      const res = await apiFetch(`/knowledge/node/${encodeURIComponent(nodeId)}`);
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Node fetch failed");
      setKbOutput(JSON.stringify(data?.data || null, null, 2));
    } catch (e) {
      setKbError(e?.message || "Node fetch failed");
    } finally {
      setKbBusy(false);
    }
  }, [kbBusy, kbNodeId]);

  const toggleModuleById = useCallback(async (action) => {
    const moduleId = String(moduleIdInput || "").trim();
    if (!moduleId || moduleActionLoading) return;
    setModuleActionLoading(true);
    setModuleActionError("");
    try {
      const path = action === "load" ? "/modules/load" : "/modules/unload";
      const res = await apiFetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ module_id: moduleId }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Module action failed");
      addLog("info", `Module ${action}: ${moduleId}`);
      await refresh();
    } catch (e) {
      setModuleActionError(e?.message || "Module action failed");
    } finally {
      setModuleActionLoading(false);
    }
  }, [addLog, moduleActionLoading, moduleIdInput, refresh]);

  const toggleService = async (name) => {
    let nextAction = "started";
    setServices((prev) =>
      prev.map((s) => {
        if (s.name !== name) return s;
        const nextStatus = s.status === "running" ? "stopped" : "running";
        nextAction = nextStatus === "running" ? "started" : "stopped";
        return { ...s, status: nextStatus };
      })
    );
    addLog("info", `${name} ${nextAction}`);
    try {
      const path = nextAction === "stopped" ? "/system/shutdown" : "/system/start";
      await apiFetch(path, { method: "POST" });
      await refresh();
    } catch (e) {
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="System Status">
      <div className="panel-actions">
        <button className="btn btn-secondary" onClick={refresh} disabled={loading}>Refresh</button>
      </div>
      {error && <div className="item-empty">{error}</div>}
      <div className="system-overview">
        <div className="stat-card">
          <Cpu size={20} />
          <div className="stat-info">
            <span className="stat-value">{systemStats.totalCpu}</span>
            <span className="stat-label">CPU Usage</span>
          </div>
        </div>
        <div className="stat-card">
          <HardDrive size={20} />
          <div className="stat-info">
            <span className="stat-value">{systemStats.totalMemory}</span>
            <span className="stat-label">Memory</span>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={20} />
          <div className="stat-info">
            <span className="stat-value">{systemStats.activeAgents}</span>
            <span className="stat-label">Active Agents</span>
          </div>
        </div>
        <div className="stat-card">
          <Clock size={20} />
          <div className="stat-info">
            <span className="stat-value">{systemStats.queuedTasks}</span>
            <span className="stat-label">Queued Tasks</span>
          </div>
        </div>
      </div>

      <div className="page-section">
        <h3 className="section-title">Services</h3>
        <div className="services-list">
          {services.map(service => (
            <div key={service.name} className="service-row">
              <div className={`service-status ${service.status}`}>
                {service.status === 'running' ? <Check size={14} /> : <X size={14} />}
              </div>
              <div className="service-info">
                <span className="service-name">{service.name}</span>
                {service.port && <span className="service-port">:{service.port}</span>}
              </div>
              <span className="service-metric">{service.uptime}</span>
              <span className="service-metric">{service.cpu}</span>
              <span className="service-metric">{service.memory}</span>
              <button 
                className={`btn btn-sm ${service.status === 'running' ? 'btn-danger' : 'btn-primary'}`}
                onClick={() => toggleService(service.name)}
              >
                {service.status === 'running' ? 'Stop' : 'Start'}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="page-section">
        <h3 className="section-title">Protected Directories</h3>
        <p className="section-desc">AI agents cannot modify these system directories:</p>
        <div className="protected-dirs">
          <code>engine/</code>
          <code>services/</code>
          <code>providers/</code>
          <code>control/</code>
        </div>
      </div>
      <details className="advanced-details">
        <summary className="advanced-summary">Tasks</summary>
        <div className="page-section">
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <button className="btn btn-secondary" onClick={refreshTasks} disabled={tasksLoading}>
              {tasksLoading ? "Loading..." : "Refresh Tasks"}
            </button>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <select className="select" value={newTaskType} onChange={(e) => setNewTaskType(e.target.value)}>
                <option value="feature">feature</option>
                <option value="bug">bug</option>
                <option value="chore">chore</option>
                <option value="research">research</option>
              </select>
              <input
                className="input"
                placeholder="New task description..."
                value={newTaskDesc}
                onChange={(e) => setNewTaskDesc(e.target.value)}
                style={{ width: 260 }}
              />
              <button className="btn btn-primary" onClick={createTask} disabled={tasksLoading || !String(newTaskDesc || "").trim()}>
                Create
              </button>
            </div>
          </div>
          {tasksError && <div className="item-empty">{tasksError}</div>}
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8 }}>
            <input
              className="input"
              placeholder="Fail message (optional)"
              value={taskFailMessage}
              onChange={(e) => setTaskFailMessage(e.target.value)}
              style={{ width: 360 }}
            />
          </div>
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
            {(Array.isArray(tasks) ? tasks : []).length === 0 ? (
              <div className="item-empty">No tasks yet.</div>
            ) : (
              (Array.isArray(tasks) ? tasks : [])
                .slice()
                .sort((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")))
                .slice(0, 25)
                .map((t) => (
                  <div key={t.task_id} className="file-row" style={{ alignItems: "center" }}>
                    <div className="file-info" style={{ flex: 1 }}>
                      <div className="file-name" style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                        <span style={{ fontWeight: 600 }}>{t.task_id}</span>
                        <span className="tag">{t.type}</span>
                        <span className={`status-tag ${t.status}`}>{t.status}</span>
                      </div>
                      <div className="file-meta" style={{ opacity: 0.9 }}>
                        {t.description}
                        {t.last_error ? ` — ${t.last_error}` : ""}
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-sm btn-secondary" onClick={() => runTask(t.task_id)} disabled={tasksLoading}>
                        Run
                      </button>
                      <button className="btn btn-sm btn-primary" onClick={() => completeTask(t.task_id)} disabled={tasksLoading}>
                        Complete
                      </button>
                      <button className="btn btn-sm btn-danger" onClick={() => failTask(t.task_id)} disabled={tasksLoading}>
                        Fail
                      </button>
                    </div>
                  </div>
                ))
            )}
          </div>
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Monitoring</summary>
        <div className="page-section">
          <div className="panel-actions">
            <button className="btn btn-secondary" onClick={refreshMonitoring} disabled={monitoringLoading}>
              {monitoringLoading ? "Loading..." : "Refresh Monitoring"}
            </button>
          </div>
          {monitoringError && <div className="item-empty">{monitoringError}</div>}
          {monitoringData ? (
            <pre className="code-block">{JSON.stringify(monitoringData, null, 2)}</pre>
          ) : (
            <div className="item-empty">Monitoring data not loaded.</div>
          )}
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Debug Console</summary>
        <div className="page-section">
          <div className="panel-actions" style={{ gap: 8 }}>
            <select className="select" value={debugSource} onChange={(e) => setDebugSource(e.target.value)}>
              <option value="system">system</option>
              <option value="pipeline">pipeline</option>
              <option value="agents">agents</option>
              <option value="deployment">deployment</option>
              <option value="errors">errors</option>
            </select>
            <select className="select" value={debugLevel} onChange={(e) => setDebugLevel(e.target.value)}>
              <option value="">level: any</option>
              <option value="info">info</option>
              <option value="warning">warning</option>
              <option value="error">error</option>
            </select>
            <button className="btn btn-secondary" onClick={refreshDebugConsole}>Refresh</button>
            <div className={`module-toggle ${debugAuto ? "active" : ""}`} onClick={() => setDebugAuto(!debugAuto)}>
              <span className="module-name">Auto-refresh</span>
              <div className={`toggle-switch ${debugAuto ? "active" : ""}`}>
                <div className="toggle-knob" />
              </div>
            </div>
            <select className="select" value={String(debugIntervalMs)} onChange={(e) => setDebugIntervalMs(parseInt(e.target.value, 10) || 5000)}>
              <option value="2000">2s</option>
              <option value="5000">5s</option>
              <option value="10000">10s</option>
              <option value="30000">30s</option>
            </select>
          </div>
          <div className="output-log" onMouseEnter={() => setDebugPaused(true)} onMouseLeave={() => setDebugPaused(false)}>
            {(Array.isArray(debugEntries) ? debugEntries : []).map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-ts">{log.time}</span>
                <span className={`log-lvl ${log.level}`}>[{String(log.level || "").toUpperCase()}]</span>
                <span className="log-msg">{log.message}</span>
              </div>
            ))}
            {(Array.isArray(debugEntries) ? debugEntries : []).length === 0 ? <div className="item-empty">No entries.</div> : null}
          </div>
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Problems</summary>
        <div className="page-section">
          <div className="panel-actions">
            <button className="btn btn-secondary" onClick={refreshProblems}>Refresh</button>
            <div className={`module-toggle ${problemsAuto ? "active" : ""}`} onClick={() => setProblemsAuto(!problemsAuto)} style={{ marginLeft: 8 }}>
              <span className="module-name">Auto-refresh</span>
              <div className={`toggle-switch ${problemsAuto ? "active" : ""}`}>
                <div className="toggle-knob" />
              </div>
            </div>
            <select className="select" value={String(problemsIntervalMs)} onChange={(e) => setProblemsIntervalMs(parseInt(e.target.value, 10) || 5000)} style={{ marginLeft: 8 }}>
              <option value="2000">2s</option>
              <option value="5000">5s</option>
              <option value="10000">10s</option>
              <option value="30000">30s</option>
            </select>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }} onMouseEnter={() => setProblemsPaused(true)} onMouseLeave={() => setProblemsPaused(false)}>
            {(Array.isArray(problems) ? problems : []).slice().reverse().slice(0, 25).map((p, i) => (
              <div key={i} className="file-row">
                <div className="file-info" style={{ flex: 1 }}>
                  <div className="file-name" style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                    <span className="tag">{p.source}</span>
                    <span className={`status-tag ${String(p.level || "error")}`}>{String(p.level || "error")}</span>
                    <span className="log-ts">{p.time}</span>
                  </div>
                  <div className="file-meta" style={{ opacity: 0.9 }}>
                    {p.message}
                  </div>
                </div>
              </div>
            ))}
            {(Array.isArray(problems) ? problems : []).length === 0 ? <div className="item-empty">No problems detected.</div> : null}
          </div>
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Engine Telemetry</summary>
        <div className="page-section">
          <div className="panel-actions">
            <button className="btn btn-secondary" onClick={refreshEngineLogs} disabled={engineLogsLoading}>
              {engineLogsLoading ? "Loading..." : "Refresh Engine Logs"}
            </button>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8, flexWrap: "wrap" }}>
            <select className="select" value={taskTypeFilter} onChange={(e) => setTaskTypeFilter(e.target.value)} style={{ width: 180 }}>
              <option value="">task_type: any</option>
              <option value="planning">planning</option>
              <option value="coding">coding</option>
              <option value="ui_design">ui_design</option>
              <option value="debugging">debugging</option>
              <option value="conversation">conversation</option>
            </select>
            <select className="select" value={engineFilter} onChange={(e) => setEngineFilter(e.target.value)} style={{ width: 160 }}>
              <option value="">engine: any</option>
              <option value="fal">fal</option>
              <option value="openai">openai</option>
              <option value="anthropic">anthropic</option>
              <option value="local">local</option>
            </select>
            <select className="select" value={successFilter} onChange={(e) => setSuccessFilter(e.target.value)} style={{ width: 160 }}>
              <option value="">success: any</option>
              <option value="true">success: true</option>
              <option value="false">success: false</option>
            </select>
          </div>
          {engineLogsError && <div className="item-empty">{engineLogsError}</div>}
          {engineLogsData ? (
            <>
              <div className="section-title" style={{ marginTop: 10 }}>Charts</div>
              {(() => {
                const entries = Array.isArray(engineLogsData?.entries) ? engineLogsData.entries : [];
                const counts = {};
                const success = {};
                entries.forEach((e) => {
                  const eng = String(e.engine || "").trim() || "unknown";
                  counts[eng] = (counts[eng] || 0) + 1;
                  success[eng] = success[eng] || { ok: 0, total: 0 };
                  success[eng].total += 1;
                  if (e.success) success[eng].ok += 1;
                });
                const max = Math.max(1, ...Object.values(counts));
                return (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                    {Object.keys(counts).length === 0 ? (
                      <div className="item-empty">No entries.</div>
                    ) : (
                      Object.keys(counts).map((eng) => {
                        const c = counts[eng];
                        const rate = success[eng] ? Math.round((success[eng].ok / Math.max(1, success[eng].total)) * 100) : 0;
                        const width = Math.max(6, Math.round((c / max) * 100));
                        return (
                          <div key={eng} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <span className="tag">{eng}</span>
                            <div style={{ flex: 1, background: "rgba(255,255,255,0.08)", borderRadius: 4, height: 10 }}>
                              <div style={{ width: `${width}%`, height: 10, background: "#4aa3ff", borderRadius: 4 }} />
                            </div>
                            <span style={{ minWidth: 40 }}>{c}</span>
                            <span className="status-tag success">ok {rate}%</span>
                          </div>
                        );
                      })
                    )}
                  </div>
                );
              })()}
              <div className="section-title" style={{ marginTop: 12 }}>Live</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {(Array.isArray(engineLiveEntries) ? engineLiveEntries : []).slice().reverse().slice(0, 10).map((e, idx) => (
                  <div key={idx} className="file-row">
                    <div className="file-info" style={{ flex: 1 }}>
                      <div className="file-name" style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                        <span className="tag">{String(e.engine || "unknown")}</span>
                        <span className="tag">{String(e.task_type || "unknown")}</span>
                        <span className={`status-tag ${e.success ? "success" : "error"}`}>{e.success ? "success" : "error"}</span>
                      </div>
                      <div className="file-meta" style={{ opacity: 0.9 }}>
                        {String(e.model || "")} — {typeof e.elapsed_ms === "number" ? `${Math.round(e.elapsed_ms)} ms` : ""}
                        {e.error ? ` — ${String(e.error)}` : ""}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="section-title" style={{ marginTop: 12 }}>Raw</div>
              <pre className="code-block">{JSON.stringify(engineLogsData, null, 2)}</pre>
            </>
          ) : (
            <div className="item-empty">Engine logs not loaded.</div>
          )}
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Recursive Loop</summary>
        <div className="page-section">
          {loopError && <div className="item-empty">{loopError}</div>}
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input
              className="input"
              placeholder="Project (optional, e.g. projects/my_game)"
              value={loopProject}
              onChange={(e) => setLoopProject(e.target.value)}
              style={{ width: 320 }}
              disabled={loopBusy}
            />
            <input
              className="input"
              placeholder="Iterations"
              value={loopIterations}
              onChange={(e) => setLoopIterations(e.target.value)}
              style={{ width: 110 }}
              disabled={loopBusy}
            />
            <input
              className="input"
              placeholder="Loop ID"
              value={loopId}
              onChange={(e) => setLoopId(e.target.value)}
              style={{ width: 260 }}
              disabled={loopBusy}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-primary" onClick={startLoop} disabled={loopBusy || !String(loopPrompt || "").trim()}>
                {loopBusy ? "Working..." : "Start"}
              </button>
              <button className="btn btn-secondary" onClick={refreshLoopStatus} disabled={loopBusy || !String(loopId || "").trim()}>
                Status
              </button>
              <button className="btn btn-secondary" onClick={pauseLoop} disabled={loopBusy || !String(loopId || "").trim()}>
                Pause
              </button>
              <button className="btn btn-secondary" onClick={resumeLoop} disabled={loopBusy || !String(loopId || "").trim()}>
                Resume
              </button>
              <button className="btn btn-danger" onClick={stopLoop} disabled={loopBusy || !String(loopId || "").trim()}>
                Stop
              </button>
            </div>
          </div>
          <textarea
            className="input"
            placeholder="Loop prompt (plan → build → test → review → refine → rebuild)..."
            value={loopPrompt}
            onChange={(e) => setLoopPrompt(e.target.value)}
            rows={3}
            style={{ width: "100%", marginTop: 8, resize: "vertical" }}
            disabled={loopBusy}
          />
          {loopStatus ? <pre className="code-block">{JSON.stringify(loopStatus, null, 2)}</pre> : <div className="item-empty">No loop status loaded.</div>}
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Modules (Advanced)</summary>
        <div className="page-section">
          <p className="section-desc">Use only if you know what you are doing. Unloading modules can disable module features.</p>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input
              className="input"
              placeholder="module_id (e.g. research, builds)"
              value={moduleIdInput}
              onChange={(e) => setModuleIdInput(e.target.value)}
              style={{ width: 280 }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-primary" onClick={() => toggleModuleById("load")} disabled={moduleActionLoading || !String(moduleIdInput || "").trim()}>
                Load
              </button>
              <button className="btn btn-danger" onClick={() => toggleModuleById("unload")} disabled={moduleActionLoading || !String(moduleIdInput || "").trim()}>
                Unload
              </button>
            </div>
          </div>
          {moduleActionError && <div className="item-empty">{moduleActionError}</div>}
          {backendStatus ? (
            <div style={{ marginTop: 10 }}>
              <div className="section-title">Loaded modules</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
                {(Array.isArray(backendStatus?.modules_loaded) ? backendStatus.modules_loaded : []).map((m) => (
                  <span key={m} className="tag">{m}</span>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Bridge Tools</summary>
        <div className="page-section">
          <p className="section-desc">Executes inside the workspace root with bridge sandbox rules.</p>
          {bridgeError && <div className="item-empty">{bridgeError}</div>}
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <select className="select" value={bridgeRole} onChange={(e) => setBridgeRole(e.target.value)} style={{ width: 200 }}>
                <option value="backend_engineer">backend_engineer</option>
                <option value="devops_engineer">devops_engineer</option>
                <option value="game_engine_engineer">game_engine_engineer</option>
                <option value="user">user</option>
              </select>
              <input
                className="input"
                placeholder="cwd (relative to workspace root)"
                value={bridgeCwd}
                onChange={(e) => setBridgeCwd(e.target.value)}
                style={{ width: 260 }}
              />
              <input
                className="input"
                placeholder='command (e.g. python -m unittest -q)'
                value={bridgeCmdText}
                onChange={(e) => setBridgeCmdText(e.target.value)}
                style={{ width: 420 }}
              />
              <button className="btn btn-primary" onClick={() => runBridgeCommand()} disabled={bridgeBusy || !String(bridgeCmdText || "").trim()}>
                {bridgeBusy ? "Running..." : "Run"}
              </button>
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button className="btn btn-secondary" onClick={() => runBridgeCommand("python -m unittest -q")} disabled={bridgeBusy}>
                Unit tests
              </button>
              <button className="btn btn-secondary" onClick={() => runBridgeCommand("python compliance_test_report.py")} disabled={bridgeBusy}>
                Compliance
              </button>
              <button className="btn btn-secondary" onClick={() => runBridgeCommand("npm -C frontend run build")} disabled={bridgeBusy}>
                Frontend build
              </button>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
            <div>
              <div className="section-title">stdout</div>
              <pre className="code-block">{bridgeStdout || "—"}</pre>
            </div>
            <div>
              <div className="section-title">stderr</div>
              <pre className="code-block">{bridgeStderr || "—"}</pre>
            </div>
          </div>
          <div style={{ height: 10 }} />
          <div className="section-title">Files</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input
              className="input"
              placeholder="path (relative to workspace root)"
              value={bridgeFilePath}
              onChange={(e) => setBridgeFilePath(e.target.value)}
              style={{ width: 520 }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-secondary" onClick={bridgeReadFile} disabled={bridgeBusy || !String(bridgeFilePath || "").trim()}>
                Read
              </button>
              <button className="btn btn-primary" onClick={bridgeWriteFile} disabled={bridgeBusy || !String(bridgeFilePath || "").trim()}>
                Write
              </button>
              <button className="btn btn-danger" onClick={bridgeDeleteFile} disabled={bridgeBusy || !String(bridgeFilePath || "").trim()}>
                Delete
              </button>
            </div>
          </div>
          <textarea
            className="input"
            value={bridgeFileContent}
            onChange={(e) => setBridgeFileContent(e.target.value)}
            placeholder="file contents..."
            style={{ width: "100%", minHeight: 160, marginTop: 8, fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace" }}
          />
          <div style={{ height: 10 }} />
          <div className="section-title">List</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input
              className="input"
              placeholder="list path"
              value={bridgeListPath}
              onChange={(e) => setBridgeListPath(e.target.value)}
              style={{ width: 520 }}
            />
            <button className="btn btn-secondary" onClick={bridgeListDir} disabled={bridgeBusy}>
              List
            </button>
          </div>
          {bridgeListOutput ? <pre className="code-block">{bridgeListOutput}</pre> : null}
        </div>
      </details>
      <details className="advanced-details">
        <summary className="advanced-summary">Knowledge Tools</summary>
        <div className="page-section">
          {kbError && <div className="item-empty">{kbError}</div>}
          <div className="section-title">Store</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input className="input" placeholder="id (optional)" value={kbStoreId} onChange={(e) => setKbStoreId(e.target.value)} style={{ width: 220 }} />
            <button className="btn btn-primary" onClick={kbStore} disabled={kbBusy || !String(kbStoreContent || "").trim()}>
              {kbBusy ? "Working..." : "Store"}
            </button>
          </div>
          <textarea className="input" placeholder="content..." value={kbStoreContent} onChange={(e) => setKbStoreContent(e.target.value)} style={{ width: "100%", minHeight: 110, marginTop: 8 }} />
          <textarea className="input" placeholder='metadata JSON (optional) e.g. {"tag":"x"}' value={kbStoreMeta} onChange={(e) => setKbStoreMeta(e.target.value)} style={{ width: "100%", minHeight: 70, marginTop: 8, fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace" }} />
          <div style={{ height: 12 }} />
          <div className="section-title">Search</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input className="input" placeholder="query" value={kbSearchQuery} onChange={(e) => setKbSearchQuery(e.target.value)} style={{ width: 520 }} />
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input className="input" placeholder="top_k" value={kbSearchK} onChange={(e) => setKbSearchK(e.target.value)} style={{ width: 90 }} />
              <button className="btn btn-secondary" onClick={kbSearch} disabled={kbBusy || !String(kbSearchQuery || "").trim()}>
                Search
              </button>
            </div>
          </div>
          <div style={{ height: 12 }} />
          <div className="section-title">Graph Edge</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input className="input" placeholder="source node id" value={kbEdgeSource} onChange={(e) => setKbEdgeSource(e.target.value)} style={{ width: 320 }} />
            <input className="input" placeholder="target node id" value={kbEdgeTarget} onChange={(e) => setKbEdgeTarget(e.target.value)} style={{ width: 320 }} />
            <button className="btn btn-secondary" onClick={kbAddEdge} disabled={kbBusy || !String(kbEdgeSource || "").trim() || !String(kbEdgeTarget || "").trim()}>
              Add
            </button>
          </div>
          <div style={{ height: 12 }} />
          <div className="section-title">Node</div>
          <div className="panel-actions" style={{ justifyContent: "space-between" }}>
            <input className="input" placeholder="node id" value={kbNodeId} onChange={(e) => setKbNodeId(e.target.value)} style={{ width: 520 }} />
            <button className="btn btn-secondary" onClick={kbGetNode} disabled={kbBusy || !String(kbNodeId || "").trim()}>
              Get
            </button>
          </div>
          {kbOutput ? <pre className="code-block">{kbOutput}</pre> : <div className="item-empty">No output yet.</div>}
        </div>
      </details>
      {backendStatus && (
        <details className="advanced-details">
          <summary className="advanced-summary">Backend Details</summary>
          <div className="page-section">
            <h3 className="section-title">Backend</h3>
            <pre className="code-block">{JSON.stringify(backendStatus, null, 2)}</pre>
          </div>
        </details>
      )}
    </Modal>
  );
};

// 5. SETTINGS PAGE
const SettingsPage = ({ isOpen, onClose, addLog }) => {
  const [settings, setSettings] = useState({
    theme: "dark",
    accentColor: "red",
    fontSize: "medium",
    notifications: true,
    sounds: false,
    autoSave: true,
    telemetry: false,
    restoreLastModal: true,
    resetOnLaunch: true,
  });
  const [infra, setInfra] = useState({
    default_model_provider: "",
    model_temperature: "",
    max_tokens: "",
    log_level: "INFO",
    local_project_root: "",
  });
  const [infraLoading, setInfraLoading] = useState(false);
  const [infraSaving, setInfraSaving] = useState(false);
  const [infraError, setInfraError] = useState("");
  const [modelRoutes, setModelRoutes] = useState(null);
  const [localProjects, setLocalProjects] = useState([]);
  const [engineCfgLoading, setEngineCfgLoading] = useState(false);
  const [engineCfgError, setEngineCfgError] = useState("");
  const [engineCfg, setEngineCfg] = useState(null);
  const [engineKeys, setEngineKeys] = useState({ fal: "", openai: "", anthropic: "" });
  const [engineKeysSet, setEngineKeysSet] = useState({ fal: false, openai: false, anthropic: false });
  const [engineEnabled, setEngineEnabled] = useState({ local: true, fal: false, openai: false, anthropic: false });
  const [engineRoutingDraft, setEngineRoutingDraft] = useState({});
  const [engineCostDraft, setEngineCostDraft] = useState({ max_cost_usd_per_day: "", max_cost_usd_per_request: "" });

  const [activeSection, setActiveSection] = useState("appearance");

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    addLog("info", `Setting updated: ${key} = ${value}`);
  };

  useEffect(() => {
    if (!isOpen) return;
    const s = localGet("agentforge_settings_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (s.settings && typeof s.settings === "object") setSettings((prev) => ({ ...prev, ...s.settings }));
      if (s.infra && typeof s.infra === "object") setInfra((prev) => ({ ...prev, ...s.infra }));
      if (typeof s.activeSection === "string") setActiveSection(s.activeSection);
      if (s.engineEnabled && typeof s.engineEnabled === "object") setEngineEnabled((prev) => ({ ...prev, ...s.engineEnabled }));
      if (s.engineRoutingDraft && typeof s.engineRoutingDraft === "object") setEngineRoutingDraft(s.engineRoutingDraft);
      if (s.engineCostDraft && typeof s.engineCostDraft === "object") setEngineCostDraft((prev) => ({ ...prev, ...s.engineCostDraft }));
      if (s.engineKeys && typeof s.engineKeys === "object") setEngineKeys((prev) => ({ ...prev, ...s.engineKeys }));
    } catch (e) {}
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    const load = async () => {
      setInfraLoading(true);
      setInfraError("");
      try {
        const [settingsRes, routesRes, projectsRes] = await Promise.all([
          apiFetch("/v2/settings"),
          apiFetch("/v2/model_routing/routes"),
          apiFetch("/v2/local_bridge/projects"),
        ]);
        const settingsData = await settingsRes.json();
        const routesData = await routesRes.json();
        const projectsData = await projectsRes.json();
        if (cancelled) return;
        if (settingsData?.success && settingsData?.data) {
          setInfra((prev) => ({
            ...prev,
            default_model_provider: settingsData.data.default_model_provider || "",
            model_temperature: settingsData.data.model_temperature ?? "",
            max_tokens: settingsData.data.max_tokens ?? "",
            log_level: settingsData.data.log_level || "INFO",
            local_project_root: settingsData.data.local_project_root || "",
          }));
        }
        setModelRoutes(routesData?.data?.routes || null);
        setLocalProjects(Array.isArray(projectsData?.data?.projects) ? projectsData.data.projects : []);
      } catch (e) {
        if (!cancelled) setInfraError("Failed to load infrastructure settings");
      } finally {
        if (!cancelled) setInfraLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    if (activeSection !== "engines") return;
    let cancelled = false;
    const load = async () => {
      setEngineCfgLoading(true);
      setEngineCfgError("");
      try {
        const res = await apiFetch("/engine_config");
        const data = await res.json();
        if (cancelled) return;
        if (!data?.success) throw new Error(data?.error || "Failed to load engine config");
        const cfg = data?.data?.config || {};
        const keysSet = data?.data?.api_keys_set || {};
        setEngineCfg(cfg);
        setEngineKeysSet({
          fal: !!keysSet?.fal,
          openai: !!keysSet?.openai,
          anthropic: !!keysSet?.anthropic,
        });
        const enabled = Array.isArray(cfg?.enabled_engines) ? cfg.enabled_engines : [];
        setEngineEnabled({
          local: enabled.includes("local") || enabled.length === 0,
          fal: enabled.includes("fal"),
          openai: enabled.includes("openai"),
          anthropic: enabled.includes("anthropic"),
        });
        setEngineRoutingDraft(cfg?.task_routing && typeof cfg.task_routing === "object" ? cfg.task_routing : {});
        const cost = cfg?.cost_controls && typeof cfg.cost_controls === "object" ? cfg.cost_controls : {};
        setEngineCostDraft({
          max_cost_usd_per_day: cost?.max_cost_usd_per_day ?? "",
          max_cost_usd_per_request: cost?.max_cost_usd_per_request ?? "",
        });
        setEngineKeys({ fal: "", openai: "", anthropic: "" });
      } catch (e) {
        if (!cancelled) setEngineCfgError(e.message || "Failed to load engine config");
      } finally {
        if (!cancelled) setEngineCfgLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isOpen, activeSection]);

  const saveInfra = async () => {
    if (infraSaving) return;
    setInfraSaving(true);
    setInfraError("");
    try {
      const body = {
        default_model_provider: infra.default_model_provider || null,
        model_temperature: infra.model_temperature === "" ? null : Number(infra.model_temperature),
        max_tokens: infra.max_tokens === "" ? null : Number(infra.max_tokens),
        log_level: infra.log_level || null,
        local_project_root: infra.local_project_root || null,
      };
      const res = await apiFetch("/v2/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Save failed");
      addLog("success", "Infrastructure settings saved");
      onClose();
    } catch (e) {
      setInfraError(e.message || "Save failed");
      addLog("error", "Infrastructure settings save failed");
    } finally {
      setInfraSaving(false);
    }
  };

  const saveEngineConfig = async () => {
    if (engineCfgLoading) return;
    setEngineCfgLoading(true);
    setEngineCfgError("");
    try {
      const enabled = Object.entries(engineEnabled)
        .filter(([_, v]) => !!v)
        .map(([k]) => k);
      const apiKeys = {};
      if (engineKeys.fal) apiKeys.fal = engineKeys.fal;
      if (engineKeys.openai) apiKeys.openai = engineKeys.openai;
      if (engineKeys.anthropic) apiKeys.anthropic = engineKeys.anthropic;
      const cost_controls = {
        max_cost_usd_per_day: engineCostDraft.max_cost_usd_per_day === "" ? null : Number(engineCostDraft.max_cost_usd_per_day),
        max_cost_usd_per_request: engineCostDraft.max_cost_usd_per_request === "" ? null : Number(engineCostDraft.max_cost_usd_per_request),
      };
      const res = await apiFetch("/engine_config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          enabled_engines: enabled,
          api_keys: apiKeys,
          cost_controls,
          task_routing: engineRoutingDraft,
        }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Save failed");
      addLog("success", "Engine config saved (local override)");
      const cfg = data?.data?.config || {};
      const keysSet = data?.data?.api_keys_set || {};
      setEngineCfg(cfg);
      setEngineKeysSet({
        fal: !!keysSet?.fal,
        openai: !!keysSet?.openai,
        anthropic: !!keysSet?.anthropic,
      });
      setEngineKeys({ fal: "", openai: "", anthropic: "" });
    } catch (e) {
      setEngineCfgError(e.message || "Save failed");
      addLog("error", "Engine config save failed");
    } finally {
      setEngineCfgLoading(false);
    }
  };

  const shortcuts = [
    { action: "Open Project", keys: "Ctrl + O" },
    { action: "Save", keys: "Ctrl + S" },
    { action: "New File", keys: "Ctrl + N" },
    { action: "Command Palette", keys: "Ctrl + Shift + P" },
    { action: "Toggle Sidebar", keys: "Ctrl + B" },
    { action: "Run Build", keys: "F5" },
    { action: "Stop Build", keys: "Shift + F5" },
    { action: "Toggle Console", keys: "Ctrl + `" },
  ];

  useEffect(() => {
    localSet("agentforge_settings_state", {
      settings,
      infra,
      activeSection,
      engineEnabled,
      engineRoutingDraft,
      engineCostDraft,
      engineKeys,
    });
  }, [settings, infra, activeSection, engineEnabled, engineRoutingDraft, engineCostDraft, engineKeys]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings">
      <div className="settings-layout">
        <div className="settings-nav">
          <button 
            className={`settings-nav-item ${activeSection === 'appearance' ? 'active' : ''}`}
            onClick={() => setActiveSection('appearance')}
          >
            <Palette size={16} /> Appearance
          </button>
          <button 
            className={`settings-nav-item ${activeSection === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveSection('notifications')}
          >
            <Bell size={16} /> Notifications
          </button>
          <button 
            className={`settings-nav-item ${activeSection === 'shortcuts' ? 'active' : ''}`}
            onClick={() => setActiveSection('shortcuts')}
          >
            <Keyboard size={16} /> Shortcuts
          </button>
          <button 
            className={`settings-nav-item ${activeSection === 'privacy' ? 'active' : ''}`}
            onClick={() => setActiveSection('privacy')}
          >
            <Shield size={16} /> Privacy
          </button>
          <button
            className={`settings-nav-item ${activeSection === 'infrastructure' ? 'active' : ''}`}
            onClick={() => setActiveSection('infrastructure')}
          >
            <Server size={16} /> Infrastructure
          </button>
          <button
            className={`settings-nav-item ${activeSection === 'engines' ? 'active' : ''}`}
            onClick={() => setActiveSection('engines')}
          >
            <Cpu size={16} /> Engines
          </button>
        </div>

        <div className="settings-content">
          {activeSection === 'appearance' && (
            <div className="settings-section">
              <h3>Appearance</h3>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Theme</span>
                  <span className="setting-desc">Choose your preferred color scheme</span>
                </div>
                <div className="theme-options">
                  <button 
                    className={`theme-btn ${settings.theme === 'dark' ? 'active' : ''}`}
                    onClick={() => updateSetting('theme', 'dark')}
                  >
                    <Moon size={16} /> Dark
                  </button>
                  <button 
                    className={`theme-btn ${settings.theme === 'light' ? 'active' : ''}`}
                    onClick={() => updateSetting('theme', 'light')}
                  >
                    <Sun size={16} /> Light
                  </button>
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Accent Color</span>
                  <span className="setting-desc">Primary highlight color</span>
                </div>
                <div className="color-options">
                  {['red', 'blue', 'green', 'purple', 'orange'].map(color => (
                    <button 
                      key={color}
                      className={`color-btn ${color} ${settings.accentColor === color ? 'active' : ''}`}
                      onClick={() => updateSetting('accentColor', color)}
                    />
                  ))}
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Font Size</span>
                  <span className="setting-desc">UI text size</span>
                </div>
                <select 
                  className="select"
                  value={settings.fontSize}
                  onChange={(e) => updateSetting('fontSize', e.target.value)}
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>
          )}

          {activeSection === 'notifications' && (
            <div className="settings-section">
              <h3>Notifications</h3>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Enable Notifications</span>
                  <span className="setting-desc">Show desktop notifications for events</span>
                </div>
                <div 
                  className={`toggle-switch-lg ${settings.notifications ? 'active' : ''}`}
                  onClick={() => updateSetting('notifications', !settings.notifications)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Sound Effects</span>
                  <span className="setting-desc">Play sounds for actions</span>
                </div>
                <div 
                  className={`toggle-switch-lg ${settings.sounds ? 'active' : ''}`}
                  onClick={() => updateSetting('sounds', !settings.sounds)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
            </div>
          )}

          {activeSection === 'shortcuts' && (
            <div className="settings-section">
              <h3>Keyboard Shortcuts</h3>
              <div className="shortcuts-list">
                {shortcuts.map((s, i) => (
                  <div key={i} className="shortcut-row">
                    <span className="shortcut-action">{s.action}</span>
                    <kbd className="shortcut-keys">{s.keys}</kbd>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'privacy' && (
            <div className="settings-section">
              <h3>Privacy & Data</h3>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Auto-Save</span>
                  <span className="setting-desc">Automatically save changes</span>
                </div>
                <div 
                  className={`toggle-switch-lg ${settings.autoSave ? 'active' : ''}`}
                  onClick={() => updateSetting('autoSave', !settings.autoSave)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Restore last modal on launch</span>
                  <span className="setting-desc">Reopen Project/Workspace/Providers/System/Settings after restart</span>
                </div>
                <div
                  className={`toggle-switch-lg ${settings.restoreLastModal ? 'active' : ''}`}
                  onClick={() => updateSetting('restoreLastModal', !settings.restoreLastModal)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Reset saved UI state on launch</span>
                  <span className="setting-desc">Clear saved layout and UI drafts each startup</span>
                </div>
                <div
                  className={`toggle-switch-lg ${settings.resetOnLaunch ? 'active' : ''}`}
                  onClick={() => updateSetting('resetOnLaunch', !settings.resetOnLaunch)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Usage Analytics</span>
                  <span className="setting-desc">Help improve AgentForgeOS</span>
                </div>
                <div 
                  className={`toggle-switch-lg ${settings.telemetry ? 'active' : ''}`}
                  onClick={() => updateSetting('telemetry', !settings.telemetry)}
                >
                  <div className="toggle-knob" />
                </div>
              </div>
              <div className="setting-row">
                <button className="btn btn-danger">
                  <Trash2 size={14} /> Clear All Data
                </button>
              </div>
            </div>
          )}

          {activeSection === 'infrastructure' && (
            <div className="settings-section">
              <h3>Infrastructure</h3>
              {infraLoading && <div className="item-empty">Loading...</div>}
              {!infraLoading && infraError && <div className="item-empty">{infraError}</div>}
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Default model provider</span>
                  <span className="setting-desc">Used by the model router</span>
                </div>
                <input
                  className="input"
                  value={infra.default_model_provider}
                  onChange={(e) => setInfra((p) => ({ ...p, default_model_provider: e.target.value }))}
                />
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Temperature</span>
                  <span className="setting-desc">Model randomness</span>
                </div>
                <input
                  className="input"
                  type="number"
                  step="0.1"
                  value={infra.model_temperature}
                  onChange={(e) => setInfra((p) => ({ ...p, model_temperature: e.target.value }))}
                />
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Max tokens</span>
                  <span className="setting-desc">Upper bound on generation length</span>
                </div>
                <input
                  className="input"
                  type="number"
                  value={infra.max_tokens}
                  onChange={(e) => setInfra((p) => ({ ...p, max_tokens: e.target.value }))}
                />
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Log level</span>
                  <span className="setting-desc">Backend log verbosity</span>
                </div>
                <select
                  className="select"
                  value={infra.log_level}
                  onChange={(e) => setInfra((p) => ({ ...p, log_level: e.target.value }))}
                >
                  <option value="DEBUG">DEBUG</option>
                  <option value="INFO">INFO</option>
                  <option value="WARNING">WARNING</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </div>
              <div className="setting-row">
                <div className="setting-info">
                  <span className="setting-label">Local project root</span>
                  <span className="setting-desc">Used by LocalBridge project discovery</span>
                </div>
                <input
                  className="input"
                  value={infra.local_project_root}
                  onChange={(e) => setInfra((p) => ({ ...p, local_project_root: e.target.value }))}
                />
              </div>
              <div className="quick-actions">
                <button className="btn btn-primary" onClick={saveInfra} disabled={infraSaving}>
                  {infraSaving ? "Saving..." : "Save Infrastructure"}
                </button>
              </div>
              <div className="page-section">
                <h3 className="section-title">Model Routing</h3>
                <pre className="code-block">{JSON.stringify(modelRoutes || {}, null, 2)}</pre>
              </div>
              <div className="page-section">
                <h3 className="section-title">Local Projects</h3>
                {localProjects.length === 0 ? (
                  <div className="item-empty">No local projects found.</div>
                ) : (
                  <div className="item-list">
                    {localProjects.map((p) => (
                      <div key={p} className="item-row">
                        <span className="item-name">{p}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeSection === 'engines' && (
            <div className="settings-section">
              <h3>Engines</h3>
              {engineCfgLoading && <div className="item-empty">Loading...</div>}
              {!engineCfgLoading && engineCfgError && <div className="item-empty">{engineCfgError}</div>}

              <div className="page-section">
                <h3 className="section-title">Enabled Engines</h3>
                <div className="module-toggles">
                  {["local", "fal", "openai", "anthropic"].map((k) => (
                    <div
                      key={k}
                      className={`module-toggle ${engineEnabled[k] ? "active" : ""}`}
                      onClick={() => setEngineEnabled((p) => ({ ...p, [k]: !p[k] }))}
                    >
                      <span className="module-name">{k}</span>
                      <div className={`toggle-switch ${engineEnabled[k] ? "active" : ""}`}>
                        <div className="toggle-knob" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="page-section">
                <h3 className="section-title">API Keys (stored locally)</h3>
                <div className="form-grid">
                  <div className="config-field">
                    <label>Fal.ai API Key {engineKeysSet.fal ? "(saved)" : ""}</label>
                    <input type="password" className="input" value={engineKeys.fal} onChange={(e) => setEngineKeys((p) => ({ ...p, fal: e.target.value }))} />
                  </div>
                  <div className="config-field">
                    <label>OpenAI API Key {engineKeysSet.openai ? "(saved)" : ""}</label>
                    <input type="password" className="input" value={engineKeys.openai} onChange={(e) => setEngineKeys((p) => ({ ...p, openai: e.target.value }))} />
                  </div>
                  <div className="config-field">
                    <label>Anthropic API Key {engineKeysSet.anthropic ? "(saved)" : ""}</label>
                    <input type="password" className="input" value={engineKeys.anthropic} onChange={(e) => setEngineKeys((p) => ({ ...p, anthropic: e.target.value }))} />
                  </div>
                </div>
              </div>

              <div className="page-section">
                <h3 className="section-title">Cost Controls</h3>
                <div className="form-grid">
                  <div className="config-field">
                    <label>Max cost per day (USD)</label>
                    <input type="number" className="input" value={engineCostDraft.max_cost_usd_per_day} onChange={(e) => setEngineCostDraft((p) => ({ ...p, max_cost_usd_per_day: e.target.value }))} />
                  </div>
                  <div className="config-field">
                    <label>Max cost per request (USD)</label>
                    <input type="number" className="input" value={engineCostDraft.max_cost_usd_per_request} onChange={(e) => setEngineCostDraft((p) => ({ ...p, max_cost_usd_per_request: e.target.value }))} />
                  </div>
                </div>
              </div>

              <div className="page-section">
                <h3 className="section-title">Task Routing</h3>
                <div className="item-empty">Edit primary engine and model per task type.</div>
                <div className="routing-grid">
                  {Object.keys(engineRoutingDraft || {}).map((task) => (
                    <div key={task} className="routing-row">
                      <div className="routing-task">{task}</div>
                      <select
                        className="select"
                        value={engineRoutingDraft[task]?.engine || ""}
                        onChange={(e) =>
                          setEngineRoutingDraft((p) => ({
                            ...p,
                            [task]: { ...(p[task] || {}), engine: e.target.value },
                          }))
                        }
                      >
                        {["local", "fal", "openai", "anthropic"].map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                      <input
                        className="input"
                        value={engineRoutingDraft[task]?.model || ""}
                        onChange={(e) =>
                          setEngineRoutingDraft((p) => ({
                            ...p,
                            [task]: { ...(p[task] || {}), model: e.target.value },
                          }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="setting-row">
                <button className="btn btn-primary" onClick={saveEngineConfig} disabled={engineCfgLoading}>
                  Save Engine Settings
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};

// 6. PROFILE PAGE
const ProfilePage = ({ isOpen, onClose, addLog }) => {
  const [profile, setProfile] = useState({
    name: "Developer",
    email: "dev@agentforge.local",
    avatar: "https://images.unsplash.com/photo-1605504836193-e77d3d9ede8a?w=100&h=100&fit=crop",
    role: "Admin",
    joinDate: "January 2024",
  });

  const [stats, setStats] = useState({
    projectsCreated: 12,
    buildsRun: 156,
    experimentsRun: 43,
    hoursActive: 89,
  });
  const [loading, setLoading] = useState(false);

  const [achievements, setAchievements] = useState([
    { id: 1, name: "First Build", desc: "Completed your first build", unlocked: true },
    { id: 2, name: "Agent Master", desc: "Used all 12 agents", unlocked: true },
    { id: 3, name: "Knowledge Seeker", desc: "Added 50 research notes", unlocked: false },
    { id: 4, name: "Deploy King", desc: "10 successful deployments", unlocked: true },
  ]);

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const [wsRes, buildsRes, sandboxRes] = await Promise.all([
          apiFetch("/workspace/status"),
          apiFetch("/modules/builds/runs"),
          apiFetch("/modules/sandbox/experiments"),
        ]);
        const ws = await wsRes.json();
        const builds = await buildsRes.json();
        const sandbox = await sandboxRes.json();
        if (cancelled) return;
        setStats((prev) => ({
          ...prev,
          projectsCreated: Array.isArray(ws?.data?.projects) ? ws.data.projects.length : prev.projectsCreated,
          buildsRun: Array.isArray(builds?.data) ? builds.data.length : prev.buildsRun,
          experimentsRun: Array.isArray(sandbox?.data) ? sandbox.data.length : prev.experimentsRun,
        }));
      } catch (e) {
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Profile">
      {loading && <div className="item-empty">Loading...</div>}
      <div className="profile-header">
        <div className="profile-avatar-section">
          <img src={profile.avatar} alt="Avatar" className="profile-avatar" />
          <button className="btn btn-secondary btn-sm">Change Avatar</button>
        </div>
        <div className="profile-info-section">
          <input 
            className="input profile-name-input" 
            value={profile.name} 
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
          />
          <div className="profile-meta">
            <span><Mail size={14} /> {profile.email}</span>
            <span><Shield size={14} /> {profile.role}</span>
            <span><Calendar size={14} /> Joined {profile.joinDate}</span>
          </div>
        </div>
      </div>

      <div className="page-section">
        <h3 className="section-title">Activity Stats</h3>
        <div className="profile-stats">
          <div className="profile-stat">
            <Folder size={20} />
            <span className="stat-value">{stats.projectsCreated}</span>
            <span className="stat-label">Projects</span>
          </div>
          <div className="profile-stat">
            <Layers size={20} />
            <span className="stat-value">{stats.buildsRun}</span>
            <span className="stat-label">Builds</span>
          </div>
          <div className="profile-stat">
            <Box size={20} />
            <span className="stat-value">{stats.experimentsRun}</span>
            <span className="stat-label">Experiments</span>
          </div>
          <div className="profile-stat">
            <Clock size={20} />
            <span className="stat-value">{stats.hoursActive}h</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
      </div>

      <div className="page-section">
        <h3 className="section-title">Achievements</h3>
        <div className="achievements-grid">
          {achievements.map(a => (
            <div key={a.id} className={`achievement-card ${a.unlocked ? 'unlocked' : 'locked'}`}>
              <Award size={24} />
              <span className="achievement-name">{a.name}</span>
              <span className="achievement-desc">{a.desc}</span>
              {!a.unlocked && <Lock size={14} className="achievement-lock" />}
            </div>
          ))}
        </div>
      </div>

      <details className="advanced-details">
        <summary className="advanced-summary">Account Actions</summary>
        <div className="page-section">
          <h3 className="section-title">Account Actions</h3>
          <div className="quick-actions">
            <button className="btn btn-secondary">
              <Key size={14} /> Change Password
            </button>
            <button className="btn btn-secondary">
              <Upload size={14} /> Export Data
            </button>
            <button className="btn btn-danger">
              <Trash2 size={14} /> Delete Account
            </button>
          </div>
        </div>
      </details>
    </Modal>
  );
};

// Components
const NavBar = ({ onOpenModal }) => (
  <header className="nav-bar">
    <div className="nav-logo">
      <div className="logo-hexagon">
        <span className="logo-letters">AF</span>
      </div>
      <span className="nav-logo-text">AgentForgeOS</span>
    </div>
    <div className="nav-pills">
      <button className="nav-pill" onClick={() => onOpenModal('project')} data-testid="nav-project">
        <Folder size={14} style={{ marginRight: 6, display: 'inline' }} />
        Project
      </button>
      <button className="nav-pill" onClick={() => onOpenModal('workspace')} data-testid="nav-workspace">
        <Monitor size={14} style={{ marginRight: 6, display: 'inline' }} />
        Workspace
      </button>
      <button className="nav-pill" onClick={() => onOpenModal('providers')} data-testid="nav-providers">
        <Globe size={14} style={{ marginRight: 6, display: 'inline' }} />
        Providers
      </button>
      <button className="nav-pill" onClick={() => onOpenModal('system')} data-testid="nav-system">
        <Cpu size={14} style={{ marginRight: 6, display: 'inline' }} />
        System
      </button>
      <button className="nav-pill" onClick={() => onOpenModal('settings')} data-testid="nav-settings">
        <Settings size={14} style={{ marginRight: 6, display: 'inline' }} />
        Settings
      </button>
      <button className="nav-pill" onClick={() => onOpenModal('profile')} data-testid="nav-profile">
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
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadFiles = async (newPath) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch(`/bridge/list?path=${encodeURIComponent(newPath)}`);
      const data = await res.json();
      if (data?.data?.entries) {
        setEntries(data.data.entries);
      }
      setPath(newPath);
      addLog("info", `Loaded workspace: ${newPath}`);
    } catch (err) {
      setError("Bridge list unavailable");
      setEntries([]);
      addLog("warn", "Bridge list unavailable");
    }
    setLoading(false);
  };

  useEffect(() => { 
    addLog("info", "Studio workspace initialized");
    loadFiles(".");
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
        {error && <div className="item-empty">{error}</div>}
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
  const [runs, setRuns] = useState([]);
  const [project, setProject] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/builds/runs");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) setRuns(data.data);
    } catch (err) {
      setError("Builds API unavailable");
      setRuns([]);
    } finally {
      setLoading(false);
    }
  };

  const triggerBuild = async () => {
    if (!project.trim()) return;
    try {
      const res = await apiFetch("/modules/builds/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Trigger failed");
      addLog("info", `Build triggered: ${data?.data?.id || "new"}`);
      setProject("");
      await loadRuns();
    } catch (err) {
      addLog("error", "Build trigger failed");
      setError(err.message || "Build trigger failed");
      setProject("");
    }
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
        {error && <div className="item-empty">{error}</div>}
        {loading ? (
          <div className="item-empty">Loading builds...</div>
        ) : runs.length === 0 ? (
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
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [draggedNode, setDraggedNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [ingestUrlsText, setIngestUrlsText] = useState("");
  const [ingestBusy, setIngestBusy] = useState(false);

  const noteToNode = (note) => ({
    id: note.id,
    type: (note.tags && note.tags[0]) || "document",
    title: note.title,
    x: 80 + Math.random() * 240,
    y: 80 + Math.random() * 180,
    connections: [],
  });

  const fetchNotes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/research/notes");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setNodes(data.data.map(noteToNode));
        addLog("info", "Loaded research notes");
      } else {
        setError(data?.error || "Unable to load notes");
      }
    } catch (err) {
      setError("Research API unavailable");
    } finally {
      setLoading(false);
    }
  }, [addLog]);

  const createNote = useCallback(async ({ title, content, tags }) => {
    try {
      const res = await apiFetch("/modules/research/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content, tags }),
      });
      const data = await res.json();
      if (data?.success && data.data) {
        setNodes((prev) => [...prev, noteToNode(data.data)]);
        addLog("info", `Note captured: ${title}`);
      }
    } catch (err) {
      addLog("warn", "Failed to capture note");
    }
  }, [addLog]);

  const runSearch = useCallback(async () => {
    if (!searchQuery.trim() || searchLoading) return;
    setSearchLoading(true);
    setSearchError(null);
    try {
      const res = await apiFetch("/modules/research/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery.trim(), top_k: 8 }),
      });
      const data = await res.json();
      if (!data?.success || !Array.isArray(data.data)) throw new Error(data?.error || "Search failed");
      setSearchResults(data.data);
      addLog("info", `Search returned ${data.data.length} results`);
    } catch (e) {
      setSearchError(e.message || "Search failed");
    } finally {
      setSearchLoading(false);
    }
  }, [addLog, searchLoading, searchQuery]);

  const uploadFilesToResearch = useCallback(async (files) => {
    const list = Array.isArray(files) ? files : Array.from(files || []);
    if (list.length === 0) return;
    setIngestBusy(true);
    try {
      for (const file of list) {
        const form = new FormData();
        form.append("file", file);
        const res = await apiFetch("/v2/research/upload", { method: "POST", body: form });
        const data = await res.json();
        if (!data?.success) {
          addLog("warn", `Research ingest failed: ${file.name}${data?.error ? ` — ${data.error}` : ""}`);
          continue;
        }
        const nodeId = data?.data?.node_id;
        addLog("info", `Research ingested file: ${file.name}${nodeId ? ` → ${nodeId}` : ""}`);
      }
    } catch (e) {
      addLog("warn", `Research ingest failed${e?.message ? `: ${e.message}` : ""}`);
    } finally {
      setIngestBusy(false);
    }
  }, [addLog]);

  const ingestUrlsToResearch = useCallback(async () => {
    const urls = String(ingestUrlsText || "")
      .split(/\r?\n/g)
      .map((s) => s.trim())
      .filter(Boolean);
    if (urls.length === 0) return;
    setIngestBusy(true);
    try {
      for (const url of urls) {
        const res = await apiFetch("/v2/research/ingest_url", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        const data = await res.json();
        if (!data?.success) {
          addLog("warn", `Research ingest failed: ${url}${data?.error ? ` — ${data.error}` : ""}`);
          continue;
        }
        const nodeId = data?.data?.node_id;
        addLog("info", `Research ingested url: ${url}${nodeId ? ` → ${nodeId}` : ""}`);
      }
      setIngestUrlsText("");
    } catch (e) {
      addLog("warn", `Research ingest failed${e?.message ? `: ${e.message}` : ""}`);
    } finally {
      setIngestBusy(false);
    }
  }, [addLog, ingestUrlsText]);

  // File drop handling
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const rect = canvasRef.current?.getBoundingClientRect();
    const x = e.clientX - (rect?.left || 0) - 60;
    const y = e.clientY - (rect?.top || 0) - 30;
    
    if (files.length > 0) {
      uploadFilesToResearch(files);
    }

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
      createNote({ title: file.name, content: `File dropped: ${file.name}`, tags: [type] });
    });
  }, [addLog, createNote, uploadFilesToResearch]);

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
    createNote({ title: newNode.title, content: "", tags: [type] });
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
    fetchNotes();
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card research-panel">
      <div className="workspace-card-title">Knowledge Graph</div>

      <div className="panel-actions column" style={{ gap: 8 }}>
        <textarea
          className="input"
          placeholder={"Paste URLs (YouTube / web pages), one per line..."}
          value={ingestUrlsText}
          onChange={(e) => setIngestUrlsText(e.target.value)}
          style={{ minHeight: 72, resize: "vertical" }}
        />
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={ingestUrlsToResearch} disabled={ingestBusy || !String(ingestUrlsText || "").trim()}>
            {ingestBusy ? "Working..." : "Ingest URLs"}
          </button>
          <label className="btn btn-secondary" style={{ display: "inline-flex", alignItems: "center", gap: 6, cursor: ingestBusy ? "not-allowed" : "pointer" }}>
            Upload files
            <input
              type="file"
              multiple
              disabled={ingestBusy}
              onChange={(e) => {
                const f = e.target.files;
                if (f && f.length > 0) uploadFilesToResearch(f);
                e.target.value = "";
              }}
              style={{ display: "none" }}
            />
          </label>
          <span style={{ fontSize: 11, opacity: 0.75 }}>Drop files on canvas also ingests.</span>
        </div>
      </div>

      <div className="panel-actions">
        <input
          className="input"
          placeholder="Search knowledge..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") runSearch();
          }}
          style={{ flex: 1 }}
        />
        <button className="btn btn-secondary" onClick={runSearch} disabled={searchLoading || !searchQuery.trim()}>
          {searchLoading ? "Searching..." : "Search"}
        </button>
      </div>
      
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

      {searchError && <div className="item-empty">{searchError}</div>}
      {searchResults.length > 0 && (
        <div className="item-list">
          {searchResults.map((r, idx) => (
            <div className="item-row" key={idx}>
              <span className="item-name">{r?.metadata?.title || r?.id || "result"}</span>
              <span className="item-meta">{typeof r?.score === "number" ? r.score.toFixed(3) : ""}</span>
            </div>
          ))}
        </div>
      )}

      {/* Canvas */}
      <div 
        ref={canvasRef}
        className="node-canvas"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {error && <div className="canvas-empty">{error}</div>}
        {loading && <div className="canvas-empty">Loading...</div>}
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
  const [assets, setAssets] = useState([]);
  const [assetType, setAssetType] = useState("image");
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/assets/list");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setAssets(data.data);
      } else if (data?.success && data?.data && Array.isArray(data.data.assets)) {
        setAssets(data.data.assets);
      }
    } catch (err) {
      setError("Assets API unavailable");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { 
    addLog("info", "Asset registry loaded");
    loadAssets();
    // eslint-disable-next-line
  }, []);

  const generateAsset = async () => {
    if (generating) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/assets/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: assetType, prompt }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Generate failed");
      addLog("info", `Asset generated: ${data?.data?.path || data?.data?.id || "new"}`);
      setPrompt("");
      await loadAssets();
    } catch (err) {
      setError(err.message || "Generate failed");
      addLog("warn", "Asset generate failed");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Generated Assets</div>
      <div className="panel-actions">
        <select className="select" value={assetType} onChange={(e) => setAssetType(e.target.value)}>
          <option value="image">image</option>
          <option value="audio">audio</option>
          <option value="document">document</option>
          <option value="video">video</option>
        </select>
        <input className="input" placeholder="Prompt (optional)" value={prompt} onChange={(e) => setPrompt(e.target.value)} style={{ flex: 1 }} />
        <button className="btn btn-primary" onClick={generateAsset} disabled={generating}>
          {generating ? "Generating..." : "Generate"}
        </button>
      </div>
      <div className="item-list">
        {error && <div className="item-empty">{error}</div>}
        {loading ? (
          <div className="item-empty">Loading assets...</div>
        ) : assets.length === 0 ? (
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
  const [deployments, setDeployments] = useState([]);
  const [project, setProject] = useState("");
  const [version, setVersion] = useState("");
  const [target, setTarget] = useState("local");
  const [dockerPort, setDockerPort] = useState("8088");
  const [k8sApply, setK8sApply] = useState(false);
  const [cloudApply, setCloudApply] = useState(false);
  const [cloudRegion, setCloudRegion] = useState("us-east-1");
  const [cloudRepo, setCloudRepo] = useState("agentforgeos");
  const [gcpProject, setGcpProject] = useState("");
  const [host, setHost] = useState("");
  const [ingressClass, setIngressClass] = useState("");
  const [useTls, setUseTls] = useState(false);
  const [tlsSecret, setTlsSecret] = useState("");
  const [clusterIssuer, setClusterIssuer] = useState("");
  const [createSecrets, setCreateSecrets] = useState(false);
  const [secretName, setSecretName] = useState("");
  const [destroyBusy, setDestroyBusy] = useState(false);
  const [engine, setEngine] = useState("web");
  const [launching, setLaunching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const s = localGet("agentforge_deploy_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.project === "string") setProject(s.project);
      if (typeof s.version === "string") setVersion(s.version);
      if (typeof s.target === "string") setTarget(s.target);
      if (typeof s.dockerPort === "string") setDockerPort(s.dockerPort);
      if (typeof s.k8sApply === "boolean") setK8sApply(s.k8sApply);
      if (typeof s.cloudApply === "boolean") setCloudApply(s.cloudApply);
      if (typeof s.cloudRegion === "string") setCloudRegion(s.cloudRegion);
      if (typeof s.cloudRepo === "string") setCloudRepo(s.cloudRepo);
      if (typeof s.gcpProject === "string") setGcpProject(s.gcpProject);
      if (typeof s.host === "string") setHost(s.host);
      if (typeof s.ingressClass === "string") setIngressClass(s.ingressClass);
      if (typeof s.useTls === "boolean") setUseTls(s.useTls);
      if (typeof s.tlsSecret === "string") setTlsSecret(s.tlsSecret);
      if (typeof s.clusterIssuer === "string") setClusterIssuer(s.clusterIssuer);
      if (typeof s.createSecrets === "boolean") setCreateSecrets(s.createSecrets);
      if (typeof s.secretName === "string") setSecretName(s.secretName);
      if (typeof s.engine === "string") setEngine(s.engine);
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_deploy_state", {
      project,
      version,
      target,
      dockerPort,
      k8sApply,
      cloudApply,
      cloudRegion,
      cloudRepo,
      gcpProject,
      host,
      ingressClass,
      useTls,
      tlsSecret,
      clusterIssuer,
      createSecrets,
      secretName,
      engine,
    });
  }, [
    project,
    version,
    target,
    dockerPort,
    k8sApply,
    cloudApply,
    cloudRegion,
    cloudRepo,
    gcpProject,
    host,
    ingressClass,
    useTls,
    tlsSecret,
    clusterIssuer,
    createSecrets,
    secretName,
    engine,
  ]);
  const loadDeployments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/deployment/list");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setDeployments(data.data);
      }
    } catch (err) {
      setError("Deployment API unavailable");
    } finally {
      setLoading(false);
    }
  }, []);

  const deploy = async () => {
    if (!project.trim()) return;
    try {
      const res = await apiFetch("/modules/deployment/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project,
          version: version || "0.0.1",
          target,
          port: target === "docker" || target === "kubernetes" || target === "aws" || target === "gcp" ? dockerPort : undefined,
          apply: target === "kubernetes" ? k8sApply : (target === "aws" || target === "gcp" ? cloudApply : undefined),
          region: target === "aws" || target === "gcp" ? cloudRegion : undefined,
          repo: target === "aws" || target === "gcp" ? cloudRepo : undefined,
          gcp_project: target === "gcp" ? gcpProject : undefined,
          host: target === "kubernetes" || target === "aws" || target === "gcp" ? host : undefined,
          ingress_class: target === "kubernetes" || target === "aws" || target === "gcp" ? ingressClass : undefined,
          use_tls: target === "kubernetes" || target === "aws" || target === "gcp" ? useTls : undefined,
          tls_secret: target === "kubernetes" || target === "aws" || target === "gcp" ? tlsSecret : undefined,
          cluster_issuer: target === "kubernetes" || target === "aws" || target === "gcp" ? clusterIssuer : undefined,
          create_secrets: target === "kubernetes" || target === "aws" || target === "gcp" ? createSecrets : undefined,
          secret_name: target === "kubernetes" || target === "aws" || target === "gcp" ? secretName : undefined,
        }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Deployment failed");
      addLog("info", `Deployment initiated: ${project} → ${target}`);
      setProject(""); setVersion("");
      await loadDeployments();
    } catch (err) {
      setError(err.message || "Deployment failed");
      addLog("error", "Deployment failed");
    }
  };

  const destroyDeployment = async (d) => {
    if (destroyBusy) return;
    setDestroyBusy(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/deployment/destroy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: d?.id, uid: d?.uid }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Destroy failed");
      addLog("warn", `Deployment destroyed: ${d?.project} → ${d?.target}`);
      await loadDeployments();
    } catch (err) {
      setError(err.message || "Destroy failed");
      addLog("warn", "Destroy failed");
    } finally {
      setDestroyBusy(false);
    }
  };

  const launch = async () => {
    if (launching) return;
    setLaunching(true);
    setError(null);
    try {
      const res = await apiFetch("/modules/deployment/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ engine, project }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Launch failed");
      addLog("info", `Launch queued: ${engine}`);
    } catch (err) {
      setError(err.message || "Launch failed");
      addLog("warn", "Launch failed");
    } finally {
      setLaunching(false);
    }
  };

  useEffect(() => { 
    addLog("info", "Deployment manager loaded");
    loadDeployments();
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
          <option value="docker">docker</option>
          <option value="kubernetes">kubernetes</option>
          <option value="aws">aws</option>
          <option value="gcp">gcp</option>
          <option value="staging">staging</option>
          <option value="production">production</option>
        </select>
        {(target === "docker" || target === "kubernetes" || target === "aws" || target === "gcp") && (
          <input className="input" placeholder="Port" value={dockerPort} onChange={(e) => setDockerPort(e.target.value)} style={{ width: 110 }} />
        )}
        {target === "kubernetes" && (
          <label style={{ display: "inline-flex", gap: 6, alignItems: "center", fontSize: 12, opacity: 0.85 }}>
            <input type="checkbox" checked={k8sApply} onChange={(e) => setK8sApply(e.target.checked)} />
            apply
          </label>
        )}
        {(target === "aws" || target === "gcp") && (
          <>
            <input className="input" placeholder="Region" value={cloudRegion} onChange={(e) => setCloudRegion(e.target.value)} style={{ width: 160 }} />
            <input className="input" placeholder="Repo" value={cloudRepo} onChange={(e) => setCloudRepo(e.target.value)} style={{ width: 160 }} />
            {target === "gcp" && (
              <input className="input" placeholder="GCP project" value={gcpProject} onChange={(e) => setGcpProject(e.target.value)} style={{ width: 180 }} />
            )}
            <label style={{ display: "inline-flex", gap: 6, alignItems: "center", fontSize: 12, opacity: 0.85 }}>
              <input type="checkbox" checked={cloudApply} onChange={(e) => setCloudApply(e.target.checked)} />
              apply
            </label>
          </>
        )}
        <button className="btn btn-danger" onClick={deploy} data-testid="deploy-btn">Deploy</button>
      </div>
      {(target === "kubernetes" || target === "aws" || target === "gcp") && (
        <div className="panel-actions">
          <input className="input" placeholder="Host (optional, for Ingress)" value={host} onChange={(e) => setHost(e.target.value)} style={{ width: 260 }} />
          <input className="input" placeholder="Ingress class (optional)" value={ingressClass} onChange={(e) => setIngressClass(e.target.value)} style={{ width: 180 }} />
          <label style={{ display: "inline-flex", gap: 6, alignItems: "center", fontSize: 12, opacity: 0.85 }}>
            <input type="checkbox" checked={useTls} onChange={(e) => setUseTls(e.target.checked)} />
            tls
          </label>
          <input className="input" placeholder="TLS secret (optional)" value={tlsSecret} onChange={(e) => setTlsSecret(e.target.value)} style={{ width: 180 }} />
          <input className="input" placeholder="Cluster issuer (optional)" value={clusterIssuer} onChange={(e) => setClusterIssuer(e.target.value)} style={{ width: 200 }} />
          <label style={{ display: "inline-flex", gap: 6, alignItems: "center", fontSize: 12, opacity: 0.85 }}>
            <input type="checkbox" checked={createSecrets} onChange={(e) => setCreateSecrets(e.target.checked)} />
            create secrets
          </label>
          <input className="input" placeholder="Secret name (optional)" value={secretName} onChange={(e) => setSecretName(e.target.value)} style={{ width: 180 }} />
        </div>
      )}
      <div className="panel-actions">
        <select className="select" value={engine} onChange={(e) => setEngine(e.target.value)}>
          <option value="web">web</option>
          <option value="unity">unity</option>
          <option value="unreal">unreal</option>
        </select>
        <button className="btn btn-secondary" onClick={launch} disabled={launching}>
          {launching ? "Launching..." : "Launch"}
        </button>
      </div>
      <div className="item-list">
        {error && <div className="item-empty">{error}</div>}
        {loading ? (
          <div className="item-empty">Loading deployments...</div>
        ) : deployments.length === 0 ? (
          <div className="item-empty">No deployments yet.</div>
        ) : (
          deployments.slice().reverse().map((d, i) => (
            <div className="item-row" key={i} style={{ alignItems: "center" }}>
              <span className={`item-badge ${d.status}`}>{d.status}</span>
              <span className="item-name">{d.project} → {d.target}</span>
              <span className="item-meta">v{d.version}{d.docker_url ? ` · ${d.docker_url}` : ""}</span>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button className="btn btn-sm btn-danger" onClick={() => destroyDeployment(d)} disabled={destroyBusy || d.status === "destroyed"}>
                  Destroy
                </button>
              </div>
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
  const [submittedPrompt, setSubmittedPrompt] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [buildSteps, setBuildSteps] = useState(
    PIPELINE_STAGES.map((name, idx) => ({ id: idx, name, status: "idle", output: "" }))
  );
  const [preview, setPreview] = useState(null);
  const [consoleOutput, setConsoleOutput] = useState([
    { type: "system", text: "Sandbox initialized. Ready for experimentation." },
  ]);
  const [experiments, setExperiments] = useState([]);
  const [pipelineId, setPipelineId] = useState("");
  const wsRef = useRef(null);
  const [godPlan, setGodPlan] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState("");
  const [lastPipelineStatus, setLastPipelineStatus] = useState("");
  const [targetGameEngine, setTargetGameEngine] = useState("auto");
  const [autoLaunchEngine, setAutoLaunchEngine] = useState(true);
  const [godProjectPath, setGodProjectPath] = useState("");

  useEffect(() => {
    const s = localGet("agentforge_sandbox_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.prompt === "string") setPrompt(s.prompt);
      if (typeof s.targetGameEngine === "string") setTargetGameEngine(s.targetGameEngine);
      if (typeof s.autoLaunchEngine === "boolean") setAutoLaunchEngine(s.autoLaunchEngine);
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_sandbox_state", {
      prompt,
      targetGameEngine,
      autoLaunchEngine,
    });
  }, [prompt, targetGameEngine, autoLaunchEngine]);
  const slugify = useCallback((text) => {
    const src = String(text || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 48);
    if (src) return src;
    return `project-${Date.now()}`;
  }, []);

  const bridgeHeadersForLaunch = useCallback(() => {
    return { "Content-Type": "application/json", "X-AgentForge-Role": "game_engine_engineer" };
  }, []);

  const createDir = useCallback(async (path) => {
    const res = await apiFetch("/bridge/create_directory", {
      method: "POST",
      headers: bridgeHeadersForLaunch(),
      body: JSON.stringify({ path: String(path) }),
    });
    const data = await res.json();
    if (!data?.success) throw new Error(data?.error || "create_directory failed");
    return data;
  }, [bridgeHeadersForLaunch]);

  const createFile = useCallback(async (path, content) => {
    const res = await apiFetch("/bridge/create_file", {
      method: "POST",
      headers: bridgeHeadersForLaunch(),
      body: JSON.stringify({ path: String(path), content: String(content ?? "") }),
    });
    const data = await res.json();
    if (!data?.success) throw new Error(data?.error || "create_file failed");
    return data;
  }, [bridgeHeadersForLaunch]);

  const launchTool = useCallback(async (tool, target) => {
    const res = await apiFetch("/bridge/launch_tool", {
      method: "POST",
      headers: bridgeHeadersForLaunch(),
      body: JSON.stringify({ tool, target }),
    });
    const data = await res.json();
    if (!data?.success) throw new Error(data?.error || "launch_tool failed");
    return data;
  }, [bridgeHeadersForLaunch]);

  const resolveEngineForPrompt = useCallback((p) => {
    const pref = String(targetGameEngine || "auto").toLowerCase();
    if (pref === "unity" || pref === "unreal") return pref;
    const t = String(p || "").toLowerCase();
    if (t.includes("unreal")) return "unreal";
    if (t.includes("unity")) return "unity";
    if (t.includes("game") || t.includes("fps") || t.includes("platformer") || t.includes("rpg")) return "unreal";
    return "unreal";
  }, [targetGameEngine]);

  const setupAndLaunchGameProject = useCallback(async (p) => {
    const engine = resolveEngineForPrompt(p);
    const name = slugify(p);
    const baseDir = `${engine}/${name}`;
    await createDir(baseDir);
    if (engine === "unity") {
      await createDir(`${baseDir}/Assets`);
      await createFile(
        `${baseDir}/README.md`,
        `# ${name}\n\nCreated by AgentForgeOS God Mode.\n\nPrompt:\n${p}\n`,
      );
      const launch = await launchTool("unity", baseDir);
      if (!launch?.data?.supported) throw new Error("Unity launch unsupported (Unity.exe not found)");
      setGodProjectPath(baseDir);
      return { engine, target: baseDir, exe: launch?.data?.exe || "" };
    }
    const uprojectPath = `${baseDir}/${name}.uproject`;
    const uproject = {
      FileVersion: 3,
      EngineAssociation: "",
      Category: "Games",
      Description: `AgentForgeOS God Mode: ${name}`,
      Modules: [],
      Plugins: [],
    };
    await createFile(`${baseDir}/README.md`, `# ${name}\n\nPrompt:\n${p}\n`);
    await createFile(uprojectPath, JSON.stringify(uproject, null, 2));
    const launch = await launchTool("unreal", uprojectPath);
    if (!launch?.data?.supported) throw new Error("Unreal launch unsupported (UnrealEditor.exe not found)");
    setGodProjectPath(baseDir);
    return { engine, target: uprojectPath, exe: launch?.data?.exe || "" };
  }, [createDir, createFile, launchTool, resolveEngineForPrompt, slugify]);

  const loadExperiments = useCallback(async () => {
    try {
      const res = await apiFetch("/modules/sandbox/experiments");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setExperiments(data.data);
      }
    } catch (e) {
    }
  }, []);

  const runExperiment = async () => {
    if (!prompt.trim() || isRunning) return;
    
    setIsRunning(true);
    const currentPrompt = prompt;
    setSubmittedPrompt(currentPrompt);
    setConsoleOutput(prev => [...prev, { type: "user", text: `> ${prompt}` }]);
    addLog("info", "Sandbox experiment started");

    try {
      setPlanLoading(true);
      setPlanError("");
      setGodPlan(null);
      setGodProjectPath("");
      const previewRes = await apiFetch("/v2/command/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: currentPrompt, brief: { source: "sandbox-godmode" } }),
      });
      const previewJson = await previewRes.json();
      if (!previewJson?.success) throw new Error(previewJson?.error || "Plan generation failed");
      setGodPlan(previewJson?.data || null);
      setConsoleOutput((prev) => [...prev, { type: "info", text: "Plan generated. Starting build..." }]);

      const res = await apiFetch("/pipeline/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: currentPrompt }),
      });
      const data = await res.json();
      if (!data?.success || !data?.pipeline_id) throw new Error(data?.error || "Pipeline start failed");
      const id = data.pipeline_id;
      setPipelineId(id);
      setBuildSteps(PIPELINE_STAGES.map((name, idx) => ({ id: idx, name, status: "idle", output: "" })));
      setConsoleOutput((prev) => [...prev, { type: "info", text: `God Mode build started: ${id}` }]);
      if (autoLaunchEngine) {
        try {
          setConsoleOutput((prev) => [...prev, { type: "info", text: "Launching game engine..." }]);
          const launched = await setupAndLaunchGameProject(currentPrompt);
          setConsoleOutput((prev) => [
            ...prev,
            { type: "success", text: `Launched ${launched.engine} (${launched.exe || "auto"})` },
          ]);
        } catch (e) {
          setConsoleOutput((prev) => [...prev, { type: "warn", text: e?.message || "Engine launch failed" }]);
        }
      }
      await loadExperiments();
      setPrompt("");
      setPlanLoading(false);
      return;
    } catch (e) {
      setConsoleOutput((prev) => [...prev, { type: "error", text: e?.message || "God Mode start failed" }]);
      setPlanError(e?.message || "God Mode start failed");
    }
    setIsRunning(false);
    setPlanLoading(false);
  };

  const resetSandbox = () => {
    setPipelineId("");
    setBuildSteps(PIPELINE_STAGES.map((name, idx) => ({ id: idx, name, status: "idle", output: "" })));
    setPreview(null);
    setGodPlan(null);
    setPlanError("");
    setLastPipelineStatus("");
    setConsoleOutput([{ type: "system", text: "Sandbox reset. Ready for new experiment." }]);
    addLog("info", "Sandbox reset");
  };

  useEffect(() => { 
    addLog("info", "Sandbox environment ready");
    loadExperiments();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (!pipelineId) return;
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (e) {
      }
      wsRef.current = null;
    }
    const wsBase = BACKEND_URL.startsWith("https://")
      ? BACKEND_URL.replace(/^https:\/\//, "wss://")
      : BACKEND_URL.replace(/^http:\/\//, "ws://");
    const wsUrl = `${wsBase}/ws?pipeline_id=${encodeURIComponent(pipelineId)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConsoleOutput((prev) => [...prev, { type: "info", text: `Connected to /ws (${pipelineId})` }]);
    };
    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        const type = msg?.type;
        const stepIndex = typeof msg?.data?.step_index === "number" ? msg.data.step_index : msg?.data?.step_id;
        const agentName = msg?.data?.agent_name || msg?.data?.agent_id || "";
        if (type === "pipeline_complete") {
          setIsRunning(false);
          setLastPipelineStatus(String(msg?.data?.status || "complete"));
          setPreview({ type: "component", content: submittedPrompt });
          setConsoleOutput((prev) => [...prev, { type: "success", text: "Experiment complete." }]);
          addLog("success", "Sandbox experiment complete");
          loadExperiments();
          return;
        }
        if (typeof stepIndex === "number") {
          if (type === "step_start") {
            setBuildSteps((prev) =>
              prev.map((s, i) => (i === stepIndex ? { ...s, status: "running" } : s))
            );
            setConsoleOutput((prev) => [...prev, { type: "info", text: `[${agentName || `Step ${stepIndex + 1}`}] started` }]);
          } else if (type === "step_complete") {
            const out = msg?.data?.output_data;
            const text = typeof out?.data?.text === "string" ? out.data.text : "";
            setBuildSteps((prev) =>
              prev.map((s, i) => (i === stepIndex ? { ...s, status: "done", output: text ? text.slice(0, 120) : "Completed" } : s))
            );
            setConsoleOutput((prev) => [...prev, { type: "info", text: `[${agentName || `Step ${stepIndex + 1}`}] completed` }]);
          } else if (type === "step_failed") {
            setBuildSteps((prev) =>
              prev.map((s, i) => (i === stepIndex ? { ...s, status: "error", output: "Failed" } : s))
            );
            setConsoleOutput((prev) => [...prev, { type: "error", text: `[${agentName || `Step ${stepIndex + 1}`}] failed` }]);
          }
        }
      } catch (e) {
      }
    };
    ws.onerror = () => {
      setConsoleOutput((prev) => [...prev, { type: "warn", text: "WebSocket error" }]);
    };
    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      try {
        ws.close();
      } catch (e) {
      }
      wsRef.current = null;
    };
  }, [addLog, loadExperiments, pipelineId, submittedPrompt]);

  const stopGodMode = useCallback(async () => {
    const pid = String(pipelineId || "").trim();
    if (!pid || !isRunning) return;
    try {
      const res = await apiFetch(`/pipeline/stop?pipeline_id=${encodeURIComponent(pid)}`, { method: "POST" });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Stop failed");
      setConsoleOutput((prev) => [...prev, { type: "warn", text: `Stop requested: ${pid}` }]);
    } catch (e) {
      setConsoleOutput((prev) => [...prev, { type: "warn", text: e?.message || "Stop failed" }]);
    }
  }, [isRunning, pipelineId]);

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
            {godPlan?.tasks && Array.isArray(godPlan.tasks) && (
              <div style={{ marginTop: 12 }}>
                <div style={{ fontSize: 11, opacity: 0.8, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Plan Tasks ({godPlan.tasks.length})
                </div>
                <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
                  {godPlan.tasks.slice(0, 12).map((t) => (
                    <div key={t.task_id} style={{ fontSize: 12, opacity: 0.9 }}>
                      <span style={{ fontWeight: 600 }}>{t.assigned_agent}</span>: {t.description}
                    </div>
                  ))}
                  {godPlan.tasks.length > 12 ? (
                    <div style={{ fontSize: 12, opacity: 0.7 }}>…and {godPlan.tasks.length - 12} more</div>
                  ) : null}
                </div>
              </div>
            )}
            {godProjectPath ? (
              <div style={{ marginTop: 12, fontSize: 12, opacity: 0.9 }}>
                <span style={{ fontWeight: 600 }}>Project:</span> {godProjectPath}
              </div>
            ) : null}
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
          {experiments.length > 0 && (
            <div className="page-section">
              <div className="workspace-card-title">Experiments</div>
              <div className="item-list">
                {experiments.slice().reverse().slice(0, 10).map((ex) => (
                  <div key={ex.id || ex.experiment_id || JSON.stringify(ex)} className="item-row">
                    <span className="item-name">{ex.id || ex.experiment_id || "experiment"}</span>
                    <span className="item-meta">{ex.status || ""}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
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
          <select
            className="select"
            value={targetGameEngine}
            onChange={(e) => setTargetGameEngine(e.target.value)}
            disabled={isRunning}
            style={{ width: 160 }}
          >
            <option value="auto">engine: auto</option>
            <option value="unreal">engine: unreal</option>
            <option value="unity">engine: unity</option>
          </select>
          <label style={{ display: "inline-flex", gap: 6, alignItems: "center", fontSize: 12, opacity: 0.85 }}>
            <input
              type="checkbox"
              checked={autoLaunchEngine}
              onChange={(e) => setAutoLaunchEngine(e.target.checked)}
              disabled={isRunning}
            />
            launch engine
          </label>
          <button className="btn btn-secondary" onClick={stopGodMode} disabled={!isRunning || !pipelineId}>
            Stop
          </button>
          <button className="btn btn-primary" onClick={runExperiment} disabled={isRunning || !prompt.trim()}>
            {isRunning ? <div className="btn-spinner" /> : <Play size={14} />}
            {isRunning ? "Building..." : "God Mode Build"}
          </button>
        </div>
        {planLoading && <div className="item-empty">Generating plan…</div>}
        {planError && <div className="item-empty">{planError}</div>}
        {lastPipelineStatus && <div className="item-empty">Last run: {lastPipelineStatus}</div>}
      </div>
    </div>
  );
};

const GameDevPanel = ({ addLog }) => {
  const [projects, setProjects] = useState([]);
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("");
  const [platform, setPlatform] = useState("cross-platform");
  const [error, setError] = useState("");
  const [prompt, setPrompt] = useState("");
  const [engine, setEngine] = useState("unreal");
  const [busy, setBusy] = useState(false);
  const [engines, setEngines] = useState(null);

  useEffect(() => {
    const s = localGet("agentforge_gamedev_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.title === "string") setTitle(s.title);
      if (typeof s.genre === "string") setGenre(s.genre);
      if (typeof s.platform === "string") setPlatform(s.platform);
      if (typeof s.prompt === "string") setPrompt(s.prompt);
      if (typeof s.engine === "string") setEngine(s.engine);
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_gamedev_state", {
      title,
      genre,
      platform,
      prompt,
      engine,
    });
  }, [title, genre, platform, prompt, engine]);
  const loadProjects = useCallback(async () => {
    try {
      const res = await apiFetch("/modules/game_dev/projects");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setProjects(data.data);
      }
    } catch (e) {
      setError("Game Dev API unavailable");
    }
  }, []);

  const loadEngines = useCallback(async () => {
    try {
      const res = await apiFetch("/modules/game_dev/engines");
      const data = await res.json();
      if (data?.success) setEngines(data.data);
    } catch (e) {
    }
  }, []);

  const createDesign = async () => {
    if (!title.trim()) return;
    setError("");
    try {
      const res = await apiFetch("/modules/game_dev/design", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, genre, platform }),
      });
      const data = await res.json();
      if (data?.success) {
        addLog("info", `Game design created: ${title}`);
        setTitle(""); setGenre("");
        await loadProjects();
        return;
      }
    } catch (e) {
      setError("Game design request failed");
    }
    addLog("error", "Game design failed");
  };

  const createProject = async () => {
    if (!title.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await apiFetch("/modules/game_dev/projects/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          engine,
          prompt: prompt || "",
          genre,
          platform,
        }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Create project failed");
      addLog("success", `Game project created (${engine}): ${title}`);
      setTitle("");
      setGenre("");
      setPrompt("");
      await loadProjects();
    } catch (e) {
      setError(e?.message || "Create project failed");
      addLog("error", "Create project failed");
    } finally {
      setBusy(false);
    }
  };

  const launchProject = async (projectId) => {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await apiFetch("/modules/game_dev/projects/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Launch failed");
      addLog("info", `Launched ${data?.data?.engine || "engine"}: ${projectId}`);
    } catch (e) {
      setError(e?.message || "Launch failed");
    } finally {
      setBusy(false);
    }
  };

  const buildProject = async (projectId) => {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await apiFetch("/modules/game_dev/projects/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, target: "win64" }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Build failed");
      addLog("success", `Build succeeded: ${projectId}`);
    } catch (e) {
      setError(e?.message || "Build failed");
      addLog("warn", `Build failed: ${projectId}`);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => { 
    addLog("info", "Game development module loaded");
    loadProjects();
    loadEngines();
    // eslint-disable-next-line
  }, []);

  return (
    <div className="workspace-card">
      <div className="workspace-card-title">Game Development</div>
      <div className="panel-actions">
        <input className="input" placeholder="Game title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input className="input" placeholder="Genre" value={genre} onChange={(e) => setGenre(e.target.value)} />
        <select className="select" value={engine} onChange={(e) => setEngine(e.target.value)} disabled={busy}>
          <option value="unreal">Unreal</option>
          <option value="unity">Unity</option>
        </select>
        <select className="select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="cross-platform">cross-platform</option>
          <option value="pc">PC</option>
          <option value="mobile">mobile</option>
          <option value="web">web</option>
        </select>
        <button className="btn btn-secondary" onClick={createDesign} disabled={busy}>Create Design Doc</button>
        <button className="btn btn-primary" onClick={createProject} disabled={busy || !title.trim()}>
          {busy ? "Working..." : "Create Game Project"}
        </button>
      </div>
      <div className="panel-actions">
        <textarea
          className="input"
          placeholder="Game prompt / requirements..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={2}
          style={{ flex: 1, resize: "vertical" }}
        />
        <button className="btn btn-secondary" onClick={loadEngines} disabled={busy}>
          Detect Engines
        </button>
        {engines?.unity && (
          <span className={`item-badge ${engines.unity.detected ? "success" : "warning"}`}>
            Unity {engines.unity.detected ? "OK" : "Missing"}
          </span>
        )}
        {engines?.unreal && (
          <span className={`item-badge ${engines.unreal.detected ? "success" : "warning"}`}>
            Unreal {engines.unreal.detected ? "OK" : "Missing"}
          </span>
        )}
      </div>
      <div className="item-list">
        {error && <div className="item-empty">{error}</div>}
        {projects.length === 0 ? (
          <div className="item-empty">No projects yet.</div>
        ) : (
          projects.slice().reverse().map((p, i) => (
            <div className="item-row" key={i} style={{ alignItems: "center" }}>
              <span className={`item-badge ${p.status}`}>{p.status}</span>
              <span className="item-name">{p.title}</span>
              <span className="item-meta">{p.engine || "—"} · {p.genre} · {p.platform}</span>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button className="btn btn-sm btn-secondary" onClick={() => launchProject(p.id)} disabled={busy}>
                  Launch
                </button>
                <button className="btn btn-sm btn-primary" onClick={() => buildProject(p.id)} disabled={busy}>
                  Build
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const SaasBuilderPanel = ({ addLog }) => {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState("");
  const [frontend, setFrontend] = useState("react");
  const [backend, setBackend] = useState("fastapi");
  const [error, setError] = useState("");

  useEffect(() => {
    const s = localGet("agentforge_saas_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.name === "string") setName(s.name);
      if (typeof s.frontend === "string") setFrontend(s.frontend);
      if (typeof s.backend === "string") setBackend(s.backend);
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_saas_state", {
      name,
      frontend,
      backend,
    });
  }, [name, frontend, backend]);
  const loadSaasProjects = useCallback(async () => {
    try {
      const res = await apiFetch("/modules/saas_builder/projects");
      const data = await res.json();
      if (data?.success && Array.isArray(data.data)) {
        setProjects(data.data);
      }
    } catch (e) {
      setError("SaaS Builder API unavailable");
    }
  }, []);

  const scaffold = async () => {
    if (!name.trim()) return;
    setError("");
    try {
      const res = await apiFetch("/modules/saas_builder/scaffold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, stack: { frontend, backend, db: "postgres" } }),
      });
      const data = await res.json();
      if (data?.success) {
        addLog("info", `SaaS scaffolded: ${name}`);
        setName("");
        await loadSaasProjects();
        return;
      }
    } catch (e) {
      setError("SaaS scaffold request failed");
    }
    addLog("error", "SaaS scaffold failed");
  };

  useEffect(() => { 
    addLog("info", "SaaS Builder ready");
    loadSaasProjects();
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
        {error && <div className="item-empty">{error}</div>}
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

  useEffect(() => {
    const s = localGet("agentforge_agent_console_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.input === "string") setInput(s.input);
      if (typeof s.activeAgentId === "string") {
        const found = AGENTS.find((a) => a.id === s.activeAgentId);
        if (found) setActiveAgent(found);
      }
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_agent_console_state", {
      input,
      activeAgentId: activeAgent?.id,
    });
  }, [input, activeAgent]);
  const getAgent = (id) => AGENTS.find(a => a.id === id) || AGENTS[0];
  const agentTaskType = (agentId) => {
    const m = {
      planner: "planning",
      architect: "planning",
      router: "planning",
      builder: "coding",
      api: "coding",
      data: "research",
      backend: "coding",
      frontend: "ui_design",
      ai: "coding",
      tester: "debugging",
      auditor: "debugging",
      stabilizer: "debugging",
    };
    return m[agentId] || "conversation";
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const prompt = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: prompt }]);
    setLoading(true);

    try {
      const providerPayload = getAgentRunProviderPayload();
      const res = await apiFetch("/agent/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, task_type: agentTaskType(activeAgent.id), agent_id: activeAgent.id, ...providerPayload })
      });
      const data = await res.json();
      const text = data?.data?.data?.text || data?.data?.error || data?.error || "Processing your request...";
      setMessages((prev) => [...prev, { role: "agent", agentId: activeAgent.id, text }]);
      addLog("info", `${activeAgent.name} responded`);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", agentId: activeAgent.id, text: "Agent request failed. Is the backend running?" },
      ]);
      addLog("error", "Agent request failed");
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
const PipelineMonitor = ({ addLog }) => {
  const [activeStage, setActiveStage] = useState(null);
  const [events, setEvents] = useState([]);
  const cursorRef = useRef(0);
  const [pipelinePrompt, setPipelinePrompt] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const eventsRef = useRef(null);

  useEffect(() => {
    const s = localGet("agentforge_pipeline_monitor_state", null);
    if (!s || typeof s !== "object") return;
    try {
      if (typeof s.pipelinePrompt === "string") setPipelinePrompt(s.pipelinePrompt);
    } catch (e) {}
  }, []);

  useEffect(() => {
    localSet("agentforge_pipeline_monitor_state", {
      pipelinePrompt,
    });
  }, [pipelinePrompt]);
  const pollEvents = useCallback(async () => {
    try {
      const cursor = cursorRef.current;
      const res = await apiFetch(`/pipeline/events?cursor=${cursor}`);
      const data = await res.json();
      if (!data?.success || !data?.data) return;
      const next = Array.isArray(data.data.events) ? data.data.events : [];
      const nextCursor = data.data.next_cursor;
      if (typeof nextCursor === "number") cursorRef.current = nextCursor;
      if (next.length) {
        setEvents((prev) => [...prev, ...next].slice(-200));
        const latest = next[next.length - 1];
        if (latest?.agent_name) setActiveStage(latest.agent_name);
      }
    } catch (e) {
    }
  }, []);

  useEffect(() => {
    pollEvents();
    const id = setInterval(pollEvents, 2500);
    return () => clearInterval(id);
  }, [pollEvents]);

  useEffect(() => {
    if (eventsRef.current) {
      eventsRef.current.scrollTop = eventsRef.current.scrollHeight;
    }
  }, [events]);

  const runPipeline = async () => {
    if (!pipelinePrompt.trim() || running) return;
    setRunning(true);
    setError(null);
    addLog?.("info", "Pipeline requested");
    try {
      const res = await apiFetch("/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: pipelinePrompt }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Pipeline run failed");
      setPipelinePrompt("");
    } catch (e) {
      setError(e.message || "Pipeline run failed");
      addLog?.("warn", "Pipeline run failed");
    } finally {
      setRunning(false);
    }
  };

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
      <div className="pipeline-events" ref={eventsRef}>
        {events.length === 0 ? (
          <div className="item-empty">No pipeline activity yet.</div>
        ) : (
          events.slice(-50).map((evt, idx) => (
            <div key={idx} className="pipeline-event">
              <span className={`event-type ${evt.event_type}`}>{evt.event_type}</span>
              <span className="event-agent">{evt.agent_name || "—"}</span>
              <span className="event-time">{evt.timestamp?.split("T")[1]?.split(".")[0] || evt.timestamp}</span>
            </div>
          ))
        )}
      </div>
      <form className="pipeline-runner" onSubmit={(e) => { e.preventDefault(); runPipeline(); }}>
        <input
          className="input"
          placeholder="Describe the outcome to generate..."
          value={pipelinePrompt}
          onChange={(e) => setPipelinePrompt(e.target.value)}
          disabled={running}
        />
        <button className="btn btn-primary" type="submit" disabled={running || !pipelinePrompt.trim()}>
          {running ? "Running..." : "Run Pipeline"}
        </button>
      </form>
      {error && <div className="pipeline-error">{error}</div>}
    </div>
  );
};

// Output Log Panel (New 3rd bottom panel)
const OutputLog = ({ logs }) => {
  const logsRef = useRef(null);
  const [logSource, setLogSource] = useState("system");
  const [backendLogs, setBackendLogs] = useState([]);

  useEffect(() => {
    const s = localGet("agentforge_outputlog_state", null);
    if (s && typeof s === "object" && typeof s.logSource === "string") {
      setLogSource(s.logSource);
    }
  }, []);

  useEffect(() => {
    localSet("agentforge_outputlog_state", { logSource });
  }, [logSource]);

  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight;
    }
  }, [logs, backendLogs, logSource]);

  useEffect(() => {
    if (logSource === "ui") return;
    let cancelled = false;
    let timer;
    const tick = async () => {
      try {
        const res = await apiFetch(`/logs?source=${encodeURIComponent(logSource)}&limit=200`);
        const payload = await res.json();
        const entries = payload?.data?.entries;
        if (!cancelled && Array.isArray(entries)) {
          setBackendLogs(entries.slice(-200));
        }
      } catch (e) {
      } finally {
        if (!cancelled) timer = setTimeout(tick, 1500);
      }
    };
    tick();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [logSource]);

  const entries = logSource === "ui" ? logs : backendLogs;

  return (
    <div className="panel-content">
      <div className="panel-title">Output Log</div>
      <div className="panel-actions">
        <select className="select" value={logSource} onChange={(e) => setLogSource(e.target.value)}>
          <option value="ui">ui</option>
          <option value="system">system</option>
          <option value="pipeline">pipeline</option>
          <option value="agents">agents</option>
          <option value="deployment">deployment</option>
          <option value="errors">errors</option>
        </select>
      </div>
      <div className="output-log" ref={logsRef}>
        {entries.map((log, i) => (
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
const Studio = ({ initialModuleId }) => {
  const [activeModule, setActiveModule] = useState(() => {
    if (initialModuleId) {
      const match = MODULES.find((m) => m.id === initialModuleId);
      if (match) return match;
    }
    try {
      const savedId = localGet("agentforge_active_module_id", null);
      if (typeof savedId === "string" && savedId) {
        const match = MODULES.find((m) => m.id === savedId);
        if (match) return match;
      }
    } catch (e) {}
    return MODULES[0];
  });
  const [logs, setLogs] = useState([{ time: formatTime(), level: "info", message: "AgentForgeOS initialized" }]);
  const [activeModal, setActiveModal] = useState(null);
  const [layoutSizes, setLayoutSizes] = useState(() => {
    const s = localGet("agentforge_layout_sizes", null);
    const defaults = { topMain: 70, leftSidebar: 15, bottomMain: 30, bottomLeft: 33, bottomMid: 34, bottomRight: 33 };
    if (!s || typeof s !== "object") return defaults;
    return {
      topMain: typeof s.topMain === "number" ? s.topMain : defaults.topMain,
      leftSidebar: typeof s.leftSidebar === "number" ? s.leftSidebar : defaults.leftSidebar,
      bottomMain: typeof s.bottomMain === "number" ? s.bottomMain : defaults.bottomMain,
      bottomLeft: typeof s.bottomLeft === "number" ? s.bottomLeft : defaults.bottomLeft,
      bottomMid: typeof s.bottomMid === "number" ? s.bottomMid : defaults.bottomMid,
      bottomRight: typeof s.bottomRight === "number" ? s.bottomRight : defaults.bottomRight,
    };
  });

  const addLog = (level, message) => {
    setLogs((prev) => [...prev.slice(-50), { time: formatTime(), level, message }]);
  };

  const openModal = (modal) => setActiveModal(modal);
  const closeModal = () => setActiveModal(null);

  useEffect(() => {
    localSet("agentforge_active_module_id", activeModule?.id || MODULES[0].id);
  }, [activeModule]);

  const saveLayoutSizes = (next) => {
    setLayoutSizes(next);
    localSet("agentforge_layout_sizes", next);
  };

  useEffect(() => {
    const restored = localGet("agentforge_active_modal", null);
    const allowed = new Set(["project", "workspace", "providers", "system", "settings"]);
    const settingsState = localGet("agentforge_settings_state", null);
    let restoreEnabled = true;
    try {
      if (settingsState && typeof settingsState === "object" && settingsState.settings) {
        const s = settingsState.settings;
        if (typeof s.restoreLastModal === "boolean") {
          restoreEnabled = s.restoreLastModal;
        }
      }
    } catch (e) {}
    if (!restoreEnabled) return;
    if (typeof restored === "string" && allowed.has(restored)) {
      setActiveModal(restored);
    }
  }, []);

  useEffect(() => {
    const allowed = new Set(["project", "workspace", "providers", "system", "settings"]);
    if (typeof activeModal === "string" && allowed.has(activeModal)) {
      localSet("agentforge_active_modal", activeModal);
    } else if (activeModal == null) {
      // Clearing modal leaves last value; do not overwrite with null to allow restore.
    }
  }, [activeModal]);

  return (
    <div className="studio-layout" data-testid="studio-layout">
      <NavBar onOpenModal={openModal} />
      <ResizablePanelGroup direction="vertical" className="studio-resizable-main">
        {/* Top: Sidebar + Workspace */}
        <ResizablePanel
          defaultSize={layoutSizes.topMain}
          minSize={40}
          onResize={(size) => saveLayoutSizes({ ...layoutSizes, topMain: size })}
        >
          <ResizablePanelGroup direction="horizontal">
            <ResizablePanel
              defaultSize={layoutSizes.leftSidebar}
              minSize={10}
              maxSize={25}
              onResize={(size) => saveLayoutSizes({ ...layoutSizes, leftSidebar: size })}
            >
              <Sidebar activeModule={activeModule} setActiveModule={setActiveModule} />
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel defaultSize={100 - layoutSizes.leftSidebar}>
              <Workspace module={activeModule} addLog={addLog} />
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
        
        <ResizableHandle className="resize-handle-vertical" />
        
        {/* Bottom: 3-way split */}
        <ResizablePanel
          defaultSize={layoutSizes.bottomMain}
          minSize={15}
          maxSize={50}
          onResize={(size) => saveLayoutSizes({ ...layoutSizes, bottomMain: size })}
        >
          <ResizablePanelGroup direction="horizontal" className="studio-bottom-panels">
            <ResizablePanel
              defaultSize={layoutSizes.bottomLeft}
              minSize={20}
              onResize={(size) => saveLayoutSizes({ ...layoutSizes, bottomLeft: size })}
            >
              <div className="panel">
                <AgentConsole addLog={addLog} />
              </div>
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel
              defaultSize={layoutSizes.bottomMid}
              minSize={20}
              onResize={(size) => saveLayoutSizes({ ...layoutSizes, bottomMid: size })}
            >
              <div className="panel">
                <PipelineMonitor addLog={addLog} />
              </div>
            </ResizablePanel>
            <ResizableHandle className="resize-handle-horizontal" />
            <ResizablePanel
              defaultSize={layoutSizes.bottomRight}
              minSize={20}
              onResize={(size) => saveLayoutSizes({ ...layoutSizes, bottomRight: size })}
            >
              <div className="panel">
                <OutputLog logs={logs} />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
      </ResizablePanelGroup>

      {/* Modal Pages */}
      <ProjectPage isOpen={activeModal === 'project'} onClose={closeModal} addLog={addLog} />
      <WorkspacePage isOpen={activeModal === 'workspace'} onClose={closeModal} addLog={addLog} />
      <ProvidersPage isOpen={activeModal === 'providers'} onClose={closeModal} addLog={addLog} />
      <SystemPage isOpen={activeModal === 'system'} onClose={closeModal} addLog={addLog} />
      <SettingsPage isOpen={activeModal === 'settings'} onClose={closeModal} addLog={addLog} />
      <ProfilePage isOpen={activeModal === 'profile'} onClose={closeModal} addLog={addLog} />
    </div>
  );
};

// ===============================================
// SETUP WIZARD - First Time Setup Flow
// ===============================================

const WIZARD_STEPS = [
  { id: 1, name: "Welcome", icon: Sparkles },
  { id: 2, name: "LLM Provider", icon: Bot },
  { id: 3, name: "Image & Voice", icon: ImageIcon },
  { id: 4, name: "Storage & Bridge", icon: HardDrive },
  { id: 5, name: "Review & Launch", icon: Rocket },
];

const SetupWizard = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [config, setConfig] = useState({
    // Engine
    engineHost: "127.0.0.1",
    enginePort: "8000",
    workspacePath: "",
    // LLM
    llmProvider: "ollama",
    ollamaUrl: "http://localhost:11434",
    ollamaModel: "llama3",
    openaiKey: "",
    openaiModel: "gpt-4.1",
    falLlmModel: "fal-ai/llama3.1-8b-instruct",
    // Image
    imageProvider: "comfyui",
    comfyuiUrl: "http://localhost:8188",
    falApiKey: "",
    // Voice
    ttsEnabled: false,
    ttsProvider: "piper",
    piperModelPath: "",
    elevenlabsKey: "",
    // Storage
    bridgeRoot: "",
    logLevel: "INFO",
    mongoEnabled: false,
    mongoType: "atlas",
    mongoUrl: "mongodb://localhost:27017",
    mongoAtlasUrl: "",
    mongoDbName: "agentforge",
  });
  const [connectionTests, setConnectionTests] = useState({
    engine: null,
    llm: null,
    image: null,
    tts: null,
    mongo: null,
  });
  const [testing, setTesting] = useState({});
  const [saveError, setSaveError] = useState("");

  const buildEnvPayload = useCallback(() => {
    const keyMap = {
      engineHost: "AGENTFORGE_HOST",
      enginePort: "AGENTFORGE_PORT",
      workspacePath: "WORKSPACE_PATH",
      llmProvider: "PROVIDER_LLM",
      ollamaUrl: "OLLAMA_BASE_URL",
      ollamaModel: "OLLAMA_MODEL",
      openaiKey: "OPENAI_API_KEY",
      openaiModel: "OPENAI_MODEL",
      falLlmModel: "FAL_LLM_MODEL",
      imageProvider: "PROVIDER_IMAGE",
      comfyuiUrl: "COMFYUI_BASE_URL",
      falApiKey: "FAL_API_KEY",
      ttsProvider: "PROVIDER_TTS",
      piperModelPath: "PIPER_MODEL_PATH",
      bridgeRoot: "BRIDGE_ROOT",
      logLevel: "LOG_LEVEL",
    };

    const payload = {};
    Object.entries(keyMap).forEach(([field, key]) => {
      const value = config[field];
      if (value != null && value !== "") payload[key] = value;
    });
    if (payload.WORKSPACE_PATH && !payload.BRIDGE_ROOT) {
      payload.BRIDGE_ROOT = payload.WORKSPACE_PATH;
    }
    if (config.mongoEnabled) {
      const uri = (config.mongoType === "atlas" ? config.mongoAtlasUrl : config.mongoUrl) || "";
      if (uri) payload.AGENTFORGE_MONGO_URI = uri;
      if (config.mongoDbName) payload.AGENTFORGE_MONGO_DB = config.mongoDbName;
    }
    return payload;
  }, [config]);

  useEffect(() => {
    let cancelled = false;
    const loadDefaults = async () => {
      try {
        const res = await apiFetch("/workspace/status");
        const data = await res.json();
        const ws = data?.data?.workspace_path;
        if (!cancelled && ws && typeof ws === "string") {
          setConfig((prev) => ({
            ...prev,
            workspacePath: prev.workspacePath || ws,
            bridgeRoot: prev.bridgeRoot || ws,
          }));
        }
      } catch (e) {
      }
    };
    loadDefaults();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const testConnection = async (type) => {
    setTesting(prev => ({ ...prev, [type]: true }));
    let success = false;
    let detail = "";
    try {
      let res;
      if (type === "engine") {
        res = await apiFetch("/system/health");
      } else if (type === "llm" || type === "image" || type === "tts" || type === "mongo") {
        res = await apiFetch(`/setup/test?type=${encodeURIComponent(type)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ config: buildEnvPayload() }),
        });
      } else {
        res = await apiFetch("/system/health");
      }
      const data = await res.json();
      if (type === "llm" || type === "image" || type === "tts" || type === "mongo") {
        const result = data?.data?.results?.[type];
        success = !!result?.ok;
        detail = typeof result?.detail === "string" ? result.detail : "";
      } else {
        success = !!data?.success;
        detail = success ? "ok" : (typeof data?.error === "string" ? data.error : "");
      }
    } catch (e) {
      success = false;
      detail = e?.message ? String(e.message) : "";
    }
    setConnectionTests(prev => ({ ...prev, [type]: { ok: success, detail } }));
    setTesting(prev => ({ ...prev, [type]: false }));
  };

  const nextStep = () => {
    if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const finishSetup = async () => {
    try {
      setSaveError("");
      const payload = buildEnvPayload();
      const res = await apiFetch("/setup/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config: payload }),
      });
      const data = await res.json();
      if (!data?.success) throw new Error(data?.error || "Failed to save setup");
      try {
        const host = String(config.engineHost || "127.0.0.1").trim();
        const port = String(config.enginePort || "8000").trim();
        if (host && port) localStorage.setItem("agentforge_backend_url", `http://${host}:${port}`);
      } catch (e) {
      }
      localStorage.setItem("agentforge_setup_complete", "true");
      onComplete();
    } catch (e) {
      setSaveError(e?.message || "Failed to save setup");
    }
  };

  // Connection status indicator
  const ConnectionStatus = ({ status, testing: isTesting }) => {
    if (isTesting) {
      return (
        <div className="connection-status pending">
          <div className="status-dot" />
          <div className="status-label">Testing...</div>
        </div>
      );
    }
    if (status === null) {
      return (
        <div className="connection-status pending">
          <div className="status-dot" />
          <div className="status-label">Not tested</div>
        </div>
      );
    }
    const ok = typeof status === "object" ? !!status.ok : !!status;
    const detail = typeof status === "object" && typeof status.detail === "string" ? status.detail : "";
    return (
      <div className={`connection-status ${ok ? "online" : "pending"}`}>
        <div className="status-dot" />
        <div className="status-label">{ok ? "Connected" : "Failed"}{detail ? ` — ${detail}` : ""}</div>
      </div>
    );
  };

  return (
    <div className="wizard-overlay">
      <div className="wizard-container">
        {/* Header */}
        <div className="wizard-header">
          <div className="wizard-logo">
            <div className="logo-hexagon large">
              <span className="logo-letters">AF</span>
            </div>
            <div className="wizard-title-group">
              <h1 className="wizard-title">AgentForgeOS Setup</h1>
              <p className="wizard-subtitle">Let's configure your local development environment</p>
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="wizard-progress">
          {WIZARD_STEPS.map((step, idx) => {
            const Icon = step.icon;
            const isActive = step.id === currentStep;
            const isComplete = step.id < currentStep;
            return (
              <div key={step.id} className={`wizard-step ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''}`}>
                <div className="wizard-step-icon">
                  {isComplete ? <Check size={16} /> : <Icon size={16} />}
                </div>
                <span className="wizard-step-name">{step.name}</span>
                {idx < WIZARD_STEPS.length - 1 && <div className="wizard-step-line" />}
              </div>
            );
          })}
        </div>

        {/* Content */}
        <div className="wizard-content">
          {/* Step 1: Welcome */}
          {currentStep === 1 && (
            <div className="wizard-step-content">
              <div className="welcome-hero">
                <Sparkles size={48} className="welcome-icon" />
                <h2>Welcome to AgentForgeOS</h2>
                <p>Your local-first AI development operating system for building software with intelligent agents.</p>
              </div>

              <div className="prereq-section">
                <h3>Prerequisites Check</h3>
                <p className="prereq-desc">Make sure you have these installed before continuing:</p>
                <div className="prereq-grid">
                  <div className="prereq-item installed">
                    <Check size={16} />
                    <span>Windows 10 (64-bit)</span>
                  </div>
                  <div className="prereq-item installed">
                    <Check size={16} />
                    <span>Python 3.11+</span>
                  </div>
                  <div className="prereq-item installed">
                    <Check size={16} />
                    <span>Git</span>
                  </div>
                  <div className="prereq-item optional">
                    <Circle size={16} />
                    <span>Node.js 20+ (for desktop)</span>
                  </div>
                  <div className="prereq-item optional">
                    <Circle size={16} />
                    <span>Rust + Cargo (for desktop)</span>
                  </div>
                </div>
              </div>

              <div className="engine-config">
                <h3>Engine Configuration</h3>
                <div className="config-row">
                  <div className="config-field">
                    <label>Host</label>
                    <input 
                      className="input" 
                      value={config.engineHost} 
                      onChange={(e) => updateConfig('engineHost', e.target.value)}
                    />
                  </div>
                  <div className="config-field">
                    <label>Port</label>
                    <input 
                      className="input" 
                      value={config.enginePort} 
                      onChange={(e) => updateConfig('enginePort', e.target.value)}
                    />
                  </div>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => testConnection('engine')}
                    disabled={testing.engine}
                  >
                    <Activity size={14} /> Test
                  </button>
                </div>
                <ConnectionStatus status={connectionTests.engine} testing={testing.engine} />
              </div>

              <div className="bootstrap-commands">
                <h3>Quick Bootstrap (PowerShell)</h3>
                <div className="code-block">
                  <code>
                    cd AgentForgeOS{'\n'}
                    python -m venv .venv{'\n'}
                    .\.venv\Scripts\Activate.ps1{'\n'}
                    pip install -r requirements.txt{'\n'}
                    python -m engine.main
                  </code>
                  <button className="copy-btn" onClick={() => navigator.clipboard.writeText('cd AgentForgeOS\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\npython -m engine.main')}>
                    Copy
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: LLM Provider */}
          {currentStep === 2 && (
            <div className="wizard-step-content">
              <div className="step-header">
                <Bot size={32} className="step-icon" />
                <div>
                  <h2>LLM Provider</h2>
                  <p>Choose how agents will communicate with language models</p>
                  <p className="section-desc muted">Fal.ai can be used for both LLM and image generation.</p>
                </div>
              </div>

              <div className="provider-selection">
                <div 
                  className={`provider-option ${config.llmProvider === 'ollama' ? 'selected' : ''}`}
                  onClick={() => updateConfig('llmProvider', 'ollama')}
                >
                  <div className="provider-option-header">
                    <Radio size={18} className={config.llmProvider === 'ollama' ? 'checked' : ''} />
                    <div className="provider-option-title">
                      <span>Ollama</span>
                      <span className="provider-badge local">Local</span>
                    </div>
                  </div>
                  <p>Run LLMs locally on your machine. No API key required.</p>
                  <a href="https://ollama.com/download/windows" target="_blank" rel="noopener noreferrer" className="provider-link">
                    <Download size={14} /> Download Ollama
                  </a>
                </div>

                <div 
                  className={`provider-option ${config.llmProvider === 'openai' ? 'selected' : ''}`}
                  onClick={() => updateConfig('llmProvider', 'openai')}
                >
                  <div className="provider-option-header">
                    <Radio size={18} className={config.llmProvider === 'openai' ? 'checked' : ''} />
                    <div className="provider-option-title">
                      <span>OpenAI</span>
                      <span className="provider-badge cloud">Cloud</span>
                    </div>
                  </div>
                  <p>Use GPT-4 and other OpenAI models via API.</p>
                  <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="provider-link">
                    <ExternalLink size={14} /> Get API Key
                  </a>
                </div>

                <div 
                  className={`provider-option ${config.llmProvider === 'fal' ? 'selected' : ''}`}
                  onClick={() => updateConfig('llmProvider', 'fal')}
                >
                  <div className="provider-option-header">
                    <Radio size={18} className={config.llmProvider === 'fal' ? 'checked' : ''} />
                    <div className="provider-option-title">
                      <span>Fal.ai</span>
                      <span className="provider-badge cloud">Cloud</span>
                    </div>
                  </div>
                  <p>Use hosted models via fal.ai with your API key.</p>
                  <a href="https://fal.ai/" target="_blank" rel="noopener noreferrer" className="provider-link">
                    <ExternalLink size={14} /> Open Fal.ai
                  </a>
                </div>
              </div>

              {config.llmProvider === 'ollama' && (
                <div className="provider-config">
                  <h3>Ollama Configuration</h3>
                  <div className="config-row">
                    <div className="config-field flex-1">
                      <label>Base URL</label>
                      <input 
                        className="input" 
                        value={config.ollamaUrl} 
                        onChange={(e) => updateConfig('ollamaUrl', e.target.value)}
                        placeholder="http://localhost:11434"
                      />
                    </div>
                    <div className="config-field">
                      <label>Model</label>
                      <select 
                        className="select"
                        value={config.ollamaModel}
                        onChange={(e) => updateConfig('ollamaModel', e.target.value)}
                      >
                        <option value="llama3">llama3</option>
                        <option value="llama3:70b">llama3:70b</option>
                        <option value="mistral">mistral</option>
                        <option value="codellama">codellama</option>
                        <option value="deepseek-coder">deepseek-coder</option>
                      </select>
                    </div>
                  </div>
                  <div className="config-row">
                    <button 
                      className="btn btn-secondary"
                      onClick={() => testConnection('llm')}
                      disabled={testing.llm}
                    >
                      <Activity size={14} /> Test Connection
                    </button>
                    <ConnectionStatus status={connectionTests.llm} testing={testing.llm} />
                  </div>
                  <div className="helper-box">
                    <AlertTriangle size={16} />
                    <div>
                      <strong>First time?</strong> Run this in PowerShell:
                      <code>ollama pull {config.ollamaModel}</code>
                    </div>
                  </div>
                </div>
              )}

              {config.llmProvider === 'openai' && (
                <div className="provider-config">
                  <h3>OpenAI Configuration</h3>
                  <div className="config-row">
                    <div className="config-field flex-1">
                      <label>API Key</label>
                      <div className="input-with-icon">
                        <Key size={14} />
                        <input 
                          type="password"
                          className="input" 
                          value={config.openaiKey} 
                          onChange={(e) => updateConfig('openaiKey', e.target.value)}
                          placeholder="sk-..."
                        />
                      </div>
                    </div>
                    <div className="config-field">
                      <label>Model</label>
                      <select 
                        className="select"
                        value={config.openaiModel}
                        onChange={(e) => updateConfig('openaiModel', e.target.value)}
                      >
                        <option value="gpt-4">gpt-4</option>
                        <option value="gpt-4-turbo">gpt-4-turbo</option>
                        <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                      </select>
                    </div>
                  </div>
                  <div className="config-row">
                    <button 
                      className="btn btn-secondary"
                      onClick={() => testConnection('llm')}
                      disabled={testing.llm || !config.openaiKey}
                    >
                      <Activity size={14} /> Test Connection
                    </button>
                    <ConnectionStatus status={connectionTests.llm} testing={testing.llm} />
                  </div>
                </div>
              )}

              {config.llmProvider === 'fal' && (
                <div className="provider-config">
                  <h3>Fal.ai Configuration</h3>
                  <div className="config-row">
                    <div className="config-field flex-1">
                      <label>API Key</label>
                      <div className="input-with-icon">
                        <Key size={14} />
                        <input
                          type="password"
                          className="input"
                          value={config.falApiKey}
                          onChange={(e) => updateConfig('falApiKey', e.target.value)}
                          placeholder="Enter API key..."
                        />
                      </div>
                    </div>
                    <div className="config-field">
                      <label>Model</label>
                      <input
                        className="input"
                        value={config.falLlmModel}
                        onChange={(e) => updateConfig('falLlmModel', e.target.value)}
                        placeholder="fal-ai/llama3.1-8b-instruct"
                      />
                    </div>
                  </div>
                  <div className="config-row">
                    <button
                      className="btn btn-secondary"
                      onClick={() => testConnection('llm')}
                      disabled={testing.llm || !config.falApiKey}
                    >
                      <Activity size={14} /> Test Connection
                    </button>
                    <ConnectionStatus status={connectionTests.llm} testing={testing.llm} />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Image & Voice */}
          {currentStep === 3 && (
            <div className="wizard-step-content">
              <div className="step-header">
                <ImageIcon size={32} className="step-icon" />
                <div>
                  <h2>Image & Voice Providers</h2>
                  <p>Configure optional media generation capabilities</p>
                </div>
              </div>

              {/* Image Provider */}
              <div className="provider-section">
                <h3><ImageIcon size={18} /> Image Generation</h3>
                <div className="provider-selection horizontal">
                  <div 
                    className={`provider-option small ${config.imageProvider === 'comfyui' ? 'selected' : ''}`}
                    onClick={() => updateConfig('imageProvider', 'comfyui')}
                  >
                    <Radio size={16} className={config.imageProvider === 'comfyui' ? 'checked' : ''} />
                    <span>ComfyUI</span>
                    <span className="provider-badge local">Local</span>
                  </div>
                  <div 
                    className={`provider-option small ${config.imageProvider === 'fal' ? 'selected' : ''}`}
                    onClick={() => updateConfig('imageProvider', 'fal')}
                  >
                    <Radio size={16} className={config.imageProvider === 'fal' ? 'checked' : ''} />
                    <span>Fal.ai</span>
                    <span className="provider-badge cloud">Cloud</span>
                  </div>
                  <div 
                    className={`provider-option small ${config.imageProvider === 'none' ? 'selected' : ''}`}
                    onClick={() => updateConfig('imageProvider', 'none')}
                  >
                    <Radio size={16} className={config.imageProvider === 'none' ? 'checked' : ''} />
                    <span>Disabled</span>
                  </div>
                </div>

                {config.imageProvider === 'comfyui' && (
                  <div className="inline-config">
                    <div className="config-field flex-1">
                      <label>ComfyUI URL</label>
                      <input 
                        className="input" 
                        value={config.comfyuiUrl} 
                        onChange={(e) => updateConfig('comfyuiUrl', e.target.value)}
                        placeholder="http://localhost:8188"
                      />
                    </div>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => testConnection('image')}
                      disabled={testing.image}
                    >
                      Test
                    </button>
                    <ConnectionStatus status={connectionTests.image} testing={testing.image} />
                  </div>
                )}

                {config.imageProvider === 'fal' && (
                  <div className="inline-config">
                    <div className="config-field flex-1">
                      <label>Fal.ai API Key</label>
                      <input 
                        type="password"
                        className="input" 
                        value={config.falApiKey} 
                        onChange={(e) => updateConfig('falApiKey', e.target.value)}
                        placeholder="Enter API key..."
                      />
                    </div>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => testConnection('image')}
                      disabled={testing.image}
                    >
                      Test
                    </button>
                  </div>
                )}
              </div>

              {/* TTS Provider */}
              <div className="provider-section">
                <h3><Mic size={18} /> Text-to-Speech</h3>
                <div className="tts-toggle">
                  <span>Enable TTS</span>
                  <div 
                    className={`toggle-switch-lg ${config.ttsEnabled ? 'active' : ''}`}
                    onClick={() => updateConfig('ttsEnabled', !config.ttsEnabled)}
                  >
                    <div className="toggle-knob" />
                  </div>
                </div>

                {config.ttsEnabled && (
                  <>
                    <div className="provider-selection horizontal">
                      <div 
                        className={`provider-option small ${config.ttsProvider === 'piper' ? 'selected' : ''}`}
                        onClick={() => updateConfig('ttsProvider', 'piper')}
                      >
                        <Radio size={16} className={config.ttsProvider === 'piper' ? 'checked' : ''} />
                        <span>Piper</span>
                        <span className="provider-badge local">Local</span>
                      </div>
                      <div 
                        className={`provider-option small ${config.ttsProvider === 'elevenlabs' ? 'selected' : ''}`}
                        onClick={() => updateConfig('ttsProvider', 'elevenlabs')}
                      >
                        <Radio size={16} className={config.ttsProvider === 'elevenlabs' ? 'checked' : ''} />
                        <span>ElevenLabs</span>
                        <span className="provider-badge cloud">Cloud</span>
                      </div>
                    </div>

                    {config.ttsProvider === 'piper' && (
                      <div className="inline-config">
                        <div className="config-field flex-1">
                          <label>Voice Model Path (optional)</label>
                          <input 
                            className="input" 
                            value={config.piperModelPath} 
                            onChange={(e) => updateConfig('piperModelPath', e.target.value)}
                            placeholder="C:\piper\en_US-lessac-medium.onnx"
                          />
                        </div>
                      </div>
                    )}

                    {config.ttsProvider === 'elevenlabs' && (
                      <div className="inline-config">
                        <div className="config-field flex-1">
                          <label>ElevenLabs API Key</label>
                          <input 
                            type="password"
                            className="input" 
                            value={config.elevenlabsKey} 
                            onChange={(e) => updateConfig('elevenlabsKey', e.target.value)}
                            placeholder="Enter API key..."
                          />
                        </div>
                        <button 
                          className="btn btn-secondary"
                          onClick={() => testConnection('tts')}
                          disabled={testing.tts}
                        >
                          Test
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Storage & Bridge */}
          {currentStep === 4 && (
            <div className="wizard-step-content">
              <div className="step-header">
                <HardDrive size={32} className="step-icon" />
                <div>
                  <h2>Storage & Bridge</h2>
                  <p>Configure file system access and logging</p>
                </div>
              </div>

              <div className="provider-section">
                <h3><Folder size={18} /> Bridge Root (Sandbox)</h3>
                <p className="section-desc">This is the root directory where agents can read/write files. Keep it isolated for safety.</p>
                <div className="config-field">
                  <label>Workspace Path</label>
                  <input 
                    className="input" 
                    value={config.workspacePath || config.bridgeRoot} 
                    onChange={(e) => {
                      updateConfig('workspacePath', e.target.value);
                      updateConfig('bridgeRoot', e.target.value);
                    }}
                    placeholder="C:\\AgentForgeOS\\workspace"
                  />
                </div>
                <div className="helper-box info">
                  <Shield size={16} />
                  <span>Agents cannot access files outside this directory.</span>
                </div>
              </div>

              <div className="provider-section">
                <h3><FileText size={18} /> Logging</h3>
                <div className="config-field">
                  <label>Log Level</label>
                  <select 
                    className="select"
                    value={config.logLevel}
                    onChange={(e) => updateConfig('logLevel', e.target.value)}
                  >
                    <option value="DEBUG">DEBUG - Verbose</option>
                    <option value="INFO">INFO - Standard</option>
                    <option value="WARNING">WARNING - Minimal</option>
                    <option value="ERROR">ERROR - Errors Only</option>
                  </select>
                </div>
              </div>

              <div className="provider-section">
                <h3><Database size={18} /> MongoDB Database</h3>
                <div className="tts-toggle">
                  <span>Enable MongoDB</span>
                  <div 
                    className={`toggle-switch-lg ${config.mongoEnabled ? 'active' : ''}`}
                    onClick={() => updateConfig('mongoEnabled', !config.mongoEnabled)}
                  >
                    <div className="toggle-knob" />
                  </div>
                </div>
                <p className="section-desc muted">Without MongoDB, data is stored in-memory (lost on restart).</p>

                {config.mongoEnabled && (
                  <div className="mongo-config">
                    <div className="provider-selection horizontal">
                      <div 
                        className={`provider-option small ${config.mongoType === 'local' ? 'selected' : ''}`}
                        onClick={() => updateConfig('mongoType', 'local')}
                      >
                        <Radio size={16} className={config.mongoType === 'local' ? 'checked' : ''} />
                        <span>Local</span>
                        <span className="provider-badge local">Free</span>
                      </div>
                      <div 
                        className={`provider-option small ${config.mongoType === 'atlas' ? 'selected' : ''}`}
                        onClick={() => updateConfig('mongoType', 'atlas')}
                      >
                        <Radio size={16} className={config.mongoType === 'atlas' ? 'checked' : ''} />
                        <span>MongoDB Atlas</span>
                        <span className="provider-badge cloud">Cloud</span>
                      </div>
                    </div>

                    {config.mongoType === 'local' && (
                      <div className="inline-config">
                        <div className="config-field flex-1">
                          <label>Local MongoDB URL</label>
                          <input 
                            className="input" 
                            value={config.mongoUrl} 
                            onChange={(e) => updateConfig('mongoUrl', e.target.value)}
                            placeholder="mongodb://localhost:27017"
                          />
                        </div>
                        <button 
                          className="btn btn-secondary"
                          onClick={() => testConnection('mongo')}
                          disabled={testing.mongo}
                        >
                          Test
                        </button>
                      </div>
                    )}

                    {config.mongoType === 'atlas' && (
                      <div className="atlas-config">
                        <div className="config-field">
                          <label>MongoDB Atlas Connection String</label>
                          <div className="input-with-icon">
                            <Key size={14} />
                            <input 
                              type="password"
                              className="input" 
                              value={config.mongoAtlasUrl} 
                              onChange={(e) => updateConfig('mongoAtlasUrl', e.target.value)}
                              placeholder="mongodb+srv://username:password@cluster.mongodb.net/agentforge"
                            />
                          </div>
                        </div>
                        <div className="config-row">
                          <div className="config-field flex-1">
                            <label>Database Name</label>
                            <input 
                              className="input" 
                              value={config.mongoDbName} 
                              onChange={(e) => updateConfig('mongoDbName', e.target.value)}
                              placeholder="agentforge"
                            />
                          </div>
                          <button 
                            className="btn btn-secondary"
                            onClick={() => testConnection('mongo')}
                            disabled={testing.mongo}
                          >
                            <Activity size={14} /> Test Connection
                          </button>
                        </div>
                        <ConnectionStatus status={connectionTests.mongo} testing={testing.mongo} />
                        <a href="https://cloud.mongodb.com" target="_blank" rel="noopener noreferrer" className="provider-link">
                          <ExternalLink size={14} /> Get MongoDB Atlas Connection String
                        </a>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 5: Review & Launch */}
          {currentStep === 5 && (
            <div className="wizard-step-content">
              <div className="step-header">
                <Rocket size={32} className="step-icon" />
                <div>
                  <h2>Review & Launch</h2>
                  <p>Confirm your configuration and start AgentForgeOS</p>
                </div>
              </div>

              <div className="review-grid">
                <div className="review-card">
                  <h4><Server size={16} /> Engine</h4>
                  <div className="review-item">
                    <span>Host:</span>
                    <code>{config.engineHost}:{config.enginePort}</code>
                  </div>
                </div>

                <div className="review-card">
                  <h4><Bot size={16} /> LLM Provider</h4>
                  <div className="review-item">
                    <span>Provider:</span>
                    <code>{config.llmProvider}</code>
                  </div>
                  <div className="review-item">
                    <span>Model:</span>
                    <code>{config.llmProvider === 'ollama' ? config.ollamaModel : config.llmProvider === 'fal' ? config.falLlmModel : config.openaiModel}</code>
                  </div>
                </div>

                <div className="review-card">
                  <h4><ImageIcon size={16} /> Image</h4>
                  <div className="review-item">
                    <span>Provider:</span>
                    <code>{config.imageProvider}</code>
                  </div>
                </div>

                <div className="review-card">
                  <h4><Mic size={16} /> TTS</h4>
                  <div className="review-item">
                    <span>Enabled:</span>
                    <code>{config.ttsEnabled ? config.ttsProvider : 'Disabled'}</code>
                  </div>
                </div>

                <div className="review-card">
                  <h4><Folder size={16} /> Storage</h4>
                  <div className="review-item">
                    <span>Workspace:</span>
                    <code>{config.workspacePath || config.bridgeRoot}</code>
                  </div>
                  <div className="review-item">
                    <span>Log Level:</span>
                    <code>{config.logLevel}</code>
                  </div>
                </div>

                <div className="review-card">
                  <h4><Database size={16} /> Database</h4>
                  <div className="review-item">
                    <span>MongoDB:</span>
                    <code>{config.mongoEnabled ? (config.mongoType === 'atlas' ? 'Atlas (Cloud)' : 'Local') : 'In-Memory'}</code>
                  </div>
                  {config.mongoEnabled && config.mongoType === 'atlas' && (
                    <div className="review-item">
                      <span>Database:</span>
                      <code>{config.mongoDbName}</code>
                    </div>
                  )}
                </div>
              </div>

              <div className="config-file-preview">
                <h4>Config File Preview (config/.env)</h4>
                <div className="code-block dark">
                  <code>
                    SETUP_COMPLETE=1{'\n'}
                    AGENTFORGE_HOST={config.engineHost}{'\n'}
                    AGENTFORGE_PORT={config.enginePort}{'\n'}
                    WORKSPACE_PATH={config.workspacePath || config.bridgeRoot}{'\n'}
                    {'\n'}
                    {config.mongoEnabled ? `# MongoDB\nAGENTFORGE_MONGO_URI=${(config.mongoType === 'atlas' ? config.mongoAtlasUrl : config.mongoUrl) || ''}\nAGENTFORGE_MONGO_DB=${config.mongoDbName}\n\n` : ''}
                    # LLM{'\n'}
                    PROVIDER_LLM={config.llmProvider}{'\n'}
                    {config.llmProvider === 'ollama' ? `OLLAMA_BASE_URL=${config.ollamaUrl}\nOLLAMA_MODEL=${config.ollamaModel}` : config.llmProvider === 'fal' ? `FAL_API_KEY=${config.falApiKey ? '***' : ''}\nFAL_LLM_MODEL=${config.falLlmModel}` : `OPENAI_API_KEY=${config.openaiKey ? '***' : ''}\nOPENAI_MODEL=${config.openaiModel}`}{'\n'}
                    {'\n'}
                    # Image{'\n'}
                    PROVIDER_IMAGE={config.imageProvider}{'\n'}
                    {config.imageProvider === 'comfyui' ? `COMFYUI_BASE_URL=${config.comfyuiUrl}` : ''}{'\n'}
                    {config.imageProvider === 'fal' ? `FAL_API_KEY=${config.falApiKey ? '***' : ''}` : ''}{'\n'}
                    {'\n'}
                    # Storage{'\n'}
                    BRIDGE_ROOT={config.workspacePath || config.bridgeRoot}{'\n'}
                    LOG_LEVEL={config.logLevel}
                  </code>
                </div>
              </div>

              <div className="launch-ready">
                <CheckCircle2 size={24} />
                <span>Ready to launch AgentForgeOS!</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="wizard-footer">
          <button 
            className="btn btn-secondary"
            onClick={prevStep}
            disabled={currentStep === 1}
          >
            <ChevronLeft size={16} /> Back
          </button>
          <div className="wizard-step-indicator">
            Step {currentStep} of {WIZARD_STEPS.length}
          </div>
          {saveError && <div className="wizard-error">{saveError}</div>}
          {currentStep < 5 ? (
            <button className="btn btn-primary" onClick={nextStep}>
              Next <ChevronRight size={16} />
            </button>
          ) : (
            <button className="btn btn-primary launch-btn" onClick={finishSetup}>
              <Rocket size={16} /> Launch Studio
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [showWizard, setShowWizard] = useState(() => {
    // Check if setup is complete (would check localStorage or config in real app)
    return localStorage.getItem('agentforge_setup_complete') !== 'true';
  });
  const [ctxMenu, setCtxMenu] = useState({ visible: false, x: 0, y: 0 });
  const ctxTargetRef = useRef(null);
  const [copyOverlay, setCopyOverlay] = useState({ visible: false, x: 0, y: 0, w: 0, h: 0, target: null });

  const handleWizardComplete = () => {
    localStorage.setItem('agentforge_setup_complete', 'true');
    setShowWizard(false);
  };

  // For demo: allow resetting wizard with ?wizard=true in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('wizard') === 'true') {
      localStorage.removeItem('agentforge_setup_complete');
      setShowWizard(true);
      apiFetch("/setup/reset", { method: "POST" }).catch(() => {});
    }
  }, []);

  useEffect(() => {
    try {
      const settingsState = localGet("agentforge_settings_state", null);
      let resetEnabled = true;
      if (settingsState && typeof settingsState === "object" && settingsState.settings) {
        const s = settingsState.settings;
        if (typeof s.resetOnLaunch === "boolean") resetEnabled = s.resetOnLaunch;
      }
      if (!resetEnabled) return;
      const keys = [
        "agentforge_active_modal",
        "agentforge_active_module_id",
        "agentforge_layout_sizes",
        "agentforge_outputlog_state",
        "agentforge_system_state",
        "agentforge_project_state",
        "agentforge_workspace_layout",
        "agentforge_workspace_modules",
        "agentforge_workspace_path_draft",
        "agentforge_providers_draft",
        "agentforge_deploy_state",
        "agentforge_sandbox_state",
        "agentforge_gamedev_state",
        "agentforge_saas_state",
        "agentforge_agent_console_state",
        "agentforge_pipeline_monitor_state",
      ];
      keys.forEach((k) => {
        try {
          localStorage.removeItem(k);
        } catch (e) {}
      });
    } catch (e) {}
  }, []);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const res = await apiFetch("/setup");
        const data = await res.json();
        if (!cancelled && data?.success) {
          const complete = !!data?.data?.setup_complete;
          if (complete) localStorage.setItem("agentforge_setup_complete", "true");
          setShowWizard(!complete);
        }
      } catch (e) {
      }
    };
    check();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const onContextMenu = (e) => {
      e.preventDefault();
      ctxTargetRef.current = e.target;
      setCtxMenu({ visible: true, x: e.clientX, y: e.clientY });
    };
    const onClick = () => setCtxMenu((v) => ({ ...v, visible: false }));
    document.addEventListener("contextmenu", onContextMenu);
    document.addEventListener("click", onClick);
    return () => {
      document.removeEventListener("contextmenu", onContextMenu);
      document.removeEventListener("click", onClick);
    };
  }, []);

  const copySelection = async () => {
    try {
      const sel = window.getSelection();
      let text = sel && sel.toString() ? sel.toString() : "";
      if (!text) {
        const el = document.activeElement;
        if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA")) {
          const start = el.selectionStart ?? 0;
          const end = el.selectionEnd ?? 0;
          text = String(el.value || "").slice(start, end);
        }
      }
      if (text) await navigator.clipboard.writeText(text);
    } catch (e) {
    } finally {
      setCtxMenu((v) => ({ ...v, visible: false }));
    }
  };

  const pasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (!text) {
        setCtxMenu((v) => ({ ...v, visible: false }));
        return;
      }
      const el = document.activeElement;
      if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA")) {
        const start = el.selectionStart ?? 0;
        const end = el.selectionEnd ?? 0;
        const v = String(el.value || "");
        const next = v.slice(0, start) + text + v.slice(end);
        el.value = next;
        const pos = start + text.length;
        try {
          el.selectionStart = el.selectionEnd = pos;
        } catch {}
        try {
          el.dispatchEvent(new Event("input", { bubbles: true }));
        } catch {}
      } else {
        document.execCommand("insertText", false, text);
      }
    } catch (e) {
    } finally {
      setCtxMenu((v) => ({ ...v, visible: false }));
    }
  };

  const copyBlock = async () => {
    try {
      const target = ctxTargetRef.current;
      let el = target;
      while (el && el !== document.body) {
        if (el.classList && el.classList.contains("code-block")) break;
        el = el.parentElement;
      }
      if (el) {
        const text = el.textContent || "";
        if (text.trim()) await navigator.clipboard.writeText(text);
      }
    } catch (e) {
    } finally {
      setCtxMenu((v) => ({ ...v, visible: false }));
    }
  };

  useEffect(() => {
    const findCodeBlock = (el) => {
      let p = el;
      while (p && p !== document.body) {
        if (p.classList && p.classList.contains("code-block")) return p;
        p = p.parentElement;
      }
      return null;
    };
    const onMouseOver = (e) => {
      const block = findCodeBlock(e.target);
      if (!block) return;
      const rect = block.getBoundingClientRect();
      setCopyOverlay({ visible: true, x: rect.right - 28, y: rect.top + 8, w: rect.width, h: rect.height, target: block });
    };
    const onMouseOut = (e) => {
      const block = findCodeBlock(e.target);
      if (!block) return;
      setCopyOverlay((v) => ({ ...v, visible: false }));
    };
    const onScroll = () => {
      setCopyOverlay((v) => ({ ...v, visible: false }));
    };
    document.addEventListener("mouseover", onMouseOver);
    document.addEventListener("mouseout", onMouseOut);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      document.removeEventListener("mouseover", onMouseOver);
      document.removeEventListener("mouseout", onMouseOut);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  const copyOverlayAction = async () => {
    try {
      const t = copyOverlay.target;
      const text = t && t.textContent ? t.textContent : "";
      if (text.trim()) await navigator.clipboard.writeText(text);
    } catch (e) {
    } finally {
      setCopyOverlay((v) => ({ ...v, visible: false }));
    }
  };

  useEffect(() => {
    const onKeyDown = (e) => {
      const key = (e.key || "").toLowerCase();
      if (e.ctrlKey && e.shiftKey && key === "v") {
        e.preventDefault();
        pasteFromClipboard();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  const selectAllAction = () => {
    try {
      const el = document.activeElement;
      if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA")) {
        if (typeof el.select === "function") el.select();
      } else {
        document.execCommand("selectAll", false, null);
      }
    } catch (e) {
    } finally {
      setCtxMenu((v) => ({ ...v, visible: false }));
    }
  };

  if (showWizard) {
    return <SetupWizard onComplete={handleWizardComplete} />;
  }

  return (
    <div className="App">
      <div style={{ display: "none" }} aria-hidden="true">
        {(() => {
          const handler = () => {
            try {
              const el = document.querySelector(".modal-container .modal-content");
              const isSystemOpen = !!document.querySelector(".modal-title") && document.querySelector(".modal-title")?.textContent === "System Status";
              if (!isSystemOpen) return;
              const evt = new Event("agentforge_system_state_save");
              window.dispatchEvent(evt);
            } catch (e) {}
          };
          window.addEventListener("beforeunload", handler);
          return null;
        })()}
      </div>
      {copyOverlay.visible ? (
        <button
          className="btn btn-ghost"
          style={{
            position: "fixed",
            left: copyOverlay.x,
            top: copyOverlay.y,
            zIndex: 9999,
            padding: "4px 8px",
            fontSize: 12,
            borderRadius: 6,
            background: "rgba(23,23,23,0.92)",
            border: "1px solid rgba(255,255,255,0.08)",
          }}
          onClick={copyOverlayAction}
        >
          Copy
        </button>
      ) : null}
      {ctxMenu.visible ? (
        <div
          style={{
            position: "fixed",
            left: ctxMenu.x,
            top: ctxMenu.y,
            zIndex: 10000,
            background: "rgba(23,23,23,0.96)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 6,
            minWidth: 160,
            boxShadow: "0 6px 24px rgba(0,0,0,0.35)",
            backdropFilter: "blur(4px)",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{ display: "flex", flexDirection: "column" }}>
            <button
              className="btn btn-ghost"
              style={{ justifyContent: "flex-start", padding: "8px 12px" }}
              onClick={copySelection}
            >
              Copy
            </button>
            {(() => {
              const target = ctxTargetRef.current;
              let el = target;
              let isCodeBlock = false;
              while (el && el !== document.body) {
                if (el.classList && el.classList.contains("code-block")) { isCodeBlock = true; break; }
                el = el.parentElement;
              }
              return isCodeBlock ? (
                <button
                  className="btn btn-ghost"
                  style={{ justifyContent: "flex-start", padding: "8px 12px" }}
                  onClick={copyBlock}
                >
                  Copy Block
                </button>
              ) : null;
            })()}
            <button
              className="btn btn-ghost"
              style={{ justifyContent: "flex-start", padding: "8px 12px" }}
              onClick={pasteFromClipboard}
            >
              Paste
            </button>
            <button
              className="btn btn-ghost"
              style={{ justifyContent: "flex-start", padding: "8px 12px" }}
              onClick={selectAllAction}
            >
              Select All
            </button>
          </div>
        </div>
      ) : null}
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Studio />} />
          <Route path="/deployment" element={<Studio initialModuleId="deployment" />} />
          <Route path="/game" element={<Studio initialModuleId="game_dev" />} />
          <Route path="/saas" element={<Studio initialModuleId="saas_builder" />} />
          <Route path="*" element={<Studio />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
