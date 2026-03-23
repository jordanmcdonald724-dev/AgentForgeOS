import { useMemo, useState } from "react";
import { useEventStream } from "./useEventStream";

/**
 * usePipelineState
 * Derives pipeline UI state from step_* and pipeline_modified events.
 */
export function usePipelineState({
  wsUrl = "/ws",
  enabled = true,
  initialSteps = [],
  initialActiveStepId,
} = {}) {
  const stream = useEventStream({ url: wsUrl, enabled });

  const [steps, setSteps] = useState(() => initialSteps);
  const [activeStepId, setActiveStepId] = useState(() => initialActiveStepId);
  const [running, setRunning] = useState(false);
  const [lastError, setLastError] = useState(null);

  useMemo(() => {
    const evt = stream.lastEvent;
    if (!evt) return null;

    switch (evt.type) {
      case "pipeline_modified": {
        const nextSteps = evt.data?.steps;
        if (Array.isArray(nextSteps)) setSteps(nextSteps);
        return null;
      }
      case "step_start": {
        const id = evt.data?.step_id || evt.data?.id || evt.data?.step;
        if (id != null) setActiveStepId(id);
        setRunning(true);
        setLastError(null);
        return null;
      }
      case "step_complete": {
        const id = evt.data?.step_id || evt.data?.id || evt.data?.step;
        if (id != null) setActiveStepId(id);
        setLastError(null);
        return null;
      }
      case "step_failed": {
        const id = evt.data?.step_id || evt.data?.id || evt.data?.step;
        if (id != null) setActiveStepId(id);
        setRunning(false);
        setLastError(evt.data?.error || "Step failed");
        return null;
      }
      case "step_retry": {
        const id = evt.data?.step_id || evt.data?.id || evt.data?.step;
        if (id != null) setActiveStepId(id);
        setRunning(true);
        setLastError(null);
        return null;
      }
      case "pipeline_complete": {
        setRunning(false);
        return null;
      }
      default:
        return null;
    }
  }, [stream.lastEvent]);

  const glowState = useMemo(() => {
    if (lastError) return "error";
    if (running) return "running";
    if (activeStepId != null) return "active";
    return "idle";
  }, [running, activeStepId, lastError]);

  return {
    streamStatus: stream.status,
    steps,
    activeStepId,
    running,
    lastError,
    glowState,
    events: stream.events,
    send: stream.send,
    clearEvents: stream.clear,
    setSteps,
    setActiveStepId,
    setRunning,
  };
}

