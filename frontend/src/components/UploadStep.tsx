// src/components/UploadStep.tsx
import React from "react";

type Props = {
  preImagePreview: string | null;
  postImagePreviews: string[];
  loading: boolean;
  error: string | null;
  onPreImageChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onPostImagesChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onAnalyze: () => void;
};

export const UploadStep: React.FC<Props> = ({
  preImagePreview,
  postImagePreviews,
  loading,
  error,
  onPreImageChange,
  onPostImagesChange,
  onAnalyze,
}) => {
  return (
    <section className="upload-section">
      <h2>1. Upload Images</h2>
      <p className="subtitle">
        Upload one <strong>pre-flight</strong> baseline photo and one or more{" "}
        <strong>post-flight</strong> images of the same bag.
      </p>

      <div className="upload-grid">
        <div className="upload-card">
          <h3>Pre-flight (Baseline)</h3>
          <input type="file" accept="image/*" onChange={onPreImageChange} />
          {preImagePreview && (
            <div className="image-container small">
              <img src={preImagePreview} alt="Pre-flight" className="image" />
            </div>
          )}
        </div>

        <div className="upload-card">
          <h3>Post-flight Images</h3>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={onPostImagesChange}
          />
          {postImagePreviews.length > 0 && (
            <div className="post-preview-grid">
              {postImagePreviews.map((url, idx) => (
                <div className="image-container tiny" key={idx}>
                  <img src={url} alt={`Post ${idx + 1}`} className="image" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <button className="primary-btn" onClick={onAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Run AI Analysis"}
      </button>

      {error && <div className="error">{error}</div>}
    </section>
  );
};
