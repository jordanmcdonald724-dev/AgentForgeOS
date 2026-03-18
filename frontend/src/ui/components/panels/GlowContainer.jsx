import React, { useMemo } from "react";

/**
 * GlowContainer
 * Drives glow intensity strictly by system state:
 * idle | active | running | error
 */
export default function GlowContainer({
  state = "idle",
  pulse = false,
  className = "",
  style,
  children,
}) {
  const glow = useMemo(() => {
    if (state === "active") return "active";
    if (state === "running") return "running";
    if (state === "error") return "error";
    return "idle";
  }, [state]);

  return (
    <div
      className={`af-glow ${pulse ? "af-pulse" : ""} ${className}`.trim()}
      data-glow={glow}
      style={style}
    >
      {children}
    </div>
  );
}

