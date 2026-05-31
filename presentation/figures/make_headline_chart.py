#!/usr/bin/env python3
"""Render the headline-result bar chart for the ICAIBD presentation.

Bars = ARC-AGI-2 accuracy; cost/task printed underneath each bar.
Palette matches slides.md (accent deep-blue family).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Deck palette
ACCENT = "#0F3D7C"
ACCENTMID = "#3B6FB0"
MUTED = "#A9BFD9"   # frontier models
GRAYREF = "#7A8794"  # human reference
INK = "#1A1A1A"

# Try Helvetica to match the deck; fall back gracefully
for fam in ("Helvetica", "Helvetica Neue", "Arial"):
    try:
        font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except Exception:
        continue
plt.rcParams["font.size"] = 13

# (label, accuracy %, cost, role)  -- sorted by accuracy descending
rows = [
    ("Human\nPanel",            100.0, "$17.00",  "human"),
    ("This work\n(public eval)", 76.1, "$19.69",  "ours"),
    ("This work\n(private)",     72.9, "$38.99",  "ours"),
    ("GPT-5.2 Pro\n(High)",      54.2, "$15.72",  "frontier"),
    ("Opus 4.5\n(64K)",          37.6, "$2.40",   "frontier"),
    ("Gemini 3\nPro",            31.1, "$0.81",   "frontier"),
]

colors = {"human": GRAYREF, "ours": ACCENT, "frontier": MUTED}

labels = [r[0] for r in rows]
vals = [r[1] for r in rows]
costs = [r[2] for r in rows]
bar_colors = [colors[r[3]] for r in rows]

fig, ax = plt.subplots(figsize=(10.5, 5.0), dpi=200)
x = range(len(rows))
bars = ax.bar(x, vals, width=0.62, color=bar_colors, zorder=3)

# Value labels on top of bars
for xi, v, role in zip(x, vals, [r[3] for r in rows]):
    ax.text(xi, v + 1.6, f"{v:.1f}%",
            ha="center", va="bottom",
            fontsize=14, fontweight="bold",
            color=ACCENT if role == "ours" else INK, zorder=4)

# Cost row beneath the system names
for xi, c in zip(x, costs):
    ax.text(xi, -0.20, c, ha="center", va="top",
            fontsize=12, color=GRAYREF,
            transform=ax.get_xaxis_transform())
ax.text(-0.62, -0.20, "Cost/task:", ha="right", va="top",
        fontsize=11, color=GRAYREF, style="italic",
        transform=ax.get_xaxis_transform())

# Axis cosmetics
ax.set_ylim(0, 108)
ax.set_ylabel("ARC-AGI-2 accuracy (pass@2)", fontsize=13, color=INK)
ax.set_xticks(list(x))
ax.set_xticklabels(labels, fontsize=12.5, color=INK)
ax.tick_params(axis="x", length=0, pad=8)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=11, color=GRAYREF)
ax.grid(axis="y", color="#D8DEE8", linewidth=0.8, zorder=0)
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#C7CED8")

# extra bottom margin for the cost row
plt.subplots_adjust(bottom=0.22, top=0.95, left=0.08, right=0.98)
out = "figures/headline_results.png"
fig.savefig(out, dpi=200, facecolor="white")
print("wrote", out)
