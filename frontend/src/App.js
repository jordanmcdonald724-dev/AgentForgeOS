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

// ===============================================
// MODAL PAGES FOR TOP NAVIGATION
// ===============================================

// Modal Container
const Modal = ({ isOpen, onClose, title, children }) => {
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
        className="modal-container"
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

  const createProject = () => {
    if (!newProjectName.trim()) return;
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
  };

  const toggleStar = (id) => {
    setProjects(projects.map(p => p.id === id ? { ...p, starred: !p.starred } : p));
  };

  const openProject = (project) => {
    addLog("info", `Opened project: ${project.name}`);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Project Manager">
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
  const [theme, setTheme] = useState("dark");
  const [activeModules, setActiveModules] = useState(["studio", "builds", "research", "sandbox"]);

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
    </Modal>
  );
};

// 3. PROVIDERS PAGE
const ProvidersPage = ({ isOpen, onClose, addLog }) => {
  const [providers, setProviders] = useState({
    llm: { provider: "ollama", apiKey: "", model: "llama3", status: "connected" },
    image: { provider: "comfyui", apiKey: "", endpoint: "http://localhost:8188", status: "connected" },
    tts: { provider: "piper", apiKey: "", voice: "en_US-lessac", status: "disconnected" },
    embedding: { provider: "ollama", apiKey: "", model: "nomic-embed-text", status: "connected" },
  });

  const providerOptions = {
    llm: ["ollama", "openai", "anthropic", "local"],
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
    // Simulate connection test
    setTimeout(() => {
      const newStatus = Math.random() > 0.3 ? 'connected' : 'error';
      updateProvider(type, 'status', newStatus);
      addLog(
        newStatus === 'connected' ? "success" : "error",
        `${type.toUpperCase()} ${newStatus === 'connected' ? 'connected' : 'failed'}`
      );
    }, 1000);
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

  const toggleService = (name) => {
    setServices(services.map(s => 
      s.name === name ? { ...s, status: s.status === 'running' ? 'stopped' : 'running' } : s
    ));
    addLog("info", `${name} ${services.find(s => s.name === name)?.status === 'running' ? 'stopped' : 'started'}`);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="System Status">
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
  });

  const [activeSection, setActiveSection] = useState("appearance");

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    addLog("info", `Setting updated: ${key} = ${value}`);
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

  const [achievements, setAchievements] = useState([
    { id: 1, name: "First Build", desc: "Completed your first build", unlocked: true },
    { id: 2, name: "Agent Master", desc: "Used all 12 agents", unlocked: true },
    { id: 3, name: "Knowledge Seeker", desc: "Added 50 research notes", unlocked: false },
    { id: 4, name: "Deploy King", desc: "10 successful deployments", unlocked: true },
  ]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Profile">
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
  const [activeModal, setActiveModal] = useState(null);

  const addLog = (level, message) => {
    setLogs((prev) => [...prev.slice(-50), { time: formatTime(), level, message }]);
  };

  const openModal = (modal) => setActiveModal(modal);
  const closeModal = () => setActiveModal(null);

  return (
    <div className="studio-layout" data-testid="studio-layout">
      <NavBar onOpenModal={openModal} />
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
    // LLM
    llmProvider: "ollama",
    ollamaUrl: "http://localhost:11434",
    ollamaModel: "llama3",
    openaiKey: "",
    openaiModel: "gpt-4",
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
    bridgeRoot: "C:\\AgentForgeOS\\workspace",
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

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const testConnection = async (type) => {
    setTesting(prev => ({ ...prev, [type]: true }));
    // Simulate connection test
    await new Promise(resolve => setTimeout(resolve, 1500));
    const success = Math.random() > 0.2; // 80% success rate for demo
    setConnectionTests(prev => ({ ...prev, [type]: success }));
    setTesting(prev => ({ ...prev, [type]: false }));
  };

  const nextStep = () => {
    if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const finishSetup = () => {
    // In real app, this would save to config/.env
    onComplete();
  };

  // Connection status indicator
  const ConnectionStatus = ({ status, testing: isTesting }) => {
    if (isTesting) {
      return <span className="connection-status testing"><div className="spinner-sm" /> Testing...</span>;
    }
    if (status === null) {
      return <span className="connection-status pending">Not tested</span>;
    }
    return status ? (
      <span className="connection-status success"><CheckCircle2 size={14} /> Connected</span>
    ) : (
      <span className="connection-status error"><XCircle size={14} /> Failed</span>
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
                    value={config.bridgeRoot} 
                    onChange={(e) => updateConfig('bridgeRoot', e.target.value)}
                    placeholder="C:\AgentForgeOS\workspace"
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
                    <code>{config.llmProvider === 'ollama' ? config.ollamaModel : config.openaiModel}</code>
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
                    <code>{config.bridgeRoot}</code>
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
                    ENGINE_HOST={config.engineHost}{'\n'}
                    ENGINE_PORT={config.enginePort}{'\n'}
                    {'\n'}
                    # LLM{'\n'}
                    LLM_PROVIDER={config.llmProvider}{'\n'}
                    {config.llmProvider === 'ollama' ? `OLLAMA_URL=${config.ollamaUrl}\nOLLAMA_MODEL=${config.ollamaModel}` : `OPENAI_API_KEY=${config.openaiKey ? '***' : ''}\nOPENAI_MODEL=${config.openaiModel}`}{'\n'}
                    {'\n'}
                    # Image{'\n'}
                    IMAGE_PROVIDER={config.imageProvider}{'\n'}
                    {config.imageProvider === 'comfyui' ? `COMFYUI_URL=${config.comfyuiUrl}` : ''}{'\n'}
                    {'\n'}
                    # Storage{'\n'}
                    BRIDGE_ROOT={config.bridgeRoot}{'\n'}
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
    }
  }, []);

  if (showWizard) {
    return <SetupWizard onComplete={handleWizardComplete} />;
  }

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
