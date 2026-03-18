import * as React from "react";

export interface AppLayoutProps {
  top: React.ReactNode;
  main: React.ReactNode;
  agentConsole: React.ReactNode;
  pipelineMonitor: React.ReactNode;
  floating?: React.ReactNode;
}

declare const AppLayout: React.FC<AppLayoutProps>;
export default AppLayout;
