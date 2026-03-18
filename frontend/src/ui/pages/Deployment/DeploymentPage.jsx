import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

export default function DeploymentPage() {
  const [activeEnv, setActiveEnv] = useState("staging");

  const environments = useMemo(
    () => [
      { id: "dev", label: "Development", region: "Local", status: "ready" },
      { id: "staging", label: "Staging", region: "us-east-2", status: "active" },
      { id: "prod", label: "Production", region: "global", status: "queued" },
    ],
    []
  );

  const checklist = useMemo(
    () => [
      { id: "artifacts", label: "Artifacts packaged", done: true },
      { id: "smoke", label: "Smoke tests green", done: true },
      { id: "rollout", label: "Rollout plan confirmed", done: false },
      { id: "monitor", label: "Monitoring hooks wired", done: false },
    ],
    []
  );

  const timeline = useMemo(
    () => [
      { id: "step-1", label: "Build verified · 09:24" },
      { id: "step-2", label: "Staging deploy · 09:32" },
      { id: "step-3", label: "QA sign-off pending" },
    ],
    []
  );

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Deployment" subtitle="Release orchestration + rollout readiness" />
    </GlassPanel>
  );

  const mainRegion = (
    <div
      className="af-scroll"
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(0, 1.3fr) minmax(0, 1.2fr)",
        gap: 12,
        height: "100%",
      }}
    >
      <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        <SectionHeader title="Environments" subtitle="Target surfaces for rollout" />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {environments.map((env) => {
            const isActive = env.id === activeEnv;
            return (
              <GlowContainer key={env.id} state={isActive ? "active" : "idle"} pulse={isActive}>
                <button
                  type="button"
                  className="af-button"
                  onClick={() => setActiveEnv(env.id)}
                  style={{
                    width: "100%",
                    justifyContent: "space-between",
                    background: isActive ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.04)",
                  }}
                >
                  <span style={{ fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    {env.label}
                  </span>
                  <span className="af-text-muted" style={{ fontSize: 12 }}>
                    {env.region} · {env.status}
                  </span>
                </button>
              </GlowContainer>
            );
          })}
        </div>
      </GlassPanel>

      <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        <SectionHeader title="Release Checklist" subtitle="Quality gates before promotion" />
        <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
          {checklist.map((item) => (
            <div
              key={item.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 10,
                padding: "8px 10px",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.06)",
                background: "rgba(15,23,42,0.82)",
              }}
            >
              <span>{item.label}</span>
              <span className="af-text-muted" style={{ letterSpacing: "0.1em", textTransform: "uppercase" }}>
                {item.done ? "done" : "pending"}
              </span>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );

  const agentConsoleRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Release Actions" subtitle="Promote builds + notify teams" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
        <button className="af-button" type="button">
          Create release bundle
        </button>
        <button className="af-button" type="button">
          Promote to staging
        </button>
        <button className="af-button" type="button">
          Trigger production rollout
        </button>
      </div>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Rollout Timeline" subtitle="Recent release events" />
      <div style={{ height: 10 }} />
      <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
        {timeline.map((entry) => (
          <li key={entry.id}>{entry.label}</li>
        ))}
      </ul>
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
