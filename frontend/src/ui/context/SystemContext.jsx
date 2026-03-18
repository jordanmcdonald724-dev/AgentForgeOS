import React, { createContext, useReducer, useContext } from "react";

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

  return (
    <SystemContext.Provider value={{ state, dispatch }}>
      {children}
    </SystemContext.Provider>
  );
}

export function useSystem() {
  return useContext(SystemContext);
}