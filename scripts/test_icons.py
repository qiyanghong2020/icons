#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("icons.py")
SPEC = importlib.util.spec_from_file_location("icons_skill", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {MODULE_PATH}")
icons = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = icons
SPEC.loader.exec_module(icons)


class IconsScriptTests(unittest.TestCase):
    def test_provider_all_skips_svgicons_when_missing(self) -> None:
        with patch.object(icons.shutil, "which", return_value=None):
            self.assertEqual(icons.provider_set("all"), {"bioicons", "iconify", "tabler"})

    def test_provider_all_includes_svgicons_when_installed(self) -> None:
        with patch.object(icons.shutil, "which", return_value="/usr/local/bin/svgicons"):
            self.assertEqual(icons.provider_set("all"), {"bioicons", "iconify", "tabler", "svgicons"})

    def test_bioicons_search_expands_common_biomedical_terms(self) -> None:
        entries = {
            "nk-cell": {"category": "blood immunology", "license": "cc-0", "author": "BioIcons"},
            "antibody": {"category": "blood immunology", "license": "cc-0", "author": "BioIcons"},
            "cancerous-cell-1": {"category": "oncology", "license": "cc-0", "author": "BioIcons"},
        }

        results = icons.search_bioicons("immune cell", 5, entries)

        self.assertIn("nk-cell", results[:2])
        self.assertIn("antibody", results)

    def test_tabler_search_uses_aliases(self) -> None:
        with patch.object(icons, "tabler_icon_names", return_value=["alert-triangle", "chart-bar", "bell"]):
            self.assertEqual(icons.search_tabler("warning", 3)[0], "tabler:alert-triangle")

    def test_download_search_limit_is_total_not_per_provider(self) -> None:
        candidates = [
            ("bioicons", "antibody"),
            ("bioicons", "antibody-1"),
            ("iconify", "pinhead:antibody"),
            ("iconify", "healthicons:antibody"),
        ]

        selected_bioicons, selected_iconify = icons.split_download_candidates(candidates, 2)

        self.assertEqual(selected_bioicons, ["antibody", "antibody-1"])
        self.assertEqual(selected_iconify, [])

    def test_write_licenses(self) -> None:
        item = icons.DownloadedIcon(
            provider="bioicons",
            icon_id="bioicons:DNA_double_helix",
            file_name="bioicons__DNA_double_helix.svg",
            collection="genomics",
            license_name="cc-0",
            license_url="https://creativecommons.org/publicdomain/zero/1.0/",
            author="BioIcons",
            source_url="https://bioicons.com/icons/DNA_double_helix",
        )

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            icons.write_licenses(out_dir, [item])
            content = (out_dir / "LICENSES.tsv").read_text(encoding="utf-8")

        self.assertIn("provider\ticon\tfile", content)
        self.assertIn("bioicons:DNA_double_helix", content)


if __name__ == "__main__":
    unittest.main()
