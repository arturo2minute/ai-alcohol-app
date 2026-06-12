import json
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ocr import extract_text_lines
from app.verifier import build_verification_result


FIELD_LABELS = {
    "brandName": "Brand Name",
    "classType": "Class/Type",
    "alcoholContent": "Alcohol Content",
    "netContents": "Net Contents",
    "governmentWarning": "Government Warning",
}


class VerifierAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest_path = (
            BACKEND_DIR.parent / "test-assets" / "labels" / "manifest.json"
        )
        cls.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cls.labels_root = manifest_path.parent

    def test_manifest_assets_match_expected_verification_outcomes(self):
        for item in self.manifest:
            with self.subTest(asset=item["id"]):
                payload = self.build_payload(item)

                self.assertFalse(payload["placeholder"])
                self.assertEqual(payload["summary"]["total"], 5)

                status_by_field = {
                    row["field"]: row["status"] for row in payload["results"]
                }
                mismatched_field_keys = {
                    field_key
                    for field_key, label in FIELD_LABELS.items()
                    if status_by_field[label] == "Mismatch"
                }

                for expected_mismatch in item["expectedMismatches"]:
                    self.assertIn(expected_mismatch, mismatched_field_keys)

                expected_outcome = item["expectedOutcome"]
                if expected_outcome == "match":
                    self.assertEqual(payload["summary"]["Mismatch"], 0)
                    self.assertEqual(payload["summary"]["Needs Review"], 0)
                elif expected_outcome == "mismatch":
                    self.assertGreater(payload["summary"]["Mismatch"], 0)
                elif expected_outcome == "match_or_needs_review":
                    self.assertEqual(payload["summary"]["Mismatch"], 0)
                else:
                    self.fail(f"Unexpected expectedOutcome: {expected_outcome}")

    def build_payload(self, item):
        image_path = self.labels_root / item["file"]
        ocr_lines = extract_text_lines(image_path.read_bytes())

        return build_verification_result(
            original_name=image_path.name,
            mime_type="image/png",
            size_bytes=image_path.stat().st_size,
            brand_name=item["expectedFields"]["brandName"],
            class_type=item["expectedFields"]["classType"],
            alcohol_content=item["expectedFields"]["alcoholContent"],
            net_contents=item["expectedFields"]["netContents"],
            ocr_lines=ocr_lines,
        )


if __name__ == "__main__":
    unittest.main()
