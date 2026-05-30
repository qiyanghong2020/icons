#!/usr/bin/env python3
"""Search and download science-friendly SVG icons from BioIcons, Iconify, and Tabler."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
import time
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
CACHE_DIR = Path.home() / ".cache" / "icons-skill"
CACHE_TTL_SECONDS = 24 * 60 * 60

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
    "警告": ["alert", "alert-triangle", "exclamation-circle"],
    "danger": ["alert", "alert-triangle", "shield-x"],
    "error": ["alert", "exclamation-circle", "circle-x"],
    "success": ["circle-check", "check"],
    "validation": ["circle-check", "checks", "clipboard-check"],
    "validate": ["circle-check", "checks", "clipboard-check"],
    "验证": ["circle-check", "checks", "clipboard-check"],
    "target": ["target", "focus"],
    "靶点": ["target", "focus"],
    "bar chart": ["chart-bar"],
    "柱状图": ["chart-bar"],
    "line chart": ["chart-line"],
    "折线图": ["chart-line"],
    "scatter": ["chart-scatter"],
    "散点图": ["chart-scatter"],
    "clipboard": ["clipboard", "copy"],
    "剪贴板": ["clipboard", "copy"],
    "search": ["search"],
    "搜索": ["search"],
    "settings": ["settings"],
    "设置": ["settings"],
    "download": ["download"],
    "下载": ["download"],
    "pipeline": ["pipeline", "route", "git-branch"],
    "流程": ["pipeline", "route", "git-branch"],
    "pathway": ["route", "git-branch", "network"],
    "通路": ["route", "git-branch", "network"],
    "flask": ["flask", "test-pipe"],
    "lab": ["flask", "microscope", "test-pipe"],
    "实验": ["flask", "microscope", "test-pipe"],
}

BIOICONS_QUERY_ALIASES = {
    "gene": ["DNA", "DNA double helix", "DNA symbolic", "chromosome", "plasmid"],
    "genomics": ["DNA", "DNA double helix", "chromosome", "genome sequencer"],
    "基因": ["DNA", "DNA double helix", "DNA symbolic", "chromosome", "plasmid"],
    "基因组": ["DNA", "DNA double helix", "chromosome", "genome sequencer"],
    "cell": ["Animal cell", "simple cell", "cell group"],
    "细胞": ["Animal cell", "simple cell", "cell group"],
    "immune": ["antibody", "immunoglobulin", "nk-cell", "dendritic-cell", "blood immunology"],
    "immune cell": [
        "nk-cell",
        "dendritic-cell",
        "hematopoetic-stem-cell",
        "lymphoid-stem-cell",
        "myeloid-stem-cell",
        "blood immunology",
        "antibody",
    ],
    "免疫": ["antibody", "immunoglobulin", "nk-cell", "dendritic-cell", "blood immunology"],
    "免疫细胞": [
        "nk-cell",
        "dendritic-cell",
        "hematopoetic-stem-cell",
        "lymphoid-stem-cell",
        "myeloid-stem-cell",
    ],
    "immunology": ["blood immunology", "antibody", "immunoglobulin", "nk-cell", "dendritic-cell"],
    "t cell": ["t_cell_receptor", "t_cell_receptor_ok"],
    "t-cell": ["t_cell_receptor", "t_cell_receptor_ok"],
    "t细胞": ["t_cell_receptor", "t_cell_receptor_ok"],
    "b cell": ["B-cell", "B-cell_cluster"],
    "b-cell": ["B-cell", "B-cell_cluster"],
    "b细胞": ["B-cell", "B-cell_cluster"],
    "nk cell": ["nk-cell"],
    "nk-cell": ["nk-cell"],
    "nk细胞": ["nk-cell"],
    "macrophage": ["macrophage"],
    "巨噬细胞": ["macrophage"],
    "dendritic cell": ["dendritic_cell", "dendritic-cell"],
    "树突状细胞": ["dendritic_cell", "dendritic-cell"],
    "antibody": ["antibody", "immunoglobulin"],
    "抗体": ["antibody", "immunoglobulin"],
    "tumor cell": ["cancerous-cell", "tumor", "oncology"],
    "tumour cell": ["cancerous-cell", "tumor", "oncology"],
    "cancer cell": ["cancerous-cell", "tumor", "oncology"],
    "cancer": ["cancerous-cell", "tumor", "oncology"],
    "癌细胞": ["cancerous-cell", "tumor", "oncology"],
    "肿瘤细胞": ["cancerous-cell", "tumor", "oncology"],
    "肿瘤": ["cancerous-cell", "tumor", "oncology"],
    "fibroblast": ["fibroblast"],
    "成纤维细胞": ["fibroblast"],
    "single cell": ["singlecell", "singlecell droplet", "singlecell clustering", "cell"],
    "single-cell": ["singlecell", "singlecell droplet", "singlecell clustering", "cell"],
    "single cell sequencing": ["singlecell", "singlecell droplet", "singlecell clustering", "sequencing"],
    "scRNA-seq": ["singlecell", "singlecell droplet", "singlecell clustering", "RNA sequencing"],
    "scrna seq": ["singlecell", "singlecell droplet", "singlecell clustering", "RNA sequencing"],
    "单细胞": ["singlecell", "singlecell droplet", "singlecell clustering", "cell"],
    "单细胞测序": ["singlecell", "singlecell droplet", "singlecell clustering", "RNA sequencing"],
    "dna": ["DNA", "DNA double helix", "DNA symbolic", "nucleic acids"],
    "rna": ["rna", "tRNA", "mRNA", "nucleic acids"],
    "dna/rna": ["DNA", "rna", "tRNA", "mRNA", "nucleic acids"],
    "dna rna": ["DNA", "rna", "tRNA", "mRNA", "nucleic acids"],
    "核酸": ["DNA", "rna", "tRNA", "mRNA", "nucleic acids"],
    "crispr": ["CRISPR", "CRISPR Cas9", "CRISPR plasmid"],
    "crispr cas9": ["CRISPR_Cas9", "CRISPR Cas9", "CRISPR plasmid"],
    "基因编辑": ["CRISPR", "CRISPR Cas9", "CRISPR plasmid"],
    "mutation": ["mutation", "CRISPR", "sequence histogram"],
    "突变": ["mutation", "CRISPR", "sequence histogram"],
    "rna-seq": ["library for RNA sequencing", "RNA sequencing", "rna"],
    "rna seq": ["library for RNA sequencing", "RNA sequencing", "rna"],
    "atac-seq": ["Tn5 chromatin ATAC", "Transposase Tn5 ATAC chromatin"],
    "atac seq": ["Tn5 chromatin ATAC", "Transposase Tn5 ATAC chromatin"],
    "sequencing": ["DNA sequencer", "genome sequencer", "sequencing flow cell", "Illumina sequencing"],
    "测序": ["DNA sequencer", "genome sequencer", "sequencing flow cell", "Illumina sequencing"],
    "methylation": ["5-methylcytosine", "5-hydroxymethylcytosine", "chromatin"],
    "甲基化": ["5-methylcytosine", "5-hydroxymethylcytosine", "chromatin"],
    "m6a": ["rna", "mRNA", "methylation"],
    "m6a甲基化": ["rna", "mRNA", "methylation"],
    "rna methylation": ["rna", "mRNA", "methylation"],
    "epigenetics": ["single nucleosome", "chromatin histones", "5-methylcytosine"],
    "表观遗传": ["single nucleosome", "chromatin histones", "5-methylcytosine"],
    "microscope": ["microscope", "electron microscope", "confocal microscope"],
    "显微镜": ["microscope", "electron microscope", "confocal microscope"],
    "virus": ["virus", "SARS-CoV-2", "phage", "influenza"],
    "病毒": ["virus", "SARS-CoV-2", "phage", "influenza"],
    "flow cytometry": ["flow-cytometer-cell-sorter"],
    "流式": ["flow-cytometer-cell-sorter"],
    "流式细胞术": ["flow-cytometer-cell-sorter"],
    "western blot": ["western_blotting"],
    "wb": ["western_blotting"],
    "蛋白印迹": ["western_blotting"],
    "qpcr": ["qpcr_machine", "qPCR_plot"],
    "rt-qpcr": ["qpcr_machine", "qPCR_plot"],
    "定量pcr": ["qpcr_machine", "qPCR_plot"],
    "apoptosis": ["apoptosis"],
    "凋亡": ["apoptosis"],
    "proliferation": ["Mitosis", "cell cycle", "cell"],
    "增殖": ["Mitosis", "cell cycle", "cell"],
    "heatmap": ["heatmap", "heatmap symmetrical"],
    "热图": ["heatmap", "heatmap symmetrical"],
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

BIOICONS_PREFERRED_RESULTS = {
    "gene": BIOICONS_PRESETS["gene"],
    "基因": BIOICONS_PRESETS["gene"],
    "cell": BIOICONS_PRESETS["cell"],
    "细胞": BIOICONS_PRESETS["cell"],
    "immune cell": ["nk-cell", "dendritic_cell", "dendritic-cell-1", "hematopoetic-stem-cell", "lymphoid-stem-cell"],
    "免疫细胞": ["nk-cell", "dendritic_cell", "dendritic-cell-1", "hematopoetic-stem-cell", "lymphoid-stem-cell"],
    "t cell": ["t_cell_receptor", "t_cell_receptor_ok"],
    "t-cell": ["t_cell_receptor", "t_cell_receptor_ok"],
    "t细胞": ["t_cell_receptor", "t_cell_receptor_ok"],
    "b cell": ["B-cell_1", "B-cell_2", "B-cell_3", "B-cell_4", "B-cell_5", "B-cell_cluster"],
    "b-cell": ["B-cell_1", "B-cell_2", "B-cell_3", "B-cell_4", "B-cell_5", "B-cell_cluster"],
    "b细胞": ["B-cell_1", "B-cell_2", "B-cell_3", "B-cell_4", "B-cell_5", "B-cell_cluster"],
    "nk cell": ["nk-cell"],
    "nk-cell": ["nk-cell"],
    "nk细胞": ["nk-cell"],
    "antibody": BIOICONS_PRESETS["antibody"],
    "抗体": BIOICONS_PRESETS["antibody"],
    "mutation": BIOICONS_PRESETS["mutation"],
    "突变": BIOICONS_PRESETS["mutation"],
    "cancer cell": ["cancer_cell", "tumor", "cancerous-cell-1", "cancerous-cell-2", "cancerous-cell-3"],
    "tumor cell": ["tumor", "cancer_cell", "cancerous-cell-1", "cancerous-cell-2", "cancerous-cell-3"],
    "癌细胞": ["cancer_cell", "tumor", "cancerous-cell-1", "cancerous-cell-2", "cancerous-cell-3"],
    "肿瘤细胞": ["tumor", "cancer_cell", "cancerous-cell-1", "cancerous-cell-2", "cancerous-cell-3"],
    "fibroblast": ["fibroblast-1", "fibroblast-2", "fibroblast-3", "fibroblast-4", "fibroblast-5"],
    "成纤维细胞": ["fibroblast-1", "fibroblast-2", "fibroblast-3", "fibroblast-4", "fibroblast-5"],
    "single cell": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading"],
    "single-cell": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading"],
    "单细胞": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading"],
    "scrna-seq": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading", "library_for_RNA_sequencing"],
    "scrna seq": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading", "library_for_RNA_sequencing"],
    "单细胞测序": ["SingleCell_Clustering_DataReduction_UMAP", "singlecell_droplet_overloading", "library_for_RNA_sequencing"],
    "methylation": ["5-methylcytosine", "5-hydroxymethylcytosine"],
    "甲基化": ["5-methylcytosine", "5-hydroxymethylcytosine"],
    "epigenetics": ["single_nucleosome", "chromatin-histones", "Chromatin_structure", "5-methylcytosine"],
    "表观遗传": ["single_nucleosome", "chromatin-histones", "Chromatin_structure", "5-methylcytosine"],
    "sequencing": ["DNA_sequencer", "genomesequencer-1", "Sequencing_flow_cell_(4_colour)", "Illumina_sequencing_reads"],
    "测序": ["DNA_sequencer", "genomesequencer-1", "Sequencing_flow_cell_(4_colour)", "Illumina_sequencing_reads"],
    "rna-seq": ["library_for_RNA_sequencing", "rna", "RNA_bulge"],
    "rna seq": ["library_for_RNA_sequencing", "rna", "RNA_bulge"],
    "atac-seq": ["Tn5_chromatin_ATAC", "Transposase_Tn5_ATAC_chromatin"],
    "atac seq": ["Tn5_chromatin_ATAC", "Transposase_Tn5_ATAC_chromatin"],
    "flow cytometry": ["flow-cytometer-cell-sorter"],
    "流式": ["flow-cytometer-cell-sorter"],
    "流式细胞术": ["flow-cytometer-cell-sorter"],
    "western blot": ["western_blotting"],
    "wb": ["western_blotting"],
    "qpcr": ["qpcr_machine", "qPCR_plot"],
    "rt-qpcr": ["qpcr_machine", "qPCR_plot"],
    "apoptosis": ["apoptosis", "apoptosis_2"],
    "凋亡": ["apoptosis", "apoptosis_2"],
    "proliferation": ["Mitosis"],
    "增殖": ["Mitosis"],
    "microscope": BIOICONS_PRESETS["lab"][:4],
    "显微镜": BIOICONS_PRESETS["lab"][:4],
    "virus": BIOICONS_PRESETS["virus"],
    "病毒": BIOICONS_PRESETS["virus"],
    "heatmap": ["heatmap", "heatmap_symmetrical", "calendar-heatmap"],
    "热图": ["heatmap", "heatmap_symmetrical", "calendar-heatmap"],
}

ICONIFY_QUERY_ALIASES = {
    "基因": ["gene", "dna"],
    "细胞": ["cell"],
    "免疫细胞": ["immune cell"],
    "抗体": ["antibody"],
    "癌细胞": ["cancer cell"],
    "肿瘤细胞": ["tumor cell"],
    "显微镜": ["microscope"],
    "病毒": ["virus"],
    "突变": ["mutation"],
    "测序": ["sequencing"],
    "单细胞": ["single cell"],
    "警告": ["warning"],
    "靶点": ["target"],
    "柱状图": ["bar chart"],
    "验证": ["validation", "check"],
    "通路": ["pathway"],
}

PLOT_QUERY_NOTICES = {
    "kaplan-meier": "Kaplan-Meier and survival curves are data plots, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "kaplan meier": "Kaplan-Meier and survival curves are data plots, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "survival": "Survival analysis is usually a data plot, not a standalone icon. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "survival curve": "Survival curves are data plots, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "生存曲线": "Survival curves are data plots, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "forest plot": "Forest plots are data visualizations, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "森林图": "Forest plots are data visualizations, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "volcano plot": "Volcano plots are data visualizations, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
    "火山图": "Volcano plots are data visualizations, not reusable icons. Prefer a plotting workflow; use chart icons only as generic placeholders.",
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


def read_cached_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def fetch_json_cached(url: str, cache_name: str, ttl_seconds: int = CACHE_TTL_SECONDS):
    path = CACHE_DIR / cache_name
    cached = read_cached_json(path) if path.exists() else None
    if cached is not None and time.time() - path.stat().st_mtime < ttl_seconds:
        return cached

    try:
        data = fetch_json(url)
    except Exception:
        if cached is not None:
            return cached
        raise

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def normalize_text(value: str) -> str:
    return (
        value.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
    )


def query_keys(query: str) -> list[str]:
    return unique_in_order([query, query.lower(), normalize_text(query)])


def query_tokens(value: str) -> list[str]:
    return [token for token in normalize_text(value).split() if len(token) > 1]


def token_matches_text(token: str, text: str, words: list[str]) -> bool:
    if len(token) <= 2:
        return token in words
    return token in text


def query_notice(query: str) -> str:
    for key in query_keys(query):
        notice = PLOT_QUERY_NOTICES.get(key)
        if notice:
            return notice
    return ""


def unique_in_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def unique_candidates_in_order(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
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
        providers = {"bioicons", "iconify", "tabler"}
        if shutil.which("svgicons"):
            providers.add("svgicons")
        return providers
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
    results: list[str] = []
    for variant in expanded_query_variants(ICONIFY_QUERY_ALIASES, query):
        encoded = urllib.parse.quote(variant)
        url = f"{ICONIFY_API_BASE}/search?query={encoded}&limit={limit}"
        data = fetch_json(url)
        results.extend(data.get("icons", []))
        results = unique_in_order(results)
        if len(results) >= limit:
            break
    return results[:limit]


def tabler_icon_names() -> list[str]:
    data = fetch_json_cached(f"{ICONIFY_API_BASE}/collection?prefix=tabler", "tabler-collection.json")
    return list(data.get("uncategorized", []))


def expanded_query_variants(alias_map: dict[str, list[str]], query: str) -> list[str]:
    variants = [query]
    for key in query_keys(query):
        variants.extend(alias_map.get(key, []))
    return unique_in_order([variant for variant in variants if variant])


def score_name_against_query(name: str, query: str) -> int:
    normalized_name = normalize_text(name)
    normalized_query = normalize_text(query)
    score = 0
    if normalized_name == normalized_query:
        score += 50
    if normalized_name.startswith(normalized_query):
        score += 15
    tokens = query_tokens(query)
    if not tokens:
        return score
    if not all(token in normalized_name for token in tokens):
        return score
    score += sum(10 if token in normalized_name.split() else 4 for token in tokens)
    return score


def search_tabler(query: str, limit: int) -> list[str]:
    names = tabler_icon_names()
    query_variants = expanded_query_variants(TABLER_QUERY_ALIASES, query)
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
    entries = fetch_json_cached(BIOICONS_META_URL, "bioicons-icons.json")
    authors = fetch_json_cached(BIOICONS_AUTHORS_URL, "bioicons-authors.json")
    tree = fetch_json_cached(BIOICONS_TREE_URL, "bioicons-tree.json")
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


def score_bioicons_entry(name: str, entry: dict, query: str, require_all_tokens: bool = True) -> int:
    normalized_name = normalize_text(name)
    normalized_category = normalize_text(entry.get("category", ""))
    normalized_query = normalize_text(query)
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

    score = 0
    if normalized_name == normalized_query:
        score += 80
    if normalized_name.startswith(normalized_query):
        score += 30
    if normalized_category == normalized_query:
        score += 15

    tokens = query_tokens(query)
    if not tokens:
        return score

    haystack_words = haystack.split()
    if require_all_tokens and not all(token_matches_text(token, haystack, haystack_words) for token in tokens):
        return score
    if not require_all_tokens and not any(token_matches_text(token, haystack, haystack_words) for token in tokens):
        return score

    name_words = normalized_name.split()
    category_words = normalized_category.split()
    for token in tokens:
        if token in name_words:
            score += 18
        elif token_matches_text(token, normalized_name, name_words):
            score += 10
        if token in category_words:
            score += 7
        elif token_matches_text(token, normalized_category, category_words):
            score += 4
        elif token_matches_text(token, haystack, haystack_words):
            score += 1

    return score


def search_bioicons(query: str, limit: int, entries_by_name: dict[str, dict] | None = None) -> list[str]:
    if query_notice(query):
        return []
    entries_by_name = entries_by_name or bioicons_entry_map()
    query_variants = expanded_query_variants(BIOICONS_QUERY_ALIASES, query)
    preferred_names = expanded_query_variants(BIOICONS_PREFERRED_RESULTS, query)[1:]
    preferred_available = [name for name in preferred_names if name in entries_by_name]
    if preferred_available:
        return preferred_available[:limit]
    scored: list[tuple[int, str]] = []

    for name, entry in entries_by_name.items():
        score = max(score_bioicons_entry(name, entry, variant) for variant in query_variants)
        if not score:
            score = score_bioicons_entry(name, entry, query, require_all_tokens=False)
        if not score:
            continue
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


def print_search_results(
    provider: str, queries: list[str], limit: int, anonymous: bool
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    providers = provider_set(provider)
    bioicons_results: list[str] = []
    iconify_results: list[str] = []
    download_candidates: list[tuple[str, str]] = []
    entries_by_name = bioicons_entry_map() if "bioicons" in providers else {}

    for query in queries:
        notice = query_notice(query)
        if notice:
            print(f"\n## Note: {query}")
            print(notice)

        if "bioicons" in providers:
            results = search_bioicons(query, limit, entries_by_name)
            bioicons_results.extend(results)
            download_candidates.extend(("bioicons", icon) for icon in results)
            print(f"\n## BioIcons: {query}")
            print("\n".join(f"bioicons:{icon}" for icon in results) if results else "(no results)")

        if "tabler" in providers:
            results = search_tabler(query, limit)
            iconify_results.extend(results)
            download_candidates.extend(("iconify", icon) for icon in results)
            print(f"\n## Tabler: {query}")
            print("\n".join(results) if results else "(no results)")

        if "iconify" in providers:
            results = search_iconify(query, limit)
            iconify_results.extend(results)
            download_candidates.extend(("iconify", icon) for icon in results)
            print(f"\n## Iconify: {query}")
            print("\n".join(results) if results else "(no results)")

        if "svgicons" in providers:
            print(f"\n## Svg/icons CLI: {query}")
            search_svgicons(query, limit, anonymous)

    return (
        unique_in_order(bioicons_results),
        unique_in_order(iconify_results),
        unique_candidates_in_order(download_candidates),
    )


def split_download_candidates(candidates: list[tuple[str, str]], limit: int) -> tuple[list[str], list[str]]:
    selected_bioicons: list[str] = []
    selected_iconify: list[str] = []
    for provider, icon in candidates[:limit]:
        if provider == "bioicons":
            selected_bioicons.append(icon)
        else:
            selected_iconify.append(icon)
    return selected_bioicons, selected_iconify


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
        description="Search and download editable SVG icons from BioIcons, Tabler, Iconify, and optional Svg/icons CLI."
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "bioicons", "iconify", "tabler", "svgicons", "all"],
        default="auto",
        help="Icon source. auto searches/downloads BioIcons, Tabler, then Iconify; all adds Svg/icons only when installed.",
    )
    parser.add_argument("--search", action="append", default=[], help="Search term. May be repeated.")
    parser.add_argument("--recommend", help="Use Svg/icons CLI to recommend icons for a brief.")
    parser.add_argument("--pick", help="Use Svg/icons CLI to pick and download one icon.")
    parser.add_argument("--limit", type=int, default=30, help="Search results per term.")
    parser.add_argument(
        "--download-search",
        type=int,
        default=0,
        help="Download the first N combined search results in provider priority order.",
    )
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
    if args.download_search < 0:
        print("--download-search must be zero or greater.", file=sys.stderr)
        return 2

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
        _, _, download_candidates = print_search_results(args.provider, args.search, args.limit, args.anonymous)
        if args.download_search:
            searched_bioicons, searched_iconify = split_download_candidates(
                download_candidates, args.download_search
            )
            selected_bioicons.extend(searched_bioicons)
            selected_iconify.extend(searched_iconify)

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
