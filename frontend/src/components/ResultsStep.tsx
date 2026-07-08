// src/components/ResultsStep.tsx
import React from "react";
import type { AnalyzeResponse, ImageResult } from "../types";
import { SeverityBadge, severityColor } from "./SeverityBadge";
import { PdfReportButton } from "./PdfReportButton";

type Props = {
  response: AnalyzeResponse;
  postImagePreviews: string[];
};

export const ResultsStep: React.FC<Props> = ({
  response,
  postImagePreviews,
}) => {
  const renderPostImageWithOverlay = (
    previewUrl: string,
    result: ImageResult
  ) => {
    return (
      <div className="post-card" key={result.image_index}>
        <div className="post-card-header">
          <span className="filename">{result.filename}</span>
          <SeverityBadge severity={result.image_severity} />
        </div>
        <div className="image-container">
          <img src={previewUrl} alt={result.filename} className="image" />
          {result.detections.map((det, idx) => {
            const b = det.box;
            const left = b.xmin_norm * 100;
            const top = b.ymin_norm * 100;
            const width = (b.xmax_norm - b.xmin_norm) * 100;
            const height = (b.ymax_norm - b.ymin_norm) * 100;

            const borderColor = severityColor[det.severity];

            return (
              <div
                key={idx}
                className="bbox"
                style={{
                  left: `${left}%`,
                  top: `${top}%`,
                  width: `${width}%`,
                  height: `${height}%`,
                  borderColor,
                }}
              >
                <span className="bbox-label">
                  {det.severity.toUpperCase()}
                </span>
              </div>
            );
          })}
        </div>
        {result.used_fallback && (
          <div className="fallback-note">
            Used full-image OpenCV fallback (no YOLO detections).
          </div>
        )}
      </div>
    );
  };

  return (
    <section className="results-section">
      <div className="results-header">
        <div>
          <h2>2. AI Analysis Results</h2>
          <p>
            Global damage rating based on all post-flight images compared with
            the pre-flight baseline.
          </p>
        </div>
        <div className="global-severity">
          <SeverityBadge severity={response.global_severity} />
        </div>
      </div>

      <div className="post-results-grid">
        {response.images.map((imgRes, idx) =>
          renderPostImageWithOverlay(postImagePreviews[idx], imgRes)
        )}
      </div>

      <div className="report-actions">
        <PdfReportButton
          response={response}
          postImagePreviews={postImagePreviews}
        />
        <button className="ghost-btn">
          Continue for Claim (placeholder)
        </button>
      </div>
    </section>
  );
};
