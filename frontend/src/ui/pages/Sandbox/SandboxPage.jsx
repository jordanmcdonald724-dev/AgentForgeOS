import React, { useEffect, useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

function ts() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

export default function SandboxPage() {
  const [nodes, setNodes] = useState(() => [
    { id: "a", label: "Planner", x: 0.18, y: 0.30, state: "idle", bornAt: Date.now() },
    { id: "b", label: "Architect", x: 0.54, y: 0.22, state: "active", bornAt: Date.now() },
    { id: "c", label: "Engineer", x: 0.70, y: 0.58, state: "idle", bornAt: Date.now() },
    { id: "d", label: "Tester", x: 0.32, y: 0.64, state: "idle", bornAt: Date.now() },
  ]);

  const edges = useMemo(
    () => [
      { from: "a", to: "b" },
      { from: "b", to: "c" },
      { from: "b", to: "d" },
    ],
    []
  );

  const [feed, setFeed] = useState(() => [
    { ts: ts(), msg: "Sandbox online" },
    { ts: ts(), msg: "Waiting for live_execution_loop…" },
  ]);

  useEffect(() => {
    // gentle activity simulation (replaced by websocket binding later)
    const timer = setInterval(() => {
      setNodes((prev) => {
        const idx = Math.floor(Math.random() * prev.length);
        return prev.map((n, i) => (i === idx ? { ...n, state: n.state === "active" ? "idle" : "active" } : n));
      });
    }, 1600);
    return () => clearInterval(timer);
  }, []);

  const addNode = () => {
    const id = Math.random().toString(16).slice(2, 8);
    const label = `Agent ${id.toUpperCase()}`;
    setNodes((prev) => [
      ...prev,
      { id, label, x: rand(0.12, 0.88), y: rand(0.18, 0.82), state: "idle", bornAt: Date.now() },
    ]);
    setFeed((prev) => [...prev, { ts: ts(), msg: `New node discovered: ${label}` }].slice(-220));
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Sandbox" subtitle="Live graph and execution feed" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel style={{ padding: 12, position: "relative" }}>
      <SectionHeader
        title="Live Graph"
        subtitle="Nodes = agents · Edges = flow"
        right={
          <button className="af-button" type="button" onClick={addNode}>
            Add Node
          </button>
        }
      />
      <div style={{ height: 12 }} />

      <div
        style={{
          position: "relative",
          height: "calc(100vh - 340px)",
          minHeight: 420,
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "radial-gradient(800px 520px at 30% 25%, rgba(184,50,69,0.08), transparent 55%), rgba(255,255,255,0.02)",
          overflow: "hidden",
        }}
      >
        <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
          {edges.map((e) => {
            const a = nodes.find((n) => n.id === e.from);
            const b = nodes.find((n) => n.id === e.to);
            if (!a || !b) return null;
            return (
              <line
                key={`${e.from}-${e.to}`}
                x1={`${a.x * 100}%`}
                y1={`${a.y * 100}%`}
                x2={`${b.x * 100}%`}
                y2={`${b.y * 100}%`}
                stroke="rgba(255,255,255,0.10)"
                strokeWidth="1"
              />
            );
          })}
        </svg>

        {nodes.map((n) => {
          const isNew = Date.now() - n.bornAt < 1200;
          return (
            <div
              key={n.id}
              style={{
                position: "absolute",
                left: `${n.x * 100}%`,
                top: `${n.y * 100}%`,
                transform: "translate(-50%, -50%)",
                transition: "left 360ms var(--af-ease), top 360ms var(--af-ease), opacity 360ms var(--af-ease)",
                opacity: isNew ? 0.0 : 1.0,
                animation: isNew ? "afNodeFadeIn 420ms var(--af-ease) forwards" : "none",
              }}
            >
              <GlowContainer state={n.state === "active" ? "active" : "idle"} pulse={n.state === "active"}>
                <div
                  style={{
                    padding: "10px 12px",
                    borderRadius: 14,
                    border: "1px solid rgba(255,255,255,0.08)",
                    background: "rgba(255,255,255,0.03)",
                    minWidth: 130,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                    <div style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}>
                      {n.label}
                    </div>
                    <span
                      aria-hidden="true"
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: 999,
                        background: n.state === "active" ? "rgba(184,50,69,0.85)" : "rgba(255,255,255,0.12)",
                      }}
                    />
                  </div>
                  <div className="af-text-muted" style={{ marginTop: 6, fontSize: 12 }}>
                    {n.state === "active" ? "Active" : "Idle"}
                  </div>
                </div>
              </GlowContainer>
            </div>
          );
        })}
      </div>

      <style>{`
        @keyframes afNodeFadeIn {
          from { opacity: 0; transform: translate(-50%, -50%) scale(0.985); }
          to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
      `}</style>
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Activity Feed" subtitle="live_execution_loop updates (scrollable)" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {feed.map((f, i) => (
          <div
            key={`${f.ts}-${i}`}
            style={{
              display: "grid",
              gridTemplateColumns: "72px 1fr",
              gap: 10,
              fontSize: 12,
              color: "rgba(230,237,243,0.90)",
            }}
          >
            <span className="af-text-muted">{f.ts}</span>
            <span>{f.msg}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );

  const pipelineRegion = null;

  return (
    <AppLayout
      top={topRegion}
      main={mainRegion}
      agentConsole={agentConsoleRegion}
      pipelineMonitor={pipelineRegion}
    />
  );
}

