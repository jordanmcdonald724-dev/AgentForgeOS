import { useEffect, useMemo, useRef, useState } from "react";

/**
 * useEventStream
 * Minimal WebSocket event multiplexer for AgentForge UI.
 *
 * Events (expected):
 * - step_start, step_complete, step_failed, step_retry, pipeline_modified
 * - agent_created
 * - loop_iteration
 *
 * Notes:
 * - This hook is transport-only; domain hooks (pipeline/agent state) derive from it.
 * - Safe in offline environments: stays idle if socket fails.
 */
export function useEventStream({
  url = "/ws",
  protocols,
  enabled = true,
  reconnect = true,
  reconnectDelayMs = 1200,
  maxBuffer = 500,
} = {}) {
  const [status, setStatus] = useState("idle"); // idle | connecting | open | closed | error
  const [lastEvent, setLastEvent] = useState(null);
  const [events, setEvents] = useState([]);

  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const shouldReconnectRef = useRef(false);

  const wsUrl = useMemo(() => {
    if (!url) return null;
    if (/^wss?:\/\//i.test(url)) return url;
    if (typeof window === "undefined") return url;
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const path = url.startsWith("/") ? url : `/${url}`;
    return `${proto}//${host}${path}`;
  }, [url]);

  useEffect(() => {
    shouldReconnectRef.current = Boolean(enabled && reconnect);
    return () => {
      shouldReconnectRef.current = false;
    };
  }, [enabled, reconnect]);

  useEffect(() => {
    if (!enabled || !wsUrl) return undefined;

    let isMounted = true;

    const connect = () => {
      if (!isMounted) return;
      setStatus("connecting");

      try {
        const ws = new WebSocket(wsUrl, protocols);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          setStatus("open");
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setStatus("closed");
          if (shouldReconnectRef.current) {
            retryRef.current = setTimeout(connect, reconnectDelayMs);
          }
        };

        ws.onerror = () => {
          if (!isMounted) return;
          setStatus("error");
        };

        ws.onmessage = (msg) => {
          if (!isMounted) return;
          let payload = msg.data;
          try {
            payload = JSON.parse(msg.data);
          } catch {
            // allow plain text messages
          }

          const evt = normalizeEvent(payload);
          setLastEvent(evt);
          setEvents((prev) => {
            const next = [...prev, evt];
            return next.length > maxBuffer ? next.slice(next.length - maxBuffer) : next;
          });
        };
      } catch {
        setStatus("error");
        if (shouldReconnectRef.current) {
          retryRef.current = setTimeout(connect, reconnectDelayMs);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (retryRef.current) clearTimeout(retryRef.current);
      retryRef.current = null;
      try {
        wsRef.current?.close();
      } catch {
        // ignore
      } finally {
        wsRef.current = null;
      }
    };
  }, [enabled, wsUrl, protocols, reconnectDelayMs, maxBuffer]);

  const send = (data) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    try {
      ws.send(typeof data === "string" ? data : JSON.stringify(data));
      return true;
    } catch {
      return false;
    }
  };

  const clear = () => setEvents([]);

  return { status, lastEvent, events, send, clear };
}

function normalizeEvent(payload) {
  // Preferred schema: { type, ts, source, data }
  if (payload && typeof payload === "object" && payload.type) {
    return {
      type: payload.type,
      ts: payload.ts || Date.now(),
      source: payload.source || payload.stream || "unknown",
      data: payload.data ?? payload.payload ?? payload,
    };
  }

  // Alternate schema: { event, ... }
  if (payload && typeof payload === "object" && payload.event) {
    return {
      type: payload.event,
      ts: payload.ts || Date.now(),
      source: payload.source || "unknown",
      data: payload.data ?? payload,
    };
  }

  // Plain text
  return { type: "message", ts: Date.now(), source: "unknown", data: payload };
}

