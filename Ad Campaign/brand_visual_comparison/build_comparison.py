"""Brand visual comparison — Ad Campaign Instagram corpus (n=10).

Compares Tata (legacy, n=4) vs. Olectra (new-age, n=4) vs. Switch (new-age, n=2)
on: dominant palette per image, palette family, feature<->perception
correlation, and low-level feature distributions.

Reuses Phase 2's exact dominant_colours() / classify_palette() so palette-family
labels are defined identically across the whole project.

Run: ../../.venv/bin/python3 build_comparison.py
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent          # .../Ad Campaign
PROJECT = ROOT.parent                                    # .../ev_bus
sys.path.insert(0, str(PROJECT / "Phase_2_Image_Analytics" / "scripts"))
from pipeline_lib import dominant_colours, classify_palette  # noqa: E402

OUT = Path(__file__).resolve().parent
CHARTS = OUT / "charts"
CHARTS.mkdir(exist_ok=True)

BRAND_COLOR = {"Tata": "#3B6FE0", "Olectra": "#12A594", "Switch": "#C9A227"}
BRAND_ORDER = ["Tata", "Olectra", "Switch"]

df = pd.read_csv(ROOT / "campaign_dataset.csv")
df["brand"] = pd.Categorical(df["brand"], categories=BRAND_ORDER, ordered=True)
df = df.sort_values(["brand", "post"]).reset_index(drop=True)

# --------------------------------------------------------------------------- #
# 1. Recompute dominant palette (k=3) per image with Phase 2's exact method
# --------------------------------------------------------------------------- #
records = []
for _, row in df.iterrows():
    img_path = ROOT / "images" / row["file"]
    bgr = cv2.imread(str(img_path))
    if bgr is None:
        print(f"WARN: could not read {img_path}")
        continue
    dc = dominant_colours(bgr, k=3)
    top_rgb = dc[0][0]
    records.append({
        "post": row["post"], "brand": row["brand"], "account": row["account"],
        "palette": dc,  # list of (rgb, share) most-common first
        "top_rgb": top_rgb,
        "palette_family": classify_palette(top_rgb),
    })
pal_df = pd.DataFrame(records)
merged = df.merge(pal_df[["post", "palette", "top_rgb", "palette_family"]], on="post")

# save a reproducible per-image table
save_df = merged.copy()
save_df["palette"] = save_df["palette"].apply(json.dumps)
save_df["top_rgb"] = save_df["top_rgb"].apply(list)
save_df[["post", "brand", "account", "top_rgb", "palette_family", "palette",
         "brightness", "saturation", "contrast", "colorfulness", "sharpness",
         "edge_density", "warm_cool_ratio", "txt_overlay",
         "p_trust", "p_modernity", "p_comfort", "p_access", "p_sustain",
         "p_operready", "p_appeal"]].to_csv(OUT / "brand_visual_comparison.csv", index=False)
print(f"Saved brand_visual_comparison.csv ({len(save_df)} rows)")

# --------------------------------------------------------------------------- #
# CHART 1 — dominant palette strip per image, grouped by brand
# --------------------------------------------------------------------------- #
fig, axes = plt.subplots(1, len(merged), figsize=(1.35 * len(merged), 4.6))
prev_brand = None
for ax, (_, r) in zip(axes, merged.iterrows()):
    y = 0.0
    for rgb, share in r["palette"]:
        ax.add_patch(mpatches.Rectangle((0, y), 1, share, color=np.array(rgb) / 255))
        y += share
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    label_color = BRAND_COLOR[r["brand"]]
    ax.set_title(f"#{r['post']}", fontsize=9, color=label_color, fontweight="bold")
    ax.set_xlabel(r["brand"], fontsize=8, color=label_color)
    if r["brand"] != prev_brand:
        ax.add_patch(mpatches.Rectangle((-0.06, -0.02), 0.02, 1.04, transform=ax.transAxes,
                                         clip_on=False, color=label_color))
        prev_brand = r["brand"]
fig.suptitle("Dominant palette per image (k=3 k-means clusters, stacked by share)\n"
             "Ad-Campaign Instagram corpus — grouped by brand", fontsize=12, y=1.04)
fig.tight_layout()
fig.savefig(CHARTS / "01_dominant_palette_per_image.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved 01_dominant_palette_per_image.png")

# --------------------------------------------------------------------------- #
# CHART 2 — palette family x brand matrix
# --------------------------------------------------------------------------- #
fam_order = ["dark/black", "white", "neutral/gray", "cool (blue)", "green",
             "warm (red/orange)", "mixed"]
present_fams = [f for f in fam_order if f in merged["palette_family"].unique()]
mat = pd.crosstab(merged["brand"], merged["palette_family"]).reindex(
    index=BRAND_ORDER, columns=present_fams, fill_value=0)

fig, ax = plt.subplots(figsize=(1.15 * len(present_fams) + 2, 3.2))
im = ax.imshow(mat.values, cmap="Blues", vmin=0, vmax=max(2, mat.values.max()), aspect="auto")
ax.set_xticks(range(len(present_fams))); ax.set_xticklabels(present_fams, rotation=25, ha="right", fontsize=9)
ax.set_yticks(range(len(BRAND_ORDER))); ax.set_yticklabels(
    [f"{b}  (n={ (merged['brand']==b).sum() })" for b in BRAND_ORDER], fontsize=9)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat.values[i, j]
        ax.text(j, i, str(v), ha="center", va="center",
                color="white" if v >= mat.values.max() * 0.6 else "#333", fontsize=11, fontweight="bold")
ax.set_title("Palette family by brand — count of images\n(top dominant-color cluster, classified with Phase 2's rule)", fontsize=11)
fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03, label="image count")
fig.tight_layout()
fig.savefig(CHARTS / "02_palette_family_by_brand.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved 02_palette_family_by_brand.png")

# --------------------------------------------------------------------------- #
# CHART 3 — feature <-> perception heatmaps: Tata vs New-age, + full corpus
# --------------------------------------------------------------------------- #
FEATURES = ["brightness", "contrast", "saturation", "colorfulness", "sharpness",
            "edge_density", "warm_cool_ratio", "txt_overlay"]
PERCEPT = ["p_trust", "p_modernity", "p_comfort", "p_access", "p_sustain", "p_operready", "p_appeal"]
PERCEPT_LABEL = ["Trust", "Modernity", "Comfort", "Access.", "Sustain.", "Op. ready", "Appeal"]

def corr_matrix(sub: pd.DataFrame) -> np.ndarray:
    mat = np.full((len(FEATURES), len(PERCEPT)), np.nan)
    for i, f in enumerate(FEATURES):
        for j, p in enumerate(PERCEPT):
            if sub[f].nunique() < 2 or sub[p].nunique() < 2:
                continue
            rho, _ = spearmanr(sub[f], sub[p])
            mat[i, j] = rho
    return mat

groups = {
    f"Tata (legacy, n={(merged['brand']=='Tata').sum()})": merged[merged["brand"] == "Tata"],
    f"Olectra + Switch (new-age, n={(merged['brand']!='Tata').sum()})": merged[merged["brand"] != "Tata"],
    f"Full corpus (n={len(merged)})": merged,
}

fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6))
for k, (ax, (title, sub)) in enumerate(zip(axes, groups.items())):
    cmat = corr_matrix(sub)
    im = ax.imshow(cmat, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(PERCEPT))); ax.set_xticklabels(PERCEPT_LABEL, rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(len(FEATURES)))
    ax.set_yticklabels(FEATURES if k == 0 else [""] * len(FEATURES), fontsize=8)
    ax.tick_params(axis="y", length=0 if k else 3.5)
    for i in range(cmat.shape[0]):
        for j in range(cmat.shape[1]):
            v = cmat[i, j]
            txt = "–" if np.isnan(v) else f"{v:+.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                     color="white" if not np.isnan(v) and abs(v) > 0.55 else "#222")
    ax.set_title(title, fontsize=10)
fig.subplots_adjust(wspace=0.12)
fig.suptitle("Feature ↔ perception correlation (Spearman ρ) — by brand group\n"
             "⚠ n=4 / n=6 per group: illustrative only — a single image can flip the sign at this sample size",
             fontsize=11, y=1.06, color="#8a3d00")
fig.colorbar(im, ax=axes, fraction=0.02, pad=0.015, label="Spearman ρ")
fig.savefig(CHARTS / "03_feature_perception_heatmap_by_brand.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved 03_feature_perception_heatmap_by_brand.png")

# --------------------------------------------------------------------------- #
# CHART 4 — low-level feature distributions by brand (dot/strip, not box —
# n=2-4 per brand makes quartile-implying boxplots misleading)
# --------------------------------------------------------------------------- #
DIST_FEATURES = ["brightness", "contrast", "saturation", "colorfulness",
                  "sharpness", "edge_density", "warm_cool_ratio", "txt_overlay"]
fig, axes = plt.subplots(2, 4, figsize=(15, 7))
rng = np.random.default_rng(7)
for ax, feat in zip(axes.flat, DIST_FEATURES):
    for xi, b in enumerate(BRAND_ORDER):
        vals = merged.loc[merged["brand"] == b, feat].values
        jitter = rng.uniform(-0.09, 0.09, size=len(vals))
        ax.scatter(np.full(len(vals), xi) + jitter, vals, color=BRAND_COLOR[b],
                   s=55, zorder=3, edgecolor="white", linewidth=0.6)
        if len(vals):
            ax.hlines(vals.mean(), xi - 0.22, xi + 0.22, color=BRAND_COLOR[b], linewidth=2.4, zorder=4)
    ax.set_xticks(range(len(BRAND_ORDER))); ax.set_xticklabels(BRAND_ORDER, fontsize=9)
    ax.set_title(feat, fontsize=10)
    ax.grid(axis="y", alpha=0.25)
fig.suptitle("Low-level feature distribution by brand — dots = individual posts, bar = mean\n"
             "(n=4 Tata · n=4 Olectra · n=2 Switch — box plots would overstate precision at this n)",
             fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig(CHARTS / "04_feature_distribution_by_brand.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved 04_feature_distribution_by_brand.png")

# --------------------------------------------------------------------------- #
# Console summary used to help write FINDINGS.md
# --------------------------------------------------------------------------- #
print("\n=== Mean low-level features by brand ===")
print(merged.groupby("brand", observed=True)[DIST_FEATURES].mean().round(1).to_string())
print("\n=== Mean perception scores by brand ===")
print(merged.groupby("brand", observed=True)[PERCEPT].mean().round(2).to_string())
print("\n=== Palette family by brand ===")
print(mat.to_string())
