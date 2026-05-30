# Icons

Codex skill for finding, previewing, and downloading editable SVG icons for
scientific figures, biomedical diagrams, flowcharts, posters, presentations, and
paper illustrations.

The skill is invoked as `$icons`.

## What It Does

- Searches and downloads reusable SVG icons into the current project.
- Supports English and common Chinese biomedical keywords.
- Writes a `preview.html` page for visual review.
- Writes `LICENSES.tsv` with source, license, author, and provenance metadata.
- Combines several icon sources behind one workflow:
  - BioIcons for biology, chemistry, immunology, genomics, oncology, cell types, and lab apparatus.
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

No login is required for normal BioIcons, Tabler, or Iconify searching and
downloading.

## Use With Codex

Example prompts:

```text
Use $icons to download DNA, antibody, and tumor-cell SVG icons.
Use $icons to find consistent flowchart icons for warnings, targets, and charts.
Use $icons to search BioIcons for microscope and single-cell assets.
Use $icons to search Chinese terms such as 抗体, 免疫细胞, 癌细胞, 甲基化, or 警告.
Use $icons to download scRNA-seq, RNA-seq, ATAC-seq, qPCR, and western blot icons.
```

## Command Line Quick Start

Run the script from the project directory where you want the icon files:

```bash
ICONS_SCRIPT="${CODEX_HOME:-$HOME/.codex}/skills/icons/scripts/icons.py"

python3 "$ICONS_SCRIPT" --provider bioicons --search "抗体" --limit 10
python3 "$ICONS_SCRIPT" --provider bioicons --search "immune cell" --limit 20
python3 "$ICONS_SCRIPT" --provider bioicons --search "scRNA-seq" --limit 10
python3 "$ICONS_SCRIPT" --provider tabler --search "warning" --download-search 5 --out warning_icons
python3 "$ICONS_SCRIPT" --icons bioicons:DNA_double_helix tabler:alert-triangle --out selected_icons
```

The script requires Python 3 and network access. `--download-search N` downloads
N total candidates from the printed search results in provider priority order.

## Common Workflows

List curated presets:

```bash
python3 "$ICONS_SCRIPT" --list-presets
```

Download a focused BioIcons set:

```bash
python3 "$ICONS_SCRIPT" --provider bioicons --preset gene antibody oncology --out bioicons_set
```

Download a consistent linear flowchart set:

```bash
python3 "$ICONS_SCRIPT" --provider tabler --preset flow chart safety --out flow_icons
```

Search first, then explicitly download reviewed candidates:

```bash
python3 "$ICONS_SCRIPT" --provider bioicons --search "fibroblast" --search "single cell" --limit 20
python3 "$ICONS_SCRIPT" --bioicons fibroblast-1 fibroblast-2 DNA_double_helix --out figure_icons
```

Download explicit BioIcons and Iconify/Tabler icons together:

```bash
python3 "$ICONS_SCRIPT" --icons bioicons:DNA_double_helix mdi:dna tabler:target --out selected_icons
```

## Keyword Support

The search layer recognizes common English terms, Chinese terms, and scientific
abbreviations. Examples include:

```text
基因 细胞 免疫细胞 抗体 癌细胞 肿瘤细胞 成纤维细胞
显微镜 病毒 甲基化 测序 单细胞 警告 验证 柱状图
T cell B cell NK cell macrophage dendritic cell fibroblast
scRNA-seq RNA-seq ATAC-seq m6A qPCR western blot flow cytometry
CRISPR apoptosis proliferation heatmap
```

Data plot concepts such as `Kaplan-Meier`, `forest plot`, `volcano plot`, and
`生存曲线` print a reminder instead of returning loose icon matches. Those are
better handled with plotting tools.

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

## Accounts And Limits

Normal use does not require logging in.

- BioIcons is accessed through public GitHub raw/API endpoints. Metadata is cached locally for 24 hours to reduce repeated requests.
- Tabler and Iconify are accessed through the public Iconify API. Routine paper-figure usage should be fine, but avoid large automated scraping runs.
- Svg/icons CLI is optional. Some recommendation, raw SVG download, collection, export, or manifest workflows may require a Pro API token.

If a public API temporarily rate-limits you, wait and rerun the command. For very
large batches, prefer downloading reviewed icon IDs explicitly rather than
repeating broad searches.

## Svg/icons CLI

The optional Svg/icons CLI can be used for prompt-style recommendations:

```bash
npm install -g @svgicons-com/cli
python3 "$ICONS_SCRIPT" --recommend "biomedical workflow with DNA, antibody, immune cell, cancer cell and validation icons" --limit 12
python3 "$ICONS_SCRIPT" --pick "microscope" --out icons
```

## Licensing Notes

Downloaded icons keep their original source licenses.

- BioIcons uses per-icon licenses such as CC0, MIT, CC-BY, and CC-BY-SA.
- Tabler Icons are MIT-licensed.
- Iconify is a delivery framework; each Iconify icon set has its own license.
- CC-BY and CC-BY-SA assets may require attribution or share-alike handling.

For papers, posters, and thesis figures, prefer CC0, MIT, Apache-2.0, or ISC
assets when suitable, and preserve attribution metadata for anything that
requires it.

## Troubleshooting

- `No icons downloaded`: search only prints candidates. Add `--download-search N`, `--preset`, `--bioicons`, or `--icons`.
- Results look visually inconsistent: use `--provider bioicons` for biological entities and `--provider tabler` for flowchart symbols.
- A statistical figure term returns a note: use a plotting workflow for the chart itself, then use icons only for labels or diagram elements.
- Svg/icons command fails: install it with `npm install -g @svgicons-com/cli`, and check whether the workflow needs Pro access.

## Development

Run local checks from the skill directory:

```bash
python3 -m py_compile scripts/icons.py scripts/test_icons.py
python3 scripts/test_icons.py
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "${CODEX_HOME:-$HOME/.codex}/skills/icons"
```
