#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/backend')

from damage_model import get_yolo_model

model = get_yolo_model()
print("\n=== YOLOv11 Model Information ===")
print(f"Model type: {model.__class__.__name__}")
print(f"Model name: {model.model.model_name if hasattr(model.model, 'model_name') else 'N/A'}")
print(f"\nClass names: {model.names}")
print(f"Number of classes: {len(model.names) if model.names else 'N/A'}")
print(f"\nClasses by ID:")
if model.names:
    for class_id, class_name in model.names.items():
        print(f"  {class_id}: {class_name}")
