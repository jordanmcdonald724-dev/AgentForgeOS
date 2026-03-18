import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import GlowContainer from "../../components/panels/GlowContainer";

const STAGES = ["blockout", "refine", "texture", "optimize", "validate"];

export default function AssetsPage() {
  const [prompt, setPrompt] = useState("");
  const [refs, setRefs] = useState("refs://none");
  const [activeStage, setActiveStage] = useState("refine");

  const previewLabel = useMemo(() => "Preview Window", []);

  const submit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setActiveStage("blockout");
    setPrompt("");
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Assets" subtitle="Prompt, references, and preview" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel
      glowState={activeStage === "validate" ? "active" : "idle"}
      className="af-scroll"
      style={{ padding: 12 }}
    >
      <SectionHeader title="Preview" subtitle="Large preview window" />
      <div style={{ height: 12 }} />
      <div
        style={{
          height: "calc(100vh - 140px)",
          minHeight: 420,
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.08)",
          background:
            "radial-gradient(700px 420px at 50% 40%, rgba(184,50,69,0.10), transparent 55%), rgba(255,255,255,0.02)",
          display: "grid",
          placeItems: "center",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase" }}>{previewLabel}</div>
          <div className="af-text-muted" style={{ marginTop: 8, fontSize: 12 }}>
            {activeStage ? `Stage: ${activeStage}` : "No stage active"}
          </div>
        </div>
      </div>
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Assets" subtitle="Prompt + references" />
      <div style={{ height: 12 }} />
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <textarea
          className="af-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe an asset…"
          aria-label="Asset prompt"
        />
        <input
          className="af-input"
          value={refs}
          onChange={(e) => setRefs(e.target.value)}
          placeholder="References (paths, URLs, IDs)…"
          aria-label="References"
        />
        <button className="af-button" type="submit">
          Generate
        </button>
      </form>
      <div style={{ height: 14 }} />
      <div className="af-divider" />
      <div style={{ height: 14 }} />
      <div className="af-text-muted" style={{ fontSize: 12 }}>
        Bind to scoring_engine for glow intensity and stage transitions.
      </div>
    </GlassPanel>
  );

  const pipelineRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Stage Tracker" subtitle="Active stage glows" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {STAGES.map((stage) => {
          const isActive = stage === activeStage;
          return (
            <GlowContainer key={stage} state={isActive ? "active" : "idle"} pulse={isActive}>
              <button
                type="button"
                className="af-button"
                onClick={() => setActiveStage(stage)}
                style={{
                  width: "100%",
                  justifyContent: "space-between",
                  background: isActive ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.04)",
                  borderColor: isActive ? "rgba(184,50,69,0.22)" : "rgba(255,255,255,0.10)",
                }}
              >
                <span style={{ fontSize: 12, letterSpacing: "0.10em", textTransform: "uppercase" }}>{stage}</span>
                <span className="af-text-muted" style={{ fontSize: 12 }}>
                  {isActive ? "Active" : "—"}
                </span>
              </button>
            </GlowContainer>
          );
        })}
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

