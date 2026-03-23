import React, { createContext, useContext, useEffect, useReducer } from "react";
import { useEventStream } from "../hooks/useEventStream";

const SystemContext = createContext();

const initialState = {
  pipeline: {
    steps: [],
    currentStep: null,
    status: "idle",
  },
  agents: {},
  logs: [],
  iteration: 0,
  score: 0,
};

function reducer(state, action) {
  switch (action.type) {
    case "STEP_START": {
      const { stepIndex, agentName } = action.payload;
      const nextAgents = agentName
        ? {
            ...state.agents,
            [agentName]: "active",
          }
        : state.agents;

      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          currentStep: stepIndex,
          status: "running",
        },
        agents: nextAgents,
      };
    }

    case "STEP_COMPLETE": {
      const { stepIndex, agentName, output } = action.payload;
      const nextAgents = agentName
        ? {
            ...state.agents,
            [agentName]: "idle",
          }
        : state.agents;

      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          currentStep: stepIndex,
          status: "running",
          steps: [
            ...state.pipeline.steps,
            { stepIndex, agentName, output, status: "complete" },
          ],
        },
        agents: nextAgents,
      };
    }

    case "STEP_FAILED": {
      const { stepIndex, agentName, error } = action.payload;
      const nextAgents = agentName
        ? {
            ...state.agents,
            [agentName]: "error",
          }
        : state.agents;

      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          status: "error",
        },
        agents: nextAgents,
        logs: [...state.logs, { type: "error", error }],
      };
    }

    case "STEP_RETRY": {
      return {
        ...state,
        logs: [...state.logs, { type: "retry", ...action.payload }],
      };
    }

    case "PIPELINE_MODIFIED": {
      return {
        ...state,
        logs: [...state.logs, { type: "pipeline_modified", ...action.payload }],
      };
    }

    case "AGENT_CREATED": {
      const { agentName } = action.payload;
      if (!agentName) return state;

      return {
        ...state,
        agents: {
          ...state.agents,
          [agentName]: "idle",
        },
      };
    }

    case "LOOP_ITERATION": {
      return {
        ...state,
        iteration: action.payload.iteration,
      };
    }

    case "SET_SCORE": {
      return {
        ...state,
        score: action.payload.score,
      };
    }

    case "ADD_LOG": {
      return {
        ...state,
        logs: [...state.logs, action.payload],
      };
    }

    default:
      return state;
  }
}

export function SystemProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { lastEvent } = useEventStream({ url: "/ws", enabled: true });

  useEffect(() => {
    if (!lastEvent) return;
    const data = lastEvent.data ?? {};
    const stepIndex = data.step_index ?? data.step_id ?? data.step;
    const agentName = data.agent_name ?? data.agent_id ?? data.agent ?? data.by;

    switch (lastEvent.type) {
      case "step_start":
        dispatch({ type: "STEP_START", payload: { stepIndex, agentName } });
        break;
      case "step_complete":
        dispatch({
          type: "STEP_COMPLETE",
          payload: {
            stepIndex,
            agentName,
            output: data.output ?? data.message ?? data.result,
          },
        });
        break;
      case "step_failed":
        dispatch({
          type: "STEP_FAILED",
          payload: { stepIndex, agentName, error: data.error ?? "Step failed" },
        });
        break;
      case "step_retry":
        dispatch({ type: "STEP_RETRY", payload: { stepIndex, agentName } });
        break;
      case "pipeline_modified":
        dispatch({ type: "PIPELINE_MODIFIED", payload: data });
        break;
      case "agent_created":
        dispatch({ type: "AGENT_CREATED", payload: { agentName } });
        break;
      case "loop_iteration":
        dispatch({ type: "LOOP_ITERATION", payload: { iteration: data.iteration ?? 0 } });
        break;
      default:
        break;
    }
  }, [lastEvent]);

  return (
    <SystemContext.Provider value={{ state, dispatch }}>
      {children}
    </SystemContext.Provider>
  );
}

export function useSystem() {
  return useContext(SystemContext);
}
