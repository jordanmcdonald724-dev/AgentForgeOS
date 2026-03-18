import React, { useEffect, useMemo, useState } from "react";
import GlowContainer from "../panels/GlowContainer";
import GlassPanel from "../panels/GlassPanel";

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

/**
 * PipelineView
 * - nodes = steps
 * - active step highlighted
 * - subtle connections
 * - optional runner glow moves step-to-step
 */
export default function PipelineView({
  steps = [],
  activeStepId,
  orientation = "vertical", // "vertical" | "horizontal"
  running = false,
  className = "",
}) {
  const safeSteps = Array.isArray(steps) ? steps : [];

  const activeIndex = useMemo(() => {
    if (!safeSteps.length) return -1;
    if (activeStepId == null) return 0;
    const idx = safeSteps.findIndex((s) => (typeof s === "string" ? s === activeStepId : s.id === activeStepId));
    return idx >= 0 ? idx : 0;
  }, [safeSteps, activeStepId]);

  const [runnerIndex, setRunnerIndex] = useState(() => (activeIndex >= 0 ? activeIndex : 0));

  useEffect(() => {
    setRunnerIndex(activeIndex >= 0 ? activeIndex : 0);
  }, [activeIndex]);

  useEffect(() => {
    if (!running || safeSteps.length <= 1) return;
    const timer = setInterval(() => {
      setRunnerIndex((prev) => (prev + 1) % safeSteps.length);
    }, 1100);
    return () => clearInterval(timer);
  }, [running, safeSteps.length]);

  const isVertical = orientation !== "horizontal";

  const runnerPos = useMemo(() => {
    if (!safeSteps.length) return 0;
    const idx = clamp(runnerIndex, 0, safeSteps.length - 1);
    return safeSteps.length === 1 ? 0 : idx / (safeSteps.length - 1);
  }, [runnerIndex, safeSteps.length]);

  return (
    <GlassPanel tight className={className} style={{ padding: 12 }}>
      <div
        style={{
          display: "flex",
          flexDirection: isVertical ? "column" : "row",
          gap: isVertical ? 10 : 12,
          position: "relative",
        }}
      >
        {/* Runner glow (controlled, smooth) */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: isVertical ? 14 : `calc(${runnerPos * 100}% - 30px)`,
              top: isVertical ? `calc(${runnerPos * 100}% - 18px)` : 14,
              width: isVertical ? 4 : 60,
              height: isVertical ? 36 : 4,
              borderRadius: 999,
              background: "rgba(184, 50, 69, 0.60)",
              boxShadow: running
                ? "0 0 26px rgba(184, 50, 69, 0.36)"
                : "0 0 18px rgba(184, 50, 69, 0.22)",
              filter: "blur(0px)",
              opacity: running ? 0.55 : 0.28,
              transition:
                "left 360ms var(--af-ease), top 360ms var(--af-ease), opacity 280ms var(--af-ease), box-shadow 280ms var(--af-ease)",
            }}
          />
        </div>

        {safeSteps.length ? (
          safeSteps.map((step, idx) => {
            const id = typeof step === "string" ? step : step.id;
            const label = typeof step === "string" ? step : step.label || step.id;
            const isActive = idx === activeIndex;
            const glowState = isActive ? (running ? "running" : "active") : "idle";

            return (
              <div
                key={id || idx}
                style={{
                  display: "flex",
                  flexDirection: isVertical ? "row" : "column",
                  alignItems: isVertical ? "center" : "flex-start",
                  gap: 10,
                  position: "relative",
                  flex: isVertical ? "none" : 1,
                  minWidth: isVertical ? "auto" : 120,
                }}
              >
                {/* connection line */}
                {idx !== 0 ? (
                  <div
                    aria-hidden="true"
                    style={{
                      position: "absolute",
                      left: isVertical ? 14 : "50%",
                      top: isVertical ? -10 : 14,
                      width: isVertical ? 1 : "calc(100% + 12px)",
                      height: isVertical ? 10 : 1,
                      transform: isVertical ? "none" : "translateX(-50%)",
                      background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent)",
                      opacity: 0.7,
                    }}
                  />
                ) : null}

                <GlowContainer state={glowState} pulse={isActive && !running}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: isVertical ? "10px 10px" : "10px 12px",
                      borderRadius: 12,
                      border: isActive ? "1px solid rgba(184, 50, 69, 0.22)" : "1px solid rgba(255,255,255,0.08)",
                      background: isActive ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.03)",
                      transition: "border-color 280ms var(--af-ease), background 280ms var(--af-ease)",
                      minWidth: isVertical ? "auto" : "100%",
                    }}
                  >
                    <span
                      aria-hidden="true"
                      style={{
                        width: 9,
                        height: 9,
                        borderRadius: 999,
                        background: isActive ? "rgba(184, 50, 69, 0.85)" : "rgba(255,255,255,0.12)",
                        boxShadow: isActive ? "0 0 18px rgba(184, 50, 69, 0.30)" : "none",
                        transition: "box-shadow 280ms var(--af-ease), background 280ms var(--af-ease)",
                        flexShrink: 0,
                      }}
                    />
                    <div style={{ minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: 12,
                          letterSpacing: "0.08em",
                          textTransform: "uppercase",
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {label}
                      </div>
                      <div className="af-text-muted" style={{ fontSize: 12 }}>
                        {isActive ? (running ? "Running" : "Active") : "Queued"}
                      </div>
                    </div>
                  </div>
                </GlowContainer>
              </div>
            );
          })
        ) : (
          <div className="af-text-muted" style={{ padding: 12, fontSize: 12 }}>
            No pipeline steps.
          </div>
        )}
      </div>
    </GlassPanel>
  );
}

