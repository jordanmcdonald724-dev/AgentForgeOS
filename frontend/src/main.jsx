import React from "react";
import ReactDOM from "react-dom/client";
import Router from "./router/Router.jsx";
import { SystemProvider } from "./ui/context/SystemContext"; // 👈 ADD THIS

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <SystemProvider>   {/* 👈 WRAP HERE */}
      <Router />
    </SystemProvider>
  </React.StrictMode>
);
