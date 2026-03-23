import { useMemo, useState } from "react";
import { useEventStream } from "./useEventStream";

/**
 * useAgentState
 * Derives agent list + per-agent state from agent_created and execution events.
 */
export function useAgentState({
  wsUrl = "/ws",
  enabled = true,
  initialAgents = [],
} = {}) {
  const stream = useEventStream({ url: wsUrl, enabled });
  const [agents, setAgents] = useState(() => initialAgents);

  useMemo(() => {
    const evt = stream.lastEvent;
    if (!evt) return null;

    if (evt.type === "agent_created") {
      const agent = evt.data?.agent || evt.data;
      if (!agent) return null;
      const id = agent.id || agent.agent_id || agent.name;
      if (!id) return null;
      setAgents((prev) => {
        if (prev.some((a) => a.id === id)) return prev;
        return [...prev, { id, name: agent.name || id, role: agent.role || "Agent", state: "idle" }];
      });
      return null;
    }

    // Common agent activity signals (best-effort)
    if (
      evt.type === "step_start" ||
      evt.type === "step_complete" ||
      evt.type === "step_failed" ||
      evt.type === "step_retry" ||
      evt.type === "loop_iteration"
    ) {
      const agentId = evt.data?.agent_id || evt.data?.agent || evt.data?.by;
      if (!agentId) return null;
      setAgents((prev) =>
        prev.map((a) =>
          a.id !== agentId
            ? a
            : {
                ...a,
                state:
                  evt.type === "step_failed"
                    ? "error"
                    : evt.type === "step_start" || evt.type === "loop_iteration" || evt.type === "step_retry"
                      ? "active"
                      : "idle",
              }
        )
      );
      return null;
    }

    return null;
  }, [stream.lastEvent]);

  const counts = useMemo(() => {
    const active = agents.filter((a) => a.state === "active").length;
    const errored = agents.filter((a) => a.state === "error").length;
    return { total: agents.length, active, errored };
  }, [agents]);

  return {
    streamStatus: stream.status,
    agents,
    counts,
    events: stream.events,
    send: stream.send,
    clearEvents: stream.clear,
    setAgents,
  };
}

