import csv
import collections
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# ── Load data ──────────────────────────────────────────────────────
FILE = "/Users/hasheerama/Downloads/lig_26_2_2026.csv"
with open(FILE, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# ── Helpers ────────────────────────────────────────────────────────
KNOWN_SOURCES = {"linkedin", "Indeed", "Glassdoor"}

def clean(val):
    return val.strip() if val and val.strip() and val.strip() != "NA" else None

def normalize_location(loc):
    """Collapse location variants into a metro area."""
    if not loc:
        return None
    loc = loc.title().strip()
    loc = re.sub(r",?\s*United States$", "", loc).strip().rstrip(",")
    # Merge variants
    mapping = {
        "New York": ["New York, Ny", "New York City, Ny", "Nyc, Ny", "Manhattan, Ny", "Brooklyn, Ny"],
        "Seattle": ["Seattle, Wa"],
        "San Francisco Bay": ["San Francisco, Ca", "San Jose, Ca", "Palo Alto, Ca", "Mountain View, Ca",
                               "Sunnyvale, Ca", "Santa Clara, Ca", "Menlo Park, Ca", "Redwood City, Ca"],
        "Chicago": ["Chicago, Il"],
        "Austin": ["Austin, Tx"],
        "Atlanta": ["Atlanta, Ga"],
        "Boston": ["Boston, Ma", "Cambridge, Ma"],
        "Dallas-Fort Worth": ["Dallas, Tx", "Fort Worth, Tx", "Irving, Tx", "Plano, Tx"],
        "Houston": ["Houston, Tx"],
        "Los Angeles": ["Los Angeles, Ca"],
        "Washington DC": ["Washington, Dc", "Arlington, Va", "Mclean, Va", "Reston, Va", "Tysons, Va"],
        "Denver": ["Denver, Co"],
        "Charlotte": ["Charlotte, Nc"],
        "Redmond": ["Redmond, Wa"],
        "Remote": ["Remote"],
    }
    for metro, variants in mapping.items():
        if loc in [v.title() for v in variants]:
            return metro
    return loc

def normalize_title(title):
    """Group similar job titles."""
    if not title:
        return None
    t = title.strip().lower()
    mapping = {
        "Software Engineer": ["software engineer", "software engineer i", "software engineer ii",
                              "software engineer iii", "sr software engineer", "senior software engineer",
                              "staff software engineer", "software development engineer"],
        "Data Engineer": ["data engineer", "data engineer ii", "senior data engineer", "sr data engineer"],
        "Data Analyst": ["data analyst", "senior data analyst", "sr data analyst", "data analyst ii"],
        "Business Analyst": ["business analyst", "senior business analyst", "sr business analyst",
                             "business analyst ii", "business systems analyst"],
        "Product Manager": ["product manager", "senior product manager", "sr product manager"],
        "Project Manager": ["project manager", "senior project manager", "sr project manager",
                            "project manager ii", "it project manager"],
        "Data Scientist": ["data scientist", "senior data scientist", "sr data scientist"],
        "ML Engineer": ["machine learning engineer", "ml engineer", "senior machine learning engineer"],
        "Full Stack Developer": ["full stack engineer", "full stack developer", "fullstack engineer",
                                 "fullstack developer"],
        "AI Engineer": ["ai engineer", "artificial intelligence engineer"],
        "DevOps Engineer": ["devops engineer", "senior devops engineer", "site reliability engineer", "sre"],
        "Product Designer": ["product designer", "senior product designer", "ux designer", "ui/ux designer"],
        "Financial Analyst": ["financial analyst", "senior financial analyst"],
        "Supply Chain": ["supply chain analyst", "supply chain manager", "supply chain specialist"],
        "Program Manager": ["program manager", "senior program manager", "technical program manager"],
        "QA Engineer": ["qa engineer", "quality assurance engineer", "test engineer", "sdet"],
        "Cloud Engineer": ["cloud engineer", "cloud architect", "aws engineer"],
        "Frontend Developer": ["frontend developer", "frontend engineer", "front end developer",
                               "front end engineer", "react developer"],
        "Backend Developer": ["backend developer", "backend engineer", "back end developer"],
    }
    for group, variants in mapping.items():
        if t in variants:
            return group
    return title.strip()

# ── Compute data for charts ────────────────────────────────────────
sources = collections.Counter(
    r["source"] for r in rows if r.get("source") in KNOWN_SOURCES
)

employers = collections.Counter(clean(r.get("employer_name")) for r in rows)
employers.pop(None, None)
top_employers = employers.most_common(15)

raw_titles = collections.Counter(normalize_title(clean(r.get("job_title"))) for r in rows)
raw_titles.pop(None, None)
top_titles = raw_titles.most_common(15)

metros = collections.Counter(normalize_location(clean(r.get("location"))) for r in rows)
metros.pop(None, None)
top_metros = metros.most_common(15)

# Source per metro (top 10 metros)
top_metro_names = [m for m, _ in top_metros[:10]]
source_metro = {}
for src in KNOWN_SOURCES:
    source_metro[src] = []
    for metro in top_metro_names:
        count = sum(
            1 for r in rows
            if r.get("source") == src and normalize_location(clean(r.get("location"))) == metro
        )
        source_metro[src].append(count)

# ── Plot ───────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.0)
palette = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2"]

fig = plt.figure(figsize=(20, 22))
fig.suptitle("Scraped Job Listings — Feb 26, 2026\n4,040 jobs from LinkedIn, Indeed & Glassdoor",
             fontsize=18, fontweight="bold", y=0.98)

# 1 ─ Source pie
ax1 = fig.add_subplot(3, 2, 1)
labels = list(sources.keys())
sizes = list(sources.values())
colors = palette[:len(labels)]
wedges, texts, autotexts = ax1.pie(
    sizes, labels=labels, autopct=lambda p: f"{p:.1f}%\n({int(round(p * sum(sizes) / 100))})",
    colors=colors, startangle=140, textprops={"fontsize": 11}
)
for t in autotexts:
    t.set_fontsize(10)
ax1.set_title("Jobs by Source", fontsize=14, fontweight="bold", pad=12)

# 2 ─ Top employers bar
ax2 = fig.add_subplot(3, 2, 2)
emp_names = [e[0][:25] for e in reversed(top_employers)]
emp_counts = [e[1] for e in reversed(top_employers)]
bars = ax2.barh(emp_names, emp_counts, color=palette[0], edgecolor="white", height=0.7)
ax2.bar_label(bars, padding=3, fontsize=9)
ax2.set_title("Top 15 Employers", fontsize=14, fontweight="bold", pad=12)
ax2.set_xlabel("Number of Listings")
ax2.tick_params(axis="y", labelsize=9)

# 3 ─ Job titles bar
ax3 = fig.add_subplot(3, 2, 3)
title_names = [t[0][:25] for t in reversed(top_titles)]
title_counts = [t[1] for t in reversed(top_titles)]
bars3 = ax3.barh(title_names, title_counts, color=palette[1], edgecolor="white", height=0.7)
ax3.bar_label(bars3, padding=3, fontsize=9)
ax3.set_title("Top 15 Job Titles (Grouped)", fontsize=14, fontweight="bold", pad=12)
ax3.set_xlabel("Number of Listings")
ax3.tick_params(axis="y", labelsize=9)

# 4 ─ Top metros bar
ax4 = fig.add_subplot(3, 2, 4)
metro_names = [m[0][:25] for m in reversed(top_metros)]
metro_counts = [m[1] for m in reversed(top_metros)]
bars4 = ax4.barh(metro_names, metro_counts, color=palette[2], edgecolor="white", height=0.7)
ax4.bar_label(bars4, padding=3, fontsize=9)
ax4.set_title("Top 15 Metro Areas", fontsize=14, fontweight="bold", pad=12)
ax4.set_xlabel("Number of Listings")
ax4.tick_params(axis="y", labelsize=9)

# 5 ─ Source × Metro stacked bar
ax5 = fig.add_subplot(3, 2, (5, 6))
import numpy as np
x = np.arange(len(top_metro_names))
width = 0.25
for i, (src, counts) in enumerate(source_metro.items()):
    ax5.bar(x + i * width, counts, width, label=src, color=palette[i], edgecolor="white")
ax5.set_xticks(x + width)
ax5.set_xticklabels(top_metro_names, rotation=30, ha="right", fontsize=10)
ax5.set_ylabel("Number of Listings")
ax5.set_title("Jobs by Source × Top 10 Metro Areas", fontsize=14, fontweight="bold", pad=12)
ax5.legend(fontsize=11)
ax5.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.tight_layout(rect=[0, 0, 1, 0.95])
out = "/Users/hasheerama/projects/Resume-pipeline/jobs_visualization.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved to {out}")
