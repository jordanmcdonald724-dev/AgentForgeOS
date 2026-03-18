import * as React from "react";

export interface SectionHeaderProps {
  title: React.ReactNode;
  right?: React.ReactNode;
  subtitle?: React.ReactNode;
  className?: string;
}

declare const SectionHeader: React.FC<SectionHeaderProps>;
export default SectionHeader;
