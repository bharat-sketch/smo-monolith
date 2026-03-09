#!/usr/bin/env python3
"""Generate rich visual diagrams for the Wynisco Infrastructure Document."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Color palette ──────────────────────────────────────
BLUE = "#3B82F6"
BLUE_LIGHT = "#DBEAFE"
GREEN = "#10B981"
GREEN_LIGHT = "#D1FAE5"
ORANGE = "#F59E0B"
ORANGE_LIGHT = "#FEF3C7"
PURPLE = "#8B5CF6"
PURPLE_LIGHT = "#EDE9FE"
RED = "#EF4444"
RED_LIGHT = "#FEE2E2"
TEAL = "#14B8A6"
TEAL_LIGHT = "#CCFBF1"
GRAY = "#6B7280"
GRAY_LIGHT = "#F3F4F6"
DARK = "#1E293B"
WHITE = "#FFFFFF"

DPI = 200
FONT = {"family": "sans-serif", "weight": "normal"}
TITLE_SIZE = 13
LABEL_SIZE = 9
SMALL_SIZE = 7.5
TINY_SIZE = 6.5


def _box(ax, x, y, w, h, label, sublabel=None, color=BLUE, text_color=WHITE,
         fontsize=LABEL_SIZE, radius=0.15, linestyle="-", linewidth=1.5,
         sublabel_size=None):
    """Draw a rounded box with centered text."""
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor=DARK, linewidth=linewidth,
        linestyle=linestyle, zorder=2,
    )
    ax.add_patch(box)
    if sublabel:
        ax.text(x, y + h*0.13, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color, zorder=3)
        ax.text(x, y - h*0.17, sublabel, ha="center", va="center",
                fontsize=sublabel_size or (fontsize - 1.5), color=text_color,
                zorder=3, style="italic")
    else:
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color, zorder=3)
    return box


def _arrow(ax, x1, y1, x2, y2, label=None, color=GRAY, style="->",
           lw=1.5, fontsize=TINY_SIZE, label_offset=(0, 0)):
    """Draw an arrow with optional label."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, color=color,
        linewidth=lw, mutation_scale=12, zorder=1,
        connectionstyle="arc3,rad=0",
    )
    ax.add_patch(arrow)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=fontsize, color=GRAY, zorder=4,
                bbox=dict(boxstyle="round,pad=0.15", facecolor=WHITE,
                          edgecolor="none", alpha=0.85))


def _diamond(ax, x, y, size, label, color=ORANGE, text_color=WHITE, fontsize=SMALL_SIZE):
    """Draw a diamond (decision) shape."""
    s = size / 2
    diamond = plt.Polygon(
        [(x, y+s), (x+s, y), (x, y-s), (x-s, y)],
        facecolor=color, edgecolor=DARK, linewidth=1.5, zorder=2,
    )
    ax.add_patch(diamond)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=text_color, zorder=3)


