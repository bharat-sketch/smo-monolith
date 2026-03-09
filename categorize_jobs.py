import csv
import re
import collections
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns

# ── Load data ──────────────────────────────────────────────────────
FILE = "/Users/hasheerama/Downloads/lig_26_2_2026.csv"
with open(FILE, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

KNOWN_SOURCES = {"linkedin", "Indeed", "Glassdoor"}
clean_rows = [r for r in rows if r.get("source") in KNOWN_SOURCES]

# ── Categorization rules (order matters — first match wins) ────────
# Each rule: (category, list of regex patterns applied to lowercase title)
RULES = [
    ("AI / ML", [
        r"\bai\b", r"\bartificial intelligence\b", r"\bmachine learning\b",
        r"\bml\b", r"\bmlops\b", r"\bdeep learning\b", r"\bnlp\b",
        r"\bnatural language\b", r"\bcomputer vision\b", r"\bllm\b",
        r"\bgenerative ai\b", r"\bgen ai\b", r"\bgenai\b",
        r"\bapplied scientist\b", r"\bresearch scientist\b",
        r"\bml engineer\b", r"\bai engineer\b",
    ]),
    ("Data Science", [
        r"\bdata scien", r"\bstatistic", r"\bquant\b",
    ]),
    ("Data Engineering", [
        r"\bdata engineer", r"\betl\b", r"\bdata pipeline\b",
        r"\bdata platform\b", r"\bdata ops\b", r"\bdataops\b",
        r"\bdata warehouse\b", r"\bbig data\b", r"\bdata infra",
        r"\bdata conversion\b",
    ]),
    ("Data / BI Analyst", [
        r"\bdata analyst", r"\bdata analysis\b",
        r"\bbusiness intelligence\b", r"\bbi developer\b", r"\bbi analyst\b",
        r"\bbi &", r"\bpower bi\b", r"\btableau\b",
        r"\banalytics engineer\b", r"\bdata analytics\b",
        r"\breporting analyst\b", r"\bdata governance\b",
        r"\bdata quality\b", r"\bdata catalog\b", r"\bdata specialist\b",
        r"\bdata management\b",
    ]),
    ("Testing / QA", [
        r"\bqa\b", r"\bquality assurance\b", r"\btest engineer\b",
        r"\bsdet\b", r"\btesting\b", r"\buat\b", r"\btest system",
        r"\bquality engineer\b",
    ]),
    ("DevOps / Cloud / Infra", [
        r"\bdevops\b", r"\bsite reliability\b", r"\bsre\b",
        r"\bplatform engineer\b", r"\bcloud engineer\b", r"\bcloud arch",
        r"\baws engineer\b", r"\binfrastructure engineer\b",
        r"\bsystems? engineer\b", r"\bnetwork engineer\b",
        r"\bsecurity engineer\b", r"\bdeployment engineer\b",
        r"\bdata center\b", r"\breliability engineer\b",
        r"\bkubernetes\b", r"\bsys admin\b", r"\bsystem admin\b",
        r"\bdisaster recovery\b",
    ]),
    ("Software Engineering", [
        r"\bsoftware eng", r"\bsoftware dev",
        r"\bfull.?stack\b", r"\bfullstack\b", r"\bfull stack\b",
        r"\bfrontend\b", r"\bfront.?end\b", r"\bbackend\b", r"\bback.?end\b",
        r"\bweb developer\b", r"\bweb engineer\b",
        r"\b\.net developer\b", r"\bjava developer\b", r"\bjava engineer\b",
        r"\bpython developer\b", r"\breact developer\b", r"\bangular developer\b",
        r"\bnode\.?js\b", r"\bios engineer\b", r"\bandroid engineer\b",
        r"\bmobile engineer\b", r"\bembedded\b", r"\bcompiler\b",
        r"\bblockchain\b", r"\bsalesforce dev",
        r"\bprogrammer\b", r"\bcobol\b", r"\bscala\b",
        r"\bsde\b", r"\bapplication developer\b", r"\bapplication builder\b",
        r"\bapplication eng\b",
        r"developer$", r"\bdev engineer\b",
        r"\bdesign technologist\b",
        r"\bagentic engineer\b",
    ]),
    ("Project / Program Manager", [
        r"\bproject manag", r"\bprogram manag", r"\bproject coord",
        r"\bprogram coord", r"\bproject schedul", r"\bscrum master\b",
        r"\bproject support\b",
    ]),
    ("Product Management", [
        r"\bproduct manag", r"\bproduct owner\b", r"\bproduct line manag",
    ]),
    ("Business Analyst", [
        r"\bbusiness analyst\b", r"\bbusiness analysis\b",
        r"\bbusiness systems analyst\b", r"\bbusiness process analyst\b",
        r"\bbusiness consultant\b", r"\berp.*analyst\b",
        r"\bbsa\b", r"\bbusiness data analyst\b",
        r"\bsap.*analyst\b", r"\bjde.*analyst\b",
    ]),
    ("UX / Design", [
        r"\bux\b", r"\bui\b", r"\buser experience\b", r"\buser interface\b",
        r"\bproduct design", r"\bgraphic design", r"\bvisual design",
        r"\bcreative design", r"\bpresentation design",
        r"\binteraction design",
    ]),
    ("Database / DBA", [
        r"\bdatabase\b", r"\bdba\b", r"\bpl/sql\b", r"\boracle dev",
        r"\bsql developer\b",
    ]),
    ("Supply Chain / Logistics", [
        r"\bsupply chain\b", r"\blogistic", r"\binventory\b",
        r"\bprocurement\b", r"\bsourcing analyst\b", r"\bplanner\b",
        r"\bplanning analyst\b", r"\bwarehouse\b", r"\bdistribution\b",
        r"\bmaterials analyst\b",
    ]),
    ("Finance / Accounting", [
        r"\bfinancial analyst\b", r"\bfinance\b", r"\baccounting\b",
        r"\bactuari", r"\btreasury\b", r"\bcredit\b", r"\brisk\b",
        r"\baudit\b", r"\bcompliance\b", r"\bbilling analyst\b",
        r"\bpayroll\b", r"\bwealth management\b", r"\bfund\b",
    ]),
]


def categorize(title):
    if not title or title.strip() == "NA":
        return "Other"
    t = title.strip().lower()
    for category, patterns in RULES:
        for pat in patterns:
            if re.search(pat, t):
                return category
    return "Other"


# ── Categorize all rows ────────────────────────────────────────────
for r in clean_rows:
    r["category"] = categorize(r.get("job_title", ""))

categories = collections.Counter(r["category"] for r in clean_rows)
print("=== CATEGORY COUNTS ===")
for cat, count in categories.most_common():
    pct = count / len(clean_rows) * 100
    print(f"  {cat:30s}  {count:>5}  ({pct:.1f}%)")
print(f"  {'TOTAL':30s}  {len(clean_rows):>5}")

# ── Source × Category ──────────────────────────────────────────────
source_cat = {}
for src in sorted(KNOWN_SOURCES):
    source_cat[src] = collections.Counter(
        r["category"] for r in clean_rows if r["source"] == src
    )

# ── Sort categories by count (descending) for plotting ─────────────
cat_order = [c for c, _ in categories.most_common()]

# ── Colors ─────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.0)
cat_colors = {
    "Software Engineering":     "#4C78A8",
    "AI / ML":                  "#E45756",
    "Data Engineering":         "#F58518",
    "Data / BI Analyst":        "#72B7B2",
    "Data Science":             "#FF9DA7",
    "Business Analyst":         "#9D755D",
    "Project / Program Manager":"#54A24B",
    "Product Management":       "#EECA3B",
    "Testing / QA":             "#B279A2",
    "UX / Design":              "#D67195",
    "DevOps / Cloud / Infra":   "#439894",
    "Supply Chain / Logistics":  "#9ECF9A",
    "Finance / Accounting":     "#BAB0AC",
    "Database / DBA":           "#76B7B2",
    "Other":                    "#CCCCCC",
}

fig = plt.figure(figsize=(22, 26))
fig.suptitle("Job Listings by Category — 4,040 scraped jobs (Feb 26, 2026)",
             fontsize=18, fontweight="bold", y=0.98)

# ═══════════════════════════════════════════════════════════════════
# 1 — Horizontal bar: jobs per category
# ═══════════════════════════════════════════════════════════════════
ax1 = fig.add_subplot(3, 2, 1)
cat_names = list(reversed(cat_order))
cat_counts = [categories[c] for c in cat_names]
colors1 = [cat_colors.get(c, "#999") for c in cat_names]
bars1 = ax1.barh(cat_names, cat_counts, color=colors1, edgecolor="white", height=0.7)
ax1.bar_label(bars1, padding=3, fontsize=9)
ax1.set_title("Jobs by Category", fontsize=14, fontweight="bold", pad=12)
ax1.set_xlabel("Number of Listings")
ax1.tick_params(axis="y", labelsize=9)

# ═══════════════════════════════════════════════════════════════════
# 2 — Pie chart (main categories only, group small into "Other")
# ═══════════════════════════════════════════════════════════════════
ax2 = fig.add_subplot(3, 2, 2)
PIE_THRESHOLD = 50
pie_data = {}
pie_other = 0
for c, cnt in categories.most_common():
    if cnt >= PIE_THRESHOLD and c != "Other":
        pie_data[c] = cnt
    else:
        pie_other += cnt
pie_data["Other (combined)"] = pie_other

pie_labels = list(pie_data.keys())
pie_sizes = list(pie_data.values())
pie_colors = [cat_colors.get(l, cat_colors["Other"]) for l in pie_labels]
wedges, texts, autotexts = ax2.pie(
    pie_sizes, labels=pie_labels,
    autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
    colors=pie_colors, startangle=140, textprops={"fontsize": 9},
    pctdistance=0.8,
)
for t in autotexts:
    t.set_fontsize(9)
ax2.set_title("Category Distribution", fontsize=14, fontweight="bold", pad=12)

# ═══════════════════════════════════════════════════════════════════
# 3 — Stacked bar: Source × Category (top 10 categories)
# ═══════════════════════════════════════════════════════════════════
ax3 = fig.add_subplot(3, 2, (3, 4))
top_cats = cat_order[:10]
src_names = sorted(KNOWN_SOURCES)
src_colors = {"Glassdoor": "#4C78A8", "Indeed": "#F58518", "linkedin": "#54A24B"}
x = np.arange(len(top_cats))
width = 0.25
for i, src in enumerate(src_names):
    vals = [source_cat[src].get(c, 0) for c in top_cats]
    ax3.bar(x + i * width, vals, width, label=src, color=src_colors[src], edgecolor="white")
ax3.set_xticks(x + width)
ax3.set_xticklabels(top_cats, rotation=35, ha="right", fontsize=10)
ax3.set_ylabel("Number of Listings")
ax3.set_title("Top 10 Categories × Source", fontsize=14, fontweight="bold", pad=12)
ax3.legend(fontsize=11)
ax3.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# ═══════════════════════════════════════════════════════════════════
# 5 — Top job titles within the 5 requested categories
# ═══════════════════════════════════════════════════════════════════
focus_cats = ["Software Engineering", "Data Engineering", "Data / BI Analyst",
              "AI / ML", "Project / Program Manager", "Testing / QA",
              "Product Management", "Data Science"]
ax5 = fig.add_subplot(3, 2, 5)
# Build top titles per focus category
cat_top_titles = {}
for cat in focus_cats:
    titles = collections.Counter(
        r["job_title"] for r in clean_rows
        if r["category"] == cat and r.get("job_title", "").strip() != "NA"
    )
    cat_top_titles[cat] = titles.most_common(3)

# Flat list for grouped horizontal bar
labels = []
values = []
colors_bar = []
for cat in reversed(focus_cats):
    for title, count in reversed(cat_top_titles[cat]):
        short = title[:35] + "..." if len(title) > 35 else title
        labels.append(f"{short}")
        values.append(count)
        colors_bar.append(cat_colors.get(cat, "#999"))
    labels.append(f"── {cat} ──")
    values.append(0)
    colors_bar.append("white")

bars5 = ax5.barh(range(len(labels)), values, color=colors_bar, edgecolor="white", height=0.7)
ax5.set_yticks(range(len(labels)))
ax5.set_yticklabels(labels, fontsize=7.5)
ax5.bar_label(bars5, padding=3, fontsize=8)
ax5.set_title("Top 3 Titles per Key Category", fontsize=14, fontweight="bold", pad=12)
ax5.set_xlabel("Count")

# ═══════════════════════════════════════════════════════════════════
# 6 — Location heatmap: top metros × focus categories
# ═══════════════════════════════════════════════════════════════════
ax6 = fig.add_subplot(3, 2, 6)

def normalize_location(loc):
    if not loc:
        return None
    loc = loc.title().strip()
    loc = re.sub(r",?\s*United States$", "", loc).strip().rstrip(",")
    mapping = {
        "New York": ["New York, Ny", "New York City, Ny", "Nyc, Ny", "Manhattan, Ny", "Brooklyn, Ny"],
        "Seattle": ["Seattle, Wa"],
        "SF Bay Area": ["San Francisco, Ca", "San Jose, Ca", "Palo Alto, Ca", "Mountain View, Ca",
                         "Sunnyvale, Ca", "Santa Clara, Ca", "Menlo Park, Ca", "Redwood City, Ca"],
        "Chicago": ["Chicago, Il"],
        "Austin": ["Austin, Tx"],
        "Atlanta": ["Atlanta, Ga"],
        "Boston": ["Boston, Ma", "Cambridge, Ma"],
        "Dallas-FW": ["Dallas, Tx", "Fort Worth, Tx", "Irving, Tx", "Plano, Tx"],
        "Washington DC": ["Washington, Dc", "Arlington, Va", "Mclean, Va", "Reston, Va"],
        "Remote": ["Remote"],
    }
    for metro, variants in mapping.items():
        if loc in [v.title() for v in variants]:
            return metro
    return loc

for r in clean_rows:
    r["metro"] = normalize_location(r.get("location", "").strip() if r.get("location", "") != "NA" else "")

top_metros = ["New York", "SF Bay Area", "Seattle", "Chicago", "Dallas-FW",
              "Boston", "Austin", "Atlanta", "Washington DC", "Remote"]
heat_cats = ["Software Engineering", "AI / ML", "Data Engineering",
             "Data / BI Analyst", "Project / Program Manager", "Product Management"]

heat_data = []
for metro in top_metros:
    row_data = []
    for cat in heat_cats:
        count = sum(1 for r in clean_rows if r["metro"] == metro and r["category"] == cat)
        row_data.append(count)
    heat_data.append(row_data)

heat_arr = np.array(heat_data)
im = ax6.imshow(heat_arr, cmap="YlOrRd", aspect="auto")
ax6.set_xticks(range(len(heat_cats)))
ax6.set_xticklabels(heat_cats, rotation=35, ha="right", fontsize=9)
ax6.set_yticks(range(len(top_metros)))
ax6.set_yticklabels(top_metros, fontsize=10)
for i in range(len(top_metros)):
    for j in range(len(heat_cats)):
        val = heat_arr[i, j]
        color = "white" if val > heat_arr.max() * 0.6 else "black"
        ax6.text(j, i, str(val), ha="center", va="center", fontsize=9, color=color)
ax6.set_title("Metro × Category Heatmap", fontsize=14, fontweight="bold", pad=12)
fig.colorbar(im, ax=ax6, shrink=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.95])
out = "/Users/hasheerama/projects/Resume-pipeline/jobs_categorized.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print(f"\nSaved visualization to {out}")

# ── Also save categorized CSV ──────────────────────────────────────
out_csv = "/Users/hasheerama/projects/Resume-pipeline/jobs_categorized.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["category", "job_title", "employer_name", "location", "source", "job_url"]
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in sorted(clean_rows, key=lambda x: x["category"]):
        writer.writerow({k: r.get(k, "") for k in fieldnames})
print(f"Saved categorized CSV to {out_csv}")
