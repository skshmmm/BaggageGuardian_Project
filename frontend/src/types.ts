// src/types.ts

export type Severity = "none" | "low" | "medium" | "high";

export type Box = {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
  xmin_norm: number;
  ymin_norm: number;
  xmax_norm: number;
  ymax_norm: number;
};

export type Detection = {
  box: Box;
  local_damage_area: number;
  box_area: number;
  severity: Severity;
  method: string;
};

export type ImageResult = {
  image_index: number;
  filename: string;
  image_width: number;
  image_height: number;
  image_severity: Severity;
  used_fallback: boolean;
  detections: Detection[];
};

export type AnalyzeResponse = {
  global_severity: Severity;
  primary_image_index: number;
  images: ImageResult[];
};
