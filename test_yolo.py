#!/usr/bin/env python3
import json
import sys
import cv2
sys.path.insert(0, '/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/backend')

from damage_model import get_yolo_model
from damage_service import read_imagefile_to_cv2

# Load test images
with open('/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/Sample images/Pre-Flight.png', 'rb') as f:
    pre_img = read_imagefile_to_cv2(f.read())

with open('/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/Sample images/Post-Flight.png', 'rb') as f:
    post_img = read_imagefile_to_cv2(f.read())

print("=== Testing YOLOv11 Detection ===\n")

# Run YOLO directly
model = get_yolo_model()
yolo_results = model(post_img, conf=0.3, verbose=False)

print(f"Number of detections at conf=0.3: {len(yolo_results[0].boxes) if yolo_results[0].boxes else 0}")

if yolo_results[0].boxes:
    print("\nDetailed detections:")
    for idx, box in enumerate(yolo_results[0].boxes):
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names.get(cls_id, "unknown")
        print(f"  Detection {idx}: class_id={cls_id}, class_name='{class_name}', confidence={conf:.3f}")
        print(f"    Box: {box.xyxy[0].tolist()}")
else:
    print("No detections found!")
