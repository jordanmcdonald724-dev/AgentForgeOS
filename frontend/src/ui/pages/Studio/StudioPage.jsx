import React, { useCallback, useEffect, useRef, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import AgentCard from "../../components/agents/AgentCard";
import PipelineView from "../../components/pipeline/PipelineView";
import { useAgentState } from "../../hooks/useAgentState";
import { usePipelineState } from "../../hooks/usePipelineState";
import { useSystem } from "../../context/SystemContext";

// Seed agents shown before any agent_created WS events arrive.
const SEED_AGENTS = [
  { id: "planner", name: "Planner", role: "Project Planner", state: "idle" },
  { id: "architect", name: "Architect", role: "System Architect", state: "idle" },
  { id: "engineer", name: "Engineer", role: "Frontend Engineer", state: "idle" },
  { id: "tester", name: "Tester", role: "Integration Tester", state: "idle" },
];

// Seed pipeline steps shown before any pipeline_modified WS events arrive.
const SEED_STEPS = [
  { id: "plan", label: "Plan" },
  { id: "route", label: "Route" },
  { id: "build", label: "Build" },
  { id: "test", label: "Test" },
  { id: "stabilize", label: "Stabilize" },
];

function nowTs() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function StudioPage() {
  // S-2: Live agent list driven by /ws agent_created + step_* events
  const { agents } = useAgentState({ initialAgents: SEED_AGENTS });

  // S-3: Live pipeline driven by /ws step_* and pipeline_modified events
  const {
    steps: pipelineSteps,
    activeStepId,
    running: pipelineRunning,
    glowState,
    events: pipelineEvents,
    setActiveStepId,
    setRunning,
  } = usePipelineState({ initialSteps: SEED_STEPS });

  // S-5: Global system state wired to /ws by G-3 (SystemContext)
  const { state: systemState } = useSystem();

  const [prompt, setPrompt] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [output, setOutput] = useState(
    "AgentForge Studio online. Send a prompt to run an agent, or wait for execution stream events."
  );
  const [logs, setLogs] = useState(() => [
    { level: "info", ts: nowTs(), msg: "Studio initialized" },
    { level: "info", ts: nowTs(), msg: "Connecting to /ws execution stream…" },
  ]);

  const appendLog = useCallback((level, msg) => {
    setLogs((prev) => [...prev, { level, ts: nowTs(), msg }].slice(-220));
  }, []);

  // S-4: Append step output from /ws step_complete events to the output panel
  const lastProcessedEvent = useRef(null);
  useEffect(() => {
    if (!pipelineEvents.length) return;
    const last = pipelineEvents[pipelineEvents.length - 1];
    if (last === lastProcessedEvent.current) return;
    lastProcessedEvent.current = last;

    const agentLabel = last.data?.agent_name || last.data?.agent_id || "agent";
    if (last.type === "step_start") {
      appendLog("info", `Step start → ${agentLabel}`);
    } else if (last.type === "step_complete") {
      appendLog("info", `Step complete ← ${agentLabel}`);
      if (last.data?.output) {
        setOutput((prev) => `${prev}\n\n[${agentLabel}] ${last.data.output}`);
      }
    } else if (last.type === "step_failed") {
      appendLog("error", `Step failed: ${last.data?.error || "unknown error"}`);
    } else if (last.type === "step_retry") {
      appendLog("warn", `Step retry: ${agentLabel}`);
    } else if (last.type === "loop_iteration") {
      appendLog("info", `Loop iteration ${last.data?.iteration ?? ""}`);
    }
  }, [pipelineEvents, appendLog]);

  // S-1: Wire prompt submit → POST /api/agent/run
  const submit = useCallback(
    async (e) => {
      e.preventDefault();
      const p = prompt.trim();
      if (!p || submitting) return;
      setPrompt("");
      setSubmitting(true);
      appendLog("info", `Prompt: "${p.slice(0, 64)}${p.length > 64 ? "…" : ""}"`);
      setOutput(`> ${p}\n\n[Waiting for agent…]`);
      setRunning(true);

      try {
        const res = await fetch("/api/agent/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: p, pipeline: false }),
        });
        const json = await res.json();
        if (json.success !== false) {
          const text =
            json.data?.response ??
            json.data?.output ??
            (typeof json.data === "string" ? json.data : JSON.stringify(json.data, null, 2));
          setOutput(`> ${p}\n\n${text}`);
          appendLog("info", "Agent response received");
        } else {
          const errText = json.error || "Unknown error";
          setOutput(`> ${p}\n\n[Error: ${errText}]`);
          appendLog("error", `Agent error: ${errText}`);
        }
      } catch {
        setOutput(`> ${p}\n\n[Network error — is the engine running on :8000?]`);
        appendLog("error", "Network error connecting to engine");
      } finally {
        setSubmitting(false);
        setRunning(false);
      }
    },
    [prompt, submitting, appendLog, setRunning]
  );

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Studio" subtitle="Unified workspace shell" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader title="Agents" subtitle="Live state from /ws" />
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
        <SectionHeader title="Input" subtitle="Runs against POST /api/agent/run" />
        <div style={{ height: 12 }} />
        <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 10 }}>
          <input
            className="af-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type a prompt…"
            aria-label="Prompt input"
            disabled={submitting}
          />
          <button className="af-button" type="submit" disabled={submitting || !prompt.trim()}>
            {submitting ? "…" : "Send"}
          </button>
        </form>
      </GlassPanel>

      <GlassPanel className="af-scroll" glowState={glowState} style={{ padding: 12 }}>
        <SectionHeader title="Output" subtitle="API response + /ws step_complete stream" />
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
          subtitle="/ws step_* drives active step"
          right={
            <button
              className="af-button"
              type="button"
              onClick={() => {
                const ids = pipelineSteps.map((s) => (typeof s === "string" ? s : s.id));
                const currentIdx = ids.indexOf(activeStepId);
                const nextId = ids[(currentIdx + 1) % ids.length];
                setActiveStepId(nextId);
                appendLog("info", `Active step: ${nextId}`);
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
          activeStepId={activeStepId}
          orientation="vertical"
          running={pipelineRunning}
        />
        <div style={{ height: 14 }} />
        <SectionHeader title="Logs" subtitle="/ws event stream" />
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

  // S-5: Display global system state from SystemContext (score, iteration, pipeline status)
  const sysStatus = systemState?.pipeline?.status ?? (pipelineRunning ? "running" : "idle");
  const sysIteration = systemState?.iteration ?? 0;
  const sysScore = systemState?.score ?? 0;

  const floating = (
    <GlassPanel tight glowState={glowState} style={{ padding: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase" }}>System State</div>
          <div className="af-text-muted" style={{ fontSize: 12 }}>
            {sysStatus}
            {sysIteration > 0 && ` · iter ${sysIteration}`}
            {sysScore > 0 && ` · score ${sysScore}`}
          </div>
        </div>
        <button
          className="af-button"
          type="button"
          onClick={() => {
            const next = !pipelineRunning;
            setRunning(next);
            appendLog("info", `Pipeline toggled: ${next ? "running" : "idle"}`);
          }}
        >
          {pipelineRunning ? "Pause" : "Resume"}
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

