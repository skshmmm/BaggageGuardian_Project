// src/components/Stepper.tsx
import React from "react";

type StepKey = "upload" | "analysis" | "report";

type Props = {
  step: StepKey;
};

export const Stepper: React.FC<Props> = ({ step }) => {
  const steps = ["Upload", "AI Analysis", "Report"];
  const activeIndex = step === "upload" ? 0 : step === "analysis" ? 1 : 2;

  return (
    <div className="stepper">
      {steps.map((label, idx) => (
        <div key={label} className="stepper-item">
          <div className={`stepper-circle ${idx <= activeIndex ? "active" : ""}`}>
            {idx + 1}
          </div>
          <span
            className={`stepper-label ${idx <= activeIndex ? "active" : ""}`}
          >
            {label}
          </span>
        </div>
      ))}
    </div>
  );
};
