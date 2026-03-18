import React, { useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

export default function ResearchPage() {
  const [ingestion] = useState(() => [
    { id: "src-1", name: "gameplay_design.md", kind: "docs", status: "indexed" },
    { id: "src-2", name: "architecture.pdf", kind: "pdf", status: "queued" },
  ]);

  const [nodes] = useState(() => [
    { id: "kg-1", title: "Architecture Pattern: ECS", used: true },
    { id: "kg-2", title: "Optimization: Frame Budgeting", used: false },
    { id: "kg-3", title: "Bug Pattern: Race Condition", used: false },
  ]);

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Research" subtitle="Ingestion + knowledge graph" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Ingestion" subtitle="GitHub · PDFs · Docs · Transcripts" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {ingestion.map((src) => (
          <GlowContainer key={src.id} state={src.status === "indexed" ? "active" : "idle"}>
            <div
              className="af-glass"
              style={{
                padding: 12,
                borderRadius: 14,
                background: "rgba(255,255,255,0.03)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {src.name}
                  </div>
                  <div className="af-text-muted" style={{ fontSize: 12 }}>
                    {src.kind} · {src.id}
                  </div>
                </div>
                <span
                  className="af-text-muted"
                  style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}
                >
                  {src.status}
                </span>
              </div>
            </div>
          </GlowContainer>
        ))}
      </div>
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Source Intake" subtitle="Conceptual controls (wired later)" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
        <button className="af-button" type="button">
          Add GitHub repo (stub)
        </button>
        <button className="af-button" type="button">
          Upload PDF / Docs (stub)
        </button>
        <button className="af-button" type="button">
          Import transcript (stub)
        </button>
      </div>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Knowledge Graph" subtitle="Nodes · categories · status" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {nodes.map((n) => (
          <GlowContainer key={n.id} state={n.used ? "active" : "idle"}>
            <div
              className="af-glass"
              style={{
                padding: 10,
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(255,255,255,0.03)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {n.title}
                  </div>
                  <div className="af-text-muted" style={{ fontSize: 12 }}>
                    {n.id}
                  </div>
                </div>
                <span
                  className="af-text-muted"
                  style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}
                >
                  {n.used ? "Used" : "Idle"}
                </span>
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

