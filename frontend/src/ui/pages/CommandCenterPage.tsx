import React, { useCallback, useEffect, useState } from "react";
import AppLayout from "../components/layout/AppLayout";
import GlassPanel from "../components/panels/GlassPanel";
import SectionHeader from "../components/panels/SectionHeader";

interface TaskDto {
  task_id: string;
  assigned_agent: string;
  status: string;
  description?: string | null;
}

interface SimulationDto {
  complexity?: string;
  duration_estimate?: string;
  project_size?: string;
  architecture_preview?: string;
  feasible?: boolean;
}

interface CommandPreviewResponse {
  success: boolean;
  data?: {
    tasks: TaskDto[];
    simulation: SimulationDto;
    build_status: string;
    recursive_loop: { stages: string[] };
  };
  error?: unknown;
}

interface ArtifactIndex {
  intent: boolean;
  architecture: boolean;
  tests: {
    results: boolean;
    performance: boolean;
    failures: boolean;
  };
  reports: {
    validation: boolean;
    security: boolean;
  };
  deploy: {
    plan: boolean;
    build_log: boolean;
  };
}

interface ProjectTaskStatus {
  task_id: string;
  agent: string;
  status: string;
  dependencies: string[];
  declared_outputs: string[];
  missing_outputs?: string[];
  phase?: string | null;
  name?: string | null;
}

interface ProjectStatusResponse {
  success: boolean;
  data?: {
    project_id: string;
    tasks: ProjectTaskStatus[];
    artifact_index: ArtifactIndex;
  };
  error?: unknown;
}

interface ShellAppLayoutProps {
  top: React.ReactNode;
  main: React.ReactNode;
  agentConsole: React.ReactNode;
  pipelineMonitor: React.ReactNode;
  floating?: React.ReactNode;
}

interface ShellGlassPanelProps {
  children?: React.ReactNode;
  tight?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}

interface ShellSectionHeaderProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  right?: React.ReactNode;
  className?: string;
}

