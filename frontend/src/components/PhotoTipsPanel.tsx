// src/components/PhotoTipsPanel.tsx
import React from "react";

export const PhotoTipsPanel: React.FC = () => {
  return (
    <aside className="sidebar">
      <h3>Photo Tips</h3>
      <p className="sidebar-intro">
        Better photos = more accurate damage verification.
      </p>
      <ul className="tips-list">
        <li>
          <strong>Pre-flight:</strong> Capture the{" "}
          <span>entire bag</span> from 2–3 angles.
        </li>
        <li>
          <strong>Post-flight:</strong> Use the <span>same angles</span> as
          pre-flight.
        </li>
        <li>
          <strong>Lighting:</strong> Avoid strong shadows; use{" "}
          <span>even, bright light</span>.
        </li>
        <li>
          <strong>Distance:</strong> Keep the bag centered; don’t cut off edges.
        </li>
        <li>
          <strong>Background:</strong> Use a <span>plain floor or wall</span>{" "}
          when possible.
        </li>
        <li>
          <strong>Focus:</strong> Hold still 1–2 seconds so the image is sharp.
        </li>
      </ul>
      <p className="sidebar-note">
        The AI compares pre- and post-flight photos. Matching angles and clear
        shots help it focus only on <strong>new damage</strong>.
      </p>
    </aside>
  );
};
