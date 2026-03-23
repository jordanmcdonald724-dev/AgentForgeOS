import React, { createContext, useContext, useMemo, useReducer } from "react";

import { useEventStream } from "../../../hooks/useEventStream";


const SystemContext = createContext(null);


function reducer(state, action) {
  switch (action.type) {
    case "step_start":
      return { ...state, lastEvent: action.payload };
    case "step_complete":
      return { ...state, lastEvent: action.payload };
    case "step_failed":
      return { ...state, lastEvent: action.payload };
    default:
      return state;
  }
}


export function SystemProvider({ children }) {
  const stream = useEventStream({ url: "/ws" });
  const [state, dispatch] = useReducer(reducer, { lastEvent: null, streamStatus: "idle" });

  useMemo(() => {
    if (!stream?.lastEvent) return null;
    dispatch({ type: stream.lastEvent.type, payload: stream.lastEvent });
    return null;
  }, [stream?.lastEvent]);

  const value = useMemo(
    () => ({
      ...state,
      streamStatus: stream.status,
      events: stream.events,
      lastEvent: stream.lastEvent ?? state.lastEvent,
      dispatch,
    }),
    [dispatch, state, stream.events, stream.lastEvent, stream.status]
  );

  return <SystemContext.Provider value={value}>{children}</SystemContext.Provider>;
}


export function useSystem() {
  return useContext(SystemContext);
}

