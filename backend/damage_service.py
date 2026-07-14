# backend/damage_service.py

from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from damage_model import get_yolo_model


# ---------- Utility: conversions ----------

def read_imagefile_to_cv2(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def normalize_box(xmin, ymin, xmax, ymax, width, height):
    return {
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
        "xmin_norm": xmin / width,
        "ymin_norm": ymin / height,
        "xmax_norm": xmax / width,
        "ymax_norm": ymax / height,
    }


# ---------- OpenCV diff pipeline ----------

def compute_damage_mask(pre_roi: np.ndarray, post_roi: np.ndarray) -> np.ndarray:
    """
    Compute binary mask of new damage between pre and post cropped regions.
    Sensitive to scratches, dents, tears, and other surface damage.
    """
    if pre_roi is None or post_roi is None:
        return np.zeros((0, 0), dtype=np.uint8)

    h = min(pre_roi.shape[0], post_roi.shape[0])
    w = min(pre_roi.shape[1], post_roi.shape[1])
    pre = cv2.resize(pre_roi, (w, h))
    post = cv2.resize(post_roi, (w, h))

    pre_gray = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)
    post_gray = cv2.cvtColor(post, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur for noise reduction
    pre_blur = cv2.GaussianBlur(pre_gray, (5, 5), 0)
    post_blur = cv2.GaussianBlur(post_gray, (5, 5), 0)

    # Compute absolute difference
    diff = cv2.absdiff(pre_blur, post_blur)
    diff = cv2.GaussianBlur(diff, (3, 3), 0)

    # Multiple threshold strategies to catch different damage types:
    # 1. Fixed threshold - catches major changes (tears, dents)
    _, fixed_thresh = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)
    
    # 2. Adaptive threshold - catches subtle changes (scratches, texture changes)
    adaptive_thresh = cv2.adaptiveThreshold(
        diff,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        4,
    )
    
    # 3. Otsu's method - automatic threshold for extreme contrasts
    _, otsu_thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Combine all thresholds to capture various damage types
    thresh = cv2.bitwise_or(fixed_thresh, adaptive_thresh)
    thresh = cv2.bitwise_or(thresh, otsu_thresh)

    # Morphological operations
    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return thresh


def extract_damage_contours(mask: np.ndarray, min_area: int = 8) -> List[np.ndarray]:
    """Extract contours from damage mask.
    
    Args:
        mask: Binary mask of damage
        min_area: Minimum contour area to consider (in pixels).
                 Lower value catches subtle damage like scratches.
    """
    if mask.size == 0:
        return []

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Lowered minimum area from 15 to 8 to catch smaller scratches and minor dents
    filtered = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]
    return filtered


# ---------- Severity Scoring ----------

def compute_severity(damage_area: float, bag_area: float) -> str:
    """
    Classify damage severity based on area ratio.
    Accounts for different damage types (scratches, dents, tears, etc.)
    """
    if bag_area <= 0:
        return "none"

    ratio = damage_area / bag_area

    # More nuanced thresholds to better distinguish damage types:
    # - Scratches/minor dents: 0.01-0.05 (low)
    # - Moderate dents/tears: 0.05-0.15 (medium)
    # - Major tears/structural damage: >0.15 (high)
    
    if ratio < 0.01:
        return "none"
    elif ratio < 0.05:
        return "low"
    elif ratio < 0.15:
        return "medium"
    else:
        return "high"


def severity_rank(severity: str) -> int:
    mapping = {"none": 0, "low": 1, "medium": 2, "high": 3}
    return mapping.get(severity, 0)


# ---------- Hybrid analysis for one post image ----------

