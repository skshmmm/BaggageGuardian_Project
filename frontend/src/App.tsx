// src/App.tsx
import React, { useState } from "react";
import axios from "axios";
import "./App.css";

import type { AnalyzeResponse } from "./types";
import { Stepper } from "./components/Stepper";
import { UploadStep } from "./components/UploadStep";
import { ResultsStep } from "./components/ResultsStep";
import { PhotoTipsPanel } from "./components/PhotoTipsPanel";
import { PdfReportButton } from "./components/PdfReportButton";

const API_BASE_URL = "http://localhost:8000"; // FastAPI backend

type StepKey = "upload" | "analysis" | "report";

function App() {
  const [preImageFile, setPreImageFile] = useState<File | null>(null);
  const [postImageFiles, setPostImageFiles] = useState<File[]>([]);
  const [preImagePreview, setPreImagePreview] = useState<string | null>(null);
  const [postImagePreviews, setPostImagePreviews] = useState<string[]>([]);
  const [response, setResponse] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<StepKey>("upload");

  // --------- Handlers ---------

  const handlePreImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreImageFile(file);
    const url = URL.createObjectURL(file);
    setPreImagePreview(url);
  };

  const handlePostImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    setPostImageFiles(files);
    const urls = files.map((f) => URL.createObjectURL(f));
    setPostImagePreviews(urls);
  };

  const handleAnalyze = async () => {
    if (!preImageFile || postImageFiles.length === 0) {
      setError(
        "Please upload one pre-flight image and at least one post-flight image."
      );
      return;
    }

    setError(null);
    setLoading(true);
    setStep("analysis");

    try {
      const formData = new FormData();
      formData.append("pre_image", preImageFile);
      postImageFiles.forEach((file) => formData.append("post_images", file));

      const res = await axios.post<AnalyzeResponse>(
        `${API_BASE_URL}/api/analyze`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResponse(res.data);
      setStep("report");
    } catch (err) {
      console.error(err);
      setError("Analysis failed. Please check the backend and try again.");
      setStep("upload");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Baggage Guardian</h1>
        <p>AI-based baggage damage verification (YOLOv8 + OpenCV)</p>
      </header>

      <Stepper step={step} />

      <div className="layout">
        <main className="main-grid">
          <UploadStep
            preImagePreview={preImagePreview}
            postImagePreviews={postImagePreviews}
            loading={loading}
            error={error}
            onPreImageChange={handlePreImageChange}
            onPostImagesChange={handlePostImagesChange}
            onAnalyze={handleAnalyze}
          />

          {response && (
            <ResultsStep
              response={response}
              postImagePreviews={postImagePreviews}
              onGeneratePdf={() => {}}
            />
          )}
        </main>

        <PhotoTipsPanel />
      </div>

      {/* Use the shared PdfReportButton inside ResultsStep instead of onGeneratePdf if you prefer */}
      {response && (
        <div style={{ display: "none" }}>
          {/* placeholder to show how PdfReportButton is used if not inside ResultsStep */}
          <PdfReportButton
            response={response}
            postImagePreviews={postImagePreviews}
          />
        </div>
      )}
    </div>
  );
}

export default App;
