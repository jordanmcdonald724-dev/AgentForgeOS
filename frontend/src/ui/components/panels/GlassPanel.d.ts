import * as React from "react";

export interface GlassPanelProps {
  glowState?: any;
  glowPulse?: boolean;
  hover?: boolean;
  tight?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
  children?: React.ReactNode;
}

declare const GlassPanel: React.FC<GlassPanelProps>;
export default GlassPanel;