# ══════════════════════════════════════════════════════════
# 1. SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════
def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Title
    ax.text(5, 6.7, "System Architecture", ha="center", fontsize=TITLE_SIZE,
            fontweight="bold", color=DARK)

    # ── Internet bar ──
    _box(ax, 5, 6.15, 8.5, 0.35, "INTERNET / USERS", color=GRAY, fontsize=SMALL_SIZE)

    # ── Tier 1: Frontends ──
    ax.text(0.5, 5.35, "FRONTEND\nTIER", ha="center", fontsize=TINY_SIZE,
            color=BLUE, fontweight="bold")
    _box(ax, 2.7, 5.3, 2.0, 0.7, "SMO Frontend", "React SPA  :3000",
         color=BLUE, fontsize=SMALL_SIZE)
    _box(ax, 5.3, 5.3, 2.0, 0.7, "Match Dashboard", "Next.js  :3001",
         color=BLUE, fontsize=SMALL_SIZE)

    # ── Tier 2: Backends ──
    ax.text(0.5, 4.05, "BACKEND\nTIER", ha="center", fontsize=TINY_SIZE,
            color=GREEN, fontweight="bold")
    _box(ax, 2.7, 4.0, 2.0, 0.7, "SMO Backend", "FastAPI  :8000",
         color=GREEN, fontsize=SMALL_SIZE)
    _box(ax, 5.3, 4.0, 2.0, 0.7, "Matching Backend", "FastAPI  :8002",
         color=GREEN, fontsize=SMALL_SIZE)

    # ── Tier 3: Data ──
    ax.text(0.5, 2.55, "DATA\nTIER", ha="center", fontsize=TINY_SIZE,
            color=ORANGE, fontweight="bold")
    _box(ax, 2.7, 2.5, 2.2, 0.9, "PostgreSQL", "pgvector + 36 tables\nsmo_local",
         color=ORANGE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _box(ax, 5.3, 2.5, 2.0, 0.7, "Redis Cache", "LLM results\n72hr TTL",
         color="#DC2626", fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)

    # ── External APIs ──
    ax.text(0.5, 1.15, "EXTERNAL\nAPIs", ha="center", fontsize=TINY_SIZE,
            color=PURPLE, fontweight="bold")
    _box(ax, 7.8, 4.0, 1.8, 0.55, "OpenAI API", "Embeddings",
         color=PURPLE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _box(ax, 7.8, 3.15, 1.8, 0.55, "Cerebras API", "LLM Scoring",
         color=PURPLE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)

    # ── Arrows ──
    # Internet → Frontends
    _arrow(ax, 3.5, 5.97, 2.7, 5.65, color=GRAY, lw=1.2)
    _arrow(ax, 5.0, 5.97, 5.3, 5.65, color=GRAY, lw=1.2)

    # Frontends → Backends
    _arrow(ax, 2.7, 4.95, 2.7, 4.35, label="REST API", color=BLUE, fontsize=TINY_SIZE)
    _arrow(ax, 5.3, 4.95, 5.3, 4.35, label="REST API", color=BLUE, fontsize=TINY_SIZE)

    # Backends → PostgreSQL
    _arrow(ax, 2.7, 3.65, 2.7, 2.95, label="asyncpg\nread-write", color=GREEN, fontsize=TINY_SIZE)
    _arrow(ax, 4.8, 3.65, 3.4, 2.95, label="asyncpg\nread-only + write 3", color=GREEN, fontsize=TINY_SIZE,
           label_offset=(0.2, 0))

    # Matching → Redis
    _arrow(ax, 5.7, 3.65, 5.4, 2.85, label="cache", color="#DC2626", fontsize=TINY_SIZE,
           label_offset=(0.35, 0))

    # Matching → External APIs
    _arrow(ax, 6.3, 4.15, 6.9, 4.05, label="HTTPS", color=PURPLE, fontsize=TINY_SIZE)
    _arrow(ax, 6.3, 3.85, 6.9, 3.25, color=PURPLE, lw=1.2)

    # Legend
    legend_y = 1.1
    for i, (label, color) in enumerate([
        ("Frontend", BLUE), ("Backend", GREEN),
        ("Data Store", ORANGE), ("External API", PURPLE),
    ]):
        lx = 1.5 + i * 2.2
        rect = FancyBboxPatch((lx - 0.25, legend_y - 0.12), 0.5, 0.24,
                              boxstyle="round,pad=0,rounding_size=0.06",
                              facecolor=color, edgecolor="none", zorder=2)
        ax.add_patch(rect)
        ax.text(lx + 0.4, legend_y, label, fontsize=TINY_SIZE, va="center", color=DARK)

    path = os.path.join(OUT_DIR, "architecture.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 2. PLATFORM DATA FLOW
# ══════════════════════════════════════════════════════════
def draw_data_flow_diagram():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    ax.text(5.5, 7.2, "How Data Connects Across the Platform", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    # ── PEOPLE column (left) ──
    _box(ax, 2, 6.2, 2.2, 0.6, "Pod / Cohort", "Candidate batch", color=TEAL, fontsize=SMALL_SIZE)
    _box(ax, 2, 5.1, 2.2, 0.7, "Candidate", "Resume, skills,\nexperience, location",
         color=BLUE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _box(ax, 2, 3.9, 2.2, 0.6, "Instructor", "Mentor pairing", color=TEAL, fontsize=SMALL_SIZE)
    _box(ax, 2, 2.8, 2.2, 0.6, "Alumni", "Placement outcomes", color=TEAL, fontsize=SMALL_SIZE)

    # ── JOBS column (right-center) ──
    _box(ax, 6.5, 6.2, 2.2, 0.6, "Employer", "Company info, blacklist", color=GREEN, fontsize=SMALL_SIZE)
    _box(ax, 6.5, 5.1, 2.2, 0.7, "Job Posting", "Title, description,\nsalary, location",
         color=GREEN, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _box(ax, 9.2, 6.2, 1.6, 0.6, "Recruiter\nContact", color="#0D9488", text_color=WHITE,
         fontsize=SMALL_SIZE)

    # ── AI MATCHING (center) ──
    _box(ax, 4.25, 3.5, 3.0, 0.65, "AI Matching Engine", "Embeddings + LLM Scoring",
         color=ORANGE, fontsize=SMALL_SIZE)

    # ── RESULTS (bottom-center) ──
    _box(ax, 4.25, 2.3, 2.6, 0.65, "Match Score + WhyCard",
         "Score, gaps, strengths", color=PURPLE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)

    # ── APPLICATION (bottom) ──
    _box(ax, 4.25, 1.1, 2.6, 0.65, "Application",
         "Candidate + Job + Consultant", color="#2563EB", fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)

    # ── QC (right-bottom) ──
    _box(ax, 8.5, 1.1, 2.0, 0.65, "QC & Performance",
         "Issues, daily scores", color=RED, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)

    # ── Arrows with labels ──
    # Pod → Candidate
    _arrow(ax, 2, 5.9, 2, 5.45, label="belongs to", color=TEAL)
    # Candidate → Instructor
    _arrow(ax, 2, 4.75, 2, 4.2, label="mentored by", color=TEAL)
    # Candidate → Alumni
    _arrow(ax, 2, 3.6, 2, 3.1, label="graduates to", color=TEAL, style="->", lw=1.0)
    # Employer → Job
    _arrow(ax, 6.5, 5.9, 6.5, 5.45, label="posts", color=GREEN)
    # Employer → Contact
    _arrow(ax, 7.6, 6.2, 8.4, 6.2, label="has", color="#0D9488")

    # Candidate → AI Matching
    _arrow(ax, 3.1, 5.05, 3.6, 3.85, label="resume &\nskills", color=BLUE,
           label_offset=(-0.4, 0.1))
    # Job → AI Matching
    _arrow(ax, 5.9, 4.75, 5.0, 3.85, label="description &\nrequirements", color=GREEN,
           label_offset=(0.5, 0.1))

    # AI → Match Score
    _arrow(ax, 4.25, 3.18, 4.25, 2.63, label="produces", color=ORANGE)

    # Match Score → Application
    _arrow(ax, 4.25, 1.98, 4.25, 1.43, label="informs", color=PURPLE)

    # Application → QC
    _arrow(ax, 5.55, 1.1, 7.5, 1.1, label="audited by", color=RED)

    # ── Domain labels ──
    ax.text(0.3, 6.5, "PEOPLE", fontsize=SMALL_SIZE, fontweight="bold",
            color=TEAL, rotation=90, va="center")
    ax.text(8.0, 5.6, "JOBS", fontsize=SMALL_SIZE, fontweight="bold",
            color=GREEN, rotation=90, va="center")

    path = os.path.join(OUT_DIR, "data_flow.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 3. APPLICATION PIPELINE
# ══════════════════════════════════════════════════════════
def draw_application_pipeline():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.5)
    ax.axis("off")

    ax.text(5, 3.2, "Application Pipeline Stages", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    stages = [
        ("Applied", "#60A5FA"),
        ("Screening", "#34D399"),
        ("Interview", "#FBBF24"),
        ("Offer", "#A78BFA"),
        ("Placed", "#10B981"),
    ]

    y_main = 2.2
    spacing = 1.85
    start_x = 0.8

    for i, (label, color) in enumerate(stages):
        x = start_x + i * spacing
        _box(ax, x, y_main, 1.5, 0.65, label, color=color,
             text_color=DARK if color in ("#FBBF24", "#34D399") else WHITE,
             fontsize=LABEL_SIZE)
        if i < len(stages) - 1:
            _arrow(ax, x + 0.75, y_main, x + spacing - 0.75, y_main, color=GRAY, lw=2)

    # Rejected branches
    reject_y = 0.9
    _box(ax, 5.0, reject_y, 1.5, 0.5, "Rejected", color=RED, fontsize=SMALL_SIZE)

    for i in range(4):
        x = start_x + i * spacing
        _arrow(ax, x, y_main - 0.35, 4.6, reject_y + 0.28,
               color="#FCA5A5", lw=0.8, style="-|>")

    ax.text(5.0, 0.35, "Any stage can result in rejection",
            ha="center", fontsize=TINY_SIZE, color=GRAY, style="italic")

    path = os.path.join(OUT_DIR, "app_pipeline.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 4. MATCH DATA CHAIN
# ══════════════════════════════════════════════════════════
def draw_match_chain():
    fig, ax = plt.subplots(figsize=(11, 7.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(5.5, 7.7, "Complete Data Chain: One Match (Example)", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    # ── STEP 1: Candidate lane (left) ──
    ax.text(2.2, 7.15, "STEP 1: Candidate Data", fontsize=LABEL_SIZE,
            fontweight="bold", color=BLUE)
    _box(ax, 2.2, 6.5, 3.5, 0.55, "John Doe  |  Pod: March 2026",
         color=BLUE_LIGHT, text_color=DARK, fontsize=SMALL_SIZE, linewidth=1)
    _box(ax, 2.2, 5.8, 3.5, 0.55, "Skills: Java, Python  |  3yr exp  |  NYC",
         color=BLUE_LIGHT, text_color=DARK, fontsize=SMALL_SIZE, linewidth=1)
    _box(ax, 2.2, 5.1, 3.5, 0.55, "Resume → Embedding (1,536 numbers)",
         color=BLUE, text_color=WHITE, fontsize=SMALL_SIZE)

    _arrow(ax, 2.2, 6.23, 2.2, 6.08, color=BLUE, lw=1)
    _arrow(ax, 2.2, 5.53, 2.2, 5.38, color=BLUE, lw=1)

    # ── STEP 2: Job lane (right) ──
    ax.text(8.3, 7.15, "STEP 2: Job Data", fontsize=LABEL_SIZE,
            fontweight="bold", color=GREEN)
    _box(ax, 8.3, 6.5, 3.5, 0.55, "Acme Corp  |  Tech  |  Not blacklisted",
         color=GREEN_LIGHT, text_color=DARK, fontsize=SMALL_SIZE, linewidth=1)
    _box(ax, 8.3, 5.8, 3.5, 0.55, "Software Engineer  |  NYC  |  $90-120K  |  2yr",
         color=GREEN_LIGHT, text_color=DARK, fontsize=SMALL_SIZE, linewidth=1)
    _box(ax, 8.3, 5.1, 3.5, 0.55, "Description → Embedding (1,536 numbers)",
         color=GREEN, text_color=WHITE, fontsize=SMALL_SIZE)

    _arrow(ax, 8.3, 6.23, 8.3, 6.08, color=GREEN, lw=1)
    _arrow(ax, 8.3, 5.53, 8.3, 5.38, color=GREEN, lw=1)

    # ── STEP 3: AI Matching (center) ──
    ax.text(5.25, 4.45, "STEP 3: AI Matching", fontsize=LABEL_SIZE,
            fontweight="bold", color=ORANGE, ha="center")

    # Hard filters
    _box(ax, 5.25, 3.85, 5.5, 0.55, "Hard Filters:  3yr >= 2yr ✓    NYC = NYC ✓    Salary overlap ✓",
         color=ORANGE_LIGHT, text_color=DARK, fontsize=SMALL_SIZE, linewidth=1.2)

    # Scores
    _box(ax, 3.3, 3.05, 3.0, 0.5, "Semantic Score: 0.82",
         color=BLUE, fontsize=SMALL_SIZE)
    _box(ax, 7.2, 3.05, 3.0, 0.5, "LLM Score: 0.78",
         color=PURPLE, fontsize=SMALL_SIZE)

    # Combined
    _box(ax, 5.25, 2.25, 5.5, 0.55, "Combined: (0.82 × 50%) + (0.78 × 50%) = 80 / 100",
         color=ORANGE, fontsize=LABEL_SIZE)

    # Arrows into matching
    _arrow(ax, 2.2, 4.83, 3.5, 4.13, color=BLUE, lw=1.5)
    _arrow(ax, 8.3, 4.83, 7.0, 4.13, color=GREEN, lw=1.5)
    _arrow(ax, 5.25, 3.58, 3.8, 3.3, color=ORANGE, lw=1)
    _arrow(ax, 5.25, 3.58, 6.7, 3.3, color=ORANGE, lw=1)
    _arrow(ax, 3.8, 2.8, 4.2, 2.53, color=BLUE, lw=1)
    _arrow(ax, 6.7, 2.8, 6.3, 2.53, color=PURPLE, lw=1)

    # ── STEP 4: Result (bottom) ──
    ax.text(5.25, 1.65, "STEP 4: Result", fontsize=LABEL_SIZE,
            fontweight="bold", color=PURPLE, ha="center")

    # WhyCard box
    result_box = FancyBboxPatch(
        (1.5, 0.15), 7.5, 1.2,
        boxstyle="round,pad=0,rounding_size=0.15",
        facecolor=PURPLE_LIGHT, edgecolor=PURPLE, linewidth=2, zorder=2,
    )
    ax.add_patch(result_box)
    ax.text(5.25, 1.05, "WhyCard  —  Score: 80/100", ha="center",
            fontsize=LABEL_SIZE, fontweight="bold", color=DARK, zorder=3)
    ax.text(5.25, 0.7, '"Strong Java match. Python is a plus."', ha="center",
            fontsize=SMALL_SIZE, color=DARK, style="italic", zorder=3)
    ax.text(5.25, 0.4, '"Gap: No AWS experience. Recommend highlighting cloud projects."',
            ha="center", fontsize=SMALL_SIZE, color=GRAY, style="italic", zorder=3)

    _arrow(ax, 5.25, 1.98, 5.25, 1.38, color=PURPLE, lw=1.5)

    path = os.path.join(OUT_DIR, "match_chain.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 5. QC WORKFLOW
# ══════════════════════════════════════════════════════════
def draw_qc_workflow():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.8)
    ax.axis("off")

    ax.text(5, 3.5, "Quality Control Issue Lifecycle", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    stages = [
        ("Detected", RED, WHITE),
        ("Open", "#F97316", WHITE),
        ("Investigating", ORANGE, DARK),
        ("Resolved", GREEN, WHITE),
    ]

    y_main = 2.5
    start_x = 1.2
    spacing = 2.2

    for i, (label, color, tc) in enumerate(stages):
        x = start_x + i * spacing
        _box(ax, x, y_main, 1.7, 0.6, label, color=color, text_color=tc,
             fontsize=LABEL_SIZE)
        if i < len(stages) - 1:
            _arrow(ax, x + 0.85, y_main, x + spacing - 0.85, y_main, color=GRAY, lw=2)

    # Dismissed branch (from Investigating)
    inv_x = start_x + 2 * spacing
    _box(ax, inv_x + 1.0, 1.3, 1.6, 0.5, "Dismissed", color=GRAY,
         fontsize=SMALL_SIZE)
    _arrow(ax, inv_x + 0.5, 2.2, inv_x + 0.6, 1.55, color=GRAY, lw=1.2)

    # Escalated branch (from Investigating)
    _box(ax, inv_x - 1.2, 1.3, 1.6, 0.5, "Escalated", color="#DC2626",
         fontsize=SMALL_SIZE)
    _arrow(ax, inv_x - 0.5, 2.2, inv_x - 0.8, 1.55, color="#DC2626", lw=1.2)
    ax.text(inv_x - 1.2, 0.8, "if severe", fontsize=TINY_SIZE, color=GRAY,
            ha="center", style="italic")

    # Detection sources
    ax.text(1.2, 1.6, "Auto-detected or\nmanually flagged", fontsize=TINY_SIZE,
            color=GRAY, ha="center", style="italic")

    path = os.path.join(OUT_DIR, "qc_workflow.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 6. DATABASE OWNERSHIP
# ══════════════════════════════════════════════════════════
def draw_db_ownership():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(4.5, 5.7, "Database Ownership Model", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    # Outer PostgreSQL container
    outer = FancyBboxPatch(
        (0.5, 0.3), 8.0, 5.0,
        boxstyle="round,pad=0,rounding_size=0.2",
        facecolor=GRAY_LIGHT, edgecolor=DARK, linewidth=2, zorder=1,
    )
    ax.add_patch(outer)
    ax.text(4.5, 5.05, "smo_local  (PostgreSQL 15 + pgvector)", ha="center",
            fontsize=LABEL_SIZE, fontweight="bold", color=DARK, zorder=3)

    # SMO tables block (largest)
    smo_block = FancyBboxPatch(
        (0.8, 3.3), 7.4, 1.5,
        boxstyle="round,pad=0,rounding_size=0.12",
        facecolor=BLUE_LIGHT, edgecolor=BLUE, linewidth=2, zorder=2,
    )
    ax.add_patch(smo_block)
    ax.text(4.5, 4.45, "SMO Backend — 33 Tables (Read-Write)", ha="center",
            fontsize=LABEL_SIZE, fontweight="bold", color=BLUE, zorder=3)
    ax.text(4.5, 3.95, "users  |  candidate_profiles  |  jobs  |  employers  |  contacts",
            ha="center", fontsize=SMALL_SIZE, color=DARK, zorder=3)
    ax.text(4.5, 3.6, "pods  |  application_events  |  interviews  |  qc_issues  |  attendance  |  ...",
            ha="center", fontsize=SMALL_SIZE, color=GRAY, zorder=3)

    # Matching tables block
    match_block = FancyBboxPatch(
        (0.8, 1.7), 3.5, 1.3,
        boxstyle="round,pad=0,rounding_size=0.12",
        facecolor=ORANGE_LIGHT, edgecolor=ORANGE, linewidth=2, zorder=2,
    )
    ax.add_patch(match_block)
    ax.text(2.55, 2.65, "Matching Service — 3 Tables", ha="center",
            fontsize=LABEL_SIZE, fontweight="bold", color=ORANGE, zorder=3)
    ax.text(2.55, 2.25, "candidate_embeddings\njob_embeddings\nmatch_scores_v2",
            ha="center", fontsize=SMALL_SIZE, color=DARK, zorder=3, linespacing=1.3)

    # Read-only access block (dashed)
    ro_block = FancyBboxPatch(
        (4.7, 1.7), 3.5, 1.3,
        boxstyle="round,pad=0,rounding_size=0.12",
        facecolor=WHITE, edgecolor=GREEN, linewidth=1.5,
        linestyle="--", zorder=2,
    )
    ax.add_patch(ro_block)
    ax.text(6.45, 2.65, "Read-Only Access (Matching)", ha="center",
            fontsize=LABEL_SIZE, fontweight="bold", color=GREEN, zorder=3)
    ax.text(6.45, 2.25, "users  |  candidate_profiles\njobs  |  employers\npods  |  universities",
            ha="center", fontsize=SMALL_SIZE, color=DARK, zorder=3, linespacing=1.3)

    # Arrow showing read-only
    _arrow(ax, 6.45, 1.7, 6.45, 1.0, color=GREEN, lw=1)
    ax.text(6.45, 0.7, "Matching service reads SMO tables\nbut never modifies them",
            ha="center", fontsize=TINY_SIZE, color=GREEN, style="italic")

    # Arrow showing ownership
    _arrow(ax, 2.55, 1.7, 2.55, 1.0, color=ORANGE, lw=1)
    ax.text(2.55, 0.7, "Matching service owns and writes\nonly these 3 tables",
            ha="center", fontsize=TINY_SIZE, color=ORANGE, style="italic")

    path = os.path.join(OUT_DIR, "db_ownership.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# 7. CACHE FLOW
# ══════════════════════════════════════════════════════════
def draw_cache_flow():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    ax.text(5, 8.2, "Two-Layer Cache Flow", ha="center",
            fontsize=TITLE_SIZE, fontweight="bold", color=DARK)

    # Start
    _box(ax, 5, 7.5, 3.0, 0.5, "Match Request Arrives", color=DARK, fontsize=SMALL_SIZE)

    # Layer 1: DB Cache
    _diamond(ax, 5, 6.5, 0.9, "DB\nCache?", color=BLUE, fontsize=TINY_SIZE)
    _arrow(ax, 5, 7.25, 5, 6.95, color=DARK, lw=1.5)

    # DB HIT
    _box(ax, 8.2, 6.5, 2.5, 0.5, "Return cached result", "~5ms",
         color=GREEN, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5.45, 6.5, 6.95, 6.5, label="HIT", color=GREEN, fontsize=SMALL_SIZE)

    # DB MISS → Hard Filter
    _box(ax, 5, 5.5, 3.0, 0.5, "Hard Filter (SQL)", "~100ms",
         color=GRAY, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5, 6.05, 5, 5.75, label="MISS", color=RED, fontsize=SMALL_SIZE)

    # Semantic ANN
    _box(ax, 5, 4.6, 3.0, 0.5, "Semantic ANN (pgvector)", "~200ms",
         color=BLUE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5, 5.25, 5, 4.85, color=GRAY, lw=1.2)

    # Layer 2: Redis
    _diamond(ax, 5, 3.6, 0.9, "Redis\nCache?", color="#DC2626", fontsize=TINY_SIZE)
    _arrow(ax, 5, 4.35, 5, 4.05, color=GRAY, lw=1.2)

    ax.text(5, 4.15, "For each candidate-job pair:", fontsize=TINY_SIZE,
            ha="center", color=GRAY, style="italic")

    # Redis HIT
    _box(ax, 8.2, 3.6, 2.5, 0.5, "Use cached LLM result", "~1ms",
         color=GREEN, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5.45, 3.6, 6.95, 3.6, label="HIT", color=GREEN, fontsize=SMALL_SIZE)

    # Redis MISS → Cerebras
    _box(ax, 5, 2.6, 3.0, 0.5, "Call Cerebras LLM", "~2-3 seconds",
         color=PURPLE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5, 3.15, 5, 2.85, label="MISS", color=RED, fontsize=SMALL_SIZE)

    # Store in Redis
    _box(ax, 8.2, 2.6, 2.5, 0.5, "Store in Redis", "TTL: 72 hours",
         color="#DC2626", fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 6.5, 2.6, 6.95, 2.6, color="#DC2626", lw=1)

    # Combine
    _box(ax, 5, 1.6, 3.0, 0.5, "Combine Scores + WhyCard", color=ORANGE, fontsize=SMALL_SIZE)
    _arrow(ax, 5, 2.35, 5, 1.85, color=GRAY, lw=1.2)

    # Store in DB
    _box(ax, 5, 0.7, 3.0, 0.5, "Store in DB Cache", "TTL: 24 hours",
         color=BLUE, fontsize=SMALL_SIZE, sublabel_size=TINY_SIZE)
    _arrow(ax, 5, 1.35, 5, 0.95, color=GRAY, lw=1.2)

    # Layer labels
    layer1_box = FancyBboxPatch(
        (0.3, 5.95), 1.2, 1.3,
        boxstyle="round,pad=0,rounding_size=0.08",
        facecolor=BLUE_LIGHT, edgecolor=BLUE, linewidth=1, zorder=1,
    )
    ax.add_patch(layer1_box)
    ax.text(0.9, 6.6, "Layer 1\nDB Cache", ha="center", fontsize=TINY_SIZE,
            fontweight="bold", color=BLUE, zorder=2)

    layer2_box = FancyBboxPatch(
        (0.3, 2.3), 1.2, 2.0,
        boxstyle="round,pad=0,rounding_size=0.08",
        facecolor=RED_LIGHT, edgecolor="#DC2626", linewidth=1, zorder=1,
    )
    ax.add_patch(layer2_box)
    ax.text(0.9, 3.3, "Layer 2\nRedis\nCache", ha="center", fontsize=TINY_SIZE,
            fontweight="bold", color="#DC2626", zorder=2)

    path = os.path.join(OUT_DIR, "cache_flow.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.2)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════
# GENERATE ALL
# ══════════════════════════════════════════════════════════
def generate_all():
    """Generate all diagrams and return dict of name → path."""
    return {
        "architecture": draw_architecture_diagram(),
        "data_flow": draw_data_flow_diagram(),
        "app_pipeline": draw_application_pipeline(),
        "match_chain": draw_match_chain(),
        "qc_workflow": draw_qc_workflow(),
        "db_ownership": draw_db_ownership(),
        "cache_flow": draw_cache_flow(),
    }


if __name__ == "__main__":
    paths = generate_all()
    for name, path in paths.items():
        size = os.path.getsize(path)
        print(f"  {name}: {path} ({size/1024:.0f} KB)")
    print(f"\nGenerated {len(paths)} diagrams in {OUT_DIR}/")
