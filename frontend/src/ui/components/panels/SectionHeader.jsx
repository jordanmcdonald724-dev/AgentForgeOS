import React from "react";

export default function SectionHeader({ title, right, subtitle, className = "" }) {
  return (
    <div className={className}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase" }}>{title}</div>
          {subtitle ? <div className="af-text-muted" style={{ fontSize: 12 }}>{subtitle}</div> : null}
        </div>
        {right ? <div>{right}</div> : null}
      </div>
      <div style={{ height: 10 }} />
      <div className="af-divider" />
    </div>
  );
}