export const CommandCenterPage: React.FC = () => {
  const [command, setCommand] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<CommandPreviewResponse["data"] | null>(null);
  const [projectStatus, setProjectStatus] = useState<ProjectStatusResponse["data"] | null>(null);

  // CC-1: categories fetched from GET /api/v2/research/categories
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetch("/api/v2/research/categories")
      .then((r) => r.json())
      .then((json: { success: boolean; data?: { categories: string[] } }) => {
        if (json.success && json.data?.categories) {
          setCategories(json.data.categories);
        }
      })
      .catch(() => {
        // best-effort; stay empty if backend unreachable
      });
  }, []);

  const toggleCategory = useCallback((cat: string) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) {
        next.delete(cat);
      } else {
        next.add(cat);
      }
      return next;
    });
  }, []);

  const fetchProjectStatus = useCallback(async (projectId: string) => {
    try {
      const res = await fetch(`/api/v2/projects/${encodeURIComponent(projectId)}/status`);
      const json: ProjectStatusResponse = await res.json();
      if (json.success) {
        setProjectStatus(json.data ?? null);
      }
    } catch {
      // best-effort only
    }
  }, []);

  const runPreview = useCallback(async () => {
    if (!command.trim()) return;
    setLoading(true);
    setError(null);
    try {
      // CC-2: pass selected categories as research_sources[]
      const researchSources = Array.from(selectedCategories).map((id) => ({
        id,
        kind: "research",
        label: id,
      }));
      const res = await fetch("/api/v2/command/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          command,
          brief: { source: "command-center" },
          research_sources: researchSources.length > 0 ? researchSources : undefined,
        }),
      });
      const json: CommandPreviewResponse = await res.json();
      if (!json.success) {
        setError("Preview failed");
      } else {
        setPreview(json.data ?? null);
        void fetchProjectStatus("session_default");
      }
    } catch {
      setError("Backend not available");
    } finally {
      setLoading(false);
    }
  }, [command, selectedCategories, fetchProjectStatus]);

  // Local, relaxed-typing aliases so this TSX file doesn't require
  // specifying optional visual props like glowState/right/floating.
  const ShellAppLayout = AppLayout as React.FC<ShellAppLayoutProps>;
  const ShellGlassPanel = GlassPanel as React.FC<ShellGlassPanelProps>;
  const ShellSectionHeader = SectionHeader as React.FC<ShellSectionHeaderProps>;

  const topRegion = (
    <ShellGlassPanel tight style={{ padding: 12 }}>
      <ShellSectionHeader title="Command Center" subtitle="Simulation-first orchestration" />
    </ShellGlassPanel>
  );

  const agentConsoleRegion = (
    <ShellGlassPanel tight style={{ padding: 12 }}>
      <ShellSectionHeader title="Input" subtitle="Describe the product or game" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <textarea
          className="af-textarea"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Describe the product or game you want AgentForge to plan and simulate…"
          aria-label="Command input"
        />

        {/* CC-1: Research context categories */}
        {categories.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span
              style={{
                fontSize: 11,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "rgba(148,163,184,0.80)",
              }}
            >
              Research context
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {categories.map((cat) => {
                const active = selectedCategories.has(cat);
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => toggleCategory(cat)}
                    style={{
                      fontSize: 11,
                      padding: "3px 10px",
                      borderRadius: 999,
                      border: `1px solid ${active ? "rgba(45,212,191,0.80)" : "rgba(148,163,184,0.40)"}`,
                      background: active ? "rgba(45,212,191,0.12)" : "rgba(15,23,42,0.85)",
                      color: active ? "rgba(45,212,191,0.96)" : "rgba(148,163,184,0.80)",
                      cursor: "pointer",
                      transition: "all 0.15s ease",
                    }}
                  >
                    {cat.replace(/_/g, " ")}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button
            className="af-button"
            type="button"
            onClick={runPreview}
            disabled={loading || !command.trim()}
          >
            {loading ? "Simulating…" : "Run Simulation"}
          </button>
          {selectedCategories.size > 0 && (
            <span style={{ fontSize: 11, color: "rgba(45,212,191,0.80)" }}>
              {selectedCategories.size} context{selectedCategories.size > 1 ? "s" : ""} selected
            </span>
          )}
          {error && <span style={{ fontSize: 12, color: "rgba(248,113,113,0.96)" }}>{error}</span>}
        </div>
      </div>
    </ShellGlassPanel>
  );

  const mainRegion = (
    <div
      className="af-scroll"
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(0, 1.6fr) minmax(0, 1.4fr)",
        gap: 12,
        height: "100%",
      }}
    >
      <ShellGlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
        <ShellSectionHeader title="Task Graph" subtitle="Planned execution across agents" />
        <div style={{ height: 4 }} />
        {(projectStatus?.tasks ?? preview?.tasks)?.length ? (
          <ul className="af-scroll" style={{ maxHeight: 260, margin: 0, padding: 0, listStyle: "none" }}>
            {(projectStatus?.tasks ?? preview?.tasks ?? []).map((t) => (
              <li
                key={t.task_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 10,
                  padding: "6px 8px",
                  borderRadius: 10,
                  border: "1px solid rgba(255,255,255,0.06)",
                  background: "rgba(15,23,42,0.82)",
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 13,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {t.task_id}
                  </div>
                  <div className="af-text-muted" style={{ fontSize: 12 }}>
                    {"assigned_agent" in t ? t.assigned_agent : t.agent}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: 10,
                    textTransform: "uppercase",
                    letterSpacing: "0.1em",
                    color: "rgba(45,212,191,0.92)",
                  }}
                >
                  {t.status}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="af-text-muted" style={{ fontSize: 12 }}>
            Task graph will appear here after simulation.
          </p>
        )}
        <div style={{ height: 10 }} />
        <ShellSectionHeader title="Recursive Loop" subtitle="Plan · Build · Test · Review · Refine" />
        <div style={{ height: 8 }} />
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {(preview?.recursive_loop.stages ?? [
            "plan",
            "build",
            "test",
            "review",
            "refine",
            "rebuild",
          ]).map((stage) => (
            <span
              key={stage}
              style={{
                fontSize: 11,
                padding: "2px 10px",
                borderRadius: 999,
                border: "1px solid rgba(148,163,184,0.70)",
                background: "rgba(15,23,42,0.85)",
              }}
            >
              {stage}
            </span>
          ))}
        </div>
      </ShellGlassPanel>

      <ShellGlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
        <ShellSectionHeader title="Agent Activity" subtitle="Mirrors task graph snapshot" />
        <div style={{ height: 4 }} />
        {(projectStatus?.tasks ?? preview?.tasks)?.length ? (
          <ul className="af-scroll" style={{ maxHeight: 160, margin: 0, padding: 0, listStyle: "none" }}>
            {(projectStatus?.tasks ?? preview?.tasks ?? []).map((t) => (
              <li key={t.task_id} style={{ fontSize: 12, color: "rgba(226,232,240,0.96)" }}>
                <span className="af-text-muted">[
                  {"assigned_agent" in t ? t.assigned_agent : t.agent}
                ]</span>{" "}
                {t.task_id} ({t.status})
              </li>
            ))}
          </ul>
        ) : (
          <p className="af-text-muted" style={{ fontSize: 12 }}>
            Agent activity will appear once a command is simulated.
          </p>
        )}
      </ShellGlassPanel>
    </div>
  );

  const pipelineRegion = (
    <ShellGlassPanel tight style={{ padding: 12 }}>
      <ShellSectionHeader title="Build Queue" subtitle="Simulation + live project" />
      <div style={{ height: 12 }} />
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          fontSize: 12,
        }}
      >
        <span className="af-text-muted">Build status</span>
        <span
          style={{
            padding: "2px 10px",
            borderRadius: 999,
            border: "1px solid rgba(148,163,184,0.70)",
            background: "rgba(15,23,42,0.90)",
            color: "rgba(45,212,191,0.96)",
          }}
        >
          {preview?.build_status ?? "pending"}
        </span>
      </div>

      {/* CC-3: Simulation report fields */}
      {preview?.simulation && Object.keys(preview.simulation).length > 0 && (
        <>
          <div style={{ height: 14 }} />
          <ShellSectionHeader title="Simulation Report" subtitle="complexity · duration · feasibility" />
          <div style={{ height: 10 }} />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: 8,
              fontSize: 11,
            }}
          >
            {preview.simulation.complexity != null && (
              <span className="af-text-muted">
                Complexity:{" "}
                <span style={{ color: "rgba(230,237,243,0.92)" }}>
                  {preview.simulation.complexity}
                </span>
              </span>
            )}
            {preview.simulation.duration_estimate != null && (
              <span className="af-text-muted">
                Duration:{" "}
                <span style={{ color: "rgba(230,237,243,0.92)" }}>
                  {preview.simulation.duration_estimate}
                </span>
              </span>
            )}
            {preview.simulation.project_size != null && (
              <span className="af-text-muted">
                Project size:{" "}
                <span style={{ color: "rgba(230,237,243,0.92)" }}>
                  {preview.simulation.project_size}
                </span>
              </span>
            )}
            {preview.simulation.feasible != null && (
              <span className="af-text-muted">
                Feasible:{" "}
                <span
                  style={{
                    color: preview.simulation.feasible
                      ? "rgba(45,212,191,0.92)"
                      : "rgba(248,113,113,0.92)",
                  }}
                >
                  {preview.simulation.feasible ? "yes" : "no"}
                </span>
              </span>
            )}
            {preview.simulation.architecture_preview != null && (
              <span
                className="af-text-muted"
                style={{ gridColumn: "1 / -1", whiteSpace: "pre-wrap", wordBreak: "break-word" }}
              >
                Architecture:{" "}
                <span style={{ color: "rgba(230,237,243,0.92)" }}>
                  {preview.simulation.architecture_preview}
                </span>
              </span>
            )}
          </div>
        </>
      )}

      {projectStatus?.artifact_index && (
        <>
          <div style={{ height: 14 }} />
          <ShellSectionHeader title="Artifact snapshot" subtitle="session_default" />
          <div style={{ height: 10 }} />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: 8,
              fontSize: 11,
            }}
          >
            <span className="af-text-muted">
              Intent: {projectStatus.artifact_index.intent ? "present" : "missing"}
            </span>
            <span className="af-text-muted">
              Architecture: {projectStatus.artifact_index.architecture ? "present" : "missing"}
            </span>
            <span className="af-text-muted">
              Tests: {projectStatus.artifact_index.tests.results ? "results" : "no results"}
            </span>
            <span className="af-text-muted">
              Reports: {projectStatus.artifact_index.reports.validation ? "validation" : "none"}
            </span>
            <span className="af-text-muted">
              Deploy plan: {projectStatus.artifact_index.deploy.plan ? "present" : "missing"}
            </span>
            <span className="af-text-muted">
              Build log: {projectStatus.artifact_index.deploy.build_log ? "present" : "missing"}
            </span>
          </div>
        </>
      )}
    </ShellGlassPanel>
  );

  return (
    <ShellAppLayout
      top={topRegion}
      main={mainRegion}
      agentConsole={agentConsoleRegion}
      pipelineMonitor={pipelineRegion}
    />
  );
};

export default CommandCenterPage;
