import React from "react";
import AppLayout from "../components/layout/AppLayout";
import GlassPanel from "../components/panels/GlassPanel";
import SectionHeader from "../components/panels/SectionHeader";

export const ProjectWorkspacePage: React.FC = () => {
	const topRegion = (
		<GlassPanel tight style={{ padding: 12 }}>
			<SectionHeader
				title="Project Workspace"
				subtitle="Central hub for files, architecture, history, and engine launch."
			/>
		</GlassPanel>
	);

	const mainRegion = (
		<div
			className="af-scroll"
			style={{
				display: "grid",
				gridTemplateColumns: "minmax(0, 1.2fr) minmax(0, 1.8fr)",
				gap: 12,
				height: "100%",
			}}
		>
			<GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
				<SectionHeader title="Project Files" subtitle="Backed by the engine project tree" />
				<div className="af-scroll" style={{ flex: 1 }}>
					<ul style={{ listStyle: "none", margin: 0, padding: 0, fontSize: 12 }}>
						<li>projects/</li>
						<li style={{ paddingLeft: 12 }}>my-agentforge-build/</li>
						<li style={{ paddingLeft: 24 }}>specs/</li>
						<li style={{ paddingLeft: 24 }}>src/</li>
						<li style={{ paddingLeft: 24 }}>assets/</li>
						<li style={{ paddingLeft: 24 }}>builds/</li>
					</ul>
				</div>
			</GlassPanel>

			<GlassPanel style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
				<SectionHeader title="Editor" subtitle="Code + configuration surface" />
				<div
					style={{
						flex: 1,
						borderRadius: 14,
						border: "1px dashed rgba(148,163,184,0.60)",
						background: "rgba(15,23,42,0.85)",
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						fontSize: 12,
						color: "rgba(148,163,184,0.95)",
					}}
				>
					Editor placeholder (Monaco, wired to project tree)
				</div>
				<div
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
						gap: 10,
						fontSize: 12,
					}}
				>
					<div>
						<div style={{ marginBottom: 4 }}>Architecture / Systems View</div>
						<p className="af-text-muted">
							Render system diagrams, module graphs, and execution lanes from architecture artifacts.
						</p>
					</div>
					<div>
						<div style={{ marginBottom: 4 }}>Build History</div>
						<ul style={{ margin: 0, paddingLeft: 16 }}>
							<li>v0.1.0 — Simulation only</li>
							<li>v0.1.1 — Local prototype build</li>
							<li>v0.2.0 — First playable slice</li>
						</ul>
					</div>
				</div>
			</GlassPanel>
		</div>
	);

	const agentConsoleRegion = (
		<GlassPanel className="af-scroll" style={{ padding: 12 }}>
			<SectionHeader title="Engine Launch" subtitle="Send builds to target engines" />
			<div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12 }}>
				<button className="af-button" type="button">
					Launch in Unity
				</button>
				<button className="af-button" type="button">
					Launch in Unreal
				</button>
				<button className="af-button" type="button">
					Launch Web Build
				</button>
			</div>
		</GlassPanel>
	);

	const pipelineRegion = (
		<GlassPanel className="af-scroll" style={{ padding: 12 }}>
			<SectionHeader title="Live Logs" subtitle="Engine + agent stream (tail)" />
			<div
				style={{
					borderRadius: 12,
					border: "1px solid rgba(30,64,175,0.65)",
					background: "rgba(15,23,42,0.95)",
					padding: 10,
					fontSize: 11,
					color: "rgba(226,232,240,0.96)",
					maxHeight: 180,
					overflowY: "auto",
				}}
			>
				<p>[guardian] build safety checks passed.</p>
				<p>[launcher] ready to dispatch build to target engine.</p>
			</div>
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

export default ProjectWorkspacePage;
