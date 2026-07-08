// src/components/PdfReportButton.tsx
import React from "react";
import type { AnalyzeResponse } from "../types";
import { jsPDF } from "jspdf";
import { severityLabel, severityColor } from "./SeverityBadge";

type Props = {
  response: AnalyzeResponse;
  postImagePreviews: string[];
};

const loadImage = (url: string): Promise<HTMLImageElement> =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(e);
    img.src = url;
  });

export const PdfReportButton: React.FC<Props> = ({
  response,
  postImagePreviews,
}) => {
  const handleClick = async () => {
    if (!response || postImagePreviews.length === 0) return;

    const primaryIndex = response.primary_image_index ?? 0;
    const primaryPreview = postImagePreviews[primaryIndex];
    const primaryResult = response.images[primaryIndex];

    try {
      const img = await loadImage(primaryPreview);

      const doc = new jsPDF("p", "mm", "a4");
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 10;

      // Header
      doc.setFontSize(18);
      doc.text("Baggage Guardian – Damage Report", margin, 15);

      doc.setFontSize(11);
      const timestamp = new Date().toLocaleString();
      doc.text(`Generated: ${timestamp}`, margin, 22);

      // Global severity
      doc.setFontSize(12);
      doc.setTextColor(severityColor[response.global_severity]);
      doc.text(
        `Global Damage Rating: ${severityLabel[response.global_severity]}`,
        margin,
        30
      );
      doc.setTextColor(0, 0, 0);

      // Legend
      doc.setFontSize(10);
      let legendY = 38;
      (["low", "medium", "high"] as const).forEach((sev) => {
        doc.setDrawColor(
          sev === "low" ? 0 : sev === "medium" ? 255 : 255,
          sev === "low" ? 255 : sev === "medium" ? 215 : 0,
          sev === "low" ? 0 : sev === "medium" ? 0 : 0
        );
        doc.rect(margin, legendY - 4, 4, 4);
        doc.setTextColor(0, 0, 0);
        doc.text(`${severityLabel[sev]}`, margin + 8, legendY);
        legendY += 6;
      });

      // Draw primary image
      const availableWidth = pageWidth - margin * 2;
      const availableHeight = pageHeight - 60;
      const imgAspect = img.width / img.height;
      let imgWidth = availableWidth;
      let imgHeight = imgWidth / imgAspect;
      if (imgHeight > availableHeight) {
        imgHeight = availableHeight;
        imgWidth = imgHeight * imgAspect;
      }

      const imgX = margin + (availableWidth - imgWidth) / 2;
      const imgY = 50;

      doc.addImage(img, "JPEG", imgX, imgY, imgWidth, imgHeight);

      // Draw damage boxes
      primaryResult.detections.forEach((det) => {
        const b = det.box;
        const x = imgX + b.xmin_norm * imgWidth;
        const y = imgY + b.ymin_norm * imgHeight;
        const w = (b.xmax_norm - b.xmin_norm) * imgWidth;
        const h = (b.ymax_norm - b.ymin_norm) * imgHeight;

        const sev = det.severity;
        if (sev === "low") {
          doc.setDrawColor(0, 255, 0);
        } else if (sev === "medium") {
          doc.setDrawColor(255, 215, 0);
        } else if (sev === "high") {
          doc.setDrawColor(255, 0, 0);
        } else {
          doc.setDrawColor(100, 100, 100);
        }
        doc.rect(x, y, w, h);
      });

      doc.save("baggage-guardian-report.pdf");
    } catch (e) {
      console.error(e);
      alert("Failed to generate PDF. Try again.");
    }
  };

  return (
    <button className="secondary-btn" onClick={handleClick}>
      Generate PDF Report
    </button>
  );
};
