import React, { createContext, useEffect, useRef, useReducer, useContext } from "react";

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

      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          currentStep: stepIndex,
          status: "running",
        },
        agents: {
          ...state.agents,
          [agentName]: "active",
        },
      };
    }

    case "STEP_COMPLETE": {
      const { stepIndex, agentName, output } = action.payload;

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
        agents: {
          ...state.agents,
          [agentName]: "idle",
        },
      };
    }

    case "STEP_FAILED": {
      const { stepIndex, agentName, error } = action.payload;

      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          status: "error",
        },
        agents: {
          ...state.agents,
          [agentName]: "error",
        },
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

  // Connect to the /ws execution stream and forward events into the reducer.
  // This makes global system state (pipeline steps, agent states, logs)
  // available to any component that calls useSystem(), without each page
  // needing to manage its own WebSocket connection.
  const wsRef = useRef(null);
  const retryRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    function connect() {
      if (!isMounted) return;
      try {
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${proto}//${window.location.host}/ws`);
        wsRef.current = ws;

        ws.onmessage = (msg) => {
          if (!isMounted) return;
          let payload;
          try {
            payload = JSON.parse(msg.data);
          } catch {
            return;
          }
          const type = payload?.type;
          const data = payload?.data ?? {};

          switch (type) {
            case "step_start":
              dispatch({
                type: "STEP_START",
                payload: {
                  stepIndex: data.step_id ?? data.step_index ?? null,
                  agentName: data.agent_id ?? data.agent_name ?? "unknown",
                },
              });
              break;
            case "step_complete":
              dispatch({
                type: "STEP_COMPLETE",
                payload: {
                  stepIndex: data.step_id ?? data.step_index ?? null,
                  agentName: data.agent_id ?? data.agent_name ?? "unknown",
                  output: data.output ?? null,
                },
              });
              break;
            case "step_failed":
              dispatch({
                type: "STEP_FAILED",
                payload: {
                  stepIndex: data.step_id ?? data.step_index ?? null,
                  agentName: data.agent_id ?? data.agent_name ?? "unknown",
                  error: data.error ?? "step failed",
                },
              });
              break;
            case "step_retry":
              dispatch({ type: "STEP_RETRY", payload: data });
              break;
            case "pipeline_modified":
              dispatch({ type: "PIPELINE_MODIFIED", payload: data });
              break;
            case "agent_created":
              dispatch({
                type: "AGENT_CREATED",
                payload: {
                  agentName: data.agent_id ?? data.agent_name ?? "unknown",
                },
              });
              break;
            case "loop_iteration":
              dispatch({
                type: "LOOP_ITERATION",
                payload: { iteration: data.iteration ?? 0 },
              });
              break;
            default:
              break;
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          // Reconnect after 1.5 s to survive backend restarts.
          retryRef.current = setTimeout(connect, 1500);
        };

        ws.onerror = () => {
          try { ws.close(); } catch { /* ignore */ }
        };
      } catch {
        // WebSocket not available (SSR, test env, etc.) — silently skip.
      }
    }

    connect();

    return () => {
      isMounted = false;
      if (retryRef.current) clearTimeout(retryRef.current);
      try { wsRef.current?.close(); } catch { /* ignore */ }
    };
  }, []);

  return (
    <SystemContext.Provider value={{ state, dispatch }}>
      {children}
    </SystemContext.Provider>
  );
}

export function useSystem() {
  return useContext(SystemContext);
}