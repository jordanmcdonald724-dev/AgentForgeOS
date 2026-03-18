import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

export default function GameDevPage() {
  const [focus, setFocus] = useState("combat");

  const systems = useMemo(
    () => [
      { id: "combat", label: "Combat Loop", status: "active" },
      { id: "progression", label: "Progression", status: "ready" },
      { id: "economy", label: "Economy", status: "queued" },
      { id: "narrative", label: "Narrative", status: "queued" },
    ],
    []
  );

  const milestones = useMemo(
    () => [
      { id: "m1", label: "Vertical slice complete" },
      { id: "m2", label: "Combat feel tuning" },
      { id: "m3", label: "Retention loop review" },
    ],
    []
  );

  const playtests = useMemo(
    () => [
      { id: "pt-1", title: "Session 14 · Core combat", status: "logged" },
      { id: "pt-2", title: "Session 15 · Tutorial flow", status: "scheduled" },
    ],
    []
  );

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Game Dev" subtitle="Systems, playtests, and tuning" />
    </GlassPanel>
  );

  const mainRegion = (
    <div
      className="af-scroll"
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(0, 1.2fr) minmax(0, 1.4fr)",
        gap: 12,
        height: "100%",
      }}
    >
      <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        <SectionHeader title="Core Systems" subtitle="Design focus + readiness" />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {systems.map((sys) => {
            const isActive = sys.id === focus;
            return (
              <GlowContainer key={sys.id} state={isActive ? "active" : "idle"} pulse={isActive}>
                <button
                  type="button"
                  className="af-button"
                  onClick={() => setFocus(sys.id)}
                  style={{
                    width: "100%",
                    justifyContent: "space-between",
                    background: isActive ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.04)",
                  }}
                >
                  <span style={{ fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    {sys.label}
                  </span>
                  <span className="af-text-muted" style={{ fontSize: 12 }}>
                    {sys.status}
                  </span>
                </button>
              </GlowContainer>
            );
          })}
        </div>
      </GlassPanel>

      <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        <SectionHeader title="Playtest Feed" subtitle="Session notes + follow-ups" />
        <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
          {playtests.map((pt) => (
            <div
              key={pt.id}
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
              <span>{pt.title}</span>
              <span className="af-text-muted" style={{ letterSpacing: "0.1em", textTransform: "uppercase" }}>
                {pt.status}
              </span>
            </div>
          ))}
        </div>
        <div style={{ height: 8 }} />
        <div className="af-text-muted" style={{ fontSize: 12 }}>
          Focus: {systems.find((sys) => sys.id === focus)?.label ?? "—"}
        </div>
      </GlassPanel>
    </div>
  );

  const agentConsoleRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Build Targets" subtitle="Send playable builds" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
        <button className="af-button" type="button">
          Package playtest build
        </button>
        <button className="af-button" type="button">
          Ship telemetry bundle
        </button>
        <button className="af-button" type="button">
          Schedule feedback review
        </button>
      </div>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Milestones" subtitle="Current sprint targets" />
      <div style={{ height: 10 }} />
      <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
        {milestones.map((item) => (
          <li key={item.id}>{item.label}</li>
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
