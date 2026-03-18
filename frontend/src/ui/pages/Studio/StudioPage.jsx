import React, { useMemo, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import AgentCard from "../../components/agents/AgentCard";
import PipelineView from "../../components/pipeline/PipelineView";

function nowTs() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function StudioPage() {
  const agents = useMemo(
    () => [
      { id: "planner", name: "Planner", role: "Project Planner", state: "idle" },
      { id: "architect", name: "Architect", role: "System Architect", state: "active" },
      { id: "engineer", name: "Engineer", role: "Frontend Engineer", state: "idle" },
      { id: "tester", name: "Tester", role: "Integration Tester", state: "idle" },
    ],
    []
  );

  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState(
    "AgentForge Studio online. Connect execution streams to drive pipeline, output, and glow."
  );
  const [logs, setLogs] = useState(() => [
    { level: "info", ts: nowTs(), msg: "Studio initialized" },
    { level: "info", ts: nowTs(), msg: "Waiting for execution_monitor events…" },
  ]);

  const pipelineSteps = useMemo(
    () => [
      { id: "plan", label: "Plan" },
      { id: "route", label: "Route" },
      { id: "build", label: "Build" },
      { id: "test", label: "Test" },
      { id: "stabilize", label: "Stabilize" },
    ],
    []
  );

  const [activeStep, setActiveStep] = useState("route");
  const [pipelineRunning, setPipelineRunning] = useState(true);

  const appendLog = (level, msg) => {
    setLogs((prev) => [...prev, { level, ts: nowTs(), msg }].slice(-220));
  };

  const submit = (e) => {
    e.preventDefault();
    const p = prompt.trim();
    if (!p) return;
    setPrompt("");
    appendLog("info", `Prompt submitted: "${p.slice(0, 64)}${p.length > 64 ? "…" : ""}"`);
    setOutput(`> ${p}\n\n[Awaiting agent_pipeline output…]`);
    setPipelineRunning(true);
    setActiveStep((s) => (s === "stabilize" ? "plan" : s));
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Studio" subtitle="Unified workspace shell" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Agents" subtitle="State-driven glow" />
      <div style={{ height: 12 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {agents.map((a) => (
          <AgentCard
            key={a.id}
            name={a.name}
            role={a.role}
            state={a.state}
            onClick={() => appendLog("info", `Selected agent: ${a.name}`)}
          />
        ))}
      </div>
    </GlassPanel>
  );

  const agentConsoleRegion = (
    <div style={{ display: "grid", gridTemplateRows: "auto 1fr", gap: 14, height: "100%" }}>
      <GlassPanel tight style={{ padding: 12 }}>
        <SectionHeader title="Input" subtitle="Ctrl+Enter to submit (optional)" />
        <div style={{ height: 12 }} />
        <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 10 }}>
          <input
            className="af-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type a prompt…"
            aria-label="Prompt input"
          />
          <button className="af-button" type="submit">
            Send
          </button>
        </form>
      </GlassPanel>

      <GlassPanel className="af-scroll" glowState={pipelineRunning ? "active" : "idle"} style={{ padding: 12 }}>
        <SectionHeader title="Output" subtitle="agent_pipeline stream binds here" />
        <div style={{ height: 12 }} />
        <pre
          style={{
            margin: 0,
            fontFamily:
              "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
            fontSize: 12,
            lineHeight: 1.55,
            whiteSpace: "pre-wrap",
            color: "rgba(230,237,243,0.92)",
          }}
        >
          {output}
        </pre>
      </GlassPanel>
    </div>
  );

  const pipelineRegion = (
    <div style={{ display: "grid", gridTemplateRows: "auto 1fr", gap: 14, height: "100%" }}>
      <GlassPanel tight style={{ padding: 12 }}>
        <SectionHeader
          title="Pipeline"
          subtitle="execution_monitor drives active step"
          right={
            <button
              className="af-button"
              type="button"
              onClick={() => {
                const ids = pipelineSteps.map((s) => s.id);
                const idx = ids.indexOf(activeStep);
                const next = ids[(idx + 1) % ids.length];
                setActiveStep(next);
                appendLog("info", `Active step: ${next}`);
              }}
            >
              Next
            </button>
          }
        />
      </GlassPanel>

      <GlassPanel className="af-scroll" style={{ padding: 12 }}>
        <PipelineView
          steps={pipelineSteps}
          activeStepId={activeStep}
          orientation="vertical"
          running={pipelineRunning}
        />
        <div style={{ height: 14 }} />
        <SectionHeader title="Logs" subtitle="event stream (scrollable)" />
        <div style={{ height: 12 }} />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {logs.map((l, i) => (
            <div
              key={`${l.ts}-${i}`}
              style={{
                display: "grid",
                gridTemplateColumns: "72px 64px 1fr",
                gap: 10,
                fontSize: 12,
                color: "rgba(230,237,243,0.90)",
                opacity: 0.95,
              }}
            >
              <span className="af-text-muted">{l.ts}</span>
              <span
                style={{
                  color:
                    l.level === "error"
                      ? "rgba(184, 50, 69, 0.92)"
                      : l.level === "warn"
                        ? "rgba(230, 237, 243, 0.86)"
                        : "rgba(230, 237, 243, 0.86)",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}
              >
                {l.level}
              </span>
              <span style={{ minWidth: 0 }}>{l.msg}</span>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );

  const floating = (
    <GlassPanel tight glowState={pipelineRunning ? "running" : "idle"} style={{ padding: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase" }}>System State</div>
          <div className="af-text-muted" style={{ fontSize: 12 }}>
            {pipelineRunning ? "Running" : "Idle"}
          </div>
        </div>
        <button
          className="af-button"
          type="button"
          onClick={() => {
            setPipelineRunning((v) => !v);
            appendLog("info", `Pipeline toggled: ${!pipelineRunning ? "running" : "idle"}`);
          }}
        >
          Toggle
        </button>
      </div>
    </GlassPanel>
  );

  return (
    <AppLayout
      top={topRegion}
      main={mainRegion}
      agentConsole={agentConsoleRegion}
      pipelineMonitor={pipelineRegion}
      floating={floating}
    />
  );
}

