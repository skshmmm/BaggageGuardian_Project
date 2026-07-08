import os
import sys
import unittest
import numpy as np
import cv2

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from damage_service import analyze_single_post_image


class DamageServiceTests(unittest.TestCase):
    def test_small_damage_region_still_returns_detection(self):
        pre = np.zeros((120, 120, 3), dtype=np.uint8)
        post = np.zeros((120, 120, 3), dtype=np.uint8)
        cv2.rectangle(post, (20, 20), (28, 28), (255, 255, 255), -1)

        result = analyze_single_post_image(pre, post)

        self.assertGreater(len(result["detections"]), 0)
        self.assertEqual(result["detections"][0]["method"], "opencv-fallback")


if __name__ == "__main__":
    unittest.main()
