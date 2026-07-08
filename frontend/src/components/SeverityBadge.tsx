// src/components/SeverityBadge.tsx
import React from "react";
import type { Severity } from "../types";

export const severityLabel: Record<Severity, string> = {
  none: "No Damage",
  low: "Low Damage",
  medium: "Medium Damage",
  high: "High Damage",
};

export const severityColor: Record<Severity, string> = {
  none: "#64748b",
  low: "#22c55e",
  medium: "#eab308",
  high: "#ef4444",
};

export const severityBgColor: Record<Severity, string> = {
  none: "rgba(148, 163, 184, 0.1)",
  low: "rgba(34, 197, 94, 0.1)",
  medium: "rgba(234, 179, 8, 0.1)",
  high: "rgba(239, 68, 68, 0.1)",
};

type Props = {
  severity: Severity;
};

export const SeverityBadge: React.FC<Props> = ({ severity }) => {
  return (
    <span
      className="severity-badge"
      style={{
        borderColor: severityColor[severity],
        backgroundColor: severityBgColor[severity],
        color: severityColor[severity],
      }}
    >
      {severityLabel[severity]}
    </span>
  );
};
