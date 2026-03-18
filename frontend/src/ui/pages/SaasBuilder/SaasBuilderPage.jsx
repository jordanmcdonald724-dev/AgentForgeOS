import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

export default function SaasBuilderPage() {
  const [segment, setSegment] = useState("founders");

  const segments = useMemo(
    () => [
      { id: "founders", label: "Founders", focus: "MVP validation" },
      { id: "teams", label: "Product Teams", focus: "Workflow scale" },
      { id: "enterprise", label: "Enterprise", focus: "Compliance + uptime" },
    ],
    []
  );

  const metrics = useMemo(
    () => [
      { id: "mrr", label: "MRR", value: "$42.6k", trend: "up" },
      { id: "retention", label: "Retention", value: "93%", trend: "steady" },
      { id: "activation", label: "Activation", value: "58%", trend: "watch" },
    ],
    []
  );

  const journey = useMemo(
    () => [
      { id: "j1", label: "Signup → Onboarding" },
      { id: "j2", label: "Activation → Collaboration" },
      { id: "j3", label: "Upgrade → Expansion" },
    ],
    []
  );

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="SaaS Builder" subtitle="Product, growth, and lifecycle planning" />
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
        <SectionHeader title="Target Segments" subtitle="Persona focus + positioning" />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {segments.map((seg) => {
            const isActive = seg.id === segment;
            return (
              <GlowContainer key={seg.id} state={isActive ? "active" : "idle"} pulse={isActive}>
                <button
                  type="button"
                  className="af-button"
                  onClick={() => setSegment(seg.id)}
                  style={{
                    width: "100%",
                    justifyContent: "space-between",
                    background: isActive ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.04)",
                  }}
                >
                  <span style={{ fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    {seg.label}
                  </span>
                  <span className="af-text-muted" style={{ fontSize: 12 }}>
                    {seg.focus}
                  </span>
                </button>
              </GlowContainer>
            );
          })}
        </div>
      </GlassPanel>

      <GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        <SectionHeader title="Growth Metrics" subtitle="Pipeline health + targets" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10 }}>
          {metrics.map((metric) => (
            <div
              key={metric.id}
              className="af-glass"
              style={{
                padding: 10,
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(15,23,42,0.82)",
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase" }}>{metric.label}</div>
              <div style={{ fontSize: 16, marginTop: 6 }}>{metric.value}</div>
              <div className="af-text-muted" style={{ fontSize: 11, marginTop: 4 }}>
                Trend: {metric.trend}
              </div>
            </div>
          ))}
        </div>
        <div className="af-text-muted" style={{ fontSize: 12 }}>
          Active segment: {segments.find((seg) => seg.id === segment)?.label ?? "—"}
        </div>
      </GlassPanel>
    </div>
  );

  const agentConsoleRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Launch Actions" subtitle="GTM and feature planning" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
        <button className="af-button" type="button">
          Generate pricing tiers
        </button>
        <button className="af-button" type="button">
          Draft onboarding flow
        </button>
        <button className="af-button" type="button">
          Prepare release notes
        </button>
      </div>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Customer Journey" subtitle="Lifecycle checkpoints" />
      <div style={{ height: 10 }} />
      <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
        {journey.map((step) => (
          <li key={step.id}>{step.label}</li>
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
