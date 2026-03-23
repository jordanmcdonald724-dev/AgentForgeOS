import React, { useCallback, useEffect, useMemo, useState } from "react";
import AppLayout from "../components/layout/AppLayout";

type ApiResponse<T> = {
  success: boolean;
  data: T;
  error: string | null;
};

type LocalProjectsData = { projects: string[] };

export default function ProjectWorkspacePage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [projects, setProjects] = useState<string[]>([]);

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v2/local_bridge/projects");
      const payload: ApiResponse<LocalProjectsData> = await res.json();
      if (!payload.success) {
        setError(payload.error || "Failed to load projects");
        setProjects([]);
        return;
      }
      const list = Array.isArray(payload.data?.projects) ? payload.data.projects : [];
      setProjects(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load projects");
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  const sorted = useMemo(() => [...projects].sort((a, b) => a.localeCompare(b)), [projects]);

  return (
    <AppLayout>
      <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <h1 style={{ margin: 0, fontSize: 20 }}>Project Workspace</h1>
          <button
            type="button"
            onClick={fetchProjects}
            disabled={loading}
            style={{
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid rgba(0,0,0,0.15)",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>
        </div>

        <div style={{ height: 10 }} />

        {error ? <div style={{ color: "rgba(220,38,38,0.92)", fontSize: 12 }}>{error}</div> : null}
        {!error && !loading && sorted.length === 0 ? (
          <div style={{ fontSize: 12, opacity: 0.8 }}>No local projects detected.</div>
        ) : null}

        <div style={{ height: 10 }} />

        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {sorted.map((p) => (
            <div
              key={p}
              style={{
                padding: "10px 12px",
                borderRadius: 12,
                border: "1px solid rgba(0,0,0,0.12)",
                background: "rgba(255,255,255,0.92)",
                fontSize: 12,
                wordBreak: "break-word",
              }}
            >
              {p}
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
