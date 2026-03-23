import React, { useCallback } from "react";

import { useAgentState } from "../../../../hooks/useAgentState";
import { usePipelineState } from "../../../../hooks/usePipelineState";
import { useSystem } from "../../context/SystemContext";


export function StudioPage() {
  const agents = useAgentState({ wsUrl: "/ws" });
  const pipeline = usePipelineState({ wsUrl: "/ws" });
  useSystem();

  const onSubmit = useCallback(async (prompt) => {
    const provider = (() => {
      try {
        const v = localStorage.getItem("agentforge_agent_run_provider");
        return typeof v === "string" && v.trim().toLowerCase() === "router" ? "router" : "";
      } catch (e) {
        return "";
      }
    })();
    const res = await fetch("/api/agent/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, ...(provider ? { provider, agent_id: "planner" } : {}) }),
    });
    return res.json();
  }, []);

  return (
    <div>
      <div>{agents.streamStatus}</div>
      <div>{pipeline.streamStatus}</div>
      <button type="button" onClick={() => onSubmit("hello")}>
        Run
      </button>
    </div>
  );
}

export default StudioPage;
