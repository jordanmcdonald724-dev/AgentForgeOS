import React, { useEffect, useMemo, useState } from "react";
import StudioPage from "../ui/pages/Studio/StudioPage.jsx";
import BuildsPage from "../ui/pages/Builds/BuildsPage.jsx";
import AssetsPage from "../ui/pages/Assets/AssetsPage.jsx";
import SandboxPage from "../ui/pages/Sandbox/SandboxPage.jsx";
import ResearchPage from "../ui/pages/Research/ResearchPage.jsx";
import CommandCenterPage from "../ui/pages/CommandCenterPage.tsx";
import ProjectWorkspacePage from "../ui/pages/ProjectWorkspacePage.tsx";
import ResearchLabPage from "../ui/pages/ResearchLabPage.tsx";

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
        return <BuildsPage />;
      case "assets":
        return <AssetsPage />;
      case "sandbox":
        return <SandboxPage />;
      case "research":
        return <ResearchPage />;
      case "studio":
      default:
        return <StudioPage />;
    }
  }, [route]);

  // While setup status is unknown, render the shell (calm, no spinner flashing)
  if (!setupComplete) return null;
  return page;
}

