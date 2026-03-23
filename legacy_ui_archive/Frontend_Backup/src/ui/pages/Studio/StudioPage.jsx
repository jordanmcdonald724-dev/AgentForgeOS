import React, { useEffect, useMemo, useRef, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import GlassPanel from "../../components/panels/GlassPanel";
import SectionHeader from "../../components/panels/SectionHeader";
import AgentCard from "../../components/agents/AgentCard";
import PipelineView from "../../components/pipeline/PipelineView";
import { useAgentState } from "../../hooks/useAgentState";
import { usePipelineState } from "../../hooks/usePipelineState";
import { useSystem } from "../../context/SystemContext";

const SEED_AGENTS = [
  { id: "planner", name: "Planner", role: "Project Planner", state: "idle" },
  { id: "architect", name: "Architect", role: "System Architect", state: "idle" },
  { id: "router", name: "Task Router", role: "Execution Router", state: "idle" },
  { id: "builder", name: "Module Builder", role: "Module Builder", state: "idle" },
  { id: "tester", name: "Integration Tester", role: "Integration Tester", state: "idle" },
];

const SEED_STEPS = [
  { id: 0, label: "Plan" },
  { id: 1, label: "Route" },
  { id: 2, label: "Build" },
  { id: 3, label: "Test" },
  { id: 4, label: "Stabilize" },
];

function nowTs() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function normalizeSteps(steps) {
  if (!Array.isArray(steps) || steps.length === 0) return SEED_STEPS;
  return steps.map((step, index) => ({
    id: step.id ?? step.step_id ?? step.step ?? index,
    label: step.label ?? step.name ?? step.title ?? `Step ${index + 1}`,
  }));
}

function formatApiOutput(payload) {
  const hasEnvelope =
    payload &&
    typeof payload === "object" &&
    "data" in payload &&
    ("success" in payload || "error" in payload);
  const data = hasEnvelope ? payload.data : payload;
  if (!data) return "";
  if (Array.isArray(data?.stages)) {
    return data.stages
      .map((entry, index) => {
        const text =
          entry?.output ??
          entry?.result ??
          entry?.message ??
          (typeof entry === "string" ? entry : JSON.stringify(entry));
        return `[stage ${index + 1}] ${String(text)}`;
      })
      .join("\n");
  }
  const text =
    data?.output ??
    data?.result ??
    data?.message ??
    data?.response ??
    (typeof data === "string" ? data : JSON.stringify(data));
  return String(text);
}

export default function StudioPage() {
  const { state: systemState } = useSystem();
  const {
    agents,
    streamStatus: agentStreamStatus,
    events: agentEvents,
  } = useAgentState({ wsUrl: "/ws", initialAgents: SEED_AGENTS });
  const pipeline = usePipelineState({
    wsUrl: "/ws",
    initialSteps: SEED_STEPS,
    initialActiveStepId: SEED_STEPS[0].id,
  });

  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState(
    "AgentForge Studio online. Submit prompt to run /api/agent/run and stream /ws events."
  );
  const [logs, setLogs] = useState(() => [
    { level: "info", ts: nowTs(), msg: "Studio initialized" },
    { level: "info", ts: nowTs(), msg: "Waiting for execution_monitor events…" },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const lastPipelineEventCount = useRef(0);

  const appendLog = (level, msg) => {
    setLogs((prev) => [...prev, { level, ts: nowTs(), msg }].slice(-220));
  };

  const pipelineSteps = useMemo(() => normalizeSteps(pipeline.steps), [pipeline.steps]);

  const activeStep = useMemo(() => {
    const raw = pipeline.activeStepId;
    if (raw == null) return pipelineSteps[0]?.id;
    if (typeof raw === "number") return pipelineSteps[raw]?.id ?? raw;
    if (typeof raw === "string" && /^\d+$/.test(raw)) {
      const idx = Number(raw);
      return pipelineSteps[idx]?.id ?? idx;
    }
    return raw;
  }, [pipeline.activeStepId, pipelineSteps]);

  const pipelineRunning = pipeline.running || submitting || systemState.pipeline.status === "running";

  useEffect(() => {
    if (pipeline.events.length <= lastPipelineEventCount.current) return;
    const newEvents = pipeline.events.slice(lastPipelineEventCount.current);
    lastPipelineEventCount.current = pipeline.events.length;

    newEvents.forEach((evt) => {
      if (evt.type === "step_start") {
        const stepId = evt.data?.step_id ?? evt.data?.step_index ?? evt.data?.step;
        appendLog("info", `Step started: ${String(stepId ?? "unknown")}`);
      }

      if (evt.type === "step_complete") {
        const stepId = evt.data?.step_id ?? evt.data?.step_index ?? evt.data?.step;
        const chunk = evt.data?.output ?? evt.data?.message ?? evt.data?.result;
        appendLog("info", `Step complete: ${String(stepId ?? "unknown")}`);
        if (chunk != null && String(chunk).trim()) {
          setOutput((prev) => `${prev}\n\n[step ${String(stepId ?? "?")}] ${String(chunk)}`);
        }
      }

      if (evt.type === "step_failed") {
        const err = evt.data?.error ?? "Step failed";
        appendLog("error", String(err));
      }
    });
  }, [pipeline.events]);

  const submit = async (e) => {
    e.preventDefault();
    const p = prompt.trim();
    if (!p || submitting) return;

    setSubmitting(true);
    setPrompt("");
    appendLog("info", `Prompt submitted: "${p.slice(0, 64)}${p.length > 64 ? "…" : ""}"`);
    setOutput(`> ${p}\n\n[Running pipeline…]`);

    try {
      const res = await fetch("/api/agent/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: p, pipeline: true }),
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(payload?.detail || payload?.error || `Request failed (${res.status})`);
      }
      const apiOutput = formatApiOutput(payload);
      if (apiOutput) {
        setOutput((prev) => `${prev}\n\n${apiOutput}`);
      }
      appendLog("info", "Pipeline request accepted");
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Unknown error";
      appendLog("error", `Run failed: ${msg}`);
      setOutput((prev) => `${prev}\n\n[error] ${msg}`);
    } finally {
      setSubmitting(false);
    }
  };

  const topRegion = (
    <GlassPanel tight style={{ padding: 12 }}>
      <SectionHeader title="Studio" subtitle="Unified workspace shell" />
    </GlassPanel>
  );

  const mainRegion = (
    <GlassPanel className="af-scroll" style={{ padding: 12 }}>
      <SectionHeader
        title="Agents"
        subtitle={`State-driven glow · ws ${agentStreamStatus} · events ${agentEvents.length}`}
      />
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
          <button className="af-button" type="submit" disabled={submitting}>
            {submitting ? "Running…" : "Send"}
          </button>
        </form>
      </GlassPanel>

      <GlassPanel className="af-scroll" glowState={pipelineRunning ? "active" : "idle"} style={{ padding: 12 }}>
        <SectionHeader title="Output" subtitle="API response + execution_monitor stream" />
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
        <SectionHeader title="Pipeline" subtitle="execution_monitor drives active step" />
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
            {pipelineRunning ? "Running" : "Idle"} · loop {systemState.iteration}
          </div>
        </div>
        <button
          className="af-button"
          type="button"
          onClick={() => appendLog("info", `System pipeline status: ${systemState.pipeline.status}`)}
        >
          Snapshot
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
