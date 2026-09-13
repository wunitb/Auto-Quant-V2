from __future__ import annotations

import re
import unittest
from pathlib import Path


CSS = (Path(__file__).parents[1] / "autoquant" / "studio_assets" / "studio.css").read_text()


def rule(selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^{{}}]*)\}}", CSS, re.DOTALL)
    if match is None:
        raise AssertionError(f"missing Studio CSS rule: {selector}")
    return match.group(1)


class StudioTypographyTests(unittest.TestCase):
    def test_declares_the_approved_readable_roles(self) -> None:
        for declaration in (
            "--type-micro: 10px",
            "--type-meta: 11px",
            "--type-data: 12px",
            "--type-body: 13px",
            "--leading-data: 19px",
            "--leading-body: 21px",
        ):
            self.assertIn(declaration, CSS)

    def test_keeps_authored_font_declarations_out_of_the_old_tiny_range(self) -> None:
        declarations = re.findall(r"(?:font-size|font)\s*:[^;]+;", CSS)
        tiny = [
            declaration
            for declaration in declarations
            if any(float(value) < 13 for value in re.findall(r"([0-9]+(?:\.[0-9]+)?)px", declaration))
        ]
        self.assertEqual(tiny, [])

    def test_report_copy_uses_body_and_data_roles(self) -> None:
        for selector in (
            ".hero-copy p",
            ".decision-brief > p",
            ".research-move-hypothesis",
            ".research-move-rationale",
            ".handoff-card p",
            ".catalog-card p",
            ".inspector-section p",
        ):
            block = rule(selector)
            self.assertIn("var(--type-body)", block)
            self.assertIn("var(--leading-body)", block)

        proof = rule(".report-decision-proof")
        self.assertIn("var(--type-data)", proof)
        self.assertIn("var(--leading-data)", proof)

    def test_tables_use_readable_data_rows_and_keep_scroll_ownership(self) -> None:
        for selector in (
            ".factor-table",
            ".rl-incremental-table > div",
            ".rl-behavior-table > div",
            ".sizing-row",
            ".mechanical-row",
            ".position-row",
            ".decision-table",
        ):
            block = rule(selector)
            self.assertIn("var(--type-data)", block)
            self.assertIn("var(--leading-data)", block)

        self.assertIn("overflow-x: auto", rule(".factor-table-wrap"))

    def test_preserves_existing_display_heading_sizes(self) -> None:
        self.assertIn("font-size: clamp(27px, 2.7vw, 38px)", rule(".hero-copy h1"))
        self.assertIn("font-size: 17px", rule(".decision-brief h2"))
        self.assertIn("font-size: 13px", rule(".handoff-card h3"))

    def test_declares_thai_faces_so_thai_prose_does_not_fall_back_arbitrarily(
        self,
    ) -> None:
        root = rule(":root")
        for face in ("Noto Sans Thai", "IBM Plex Sans Thai", "Thonburi"):
            self.assertIn(face, root)
        # Latin must still resolve to Inter first.
        self.assertLess(root.index("Inter"), root.index("Noto Sans Thai"))

    def test_leading_clears_stacked_thai_tone_marks(self) -> None:
        """Thai stacks a vowel and a tone mark above the base glyph.

        Below ~1.5 the marks clip against the line above, so every role that
        carries model-authored prose has to keep that headroom.
        """
        roles = {"--type-data": "--leading-data", "--type-body": "--leading-body"}
        root = rule(":root")
        for size_var, leading_var in roles.items():
            size = float(re.search(rf"{size_var}: ([0-9.]+)px", root).group(1))
            leading = float(re.search(rf"{leading_var}: ([0-9.]+)px", root).group(1))
            self.assertGreaterEqual(
                leading / size,
                1.5,
                f"{leading_var}/{size_var} = {leading / size:.2f}, clips Thai",
            )

        for selector in (
            ".hero-copy h1",
            ".decision-brief h2",
            ".research-move h3",
            ".workspace-context > strong",
        ):
            block = rule(selector)
            ratio = float(re.search(r"line-height: ([0-9.]+)\s*;", block).group(1))
            self.assertGreaterEqual(
                ratio, 1.2, f"{selector} line-height {ratio} clips Thai tone marks"
            )


if __name__ == "__main__":
    unittest.main()
