import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

function scoreToGlow(score) {
  if (score == null) return "idle";
  if (score >= 0.85) return "running";
  if (score >= 0.65) return "active";
  return "idle";
}

export default function BuildsPage() {
  const [text, setText] = useState("");
  const [type, setType] = useState("module");

  const modules = useMemo(
    () => [
      { id: "core", name: "Core Engine", status: "ready" },
      { id: "bridge", name: "Bridge", status: "ready" },
      { id: "ui", name: "UI Shell", status: "active" },
      { id: "providers", name: "Providers", status: "queued" },
      { id: "tests", name: "Integration Tests", status: "queued" },
    ],
    []
  );

  const [strip, setStrip] = useState(() => [
    { step: "resolve", score: 0.78, status: "running" },
    { step: "compile", score: 0.72, status: "queued" },
    { step: "verify", score: 0.66, status: "queued" },
    { step: "package", score: 0.61, status: "queued" },
  ]);

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setStrip((prev) =>
      prev.map((s, i) => (i === 0 ? { ...s, status: "running", score: Math.min(0.92, s.score + 0.06) } : s))
    );
    setText("");
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Builds" subtitle="Request builds + track modules" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Architecture" subtitle="Modules (calm, OS-like)" />
      <div style={{ height: 12 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: 12 }}>
        {modules.map((m) => (
          <GlowContainer
            key={m.id}
            state={m.status === "active" ? "active" : m.status === "ready" ? "idle" : "idle"}
            pulse={m.status === "active"}
          >
            <div
              className="af-glass"
              style={{
                gridColumn: "span 4",
                padding: 12,
                borderRadius: 14,
                background: "rgba(255,255,255,0.03)",
                boxShadow: "0 12px 34px rgba(0,0,0,0.45)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {m.name}
                  </div>
                  <div className="af-text-muted" style={{ fontSize: 12 }}>
                    {m.id}
                  </div>
                </div>
                <span
                  className="af-text-muted"
                  style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}
                >
                  {m.status}
                </span>
              </div>
              <div style={{ height: 10 }} />
              <div className="af-divider" />
              <div style={{ height: 10 }} />
              <div className="af-text-muted" style={{ fontSize: 12 }}>
                Status tracked by execution_monitor.
              </div>
            </div>
          </GlowContainer>
        ))}
      </div>
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Build" subtitle="Request + type" />
      <div style={{ height: 12 }} />
      <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1fr 180px auto", gap: 10 }}>
        <input
          className="af-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe what to build…"
          aria-label="Build request"
        />
        <select className="af-select" value={type} onChange={(e) => setType(e.target.value)} aria-label="Build type">
          <option value="module">Module</option>
          <option value="feature">Feature</option>
          <option value="patch">Patch</option>
        </select>
        <button className="af-button" type="submit">
          Queue
        </button>
      </form>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Execution Strip" subtitle="step · score · status" />
      <div style={{ height: 12 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: 10 }}>
        {strip.map((s) => (
          <GlowContainer key={s.step} state={s.status === "running" ? "running" : "idle"}>
            <div
              style={{
                gridColumn: "span 3",
                padding: 10,
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(255,255,255,0.03)",
                transition: "background 280ms var(--af-ease), border-color 280ms var(--af-ease)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                <div style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}>{s.step}</div>
                <div className="af-text-muted" style={{ fontSize: 12 }}>
                  {s.status}
                </div>
              </div>
              <div style={{ height: 10 }} />
              <div
                style={{
                  height: 6,
                  borderRadius: 999,
                  background: "rgba(255,255,255,0.06)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.round((s.score || 0) * 100)}%`,
                    background: "linear-gradient(90deg, rgba(184,50,69,0.25), rgba(184,50,69,0.55))",
                    boxShadow: `0 0 22px rgba(184,50,69,0.22)`,
                    opacity: s.status === "running" ? 0.95 : 0.65,
                    transition: "width 360ms var(--af-ease), opacity 280ms var(--af-ease)",
                  }}
                />
              </div>
              <div style={{ height: 8 }} />
              <div className="af-text-muted" style={{ fontSize: 12 }}>
                Score: {Math.round((s.score || 0) * 100)}% · Glow: {scoreToGlow(s.score)}
              </div>
            </div>
          </GlowContainer>
        ))}
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

