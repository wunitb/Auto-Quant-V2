"""Thai-language support across the report contract.

The AutoQuant desk works in English internally, but report prose is authored in
the caller's language. These tests pin the layers that silently mangle Thai:
schema validation, UTF-8 round-tripping, and the ASCII-only machine ids.
"""
from __future__ import annotations

import json
import re
import unicodedata
import unittest

from autoquant.reports import (
    FINDING_ID,
    REPORT_ANALYSIS_KIND,
    SCHEMA_VERSION,
    validate_report_analysis,
)

THAI_RANGE = re.compile(r"[฀-๿]")


def thai_analysis() -> dict:
    """A report analysis whose every prose field is Thai."""
    return {
        "schemaVersion": SCHEMA_VERSION,
        "kind": REPORT_ANALYSIS_KIND,
        "title": "ทดสอบรายงานภาษาไทยบน BTCUSD",
        "executiveSummary": (
            "โมเมนตัมระยะสั้นอ่อนลงชัดเจนในกรอบ 10 วัน "
            "ขณะที่เทรนด์ระยะยาวยังไม่เสียโครงสร้าง"
        ),
        "findings": [
            {
                "id": "momentum-decay-10d",
                "claim": "ค่า slope 10 วันติดลบที่ -467 ต่อวัน สวนทางกับ slope 50 วันที่ยังเป็นบวก",
                "confidence": "medium",
                "evidenceRefs": [
                    {
                        "kind": "run",
                        "id": "run-0001",
                        "artifactPath": "runs/run-0001/metrics.json",
                    }
                ],
            }
        ],
        "recommendations": [],
        "limitations": ["ข้อมูลรายวันมาจาก yfinance ซึ่งเป็นแหล่งที่ล่าช้า"],
        "unresolvedQuestions": ["ยังไม่ได้เทียบกับข้อมูลเรียลไทม์ของโบรกเกอร์"],
    }


class ThaiReportContractTests(unittest.TestCase):
    def test_validator_accepts_thai_prose(self) -> None:
        normalized = validate_report_analysis(thai_analysis())
        self.assertTrue(THAI_RANGE.search(normalized["title"]))
        self.assertTrue(THAI_RANGE.search(normalized["executiveSummary"]))
        self.assertTrue(THAI_RANGE.search(normalized["findings"][0]["claim"]))

    def test_thai_survives_the_json_round_trip_as_utf8(self) -> None:
        normalized = validate_report_analysis(thai_analysis())
        raw = json.dumps(normalized, indent=2, ensure_ascii=False, sort_keys=True)
        self.assertNotIn("\\u0e", raw.lower(), "Thai was escaped instead of written as UTF-8")
        self.assertEqual(json.loads(raw)["title"], normalized["title"])

    def test_thai_prose_stays_in_composed_form(self) -> None:
        """Decomposed tone marks render inconsistently across fonts."""
        analysis = thai_analysis()
        for value in (analysis["title"], analysis["executiveSummary"]):
            self.assertTrue(unicodedata.is_normalized("NFC", value))

    def test_machine_ids_stay_ascii_kebab_case(self) -> None:
        """Finding ids are identifiers, not prose — Thai must be rejected there."""
        self.assertIsNone(FINDING_ID.fullmatch("โมเมนตัม"))
        self.assertIsNotNone(FINDING_ID.fullmatch("momentum-decay-10d"))

        analysis = thai_analysis()
        analysis["findings"][0]["id"] = "โมเมนตัม"
        with self.assertRaises(Exception):
            validate_report_analysis(analysis)


if __name__ == "__main__":
    unittest.main()
