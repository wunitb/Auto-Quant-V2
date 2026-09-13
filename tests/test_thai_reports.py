"""Thai-language support across the report contract.

The AutoQuant desk works in English internally, but report prose is authored in
the caller's language. These tests pin the layers that silently mangle Thai:
schema validation, UTF-8 round-tripping, and the ASCII-only machine ids.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unicodedata
import unittest
from copy import deepcopy
from contextlib import ExitStack
from unittest.mock import patch

import jsonschema

from autoquant.reports import (
    FINDING_ID,
    REPORT_ANALYSIS_JSON_SCHEMA,
    REPORT_ANALYSIS_KIND,
    SCHEMA_VERSION,
    _render_markdown,
    load_report,
    publish_report,
    validate_report_analysis,
)
from autoquant.sessions import load_session, start_session
from autoquant.studies import create_study
from autoquant.workspace import AutoQuantValidationError
from tests.study_helpers import make_project, request_definition, study_definition

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


def rendering_report() -> dict:
    """Fixed renderer input, independent of clocks and generated identities."""
    request = request_definition()
    request.update(question="สัญญาณยังใช้ได้หรือไม่", decisionContext="ประเมินก่อนตัดสินใจ")
    return {
        "id": "report-example",
        "request": request,
        "analysis": thai_analysis(),
        "sessionId": "session-example",
        "brief": {"id": "brief-example"},
        "harness": {"id": "test-harness", "version": "1.0.0", "commit": "abc123"},
        "evidence": {
            "session": {
                "baseline": {"runId": "run-0001", "metric": "net_sharpe", "value": -1.25},
                "leader": {"runId": "run-0001", "metric": "net_sharpe", "value": -1.25},
                "studyId": "test-study",
                "locks": {"datasetHash": "a" * 64, "dependencyHash": "b" * 64},
            },
            "runs": [{"id": "run-0001", "metrics": {
                "research_horizon": {
                    "primaryForwardBars": 10,
                    "diagnosticForwardBars": [5, 20],
                    "source": {"horizonPolicy": "request.horizonPolicy"},
                },
            }}],
            "experiments": [],
            "campaigns": [],
            "selectionIntegrity": {
                "selectionMetric": "net_sharpe",
                "selectionSplit": "validation",
                "candidateTrials": 1,
                "evaluatedRuns": 1,
                "verdicts": {"KEEP": 0, "REVERT": 0, "CRASH": 0},
                "testRole": "audit-only",
                "testEntersSelection": False,
                "externalHoldoutRequired": True,
                "warning": "ต้องทดสอบกับข้อมูลช่วงอื่น",
            },
        },
    }


class ThaiReportContractTests(unittest.TestCase):
    def test_language_contract_and_machine_fields(self) -> None:
        original = thai_analysis()
        self.assertEqual(validate_report_analysis(original), original)
        self.assertNotIn("language", REPORT_ANALYSIS_JSON_SCHEMA["required"])
        self.assertEqual(REPORT_ANALYSIS_JSON_SCHEMA["properties"]["language"]["default"], "en")
        for language in ("en", "th"):
            with self.subTest(language=language):
                analysis = {**original, "language": language}
                jsonschema.validate(analysis, REPORT_ANALYSIS_JSON_SCHEMA)
                normalized = validate_report_analysis(analysis)
                self.assertEqual(normalized.pop("language"), language)
                self.assertEqual(normalized, original)

    def test_unsupported_language_fails_validation(self) -> None:
        for language in ("ja", "TH", "th-TH", "", None, 1, [], {}):
            with self.subTest(language=language):
                analysis = {**thai_analysis(), "language": language}
                with self.assertRaises(AutoQuantValidationError) as raised:
                    validate_report_analysis(analysis)
                issue = raised.exception.issues[0]
                self.assertEqual(issue.path, "report-analysis/language")
                self.assertEqual(issue.code, "schema.choice")
                self.assertIn("en (English) or th (Thai)", issue.message)
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(analysis, REPORT_ANALYSIS_JSON_SCHEMA)

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


class ThaiReportRenderingTests(unittest.TestCase):
    def test_frozen_leader_sections_receive_thai_headings(self) -> None:
        report = rendering_report()
        report["analysis"]["language"] = "th"
        report["evidence"]["leaderDecisionSupport"] = {}
        headings = {
            "factor_input_availability": "ความพร้อมของข้อมูล Factor",
            "factor_qualification": "ผลการประเมินคุณสมบัติ Factor",
            "factor_components": "องค์ประกอบ Factor",
            "mechanical_decision": "การตัดสินใจตามกฎ",
            "sizing_anatomy": "รายละเอียดการกำหนดขนาดสถานะ",
            "diversification_stress": "การทดสอบภาวะกดดันด้านการกระจายความเสี่ยง",
            "strategy_viability": "ความเป็นไปได้ในการใช้กลยุทธ์",
            "signal_monetization": "การแปลงสัญญาณเป็นผลตอบแทน",
            "rl_factor_fusion_diagnosis": "ผลวิเคราะห์การผสาน Factor ของ RL",
        }
        with ExitStack() as stack:
            for helper in headings:
                stack.enter_context(patch(
                    f"autoquant.reports.{helper}_markdown_lines",
                    side_effect=lambda support, *, heading: [heading, ""],
                ))
            rendered = _render_markdown(report)
        for heading in headings.values():
            self.assertIn(f"## {heading}", rendered)
        self.assertEqual(rendered.count("จาก Run ผู้นำที่ตรึงไว้"), 9)
        self.assertNotIn("## Frozen leader-Run", rendered)

    def test_omitted_language_preserves_original_english_bytes(self) -> None:
        # Captured with the pre-language renderer, including its final newline.
        report = rendering_report()
        original_hash = "beed3fa71d7c2df09f342b25229004bd83e2cbc63b1eaea210b1a1d2f9369884"
        rendered = _render_markdown(report).encode("utf-8")
        self.assertEqual(hashlib.sha256(rendered).hexdigest(), original_hash)
        report["analysis"]["language"] = "en"
        self.assertEqual(_render_markdown(report).encode("utf-8"), rendered)

    def test_thai_scaffolding_preserves_prose_and_machine_evidence(self) -> None:
        report = rendering_report()
        # Text resembling scaffolding inside authored prose must never be replaced.
        report["analysis"]["executiveSummary"] += "\n## Findings\n**Question:** 12bps"
        english = _render_markdown(report)
        report["analysis"]["language"] = "th"
        before = deepcopy(report)
        thai = _render_markdown(report)
        self.assertEqual(report, before)
        self.assertEqual(re.findall(r"`[^`]*`", thai), re.findall(r"`[^`]*`", english))
        self.assertEqual(re.findall(r"-?\d+(?:\.\d+)?", thai), re.findall(r"-?\d+(?:\.\d+)?", english))
        self.assertIn(report["analysis"]["executiveSummary"], thai)
        self.assertIn("### momentum-decay-10d", thai)
        self.assertIn("**medium**", thai)
        self.assertIn("net_sharpe=-1.25", thai)
        self.assertIn("10` decision bars", thai)
        for heading in (
            "โจทย์วิจัย", "สรุปสำหรับผู้บริหาร", "สถานะหลักฐาน",
            "ความน่าเชื่อถือของกระบวนการคัดเลือกงานวิจัย", "ข้อค้นพบ",
            "ข้อเสนอแนะ", "ข้อจำกัด", "คำถามที่ยังไม่มีข้อยุติ", "การทำซ้ำและส่งต่องาน",
        ):
            self.assertIn(f"## {heading}\n", thai)
        for label in (
            "คำถาม", "บริบทการตัดสินใจ", "สินทรัพย์", "ทิศทาง / กรอบเวลา",
            "ระยะคาดการณ์ล่วงหน้าเชิงตัวเลข", "แหล่งที่มาที่ผู้ขอระบุ",
        ):
            self.assertIn(f"**{label}:**", thai)
        self.assertIn(
            "> ขอบเขตอำนาจ: ใช้เป็นข้อมูลเชิงปริมาณประกอบการตัดสินใจเท่านั้น รายงานนี้ไม่ใช่คำสั่งซื้อขาย\n"
            "> ไม่ใช่คำยืนยันจากโบรกเกอร์ และไม่ได้รับการยืนยันว่ามีต้นทางจาก OpenAlice",
            thai,
        )
        self.assertNotIn("> Authority:", thai)

    def test_thai_empty_sections_and_recommendations(self) -> None:
        report = rendering_report()
        analysis = report["analysis"]
        analysis.update(language="th", limitations=[], unresolvedQuestions=[])
        report["evidence"]["runs"][0]["metrics"] = {}
        rendered = _render_markdown(report)
        self.assertIn("ไม่มีข้อเสนอแนะให้ดำเนินการ", rendered)
        self.assertIn("ไม่ได้ระบุข้อจำกัดเพิ่มเติม", rendered)
        self.assertIn("ไม่ได้ระบุคำถามที่ยังไม่มีข้อยุติ", rendered)
        self.assertIn("**ระยะคาดการณ์ล่วงหน้าเชิงตัวเลข:**", rendered)
        analysis["recommendations"] = [{
            "action": "ตรวจสอบข้อมูลเพิ่ม", "rationale": "หลักฐานยังไม่เพียงพอ",
            "conditions": [], "evidenceRefs": analysis["findings"][0]["evidenceRefs"],
        }]
        rendered = _render_markdown(report)
        self.assertIn("1. **ตรวจสอบข้อมูลเพิ่ม**", rendered)
        self.assertIn("เงื่อนไข: ไม่ได้ระบุ", rendered)
        self.assertIn("หลักฐาน: `run:run-0001#runs/run-0001/metrics.json`", rendered)

    def test_thai_publication_round_trips_without_rewriting_prior_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, project = make_project(directory)
            create_study(project, study_definition())
            session = start_session(project, "factor-quality", request=request_definition())
            analysis = thai_analysis()
            analysis["findings"][0]["evidenceRefs"] = [{
                "kind": "run", "id": session.manifest["baseline"]["runId"],
                "artifactPath": "artifacts/report.json",
            }]
            prior = publish_report(project, session.manifest["id"], analysis)
            prior_bytes = {p.name: p.read_bytes() for p in prior.root_dir.iterdir()}
            analysis["language"] = "th"
            current = publish_report(project, session.manifest["id"], analysis)
            session = load_session(project, session.manifest["id"])
            loaded = load_report(project, session, current.report["id"])
            self.assertEqual(loaded.analysis, analysis)
            self.assertIn("## ข้อค้นพบ", (loaded.root_dir / "report.md").read_text())
            for key in ("runs", "session"):
                self.assertEqual(loaded.report["evidence"][key], prior.report["evidence"][key])
            self.assertEqual(loaded.report["request"], prior.report["request"])
            self.assertEqual(loaded.report["tradingAuthority"], "none")
            load_report(project, session, prior.report["id"])
            self.assertEqual(
                {p.name: p.read_bytes() for p in prior.root_dir.iterdir()}, prior_bytes,
            )


if __name__ == "__main__":
    unittest.main()
