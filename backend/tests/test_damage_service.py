import os
import sys
import unittest
from unittest.mock import patch
import numpy as np
import cv2

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import damage_service
from damage_service import analyze_single_post_image


class DamageServiceTests(unittest.TestCase):
    def test_small_damage_region_still_returns_detection(self):
        pre = np.zeros((120, 120, 3), dtype=np.uint8)
        post = np.zeros((120, 120, 3), dtype=np.uint8)
        cv2.rectangle(post, (20, 20), (28, 28), (255, 255, 255), -1)

        result = analyze_single_post_image(pre, post)

        self.assertGreater(len(result["detections"]), 0)
        self.assertEqual(result["detections"][0]["method"], "opencv-fallback")

    def test_subtle_low_contrast_damage_returns_detection(self):
        pre = np.zeros((200, 200, 3), dtype=np.uint8)
        post = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(post, (70, 70), (120, 120), (12, 12, 12), -1)

        result = analyze_single_post_image(pre, post)

        self.assertGreater(len(result["detections"]), 0)

    def test_yolo_box_is_refined_to_damage_contour(self):
        pre = np.zeros((100, 100, 3), dtype=np.uint8)
        post = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(post, (20, 20), (30, 30), (255, 255, 255), -1)

        class FakeBox:
            def __init__(self, cls_id):
                self.cls = np.array([cls_id], dtype=np.float32)
                self.xyxy = np.array([[0, 0, 60, 60]], dtype=np.float32)
                self.conf = np.array([0.9], dtype=np.float32)

        class FakeResult:
            def __init__(self, cls_id):
                self.boxes = [FakeBox(cls_id)]

        class FakeModel:
            names = {0: "scratch"}

            def __call__(self, img, conf=0.3, verbose=False):
                return [FakeResult(0)]

        with patch.object(damage_service, "get_yolo_model", return_value=FakeModel()):
            result = analyze_single_post_image(pre, post)

        detection = result["detections"][0]
        assert detection["box"]["xmax"] - detection["box"]["xmin"] < 60
        assert detection["box"]["ymax"] - detection["box"]["ymin"] < 60

    def test_non_zero_damage_class_uses_yolo_detection(self):
        class FakeBox:
            def __init__(self, cls_id):
                self.cls = np.array([cls_id], dtype=np.float32)
                self.xyxy = np.array([[0, 0, 20, 20]], dtype=np.float32)
                self.conf = np.array([0.9], dtype=np.float32)

        class FakeResult:
            def __init__(self, cls_id):
                self.boxes = [FakeBox(cls_id)]

        class FakeModel:
            names = {0: "broken", 6: "scratch"}

            def __call__(self, img, conf=0.3, verbose=False):
                return [FakeResult(6)]

        pre = np.zeros((100, 100, 3), dtype=np.uint8)
        post = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch.object(damage_service, "get_yolo_model", return_value=FakeModel()):
            result = analyze_single_post_image(pre, post)

        self.assertEqual(result["detections"][0]["method"], "yolo+opencv")
        self.assertFalse(result["used_fallback"])


if __name__ == "__main__":
    unittest.main()
