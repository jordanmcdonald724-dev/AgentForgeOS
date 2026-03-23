import React, { useCallback, useEffect, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";

export default function SaasBuilderPage() {
  const [projects, setProjects] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [stack, setStack] = useState("react-fastapi");
  const [selectedProject, setSelectedProject] = useState(null);
  const [featureName, setFeatureName] = useState("");
  const [featureDesc, setFeatureDesc] = useState("");
  const [addingFeature, setAddingFeature] = useState(false);
  const [error, setError] = useState(null);

  const STACKS = {
    "react-fastapi": { frontend: "react", backend: "fastapi", db: "postgres" },
    "react-express": { frontend: "react", backend: "express", db: "mongodb" },
    "vue-django": { frontend: "vue", backend: "django", db: "postgres" },
    "next-rails": { frontend: "next", backend: "rails", db: "postgres" },
  };

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/saas_builder/status");
      const json = await res.json();
      if (json.success) setStatus(json.data);
    } catch { /* offline */ }
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/saas_builder/projects");
      const json = await res.json();
      if (json.success) setProjects(json.data ?? []);
    } catch { /* offline */ }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchProjects();
  }, [fetchStatus, fetchProjects]);

  const scaffoldProject = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/modules/saas_builder/scaffold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: projectName, stack: STACKS[stack] }),
      });
      const json = await res.json();
      if (json.success) {
        setProjectName("");
        await fetchProjects();
        await fetchStatus();
      } else {
        setError("Scaffold failed");
      }
    } catch {
      setError("Backend not available");
    } finally {
      setLoading(false);
    }
  };

  const addFeature = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    setAddingFeature(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/modules/saas_builder/projects/${selectedProject.id}/feature`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: featureName, description: featureDesc }),
        }
      );
      const json = await res.json();
      if (json.success) {
        setFeatureName("");
        setFeatureDesc("");
        await fetchProjects();
        // refresh selected project data
        setProjects((prev) =>
          prev.map((p) =>
            p.id === selectedProject.id
              ? { ...p, features: [...(p.features ?? []), json.data] }
              : p
          )
        );
        setSelectedProject((prev) =>
          prev ? { ...prev, features: [...(prev.features ?? []), json.data] } : prev
        );
      } else {
        setError("Add feature failed");
      }
    } catch {
      setError("Backend not available");
    } finally {
      setAddingFeature(false);
    }
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader
        title="SaaS Builder"
        subtitle="Scaffold, feature planning, and full-stack project management"
        right={
          <span style={{ fontSize: 12, color: "rgba(45,212,191,0.92)" }}>
            {status ? `${status.total_projects} projects` : "—"}
          </span>
        }
      />
    </GlassPanel>
  );

  const mainRegion = (
    <div
      className="af-scroll"
      style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)", gap: 12, height: "100%" }}
    >
      <GlassPanel className="af-scroll" style={{ padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        <SectionHeader title="Projects" subtitle="Click a project to manage features" />
        <div style={{ height: 4 }} />
        {projects.length === 0 ? (
          <p className="af-text-muted" style={{ fontSize: 12 }}>
            No projects yet. Scaffold one from the right panel.
          </p>
        ) : (
          projects.map((p) => (
            <div
              key={p.id}
              onClick={() => setSelectedProject(p)}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: `1px solid ${selectedProject?.id === p.id ? "rgba(45,212,191,0.40)" : "rgba(255,255,255,0.06)"}`,
                background: selectedProject?.id === p.id ? "rgba(45,212,191,0.06)" : "rgba(15,23,42,0.82)",
                cursor: "pointer",
                fontSize: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                <span style={{ fontWeight: 500 }}>{p.name}</span>
                <span className="af-text-muted">{p.features?.length ?? 0} features</span>
              </div>
              <div className="af-text-muted">
                {p.stack?.frontend} / {p.stack?.backend} / {p.stack?.db}
              </div>
            </div>
          ))
        )}
      </GlassPanel>

      <GlassPanel className="af-scroll" style={{ padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        {selectedProject ? (
          <>
            <SectionHeader title={selectedProject.name} subtitle="Features" />
            <div style={{ height: 4 }} />
            {(selectedProject.features ?? []).length === 0 ? (
              <p className="af-text-muted" style={{ fontSize: 12 }}>No features yet.</p>
            ) : (
              selectedProject.features.map((f) => (
                <div
                  key={f.id}
                  style={{
                    padding: "8px 10px",
                    borderRadius: 10,
                    border: "1px solid rgba(255,255,255,0.06)",
                    background: "rgba(15,23,42,0.82)",
                    fontSize: 12,
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: 2 }}>{f.name}</div>
                  {f.description && <div className="af-text-muted">{f.description}</div>}
                </div>
              ))
            )}
            <div style={{ height: 8 }} />
            <form onSubmit={addFeature} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <input
                className="af-input"
                value={featureName}
                onChange={(e) => setFeatureName(e.target.value)}
                placeholder="Feature name…"
              />
              <input
                className="af-input"
                value={featureDesc}
                onChange={(e) => setFeatureDesc(e.target.value)}
                placeholder="Description (optional)…"
              />
              <button className="af-button" type="submit" disabled={addingFeature || !featureName.trim()}>
                {addingFeature ? "Adding…" : "Add Feature"}
              </button>
            </form>
          </>
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
            <p className="af-text-muted" style={{ fontSize: 12 }}>
              Select a project to manage its features.
            </p>
          </div>
        )}
      </GlassPanel>
    </div>
  );

  const agentConsoleRegion = (
    <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
      <SectionHeader title="Scaffold Project" subtitle="Create a new SaaS project" />
      <form onSubmit={scaffoldProject} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <input
          className="af-input"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          placeholder="Project name…"
          aria-label="Project name"
        />
        <select
          value={stack}
          onChange={(e) => setStack(e.target.value)}
          style={{
            background: "rgba(15,23,42,0.90)",
            color: "inherit",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: 8,
            padding: "6px 10px",
            fontSize: 12,
          }}
        >
          <option value="react-fastapi">React + FastAPI + PostgreSQL</option>
          <option value="react-express">React + Express + MongoDB</option>
          <option value="vue-django">Vue + Django + PostgreSQL</option>
          <option value="next-rails">Next.js + Rails + PostgreSQL</option>
        </select>
        <button className="af-button" type="submit" disabled={loading || !projectName.trim()}>
          {loading ? "Scaffolding…" : "Scaffold Project"}
        </button>
      </form>
      {error && <p style={{ fontSize: 12, color: "rgba(248,113,113,0.96)" }}>{error}</p>}
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Module Status" subtitle="SaaS Builder readiness" />
      <div style={{ height: 12 }} />
      <div style={{ fontSize: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="af-text-muted">Module</span>
          <span style={{ color: "rgba(45,212,191,0.92)" }}>{status?.status ?? "—"}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="af-text-muted">Total projects</span>
          <span>{status?.total_projects ?? 0}</span>
        </div>
      </div>
    </GlassPanel>
  );

  return (
    <AppLayout
      top={topRegion}
      main={mainRegion}
      agentConsole={agentConsoleRegion}
      pipelineMonitor={pipelineRegion}
    />
  );
}
