#!/usr/bin/env python3
"""Search and download science-friendly SVG icons from BioIcons, Iconify, and Tabler."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ICONIFY_API_BASE = "https://api.iconify.design"
BIOICONS_RAW_BASE = "https://raw.githubusercontent.com/duerrsimon/bioicons/main"
BIOICONS_META_URL = f"{BIOICONS_RAW_BASE}/static/icons/icons.json"
BIOICONS_AUTHORS_URL = f"{BIOICONS_RAW_BASE}/static/icons/authors.json"
BIOICONS_TREE_URL = "https://api.github.com/repos/duerrsimon/bioicons/git/trees/main?recursive=1"
USER_AGENT = "Codex icons skill"

ICONIFY_PRESETS = {
    "cell": [
        "healthicons:blood-cells",
        "healthicons:blood-cells-outline",
        "pinhead:blood-cells",
        "hugeicons:cells",
        "streamline:bacteria-virus-cells-biology",
        "streamline-color:bacteria-virus-cells-biology",
        "tabler:cell",
        "uil:cell",
    ],
    "gene": [
        "material-symbols:genetics",
        "medical-icon:genetics",
        "mdi:dna",
        "tabler:dna",
        "lucide:dna",
        "hugeicons:dna",
        "ph:dna-duotone",
        "solar:dna-bold-duotone",
        "healthicons:virus-mutation",
        "healthicons:virus-mutation-outline",
    ],
    "dna": [
        "mdi:dna",
        "tabler:dna",
        "lucide:dna",
        "hugeicons:dna",
        "ph:dna",
        "ph:dna-duotone",
        "solar:dna-bold-duotone",
    ],
    "mutation": [
        "healthicons:virus-mutation",
        "healthicons:virus-mutation-outline",
        "covid:mutation-1",
        "covid:mutation-2",
    ],
    "virus": [
        "healthicons:virus",
        "healthicons:virus-outline",
        "healthicons:virus-mutation",
        "streamline:bacteria-virus-cells-biology",
        "streamline-color:bacteria-virus-cells-biology",
    ],
    "lab": [
        "healthicons:microscope",
        "healthicons:microscope-outline",
        "mdi:microscope",
        "tabler:microscope",
        "healthicons:test-tubes",
        "healthicons:test-tubes-outline",
    ],
}

TABLER_PRESETS = {
    "flow": [
        "tabler:arrow-right",
        "tabler:arrow-down",
        "tabler:git-branch",
        "tabler:route",
        "tabler:target",
        "tabler:circle-check",
        "tabler:alert-triangle",
        "tabler:info-circle",
        "tabler:ban",
        "tabler:loader-2",
    ],
    "ui": [
        "tabler:search",
        "tabler:settings",
        "tabler:filter",
        "tabler:download",
        "tabler:upload",
        "tabler:copy",
        "tabler:clipboard",
        "tabler:edit",
        "tabler:trash",
        "tabler:plus",
    ],
    "chart": [
        "tabler:chart-bar",
        "tabler:chart-line",
        "tabler:chart-pie",
        "tabler:chart-scatter",
        "tabler:timeline",
        "tabler:table",
        "tabler:percentage",
        "tabler:sum",
    ],
    "lab-linear": [
        "tabler:flask",
        "tabler:microscope",
        "tabler:test-pipe",
        "tabler:vaccine",
        "tabler:dna",
        "tabler:cell",
        "tabler:stethoscope",
        "tabler:heart",
    ],
    "safety": [
        "tabler:alert-triangle",
        "tabler:exclamation-circle",
        "tabler:shield",
        "tabler:shield-check",
        "tabler:shield-x",
        "tabler:lock",
        "tabler:biohazard",
        "tabler:radioactive",
    ],
}

TABLER_QUERY_ALIASES = {
    "warning": ["alert", "alert-triangle", "exclamation-circle"],
    "danger": ["alert", "alert-triangle", "shield-x"],
    "error": ["alert", "exclamation-circle", "circle-x"],
    "success": ["circle-check", "check"],
    "target": ["target", "focus"],
    "bar chart": ["chart-bar"],
    "line chart": ["chart-line"],
    "scatter": ["chart-scatter"],
    "clipboard": ["clipboard", "copy"],
    "flask": ["flask", "test-pipe"],
    "lab": ["flask", "microscope", "test-pipe"],
}

BIOICONS_PRESETS = {
    "cell": [
        "Animal_cell",
        "simple_cell1",
        "cell_group",
        "redbloodcell",
        "stem_cell_colony",
        "cells_matrix",
        "cell_clumps",
        "cell-complete",
        "nk-cell",
        "dendritic-cell-1",
    ],
    "gene": [
        "DNA_symbolic_extending",
        "CRISPR_Cas9",
        "CRISPR_plasmid",
        "CRISPR_Cas9_expression_vector",
        "sequence_histogram",
        "chromatin-histones",
        "chromatin-structure",
        "plasmid-2",
        "restriction_enzyme",
        "DNA_double_helix",
    ],
    "dna": [
        "DNA_double_helix",
        "DNA",
        "DNA_symbolic_extending",
        "ssDNA-single-stranded",
        "plasmid-2",
        "CRISPR_Cas9_vector",
        "restriction_enzyme",
        "rna",
        "tRNA",
        "mRNA_vaccine-vector",
    ],
    "mutation": [
        "patient_mutant",
        "CRISPR_Cas9",
        "CRISPR_plasmid",
        "CRISPR_Cas9_expression_vector",
        "sequence_histogram",
    ],
    "virus": [
        "SARS-CoV-2",
        "virus-sketch",
        "sars-cov-2-spike-closed",
        "sars-cov-2-spike-open",
        "phage",
        "influenza-virus",
        "hiv-virus",
        "adeno-virus",
    ],
    "lab": [
        "microscope",
        "microscope-cartoon",
        "desktop_electron_microscope",
        "confocal-scanning-laser-microscope-CSLM",
        "centrifuge",
        "spectrophotometer",
        "96_well_plate",
        "CC_dish",
        "T75_flask",
        "flow-cytometer-cell-sorter",
    ],
    "antibody": [
        "antibody",
        "antibody-1",
        "antibody-2",
        "antibody-ligand-1",
        "antibody-radio-tag-1",
        "immunoglobulin-2",
    ],
    "oncology": [
        "tumor",
        "cancerous-cell-1",
        "cancerous-cell-2",
        "cancerous-cell-3",
        "normal-cell-1",
        "carcinoma",
        "angiogenesis",
    ],
}

LICENSE_URLS = {
    "bsd": "https://opensource.org/licenses/BSD-3-Clause",
    "cc-0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc-by-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "cc-by-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-sa-3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "cc-by-sa-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "mit": "https://opensource.org/licenses/MIT",
}


@dataclass(frozen=True)
class DownloadedIcon:
    provider: str
    icon_id: str
    file_name: str
    collection: str
    license_name: str
    license_url: str
    author: str
    source_url: str


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def fetch_json(url: str):
    return json.loads(fetch_bytes(url).decode("utf-8"))


def normalize_text(value: str) -> str:
    return (
        value.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
    )


def unique_in_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def safe_file_part(value: str) -> str:
    return (
        value.replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
    )


def iconify_parts(icon: str) -> tuple[str, str]:
    if ":" not in icon:
        raise ValueError(f"Iconify icon must be prefix:name, got {icon!r}")
    prefix, name = icon.split(":", 1)
    if not prefix or not name:
        raise ValueError(f"Iconify icon must be prefix:name, got {icon!r}")
    return prefix, name


def iconify_file_name(icon: str) -> str:
    prefix, name = iconify_parts(icon)
    return f"iconify__{prefix}__{safe_file_part(name)}.svg"


def bioicons_file_name(icon: str) -> str:
    return f"bioicons__{safe_file_part(icon)}.svg"


def provider_set(provider: str) -> set[str]:
    if provider == "all":
        return {"bioicons", "iconify", "tabler", "svgicons"}
    if provider == "auto":
        return {"bioicons", "tabler", "iconify"}
    return {provider}


def list_presets() -> None:
    print("\n# BioIcons presets")
    for preset, icons in sorted(BIOICONS_PRESETS.items()):
        print(f"\n## {preset}")
        print("\n".join(f"bioicons:{icon}" for icon in icons))
    print("\n# Iconify presets")
    for preset, icons in sorted(ICONIFY_PRESETS.items()):
        print(f"\n## {preset}")
        print("\n".join(icons))
    print("\n# Tabler presets")
    for preset, icons in sorted(TABLER_PRESETS.items()):
        print(f"\n## {preset}")
        print("\n".join(icons))


def search_iconify(query: str, limit: int) -> list[str]:
    encoded = urllib.parse.quote(query)
    url = f"{ICONIFY_API_BASE}/search?query={encoded}&limit={limit}"
    data = fetch_json(url)
    return list(data.get("icons", []))


def tabler_icon_names() -> list[str]:
    data = fetch_json(f"{ICONIFY_API_BASE}/collection?prefix=tabler")
    return list(data.get("uncategorized", []))


def score_name_against_query(name: str, query: str) -> int:
    tokens = [token for token in normalize_text(query).split() if token]
    if not tokens:
        return 0
    normalized_name = normalize_text(name)
    if not all(token in normalized_name for token in tokens):
        return 0
    score = sum(10 if token in normalized_name.split() else 4 for token in tokens)
    if normalized_name == normalize_text(query):
        score += 50
    if normalized_name.startswith(normalize_text(query)):
        score += 15
    return score


def search_tabler(query: str, limit: int) -> list[str]:
    names = tabler_icon_names()
    query_variants = [query, *TABLER_QUERY_ALIASES.get(query.lower(), [])]
    scored: list[tuple[int, str]] = []
    for name in names:
        score = max(score_name_against_query(name, variant) for variant in query_variants)
        if score:
            scored.append((score, name))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [f"tabler:{name}" for _, name in scored[:limit]]


def iconify_collection_info(prefixes: list[str]) -> dict:
    if not prefixes:
        return {}
    encoded = urllib.parse.quote(",".join(sorted(set(prefixes))), safe=",")
    url = f"{ICONIFY_API_BASE}/collections?prefixes={encoded}"
    return fetch_json(url)


def download_iconify(icon: str, out_dir: Path, collections: dict) -> DownloadedIcon:
    prefix, name = iconify_parts(icon)
    encoded_prefix = urllib.parse.quote(prefix)
    encoded_name = urllib.parse.quote(name)
    source_url = f"{ICONIFY_API_BASE}/{encoded_prefix}/{encoded_name}.svg?height=none&box=1"
    data = fetch_bytes(source_url)
    if b"<svg" not in data[:300]:
        raise RuntimeError(f"Iconify did not return SVG for {icon}")
    file_name = iconify_file_name(icon)
    (out_dir / file_name).write_bytes(data)

    info = collections.get(prefix, {})
    license_info = info.get("license") or {}
    author = info.get("author") or {}
    return DownloadedIcon(
        provider="iconify",
        icon_id=icon,
        file_name=file_name,
        collection=info.get("name", prefix),
        license_name=license_info.get("spdx") or license_info.get("title", ""),
        license_url=license_info.get("url", ""),
        author=author.get("name", ""),
        source_url=f"https://icon-sets.iconify.design/{prefix}/{name}/",
    )


def bioicons_metadata() -> tuple[list[dict], dict[str, str], dict[str, str]]:
    entries = fetch_json(BIOICONS_META_URL)
    authors = fetch_json(BIOICONS_AUTHORS_URL)
    tree = fetch_json(BIOICONS_TREE_URL)
    paths_by_name: dict[str, str] = {}
    for item in tree.get("tree", []):
        path = item.get("path", "")
        if not path.startswith("static/icons/") or not path.endswith(".svg"):
            continue
        name = Path(path).stem
        paths_by_name.setdefault(name, path)
    return entries, authors, paths_by_name


def bioicons_entry_map() -> dict[str, dict]:
    entries, authors, paths_by_name = bioicons_metadata()
    result: dict[str, dict] = {}
    for entry in entries:
        name = entry.get("name", "")
        if not name:
            continue
        path = paths_by_name.get(name)
        if not path:
            continue
        enriched = dict(entry)
        enriched["path"] = path
        enriched["author_url"] = authors.get(entry.get("author", ""), "")
        result[name] = enriched
    for name, path in paths_by_name.items():
        if name in result:
            continue
        parts = path.split("/")
        if len(parts) < 5:
            continue
        result[name] = {
            "name": name,
            "license": parts[2],
            "category": parts[3],
            "author": parts[4],
            "path": path,
            "author_url": authors.get(parts[4].replace("_", " "), ""),
        }
    return result


def bioicons_source_url(path: str) -> str:
    quoted = urllib.parse.quote(path)
    return f"{BIOICONS_RAW_BASE}/{quoted}"


def bioicons_page_url(icon: str) -> str:
    return f"https://bioicons.com/icons/{urllib.parse.quote(icon)}"


def search_bioicons(query: str, limit: int, entries_by_name: dict[str, dict] | None = None) -> list[str]:
    entries_by_name = entries_by_name or bioicons_entry_map()
    tokens = [token for token in normalize_text(query).split() if token]
    scored: list[tuple[int, str]] = []
    for name, entry in entries_by_name.items():
        haystack = normalize_text(
            " ".join(
                [
                    name,
                    entry.get("category", ""),
                    entry.get("license", ""),
                    entry.get("author", ""),
                ]
            )
        )
        if tokens and not all(token in haystack for token in tokens):
            continue
        score = 0
        normalized_name = normalize_text(name)
        normalized_category = normalize_text(entry.get("category", ""))
        for token in tokens:
            if token in normalized_name:
                score += 10
            if token in normalized_category:
                score += 4
            if token in haystack:
                score += 1
        scored.append((score, name))
    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return [name for _, name in scored[:limit]]


def download_bioicons(icon: str, out_dir: Path, entries_by_name: dict[str, dict]) -> DownloadedIcon:
    if icon not in entries_by_name:
        matches = search_bioicons(icon, 5, entries_by_name)
        hint = f" Close matches: {', '.join(matches)}" if matches else ""
        raise RuntimeError(f"BioIcons icon not found: {icon}.{hint}")
    entry = entries_by_name[icon]
    path = entry["path"]
    source_url = bioicons_source_url(path)
    data = fetch_bytes(source_url)
    if b"<svg" not in data[:500]:
        raise RuntimeError(f"BioIcons did not return SVG for {icon}")
    file_name = bioicons_file_name(icon)
    (out_dir / file_name).write_bytes(data)
    license_name = entry.get("license", "")
    return DownloadedIcon(
        provider="bioicons",
        icon_id=f"bioicons:{icon}",
        file_name=file_name,
        collection=entry.get("category", "BioIcons"),
        license_name=license_name,
        license_url=LICENSE_URLS.get(license_name, ""),
        author=entry.get("author", ""),
        source_url=bioicons_page_url(icon),
    )


def run_svgicons_command(command: list[str]) -> int:
    svgicons = shutil.which("svgicons")
    if not svgicons:
        print(
            "Svg/icons CLI is not installed. Install it with: npm install -g @svgicons-com/cli",
            file=sys.stderr,
        )
        return 127
    process = subprocess.run([svgicons, *command], check=False)
    return process.returncode


def search_svgicons(query: str, limit: int, anonymous: bool) -> int:
    command = ["search", query, "--limit", str(limit)]
    if anonymous:
        command.append("--anonymous")
    return run_svgicons_command(command)


def recommend_svgicons(brief: str, limit: int) -> int:
    return run_svgicons_command(["recommend", brief, "--limit", str(limit)])


def pick_svgicons(query: str, out_dir: Path) -> int:
    return run_svgicons_command(["pick", query, "--download", "--output", str(out_dir)])


def print_search_results(provider: str, queries: list[str], limit: int, anonymous: bool) -> tuple[list[str], list[str]]:
    providers = provider_set(provider)
    bioicons_results: list[str] = []
    iconify_results: list[str] = []
    entries_by_name = bioicons_entry_map() if "bioicons" in providers else {}

    for query in queries:
        if "bioicons" in providers:
            results = search_bioicons(query, limit, entries_by_name)
            bioicons_results.extend(results)
            print(f"\n## BioIcons: {query}")
            print("\n".join(f"bioicons:{icon}" for icon in results) if results else "(no results)")

        if "tabler" in providers:
            results = search_tabler(query, limit)
            iconify_results.extend(results)
            print(f"\n## Tabler: {query}")
            print("\n".join(results) if results else "(no results)")

        if "iconify" in providers:
            results = search_iconify(query, limit)
            iconify_results.extend(results)
            print(f"\n## Iconify: {query}")
            print("\n".join(results) if results else "(no results)")

        if "svgicons" in providers:
            print(f"\n## Svg/icons CLI: {query}")
            search_svgicons(query, limit, anonymous)

    return unique_in_order(bioicons_results), unique_in_order(iconify_results)


def write_licenses(out_dir: Path, downloaded: list[DownloadedIcon]) -> None:
    lines = ["provider\ticon\tfile\tcollection\tlicense\tlicense_url\tauthor\tsource_url"]
    for item in downloaded:
        row = [
            item.provider,
            item.icon_id,
            item.file_name,
            item.collection,
            item.license_name,
            item.license_url,
            item.author,
            item.source_url,
        ]
        lines.append("\t".join(cell.replace("\t", " ") for cell in row))
    (out_dir / "LICENSES.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_preview(out_dir: Path, downloaded: list[DownloadedIcon]) -> None:
    cards = []
    for item in downloaded:
        cards.append(
            f"""      <article class="item">
        <div class="thumb"><img src="{html.escape(item.file_name)}" alt=""></div>
        <p class="name">{html.escape(item.icon_id)}</p>
        <p class="meta">{html.escape(item.collection)}</p>
        <p class="license">{html.escape(item.license_name)}</p>
      </article>"""
        )

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Science SVG Icon Preview</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #202124; background: #f7f8fa; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 28px; }}
    h1 {{ margin: 0 0 18px; font-size: 24px; font-weight: 700; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }}
    .item {{ border: 1px solid #d9dde3; border-radius: 8px; background: #fff; padding: 16px; }}
    .thumb {{
      display: grid; place-items: center; height: 150px; margin-bottom: 12px;
      border: 1px solid #eceff3;
      background:
        linear-gradient(45deg, #f3f4f6 25%, transparent 25%),
        linear-gradient(-45deg, #f3f4f6 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #f3f4f6 75%),
        linear-gradient(-45deg, transparent 75%, #f3f4f6 75%);
      background-position: 0 0, 0 8px, 8px -8px, -8px 0;
      background-size: 16px 16px;
    }}
    img {{ max-width: 104px; max-height: 104px; }}
    .name {{ margin: 0; font-size: 13px; line-height: 1.35; overflow-wrap: anywhere; }}
    .meta {{ margin: 5px 0 0; font-size: 12px; color: #3c4043; overflow-wrap: anywhere; }}
    .license {{ margin: 5px 0 0; font-size: 12px; color: #5f6368; }}
  </style>
</head>
<body>
  <main>
    <h1>Science SVG Icon Preview</h1>
    <section class="grid">
{chr(10).join(cards)}
    </section>
  </main>
</body>
</html>
"""
    (out_dir / "preview.html").write_text(page, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search and download editable SVG icons from BioIcons, Iconify, and optional Svg/icons CLI."
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "bioicons", "iconify", "tabler", "svgicons", "all"],
        default="auto",
        help="Icon source. auto searches/downloads BioIcons, Tabler, then Iconify.",
    )
    parser.add_argument("--search", action="append", default=[], help="Search term. May be repeated.")
    parser.add_argument("--recommend", help="Use Svg/icons CLI to recommend icons for a brief.")
    parser.add_argument("--pick", help="Use Svg/icons CLI to pick and download one icon.")
    parser.add_argument("--limit", type=int, default=30, help="Search results per term.")
    parser.add_argument("--download-search", type=int, default=0, help="Download the first N search results per term.")
    parser.add_argument("--preset", nargs="+", help="Curated preset(s), e.g. gene cell dna antibody oncology.")
    parser.add_argument("--icons", nargs="+", help="Explicit icons. Use bioicons:name or Iconify prefix:name.")
    parser.add_argument("--bioicons", nargs="+", help="Explicit BioIcons names, e.g. DNA_double_helix CRISPR_Cas9.")
    parser.add_argument("--out", default="science_icons", help="Output directory.")
    parser.add_argument("--list-presets", action="store_true", help="List preset names and icons.")
    parser.add_argument("--anonymous", action="store_true", help="Pass --anonymous to Svg/icons CLI search.")
    parser.add_argument("--no-preview", action="store_true", help="Do not generate preview.html.")
    parser.add_argument("--dry-run", action="store_true", help="Print icons that would be downloaded.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_presets:
        list_presets()
        return 0

    out_dir = Path(args.out)
    if args.recommend:
        return recommend_svgicons(args.recommend, args.limit)
    if args.pick:
        out_dir.mkdir(parents=True, exist_ok=True)
        return pick_svgicons(args.pick, out_dir)

    providers = provider_set(args.provider)
    selected_bioicons: list[str] = []
    selected_iconify: list[str] = []

    if args.preset:
        for preset in args.preset:
            known = False
            if "bioicons" in providers and preset in BIOICONS_PRESETS:
                selected_bioicons.extend(BIOICONS_PRESETS[preset])
                known = True
            if "tabler" in providers and preset in TABLER_PRESETS:
                selected_iconify.extend(TABLER_PRESETS[preset])
                known = True
            if "iconify" in providers and preset in ICONIFY_PRESETS:
                selected_iconify.extend(ICONIFY_PRESETS[preset])
                known = True
            if not known:
                print(f"Unknown preset for provider {args.provider}: {preset}", file=sys.stderr)
                return 2

    if args.icons:
        for icon in args.icons:
            if icon.startswith("bioicons:"):
                selected_bioicons.append(icon.split(":", 1)[1])
            else:
                selected_iconify.append(icon)

    if args.bioicons:
        selected_bioicons.extend(args.bioicons)

    if args.search:
        bioicons_results, iconify_results = print_search_results(args.provider, args.search, args.limit, args.anonymous)
        if args.download_search:
            selected_bioicons.extend(bioicons_results[: args.download_search])
            selected_iconify.extend(iconify_results[: args.download_search])

    selected_bioicons = unique_in_order(selected_bioicons)
    selected_iconify = unique_in_order(selected_iconify)

    if not selected_bioicons and not selected_iconify:
        if args.search:
            print("\nNo icons downloaded. Add --download-search N, --preset, --bioicons, or --icons.")
            return 0
        print("Nothing to do. Use --search, --preset, --icons, --bioicons, --recommend, --pick, or --list-presets.", file=sys.stderr)
        return 2

    for icon in selected_iconify:
        iconify_parts(icon)

    if args.dry_run:
        print("\nBioIcons selected:")
        print("\n".join(f"bioicons:{icon}" for icon in selected_bioicons) or "(none)")
        print("\nIconify selected:")
        print("\n".join(selected_iconify) or "(none)")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[DownloadedIcon] = []
    failures: list[tuple[str, str]] = []

    entries_by_name = bioicons_entry_map() if selected_bioicons else {}
    for icon in selected_bioicons:
        try:
            item = download_bioicons(icon, out_dir, entries_by_name)
            downloaded.append(item)
            print(f"downloaded {item.icon_id} -> {out_dir / item.file_name}")
        except Exception as exc:
            failures.append((f"bioicons:{icon}", str(exc)))
            print(f"failed bioicons:{icon}: {exc}", file=sys.stderr)

    collections = iconify_collection_info([iconify_parts(icon)[0] for icon in selected_iconify])
    for icon in selected_iconify:
        try:
            item = download_iconify(icon, out_dir, collections)
            downloaded.append(item)
            print(f"downloaded {item.icon_id} -> {out_dir / item.file_name}")
        except Exception as exc:
            failures.append((icon, str(exc)))
            print(f"failed {icon}: {exc}", file=sys.stderr)

    write_licenses(out_dir, downloaded)
    if not args.no_preview:
        write_preview(out_dir, downloaded)

    print(f"\nWrote {len(downloaded)} SVG file(s) to {out_dir}")
    print(f"Wrote {out_dir / 'LICENSES.tsv'}")
    if not args.no_preview:
        print(f"Wrote {out_dir / 'preview.html'}")

    if failures:
        print("\nFailures:", file=sys.stderr)
        for icon, message in failures:
            print(f"- {icon}: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
