import React, { useCallback, useEffect, useMemo, useState } from "react";
import AppLayout from "../components/layout/AppLayout";

type ApiResponse<T> = {
  success: boolean;
  data: T;
  error: string | null;
};

type CategoriesData = { categories: string[] };
type ResearchNode = { id: string } & Record<string, unknown>;
type NodesData = { nodes: ResearchNode[] };

export default function ResearchLabPage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [categories, setCategories] = useState<string[]>([]);
  const [nodes, setNodes] = useState<ResearchNode[]>([]);
  const [query, setQuery] = useState<string>("");
  const [urlText, setUrlText] = useState<string>("");
  const [ingesting, setIngesting] = useState<boolean>(false);
  const [ingestLog, setIngestLog] = useState<string[]>([]);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [catsRes, nodesRes] = await Promise.all([
        fetch("/api/v2/research/categories"),
        fetch("/api/v2/research/nodes"),
      ]);
      const catsPayload: ApiResponse<CategoriesData> = await catsRes.json();
      const nodesPayload: ApiResponse<NodesData> = await nodesRes.json();

      if (catsPayload.success && Array.isArray(catsPayload.data?.categories)) {
        setCategories(catsPayload.data.categories);
      } else {
        setCategories([]);
      }

      if (nodesPayload.success && Array.isArray(nodesPayload.data?.nodes)) {
        setNodes(nodesPayload.data.nodes);
      } else {
        setNodes([]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load research data");
      setCategories([]);
      setNodes([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return nodes.slice(0, 50);
    return nodes
      .filter((n) => {
        const id = typeof n.id === "string" ? n.id : "";
        const label = typeof n.label === "string" ? n.label : "";
        return id.toLowerCase().includes(q) || label.toLowerCase().includes(q);
      })
      .slice(0, 50);
  }, [nodes, query]);

  const addIngestLog = useCallback((line: string) => {
    setIngestLog((prev) => [line, ...prev].slice(0, 20));
  }, []);

  const ingestUrls = useCallback(async () => {
    const lines = urlText
      .split(/\r?\n/g)
      .map((s) => s.trim())
      .filter(Boolean);
    if (lines.length === 0) return;

    setIngesting(true);
    setError("");
    try {
      for (const url of lines) {
        const res = await fetch("/api/v2/research/ingest_url", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        const payload: ApiResponse<{ node_id: string; kind: string; label: string }> = await res.json();
        if (!payload.success) {
          addIngestLog(`FAILED: ${url} — ${payload.error || "error"}`);
        } else {
          addIngestLog(`OK: ${url} → ${payload.data.node_id}`);
        }
      }
      setUrlText("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  }, [addIngestLog, refresh, urlText]);

  const uploadFiles = useCallback(
    async (files: FileList | File[]) => {
      const list = Array.isArray(files) ? files : Array.from(files);
      if (list.length === 0) return;

      setIngesting(true);
      setError("");
      try {
        for (const file of list) {
          const form = new FormData();
          form.append("file", file);
          const res = await fetch("/api/v2/research/upload", { method: "POST", body: form });
          const payload: ApiResponse<{ node_id: string }> = await res.json();
          if (!payload.success) {
            addIngestLog(`FAILED: ${file.name} — ${payload.error || "error"}`);
          } else {
            addIngestLog(`OK: ${file.name} → ${payload.data.node_id}`);
          }
        }
        await refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
      } finally {
        setIngesting(false);
      }
    },
    [addIngestLog, refresh],
  );

  return (
    <AppLayout>
      <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <h1 style={{ margin: 0, fontSize: 20 }}>Research Lab</h1>
          <button
            type="button"
            onClick={refresh}
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

        <div style={{ height: 10 }} />

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ border: "1px solid rgba(0,0,0,0.12)", borderRadius: 12, padding: 12 }}>
            <div style={{ fontWeight: 600 }}>Ingest URLs & Files</div>
            <div style={{ height: 8 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <textarea
                value={urlText}
                onChange={(e) => setUrlText(e.target.value)}
                placeholder={"Paste URLs (YouTube or web pages), one per line…"}
                aria-label="URLs to ingest"
                style={{
                  width: "100%",
                  minHeight: 86,
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(0,0,0,0.15)",
                  resize: "vertical",
                }}
              />
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <button
                  type="button"
                  onClick={ingestUrls}
                  disabled={ingesting || urlText.trim().length === 0}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 10,
                    border: "1px solid rgba(0,0,0,0.15)",
                    cursor: ingesting || urlText.trim().length === 0 ? "not-allowed" : "pointer",
                  }}
                >
                  {ingesting ? "Working…" : "Ingest URLs"}
                </button>
                <label
                  style={{
                    padding: "10px 12px",
                    borderRadius: 10,
                    border: "1px solid rgba(0,0,0,0.15)",
                    cursor: ingesting ? "not-allowed" : "pointer",
                    background: "rgba(255,255,255,0.92)",
                  }}
                >
                  Upload files
                  <input
                    type="file"
                    multiple
                    disabled={ingesting}
                    onChange={(e) => {
                      const f = e.target.files;
                      if (f) void uploadFiles(f);
                      e.target.value = "";
                    }}
                    style={{ display: "none" }}
                  />
                </label>
                <span style={{ fontSize: 12, opacity: 0.75 }}>
                  Drop supported docs here (uploads to workspace temp and ingests)
                </span>
              </div>

              <div
                onDragOver={(e) => {
                  e.preventDefault();
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  const f = e.dataTransfer?.files;
                  if (f && f.length > 0) void uploadFiles(f);
                }}
                style={{
                  border: "2px dashed rgba(0,0,0,0.18)",
                  borderRadius: 12,
                  padding: 12,
                  background: "rgba(255,255,255,0.60)",
                  fontSize: 12,
                  opacity: ingesting ? 0.6 : 1,
                }}
              >
                Drop files here to ingest
              </div>

              {ingestLog.length > 0 ? (
                <div
                  style={{
                    border: "1px solid rgba(0,0,0,0.10)",
                    borderRadius: 10,
                    padding: 10,
                    background: "rgba(255,255,255,0.92)",
                    fontSize: 12,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {ingestLog.slice(0, 8).map((l) => (
                    <div key={l}>{l}</div>
                  ))}
                </div>
              ) : null}
            </div>
          </div>

          <div style={{ border: "1px solid rgba(0,0,0,0.12)", borderRadius: 12, padding: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
              <div style={{ fontWeight: 600 }}>Categories</div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>{categories.length} total</div>
            </div>
            <div style={{ height: 10 }} />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {categories.map((cat) => (
                <span
                  key={cat}
                  style={{
                    fontSize: 12,
                    padding: "4px 10px",
                    borderRadius: 999,
                    border: "1px solid rgba(0,0,0,0.18)",
                    background: "rgba(255,255,255,0.92)",
                  }}
                >
                  {cat.replace(/_/g, " ")}
                </span>
              ))}
              {categories.length === 0 ? <span style={{ fontSize: 12, opacity: 0.8 }}>No categories.</span> : null}
            </div>
          </div>

          <div style={{ border: "1px solid rgba(0,0,0,0.12)", borderRadius: 12, padding: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
              <div style={{ fontWeight: 600 }}>Knowledge Nodes</div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>{nodes.length} total</div>
            </div>
            <div style={{ height: 10 }} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter by id or label…"
              aria-label="Filter nodes"
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid rgba(0,0,0,0.15)",
              }}
            />
            <div style={{ height: 10 }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {filtered.map((n) => (
                <div
                  key={n.id}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 12,
                    border: "1px solid rgba(0,0,0,0.12)",
                    background: "rgba(255,255,255,0.92)",
                    fontSize: 12,
                    wordBreak: "break-word",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{n.id}</div>
                  {typeof n.label === "string" && n.label.trim() ? (
                    <div style={{ opacity: 0.85, marginTop: 2 }}>{n.label}</div>
                  ) : null}
                </div>
              ))}
              {!loading && !error && filtered.length === 0 ? (
                <div style={{ fontSize: 12, opacity: 0.8 }}>No nodes found.</div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
