#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, '/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/backend')

from damage_service import read_imagefile_to_cv2, analyze_all_images

# Load test images
with open('/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/Sample images/Pre-Flight.png', 'rb') as f:
    pre_img = read_imagefile_to_cv2(f.read())

with open('/Users/sakshamshandilya/Desktop/Baggage Guardian/BaggageGuardian_Project/Sample images/Post-Flight.png', 'rb') as f:
    post_img = read_imagefile_to_cv2(f.read())

# Run analysis
result = analyze_all_images(pre_img, [post_img])

# Pretty print results
print(json.dumps({
    'global_severity': result['global_severity'],
    'primary_image_index': result['primary_image_index'],
    'images': [
        {
            'image_width': img['image_width'],
            'image_height': img['image_height'],
            'image_severity': img['image_severity'],
            'total_damage_area': img['total_damage_area'],
            'bag_area': img['bag_area'],
            'used_fallback': img['used_fallback'],
            'detections_count': len(img['detections']),
            'detections': img['detections'],
        }
        for img in result['images']
    ]
}, indent=2))
