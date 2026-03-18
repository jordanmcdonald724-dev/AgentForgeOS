import React, { useCallback, useEffect, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";

export default function DeploymentPage() {
  const [deployments, setDeployments] = useState([]);
  const [status, setStatus] = useState(null);
  const [launching, setLaunching] = useState(false);
  const [deployTarget, setDeployTarget] = useState("local");
  const [lastLaunch, setLastLaunch] = useState(null);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/deployment/status");
      const json = await res.json();
      if (json.success) setStatus(json.data);
    } catch { /* offline */ }
  }, []);

  const fetchDeployments = useCallback(async () => {
    try {
      const res = await fetch("/api/modules/deployment/list");
      const json = await res.json();
      if (json.success) setDeployments(json.data ?? []);
    } catch { /* offline */ }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchDeployments();
  }, [fetchStatus, fetchDeployments]);

  const triggerDeploy = async (e) => {
    e.preventDefault();
    setLaunching(true);
    setError(null);
    try {
      const res = await fetch("/api/modules/deployment/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: deployTarget }),
      });
      const json = await res.json();
      if (json.success) {
        await fetchDeployments();
        await fetchStatus();
      } else {
        setError("Deploy failed");
      }
    } catch {
      setError("Backend not available");
    } finally {
      setLaunching(false);
    }
  };

  const launchEngine = async (engine) => {
    setLaunching(true);
    setError(null);
    setLastLaunch(null);
    try {
      const res = await fetch("/api/modules/deployment/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ engine }),
      });
      const json = await res.json();
      setLastLaunch(json.data ?? json);
      if (!json.success) setError(json.error ?? "Launch failed");
    } catch {
      setError("Backend not available");
    } finally {
      setLaunching(false);
    }
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader
        title="Deployment"
        subtitle="Deploy projects and launch engine targets"
        right={
          <span style={{ fontSize: 12, color: "rgba(45,212,191,0.92)" }}>
            {status ? `${status.total_deployments} deployments` : "—"}
          </span>
        }
      />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Deployment History" subtitle="All recorded deployments" />
      <div style={{ height: 12 }} />
      {deployments.length === 0 ? (
        <p className="af-text-muted" style={{ fontSize: 12 }}>
          No deployments yet. Trigger one from the panel on the left.
        </p>
      ) : (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          {deployments.map((d) => (
            <li
              key={d.id}
              style={{
                padding: "8px 12px",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.06)",
                background: "rgba(15,23,42,0.82)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                fontSize: 12,
              }}
            >
              <div>
                <div style={{ marginBottom: 2 }}>
                  {d.project} → <span style={{ color: "rgba(148,163,184,0.85)" }}>{d.target}</span>
                </div>
                <div className="af-text-muted">{d.initiated_at}</div>
              </div>
              <span
                style={{
                  fontSize: 10,
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  color: d.status === "pending" ? "rgba(251,191,36,0.92)" : "rgba(45,212,191,0.92)",
                }}
              >
                {d.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
      <SectionHeader title="Trigger Deploy" subtitle="Deploy to a target environment" />
      <form onSubmit={triggerDeploy} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <select
          className="af-input"
          value={deployTarget}
          onChange={(e) => setDeployTarget(e.target.value)}
          aria-label="Deployment target"
          style={{ background: "rgba(15,23,42,0.90)", color: "inherit", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8, padding: "6px 10px", fontSize: 12 }}
        >
          <option value="local">Local</option>
          <option value="staging">Staging</option>
          <option value="production">Production</option>
        </select>
        <button className="af-button" type="submit" disabled={launching}>
          {launching ? "Deploying…" : "Deploy"}
        </button>
      </form>

      <div style={{ height: 4 }} />
      <SectionHeader title="Engine Launch" subtitle="Send build to target engine" />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
        <button className="af-button" type="button" onClick={() => launchEngine("web")} disabled={launching}>
          Launch Web Build
        </button>
        <button
          className="af-button"
          type="button"
          title="Engine bridge coming soon"
          disabled
          style={{ opacity: 0.45, cursor: "not-allowed" }}
        >
          Launch in Unity (coming soon)
        </button>
        <button
          className="af-button"
          type="button"
          title="Engine bridge coming soon"
          disabled
          style={{ opacity: 0.45, cursor: "not-allowed" }}
        >
          Launch in Unreal (coming soon)
        </button>
      </div>

      {error && <p style={{ fontSize: 12, color: "rgba(248,113,113,0.96)" }}>{error}</p>}
      {lastLaunch && (
        <div style={{ fontSize: 12, marginTop: 4 }}>
          <span className="af-text-muted">Engine: </span>{lastLaunch.engine ?? "—"}{" "}
          <span className="af-text-muted">Status: </span>
          <span style={{ color: "rgba(45,212,191,0.92)" }}>{lastLaunch.status ?? "queued"}</span>
        </div>
      )}
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Module Status" subtitle="Deployment engine readiness" />
      <div style={{ height: 12 }} />
      <div style={{ fontSize: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="af-text-muted">Module</span>
          <span style={{ color: "rgba(45,212,191,0.92)" }}>{status?.status ?? "—"}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="af-text-muted">Total deployments</span>
          <span>{status?.total_deployments ?? 0}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="af-text-muted">Description</span>
          <span style={{ color: "rgba(148,163,184,0.85)" }}>{status?.description ?? "—"}</span>
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
