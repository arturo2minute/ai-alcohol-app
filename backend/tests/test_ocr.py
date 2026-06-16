import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ocr import get_ocr_engine, resize_for_ocr


class OCRHelperTests(unittest.TestCase):
    def tearDown(self):
        get_ocr_engine.cache_clear()

    def test_resize_for_ocr_downscales_large_images(self):
        import numpy as np

        image = np.zeros((1200, 2400, 3), dtype=np.uint8)

        resized_image, original_dimensions, resized_dimensions = resize_for_ocr(image)

        self.assertEqual(original_dimensions, (2400, 1200))
        self.assertEqual(resized_dimensions, (1600, 800))
        self.assertEqual(resized_image.shape[:2], (800, 1600))

    def test_resize_for_ocr_keeps_smaller_images_unchanged(self):
        import numpy as np

        image = np.zeros((900, 1200, 3), dtype=np.uint8)

        resized_image, original_dimensions, resized_dimensions = resize_for_ocr(image)

        self.assertEqual(original_dimensions, (1200, 900))
        self.assertEqual(resized_dimensions, (1200, 900))
        self.assertIs(resized_image, image)

    def test_get_ocr_engine_initializes_once(self):
        fake_module = types.SimpleNamespace()

        class FakeRapidOCR:
            instances = 0

            def __init__(self):
                type(self).instances += 1

        fake_module.RapidOCR = FakeRapidOCR

        with patch.dict(sys.modules, {"rapidocr_onnxruntime": fake_module}):
            first_engine = get_ocr_engine()
            second_engine = get_ocr_engine()

        self.assertIs(first_engine, second_engine)
        self.assertEqual(FakeRapidOCR.instances, 1)


if __name__ == "__main__":
    unittest.main()