def analyze_single_post_image(
    pre_img: np.ndarray,
    post_img: np.ndarray,
    damage_class_id: int | None = None,
    yolo_conf: float = 0.25,
) -> Dict[str, Any]:
    """
    Run YOLO on post_img, refine with OpenCV diff vs pre_img,
    and fall back to full-image diff if YOLO finds nothing.
    Returns dict with detections + severity.
    """
    h, w, _ = post_img.shape
    model = get_yolo_model()

    # --- 1. YOLO detection ---
    yolo_results = model(
        post_img,
        conf=yolo_conf,
        verbose=False
    )

    detections = []
    total_damage_area = 0.0
    yolo_box_found = False

    # Assume one image in results
    for r in yolo_results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            if damage_class_id is not None and cls_id != damage_class_id:
                continue

            # Accept all classes from the YOLO model (YOLOv11 is trained on damage types)
            # The model should only output damage-related classes, so we don't need strict filtering
            class_name = None
            if hasattr(model, "names") and model.names is not None:
                class_name = model.names.get(cls_id, "")

            yolo_box_found = True

            # xyxy box
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            xmin, ymin, xmax, ymax = map(int, [x1, y1, x2, y2])

            # Safety clamp
            xmin = max(0, xmin)
            ymin = max(0, ymin)
            xmax = min(w - 1, xmax)
            ymax = min(h - 1, ymax)

            # crop ROIs
            pre_roi = pre_img[ymin:ymax, xmin:xmax]
            post_roi = post_img[ymin:ymax, xmin:xmax]

            if pre_roi.size == 0 or post_roi.size == 0:
                continue

            # OpenCV diff in ROI
            mask = compute_damage_mask(pre_roi, post_roi)
            contours = extract_damage_contours(mask)

            box_area = (xmax - xmin) * (ymax - ymin)

            if not contours:
                detections.append(
                    {
                        "box": normalize_box(xmin, ymin, xmax, ymax, w, h),
                        "local_damage_area": 0.0,
                        "box_area": box_area,
                        "severity": "low",
                        "method": "yolo+opencv",
                    }
                )
                continue

            contour = max(contours, key=cv2.contourArea)
            contour_points = contour.reshape(-1, 2)
            if len(contour_points) > 0:
                ys, xs = contour_points[:, 1], contour_points[:, 0]
                refined_xmin = max(0, xmin + int(xs.min()))
                refined_ymin = max(0, ymin + int(ys.min()))
                refined_xmax = min(w - 1, xmin + int(xs.max()))
                refined_ymax = min(h - 1, ymin + int(ys.max()))
            else:
                refined_xmin, refined_ymin, refined_xmax, refined_ymax = xmin, ymin, xmax, ymax

            # Sum contour area in ROI
            roi_damage_area = sum(cv2.contourArea(c) for c in contours)

            # Compute damage area in full-image coordinates
            # NOTE: contour areas are in ROI pixels; it's fine for ratio computation
            total_damage_area += roi_damage_area

            refined_box_area = (refined_xmax - refined_xmin) * (refined_ymax - refined_ymin)
            box_severity = compute_severity(roi_damage_area, refined_box_area)

            detections.append(
                {
                    "box": normalize_box(refined_xmin, refined_ymin, refined_xmax, refined_ymax, w, h),
                    "local_damage_area": roi_damage_area,
                    "box_area": refined_box_area,
                    "severity": box_severity,
                    "method": "yolo+opencv",
                }
            )

    # --- 2. Fallback: full-image diff only if YOLO never identified a damage box ---
    used_fallback = False
    if len(detections) == 0 and not yolo_box_found:
        used_fallback = True
        mask = compute_damage_mask(pre_img, post_img)
        # Use lower min_area for full image to catch subtle damage
        contours = extract_damage_contours(mask, min_area=8)

        total_damage_area = sum(cv2.contourArea(c) for c in contours)
        bag_area = w * h

        full_severity = compute_severity(total_damage_area, bag_area)

        if contours:
            # Use a bounding box around the largest connected damage region.
            contour = max(contours, key=cv2.contourArea)
            x, y, box_w, box_h = cv2.boundingRect(contour)
            x2 = min(w - 1, x + box_w)
            y2 = min(h - 1, y + box_h)

            detections.append(
                {
                    "box": normalize_box(x, y, x2, y2, w, h),
                    "local_damage_area": total_damage_area,
                    "box_area": bag_area,
                    "severity": full_severity,
                    "method": "opencv-fallback",
                }
            )

    # --- 3. Image-level severity ---
    bag_area = w * h  # TODO: replace with actual bag mask later
    image_severity = compute_severity(total_damage_area, bag_area)

    return {
        "image_width": w,
        "image_height": h,
        "detections": detections,
        "total_damage_area": total_damage_area,
        "bag_area": bag_area,
        "image_severity": image_severity,
        "used_fallback": used_fallback,
    }


# ---------- Multi-image aggregation ----------

def analyze_all_images(
    pre_img: np.ndarray,
    post_images: List[np.ndarray]
) -> Dict[str, Any]:
    results_per_image = []
    best_idx = None
    best_ratio = 0.0
    global_severity = "none"

    for idx, post_img in enumerate(post_images):
        res = analyze_single_post_image(pre_img, post_img)
        results_per_image.append(res)

        # ratio for this image
        if res["bag_area"] > 0:
            ratio = res["total_damage_area"] / res["bag_area"]
        else:
            ratio = 0.0

        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = idx

        # update global severity
        if severity_rank(res["image_severity"]) > severity_rank(global_severity):
            global_severity = res["image_severity"]

    return {
        "global_severity": global_severity,
        "primary_image_index": best_idx,
        "images": results_per_image,
    }