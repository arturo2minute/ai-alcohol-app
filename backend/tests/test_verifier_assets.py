import json
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ocr import extract_text_lines
from app.verifier import (
    build_verification_result,
    build_verification_result_row,
    extract_alcohol_content,
    extract_government_warning,
)


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

    def test_manifest_assets_match_acceptable_verification_results(self):
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

                for expected_mismatch in item["expectedMismatchFields"]:
                    self.assertIn(expected_mismatch, mismatched_field_keys)

                actual_overall_result = self.build_overall_result(payload["summary"])
                self.assertIn(
                    actual_overall_result,
                    item["acceptableOverallResults"],
                )

    def test_extract_alcohol_content_matches_abv_lines(self):
        self.assertEqual(extract_alcohol_content(["6.8%ABV"]), "6.8%ABV")

    def test_alcohol_content_treats_abv_as_equivalent_to_alc_vol(self):
        result = build_verification_result_row(
            {"key": "alcoholContent", "label": "Alcohol Content"},
            "6.8% Alc./Vol.",
            "6.8%ABV",
        )

        self.assertEqual(result["status"], "Match")

    def test_extract_government_warning_stops_after_warning_boundary(self):
        lines = [
            "CASCADE ERIDGE CELLARS",
            "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not",
            "drink alcoholic beverages during pregnancy because of the risk of birth defects. (2)",
            "Consumption of alcoholic beverages impairs your ability to drive a car or",
            "operate machinery, and may cause health problems.",
            "13.5% Alc./Vol.",
            "750ML",
        ]

        self.assertEqual(
            extract_government_warning(lines),
            (
                "GOVERNMENT WARNING: (1) According to the Surgeon General, women should "
                "not drink alcoholic beverages during pregnancy because of the risk of "
                "birth defects. (2) Consumption of alcoholic beverages impairs your "
                "ability to drive a car or operate machinery, and may cause health "
                "problems."
            ),
        )

    def test_extract_government_warning_trims_inline_trailing_text(self):
        lines = [
            "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not",
            "drink alcoholic beverages during pregnancy because of the risk of birth defects. (2)",
            "Consumption of alcoholic beverages impairs your ability to drive a car or",
            "operate machinery, and may cause health problems 13.5% Alc./Vol. 750ML",
        ]

        self.assertEqual(
            extract_government_warning(lines),
            (
                "GOVERNMENT WARNING: (1) According to the Surgeon General, women should "
                "not drink alcoholic beverages during pregnancy because of the risk of "
                "birth defects. (2) Consumption of alcoholic beverages impairs your "
                "ability to drive a car or operate machinery, and may cause health "
                "problems"
            ),
        )

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

    def build_overall_result(self, summary):
        if summary["Mismatch"] > 0:
            return "fail"
        if summary["Needs Review"] > 0:
            return "review_required"
        return "pass"


if __name__ == "__main__":
    unittest.main()
