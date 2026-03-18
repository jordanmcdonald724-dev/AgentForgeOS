import React, { useCallback, useState } from "react";
import AppLayout from "../components/layout/AppLayout";
import GlassPanel from "../components/panels/GlassPanel";
import SectionHeader from "../components/panels/SectionHeader";

interface IngestResult {
	success: boolean;
	source?: string;
	items_indexed?: number;
}

export const ResearchLabPage: React.FC = () => {
	const [ingesting, setIngesting] = useState(false);
	const [lastResult, setLastResult] = useState<IngestResult | null>(null);
	const [error, setError] = useState<string | null>(null);

	const ingestSampleRepo = useCallback(async () => {
		setIngesting(true);
		setError(null);
		setLastResult(null);
		try {
			const res = await fetch("/api/v2/research/ingest", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					provider: "github",
					repo: "agentforge/sample-game-project",
				}),
			});
			const json = (await res.json()) as IngestResult;
			if (!json.success) {
				setError("Ingestion failed");
			} else {
				setLastResult(json);
			}
		} catch (e) {
			setError("Backend not available");
		} finally {
			setIngesting(false);
		}
	}, []);

	const topRegion = (
		<GlassPanel tight style={{ padding: 12 }}>
			<SectionHeader
				title="Research Lab"
				subtitle="Ingest repos, docs, and transcripts into the AgentForge knowledge graph."
			/>
		</GlassPanel>
	);

	const mainRegion = (
		<div
			className="af-scroll"
			style={{
				display: "grid",
				gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1.5fr)",
				gap: 12,
				height: "100%",
			}}
		>
			<GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
				<SectionHeader title="Ingestion" subtitle="GitHub · PDFs · Docs · Transcripts" />
				<p className="af-text-muted" style={{ fontSize: 12 }}>
					Wire this panel to the real engine ingestion endpoints. For now, it calls a sample GitHub ingest.
				</p>
				<div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
					<button
						className="af-button"
						type="button"
						onClick={ingestSampleRepo}
						disabled={ingesting}
					>
						{ingesting ? "Ingesting…" : "Ingest sample GitHub repo"}
					</button>
					<button className="af-button" type="button" disabled>
						Ingest PDFs / docs (coming soon)
					</button>
					<button className="af-button" type="button" disabled>
						Ingest transcripts (coming soon)
					</button>
				</div>
				{error && (
					<p style={{ fontSize: 12, color: "rgba(248,113,113,0.96)" }}>{error}</p>
				)}
				{lastResult && (
					<div style={{ fontSize: 12, marginTop: 4 }}>
						<p>Source: {lastResult.source ?? "unknown"}</p>
						<p>Items indexed: {lastResult.items_indexed ?? 0}</p>
					</div>
				)}
			</GlassPanel>

			<GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
				<SectionHeader title="Knowledge Graph" subtitle="Entities · systems · relationships" />
				<div
					style={{
						flex: 1,
						borderRadius: 16,
						border: "1px dashed rgba(148,163,184,0.65)",
						background: "rgba(15,23,42,0.90)",
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						fontSize: 12,
						color: "rgba(148,163,184,0.95)",
					}}
				>
					Graph visualization placeholder (vector store + graph engine)
				</div>
			</GlassPanel>
		</div>
	);

	const agentConsoleRegion = (
		<GlassPanel className="af-scroll" style={{ padding: 12 }}>
			<SectionHeader title="Research Notes" subtitle="Scratchpad for queries and findings" />
			<div
				style={{
					borderRadius: 12,
					border: "1px solid rgba(51,65,85,0.85)",
					background: "rgba(15,23,42,0.95)",
					minHeight: 80,
				}}
			/>
		</GlassPanel>
	);

	const pipelineRegion = (
		<GlassPanel className="af-scroll" style={{ padding: 12 }}>
			<SectionHeader title="Research Insights" subtitle="Patterns from ingested sources" />
			<ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
				<li>Common failure points in live-ops economy design.</li>
				<li>Patterns for fast iteration on combat feel.</li>
				<li>Known good onboarding flows for complex games.</li>
			</ul>
		</GlassPanel>
	);

	return (
		<AppLayout
			top={topRegion}
			main={mainRegion}
			agentConsole={agentConsoleRegion}
			pipelineMonitor={pipelineRegion}
		/>
	);
};

export default ResearchLabPage;
