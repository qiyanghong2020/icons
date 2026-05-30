# Icons

Codex skill for finding, previewing, and downloading editable SVG icons for
scientific figures, biomedical diagrams, flowcharts, and UI-style figure
elements.

The skill is invoked as `$icons`.

## What It Does

- Searches and downloads SVG icons into the current project.
- Generates a `preview.html` page for quick visual review.
- Generates `LICENSES.tsv` with source, license, author, and provenance metadata.
- Combines several icon sources behind one workflow:
  - BioIcons for biology, chemistry, immunology, genomics, oncology, cell culture, and lab apparatus.
  - Tabler Icons for consistent 24x24 linear flowchart and UI symbols.
  - Iconify for broad open-source icon coverage.
  - Svg/icons CLI as an optional prompt-style recommendation workflow.

This skill does not generate new icons from scratch and does not replace plotting
tools for statistical figures.

## Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/qiyanghong2020/icons.git "${CODEX_HOME:-$HOME/.codex}/skills/icons"
```

If it is already installed, update it with:

```bash
git -C "${CODEX_HOME:-$HOME/.codex}/skills/icons" pull
```

## Use With Codex

Example prompts:

```text
Use $icons to download DNA, antibody, and tumor-cell SVG icons.
Use $icons to find consistent flowchart icons for warnings, targets, and charts.
Use $icons to search BioIcons for microscope and single-cell assets.
```

## Command Line

Run the script from the project directory where you want the icon files:

```bash
ICONS_SCRIPT="${CODEX_HOME:-$HOME/.codex}/skills/icons/scripts/icons.py"

python3 "$ICONS_SCRIPT" --list-presets
python3 "$ICONS_SCRIPT" --provider bioicons --preset gene --out gene_icons
python3 "$ICONS_SCRIPT" --provider bioicons --preset antibody oncology --out bioicons_set
python3 "$ICONS_SCRIPT" --provider tabler --preset flow chart safety --out flow_icons
python3 "$ICONS_SCRIPT" --provider all --search "antibody" --limit 20
python3 "$ICONS_SCRIPT" --provider bioicons --search "immune cell" --limit 20
python3 "$ICONS_SCRIPT" --provider tabler --search "warning" --download-search 5 --out warning_icons
python3 "$ICONS_SCRIPT" --icons bioicons:DNA_double_helix mdi:dna lucide:dna --out selected_icons
```

The script requires Python 3 and network access.
`--download-search N` downloads N total candidates from the printed search
results in provider priority order.

## Providers

| Provider | Best For | Notes |
| --- | --- | --- |
| `auto` | Default scientific workflow | Searches/downloads BioIcons, then Tabler, then Iconify |
| `bioicons` | Biomedical and life-science illustrations | Per-icon license and author metadata |
| `tabler` | Flowchart, warning, target, chart, shield, clipboard, and UI symbols | MIT-licensed Tabler icons via Iconify |
| `iconify` | Broad open-source icon coverage | Each icon set has its own license |
| `svgicons` | Prompt-style recommendation and Pro workflows | Requires local `svgicons` CLI; some actions may require a Pro token |
| `all` | Broad exploration | Searches BioIcons, Tabler, Iconify, and Svg/icons only when the CLI is installed |

## Presets

BioIcons-oriented presets:

```text
gene dna cell mutation virus lab antibody oncology
```

Tabler-oriented presets:

```text
flow ui chart lab-linear safety
```

Iconify-oriented presets:

```text
gene dna cell mutation virus lab
```

Use `scripts/icons.py --list-presets` to see the exact icon names in each preset.

## Output

Each download writes:

```text
<output>/
  *.svg
  LICENSES.tsv
  preview.html
```

Keep `LICENSES.tsv` with any figure source files. It is the provenance record for
the downloaded icons.

## Svg/icons CLI

The optional Svg/icons CLI can be used for prompt-style recommendations:

```bash
npm install -g @svgicons-com/cli
python3 "$ICONS_SCRIPT" --recommend "biomedical workflow with DNA, antibody, immune cell, cancer cell and validation icons" --limit 12
python3 "$ICONS_SCRIPT" --pick "microscope" --out icons
```

Raw SVG downloads, collections, exports, or license manifests may require Svg/icons
Pro access.

## Licensing Notes

Downloaded icons keep their original source licenses.

- BioIcons uses per-icon licenses such as CC0, MIT, CC-BY, and CC-BY-SA.
- Tabler Icons are MIT-licensed.
- Iconify is a delivery framework; each Iconify icon set has its own license.
- CC-BY and CC-BY-SA assets may require attribution or share-alike handling.

For papers, posters, and thesis figures, prefer CC0, MIT, Apache-2.0, or ISC
assets when suitable, and preserve attribution metadata for anything that
requires it.
