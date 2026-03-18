import React from "react";
import GlassPanel from "../panels/GlassPanel";
import "../../styles/agentforge.css";

const NAV_ITEMS = [
  { id: "command-center", label: "Command Center", href: "#/command-center" },
  { id: "workspace", label: "Project Workspace", href: "#/workspace" },
  { id: "research-lab", label: "Research Lab", href: "#/research-lab" },
  { id: "studio", label: "Studio", href: "#/studio" },
  { id: "builds", label: "Builds", href: "#/builds" },
  { id: "assets", label: "Assets", href: "#/assets" },
  { id: "deployment", label: "Deployment", href: "#/deployment" },
  { id: "sandbox", label: "Sandbox", href: "#/sandbox" },
  { id: "game", label: "Game Dev", href: "#/game" },
  { id: "saas", label: "SaaS Builder", href: "#/saas" },
  { id: "research", label: "Research", href: "#/research" },
];

export default function AppLayout({
  top,
  main,
  agentConsole,
  pipelineMonitor,
  floating,
}) {
  return (
    <div className="af-root">
      <div className="af-layout">
        <aside className="af-sidebar">
          <div className="af-sidebar-inner">
            <GlassPanel tight className="af-brand">
              <div className="af-brand-title">AgentForge</div>
              <div className="af-brand-chip">Premium UI</div>
            </GlassPanel>

            <GlassPanel tight className="af-nav">
              {NAV_ITEMS.map((item) => (
                <a key={item.id} href={item.href} className="af-nav-item">
                  <span
                    aria-hidden="true"
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 999,
                      background: "rgba(255,255,255,0.10)",
                    }}
                  />
                  <span style={{ fontSize: 13 }}>{item.label}</span>
                </a>
              ))}
            </GlassPanel>

            <div style={{ flex: 1 }} />

            <GlassPanel tight className="af-text-muted" style={{ padding: 12, fontSize: 12 }}>
              Calm, state-driven glow. Dark-only.
            </GlassPanel>
          </div>
        </aside>

        <main className="af-main">
          <div className="af-main-grid">
            <header className="af-main-top">{top}</header>
            <section className="af-main-center">{main}</section>
            <section className="af-main-bottom-left">{agentConsole}</section>
            <section className="af-main-bottom-right">{pipelineMonitor}</section>
          </div>
        </main>
      </div>

      {floating ? <div className="af-floating">{floating}</div> : null}
    </div>
  );
}

