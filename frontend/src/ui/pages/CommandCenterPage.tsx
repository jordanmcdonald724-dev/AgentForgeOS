import React, { useCallback, useEffect, useMemo, useState } from "react";
import AppLayout from "../components/layout/AppLayout";

type ApiResponse<T> = {
  success: boolean;
  data: T;
  error: string | null;
};

type CommandPreviewTask = {
  task_id: string;
  assigned_agent: string;
  status: string;
  dependencies: string[];
  description: string;
  outputs: Record<string, unknown>;
};

type CommandPreviewData = {
  tasks: CommandPreviewTask[];
  simulation: Record<string, unknown>;
  build_status: string;
  recursive_loop: { stages: string[] };
  research?: { ingested?: unknown[] };
};

type ProjectStatusTask = {
  task_id: string;
  agent: string;
  status: string;
  dependencies: string[];
  declared_outputs: string[];
  missing_outputs: string[];
  phase: string | null;
  name: string | null;
};

type ProjectStatusData = {
  project_id: string;
  tasks: ProjectStatusTask[];
  artifact_index: Record<string, unknown>;
};

type ResearchCategoriesData = { categories: string[] };

function safeStringify(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export default function CommandCenterPage() {
  const [command, setCommand] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const [preview, setPreview] = useState<CommandPreviewData | null>(null);

  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(() => new Set());

  const [projectId, setProjectId] = useState<string>("session_default");
  const [projectStatus, setProjectStatus] = useState<ProjectStatusData | null>(null);

  useEffect(() => {
    fetch("/api/v2/research/categories")
      .then((r) => r.json())
      .then((payload: ApiResponse<ResearchCategoriesData>) => {
        if (payload.success && Array.isArray(payload.data?.categories)) {
          setCategories(payload.data.categories);
        }
      })
      .catch(() => {
        setCategories([]);
      });
  }, []);

  const toggleCategory = useCallback((cat: string) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  }, []);

  const selectedCategoryList = useMemo(() => Array.from(selectedCategories), [selectedCategories]);

  const runPreview = useCallback(async () => {
    const trimmed = command.trim();
    if (!trimmed) return;

    setLoading(true);
    setError("");
    setPreview(null);

    try {
      const researchSources =
        selectedCategoryList.length > 0
          ? selectedCategoryList.map((id) => ({ id, kind: "category", label: id }))
          : undefined;

      const res = await fetch("/api/v2/command/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          command: trimmed,
          brief: { source: "command-center" },
          research_sources: researchSources,
        }),
      });

      const payload: ApiResponse<CommandPreviewData> = await res.json();
      if (!payload.success) {
        setError(payload.error || "Preview failed");
        return;
      }
      setPreview(payload.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Preview failed");
    } finally {
      setLoading(false);
    }
  }, [command, selectedCategoryList]);

  const fetchStatus = useCallback(async () => {
    const trimmed = projectId.trim();
    if (!trimmed) return;
    setError("");
    setProjectStatus(null);
    try {
      const res = await fetch(`/api/v2/projects/${encodeURIComponent(trimmed)}/status`);
      const payload: ApiResponse<ProjectStatusData> = await res.json();
      if (!payload.success) {
        setError(payload.error || "Status failed");
        return;
      }
      setProjectStatus(payload.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Status failed");
    }
  }, [projectId]);

  return (
    <AppLayout>
      <div style={{ padding: 16, maxWidth: 1200, margin: "0 auto" }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>Command Center</h1>
        <div style={{ height: 10 }} />

        <div style={{ display: "flex", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 520px", minWidth: 320 }}>
            <div style={{ display: "flex", gap: 8 }}>
              <input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Describe what you want to build…"
                aria-label="Command"
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.15)",
                }}
              />
              <button
                type="button"
                onClick={runPreview}
                disabled={loading || !command.trim()}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.15)",
                  cursor: loading || !command.trim() ? "not-allowed" : "pointer",
                }}
              >
                {loading ? "Simulating…" : "Run Simulation"}
              </button>
            </div>

            <div style={{ height: 10 }} />

            {categories.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ fontSize: 12, opacity: 0.8 }}>Research context</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {categories.map((cat) => {
                    const active = selectedCategories.has(cat);
                    return (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => toggleCategory(cat)}
                        style={{
                          fontSize: 12,
                          padding: "4px 10px",
                          borderRadius: 999,
                          border: `1px solid ${active ? "rgba(45,212,191,0.80)" : "rgba(0,0,0,0.18)"}`,
                          background: active ? "rgba(45,212,191,0.12)" : "rgba(255,255,255,0.90)",
                          cursor: "pointer",
                        }}
                      >
                        {cat.replace(/_/g, " ")}
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : null}

            <div style={{ height: 10 }} />

            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                placeholder="project id"
                aria-label="Project id"
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.15)",
                }}
              />
              <button
                type="button"
                onClick={fetchStatus}
                disabled={!projectId.trim()}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.15)",
                  cursor: !projectId.trim() ? "not-allowed" : "pointer",
                }}
              >
                Load Status
              </button>
            </div>

            {error ? (
              <>
                <div style={{ height: 10 }} />
                <div style={{ color: "rgba(220,38,38,0.92)", fontSize: 12 }}>{error}</div>
              </>
            ) : null}
          </div>

          <div style={{ flex: "1 1 520px", minWidth: 320 }}>
            <div style={{ border: "1px solid rgba(0,0,0,0.12)", borderRadius: 12, padding: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <div style={{ fontWeight: 600 }}>Preview</div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>{preview?.build_status ?? "—"}</div>
              </div>
              <div style={{ height: 10 }} />
              <pre style={{ margin: 0, fontSize: 12, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {preview ? safeStringify(preview) : "Run a simulation to see tasks and outputs."}
              </pre>
            </div>

            <div style={{ height: 12 }} />

            <div style={{ border: "1px solid rgba(0,0,0,0.12)", borderRadius: 12, padding: 12 }}>
              <div style={{ fontWeight: 600 }}>Project Status</div>
              <div style={{ height: 10 }} />
              <pre style={{ margin: 0, fontSize: 12, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {projectStatus ? safeStringify(projectStatus) : "Load a project status to see artifact index."}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
