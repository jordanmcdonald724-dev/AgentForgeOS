import React, { useCallback, useEffect, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";

export default function GameDevPage() {
  const [projects, setProjects] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("rpg");
  const [platform, setPlatform] = useState("cross-platform");
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/game_dev/status");
      const json = await res.json();
      if (json.success) setStatus(json.data);
    } catch { /* offline */ }
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/game_dev/projects");
      const json = await res.json();
      if (json.success) setProjects(json.data ?? []);
    } catch { /* offline */ }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchProjects();
  }, [fetchStatus, fetchProjects]);

  const createDesign = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/modules/game_dev/design", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, genre, platform, description }),
      });
      const json = await res.json();
      if (json.success) {
        setTitle("");
        setDescription("");
        await fetchProjects();
        await fetchStatus();
      } else {
        setError("Design creation failed");
      }
    } catch {
      setError("Backend not available");
    } finally {
      setLoading(false);
    }
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader
        title="Game Dev"
        subtitle="Design, scene scaffolding, and asset pipeline"
        right={
          <span style={{ fontSize: 12, color: "rgba(45,212,191,0.92)" }}>
            {status ? `${status.total_projects} projects` : "—"}
          </span>
        }
      />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Game Projects" subtitle="All design documents" />
      <div style={{ height: 12 }} />
      {projects.length === 0 ? (
        <p className="af-text-muted" style={{ fontSize: 12 }}>
          No projects yet. Create a game design document from the panel on the left.
        </p>
      ) : (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          {projects.map((p) => (
            <li
              key={p.id}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.06)",
                background: "rgba(15,23,42,0.82)",
                fontSize: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontWeight: 500 }}>{p.title}</span>
                <span className="af-text-muted">{p.status}</span>
              </div>
              <div className="af-text-muted">{p.genre} · {p.platform}</div>
              {p.description && (
                <div style={{ marginTop: 4, color: "rgba(226,232,240,0.75)" }}>{p.description}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
      <SectionHeader title="Create Design Doc" subtitle="New game project scaffold" />
      <form onSubmit={createDesign} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <input
          className="af-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Game title…"
          aria-label="Game title"
        />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <select
            className="af-input"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            style={{ background: "rgba(15,23,42,0.90)", color: "inherit", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8, padding: "6px 10px", fontSize: 12 }}
          >
            <option value="rpg">RPG</option>
            <option value="fps">FPS</option>
            <option value="rts">RTS</option>
            <option value="puzzle">Puzzle</option>
            <option value="platformer">Platformer</option>
            <option value="simulation">Simulation</option>
            <option value="unknown">Other</option>
          </select>
          <select
            className="af-input"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            style={{ background: "rgba(15,23,42,0.90)", color: "inherit", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8, padding: "6px 10px", fontSize: 12 }}
          >
            <option value="cross-platform">Cross-platform</option>
            <option value="pc">PC</option>
            <option value="mobile">Mobile</option>
            <option value="console">Console</option>
            <option value="web">Web</option>
          </select>
        </div>
        <textarea
          className="af-textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="High-level description…"
          aria-label="Game description"
        />
        <button className="af-button" type="submit" disabled={loading || !title.trim()}>
          {loading ? "Creating…" : "Create Design Doc"}
        </button>
      </form>
      {error && <p style={{ fontSize: 12, color: "rgba(248,113,113,0.96)" }}>{error}</p>}
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Module Status" subtitle="Game Dev engine readiness" />
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
        <div style={{ marginTop: 8 }}>
          <span className="af-text-muted" style={{ fontSize: 12 }}>
            Scene scaffolding, Unity/Unreal integration, and asset pipeline are coming in future iterations.
          </span>
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