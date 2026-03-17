import React, { useMemo } from "react";
import GlassPanel from "../panels/GlassPanel";

const STATE_LABEL = {
  idle: "Idle",
  active: "Active",
  error: "Error",
};

function normalizeState(state) {
  if (state === "active" || state === "error") return state;
  return "idle";
}

export default function AgentCard({
  name = "Agent",
  role = "Role",
  state = "idle",
  compact = false,
  onClick,
}) {
  const s = useMemo(() => normalizeState(state), [state]);
  const glowPulse = s === "active";

  const indicator = useMemo(() => {
    if (s === "active") return { bg: "rgba(184, 50, 69, 0.85)", ring: "rgba(184, 50, 69, 0.35)" };
    if (s === "error") return { bg: "rgba(184, 50, 69, 0.95)", ring: "rgba(184, 50, 69, 0.55)" };
    return { bg: "rgba(255,255,255,0.14)", ring: "rgba(184, 50, 69, 0.16)" };
  }, [s]);

  return (
    <GlassPanel
      tight
      hover={Boolean(onClick)}
      glowState={s}
      glowPulse={glowPulse}
      className="af-glass--hover"
      style={{
        padding: compact ? 10 : 12,
        cursor: onClick ? "pointer" : "default",
      }}
      onClick={onClick}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div
          aria-hidden="true"
          style={{
            width: compact ? 34 : 40,
            height: compact ? 34 : 40,
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.10)",
            background:
              "radial-gradient(16px 16px at 35% 30%, rgba(255,255,255,0.10), transparent 60%), rgba(255,255,255,0.03)",
            boxShadow: "0 10px 22px rgba(0,0,0,0.35)",
            display: "grid",
            placeItems: "center",
            color: "rgba(230,237,243,0.75)",
            fontSize: 12,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          AF
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {name}
              </div>
              <div
                className="af-text-muted"
                style={{
                  fontSize: 12,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {role}
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
              <span
                aria-hidden="true"
                style={{
                  width: 9,
                  height: 9,
                  borderRadius: 999,
                  background: indicator.bg,
                  boxShadow: `0 0 0 1px rgba(255,255,255,0.10), 0 0 18px ${indicator.ring}`,
                  transition: "box-shadow var(--af-t) var(--af-ease), background var(--af-t) var(--af-ease)",
                }}
              />
              <span className="af-text-muted" style={{ fontSize: 12 }}>
                {STATE_LABEL[s]}
              </span>
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

