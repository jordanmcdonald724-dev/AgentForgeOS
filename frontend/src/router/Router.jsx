import React, { useEffect, useMemo, useState } from "react";
import StudioPage from "../ui/pages/Studio/StudioPage.jsx";
import CommandCenterPage from "../ui/pages/CommandCenterPage.tsx";
import ProjectWorkspacePage from "../ui/pages/ProjectWorkspacePage.tsx";
import ResearchLabPage from "../ui/pages/ResearchLabPage.tsx";

function PlaceholderPage({ title }) {
  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <div style={{ marginTop: 8, opacity: 0.8 }}>Coming soon.</div>
    </div>
  );
}

function getRoute() {
  const raw = window.location.hash || "#/studio";
  const cleaned = raw.replace(/^#\//, "").replace(/^#/, "");
  const route = cleaned.split("?")[0].split("#")[0];
  return route || "studio";
}

export default function Router() {
  const [route, setRoute] = useState(() => getRoute());
  const [setupComplete, setSetupComplete] = useState(true);

  useEffect(() => {
    const onHash = () => setRoute(getRoute());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    // Preserve existing first-run redirect behavior:
    // if setup is incomplete, send to /wizard.html (static, backend-served).
    fetch("/api/setup")
      .then((r) => r.json())
      .then((payload) => {
        const complete = Boolean(payload?.data?.setup_complete);
        setSetupComplete(complete);
        if (!complete) window.location.href = "/wizard.html";
      })
      .catch(() => {
        // offline / backend not running: allow UI to load
        setSetupComplete(true);
      });
  }, []);

  const page = useMemo(() => {
    switch (route) {
      case "command-center":
        return <CommandCenterPage />;
      case "workspace":
        return <ProjectWorkspacePage />;
      case "research-lab":
        return <ResearchLabPage />;
      case "builds":
        return <PlaceholderPage title="Builds" />;
      case "assets":
        return <PlaceholderPage title="Assets" />;
      case "deployment":
        return <PlaceholderPage title="Deployment" />;
      case "game":
        return <PlaceholderPage title="Game Dev" />;
      case "saas":
        return <PlaceholderPage title="SaaS Builder" />;
      case "sandbox":
        return <PlaceholderPage title="Sandbox" />;
      case "research":
        return <PlaceholderPage title="Research" />;
      case "studio":
      default:
        return <StudioPage />;
    }
  }, [route]);

  // While setup status is unknown, render the shell (calm, no spinner flashing)
  if (!setupComplete) return null;
  return page;
}

