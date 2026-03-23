import React from "react";

export default function AppLayout({ children }) {
  return (
    <div>
      <nav>
        <a href="#/command-center">Command Center</a>
        <a href="#/workspace">Workspace</a>
        <a href="#/research-lab">Research Lab</a>
      </nav>
      <main>{children}</main>
    </div>
  );
}
