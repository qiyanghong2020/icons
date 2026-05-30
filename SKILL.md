---
name: icons
description: Find, preview, and download editable SVG icons for biomedical, scientific, flowchart, and UI diagrams from BioIcons, Tabler Icons, Iconify, and optional Svg/icons CLI. Use when Codex needs icon assets for English or Chinese biomedical keywords such as genes, DNA/RNA, cells, antibodies, immune cells, cancer, mutations, viruses, lab equipment, pathways, mechanisms, warnings, targets, charts, shields, clipboards, thesis figures, papers, posters, presentations, or UI diagrams, especially when the user wants reusable local SVG files plus license/provenance metadata.
---

# Icons

## Overview

Use this skill to search and download publication-friendly SVG icon assets into the current project. BioIcons is preferred for life-science concepts; Tabler Icons is preferred for consistent 24x24 linear flowchart/UI symbols; Iconify is used for broad open-source icon coverage; Svg/icons CLI is optional for prompt-style recommendations and Pro workflows.

## Quick Start

Resolve `scripts/icons.py` relative to this skill directory and run it with the target project as the working directory so output files land in that project.

```bash
python3 /path/to/skills/icons/scripts/icons.py --list-presets
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --preset gene --out gene_icons
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --preset antibody oncology --out bioicons_set
python3 /path/to/skills/icons/scripts/icons.py --provider tabler --preset flow chart safety --out flow_icons
python3 /path/to/skills/icons/scripts/icons.py --provider all --search "antibody" --limit 20
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --search "抗体" --limit 10
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --search "immune cell" --limit 20
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --search "scRNA-seq" --limit 10
python3 /path/to/skills/icons/scripts/icons.py --provider tabler --search "warning" --download-search 5 --out warning_icons
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --search "microscope" --download-search 6 --out microscope_icons
python3 /path/to/skills/icons/scripts/icons.py --icons bioicons:DNA_double_helix mdi:dna lucide:dna --out selected_icons
```

The script writes SVG files, `LICENSES.tsv`, and `preview.html`.

## Provider Choice

- Use `--provider auto` by default. It searches/downloads BioIcons first, then Tabler, then Iconify.
- Use `--provider bioicons` for biology, chemistry, molecular biology, genomics, immunology, oncology, cell culture, and lab apparatus.
- Use `--provider tabler` for uniform linear process symbols: arrows, warnings, targets, charts, clipboards, shields, search, settings, and simple lab/UI icons.
- Use `--provider iconify` for broad UI/general icons or when a BioIcons result is too illustrative.
- Use `--provider all` when exploring broadly; it skips Svg/icons unless the CLI is installed.
- Use `--provider svgicons`, `--recommend`, or `--pick` only when the local `svgicons` CLI is installed. Some Svg/icons workflows require a Pro API token.

## Workflow

1. Start with a preset when the request matches one: `gene`, `dna`, `cell`, `mutation`, `virus`, `lab`, `antibody`, `oncology`, `flow`, `ui`, `chart`, `lab-linear`, or `safety`.
2. Search before downloading when the concept is specific. English, common Chinese terms, and scientific abbreviations are supported, including `抗体`, `免疫细胞`, `癌细胞`, `甲基化`, `scRNA-seq`, `RNA-seq`, and `ATAC-seq`:

```bash
python3 /path/to/skills/icons/scripts/icons.py --provider bioicons --search "fibroblast" --search "single cell" --limit 20
```

3. Download reviewed candidates explicitly:

```bash
python3 /path/to/skills/icons/scripts/icons.py --bioicons fibroblast-1 fibroblast-2 DNA_double_helix --out figure_icons
python3 /path/to/skills/icons/scripts/icons.py --icons tabler:alert-triangle tabler:target tabler:chart-bar --out flow_icons
```

4. Use `--download-search N` only for exploration. It downloads N total candidates from the printed search results in provider priority order. Search results can include visually inconsistent or semantically loose matches.
5. Open or mention `preview.html` so the user can inspect the downloaded set.
6. If a query is a data plot concept such as Kaplan-Meier, forest plot, or volcano plot, prefer a plotting workflow rather than downloading an icon placeholder.

## Svg/icons CLI

If `svgicons` is installed, use it for prompt-style recommendation:

```bash
python3 /path/to/skills/icons/scripts/icons.py --recommend "biomedical workflow with DNA, antibody, immune cell, cancer cell and validation icons" --limit 12
python3 /path/to/skills/icons/scripts/icons.py --pick "microscope" --out icons
```

If the command fails because the CLI is missing, tell the user to install it with `npm install -g @svgicons-com/cli`. If raw SVG download, collections, exports, or license manifests require Pro access, state that clearly.

## Licensing

Always preserve `LICENSES.tsv`. BioIcons icons have per-icon licenses and authors. Tabler Icons are MIT-licensed through the Iconify `tabler:` collection. Iconify's framework license does not cover every icon; each icon set has its own license.

Prefer permissive icons (`CC0`, `MIT`, `Apache-2.0`, `ISC`) for papers when suitable. `CC-BY-*` and `CC-BY-SA-*` assets may require attribution or share-alike obligations; call that out in the final response when present.

## Figure Guidance

Use BioIcons SVGs for biological entities and Tabler SVGs for diagram structure, state, process, and interface symbols. Do not present generic icons as exact biological structures. For data plots, statistics, Kaplan-Meier curves, forest plots, or full figure panels, use plotting or drawing workflows instead.
