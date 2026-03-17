import React from "react";
import GlowContainer from "./GlowContainer";

/**
 * GlassPanel
 * Reusable premium glass panel with optional state glow.
 */
export default function GlassPanel({
  glowState,
  glowPulse = false,
  hover = false,
  tight = false,
  className = "",
  style,
  onClick,
  children,
}) {
  const panel = (
    <div
      className={[
        "af-glass",
        tight ? "af-glass--tight" : "",
        hover ? "af-glass--hover" : "",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      style={style}
      onClick={onClick}
    >
      {children}
    </div>
  );

  if (!glowState) return panel;
  return (
    <GlowContainer state={glowState} pulse={glowPulse}>
      {panel}
    </GlowContainer>
  );
}

