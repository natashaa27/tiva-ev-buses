"""Phase 2 · end-to-end image-analytics runner (CLI mirror of the notebook).

Runs every stage on all images in `images/` and writes structured outputs:

  data/ev_bus_image_analysis.csv        master table (1 row/image, all features)
  data/image_rag_documents.jsonl        RAG-ready docs (handoff to Phase 3)
  data/perception_coding_template.csv   blank sheet for human/independent coders
  outputs/reports/summary_stats.json    corpus-level summary
  outputs/reports/feature_perception_tests.json / .md   the 5 hypothesis tests
  outputs/reports/strategic_findings_from_ocr.md        OCR sentiment + LDA
  outputs/reports/blip_captions.md
  outputs/reports/feature_dictionary.md                 what every column means
  outputs/charts/*.png                                   charts

Usage:  python scripts/run_full_pipeline.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_lib as L

sns.set_style("whitegrid")

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
DATA = ROOT / "data"
CHARTS = ROOT / "outputs" / "charts"
REPORTS = ROOT / "outputs" / "reports"
for d in (DATA, CHARTS, REPORTS):
    d.mkdir(parents=True, exist_ok=True)


def ar_bucket(r):
    return "portrait (<0.9)" if r < 0.9 else ("landscape (>1.1)" if r > 1.1 else "square (~1:1)")


def main():
    print(f"Images dir: {IMAGES}  |  device: {L._device()}")
    df = L.build_dataframe(IMAGES, verbose=True)
    print(f"\nBuilt master table: {len(df)} images x {df.shape[1]} columns")

    df = L.add_sentiment(df)
    topics = L.lda_topics(df)
    df["ar_bucket"] = df["aspect_ratio"].apply(ar_bucket)

    # ---- save master CSV ----
    csv = DATA / "ev_bus_image_analysis.csv"
    df.to_csv(csv, index=False)
    print(f"Wrote {csv}  ({df.shape[1]} cols)")

    # ---- perception coder template ----
    tmpl = L.perception_template(df)
    tmpl_path = DATA / "perception_coding_template.csv"
    tmpl.to_csv(tmpl_path, index=False)
    print(f"Wrote {tmpl_path}")

    # ---- RAG JSONL ----
    meta_cols = ["brightness", "contrast", "saturation", "sharpness", "colourfulness",
                 "edge_density", "warm_cool_bias", "palette_family", "hl_setting",
                 "hl_bus_visible", "hl_passenger_driver_visible", "hl_charger_depot_flag",
                 "hl_accessibility_flag", "hl_fleet_scale_deploy", "hl_operational_proof_flag",
                 "obj_bus_count", "obj_person_count", "nf_label", "nf_compound",
                 "pxy_trust", "pxy_modernity", "pxy_comfort", "pxy_accessibility",
                 "pxy_env_friendliness", "pxy_operational_readiness", "pxy_visual_appeal"]
    jsonl = DATA / "image_rag_documents.jsonl"
    with open(jsonl, "w", encoding="utf-8") as f:
        for _, r in df.iterrows():
            doc = {
                "doc_id": r["image_id"], "modality": "image", "file_path": r["file_path"],
                "text_for_index": f"CAPTION: {r.get('blip_caption','')}\nOCR: {r.get('ocr_text','')}",
                "metadata": {k: (None if (isinstance(r.get(k), float) and pd.isna(r.get(k))) else r.get(k))
                             for k in meta_cols},
            }
            f.write(json.dumps(doc, ensure_ascii=False, default=str) + "\n")
    print(f"Wrote {jsonl}")

    # ---- hypothesis tests ----
    tests = L.hypothesis_tests(df, perception_prefix="pxy_")
    with open(REPORTS / "feature_perception_tests.json", "w") as f:
        json.dump(tests, f, indent=2, default=str)
    with open(REPORTS / "feature_perception_tests.md", "w") as f:
        f.write("# Phase 2 · Feature → Perception hypothesis tests\n\n")
        f.write("_Perception = CLIP zero-shot **proxy** (`pxy_*`, 0-100). Re-run on human "
                "`coder_*` ratings once `perception_coding_template.csv` is filled. "
                f"n={len(df)} — exploratory._\n\n")
        for t in tests:
            f.write(f"## {t['id']}. {t['question']}\n\n")
            f.write(f"- **Test:** {t['test']}\n")
            f.write(f"- **Result:** `{t['result']}`\n")
            f.write(f"- **Reads as:** {t['reads']}\n")
            r = t["result"]
            if isinstance(r, dict) and "delta" in r and r["delta"] is not None:
                verdict = "SUPPORTS" if r["delta"] > 0 else "does NOT support"
                f.write(f"- **Direction:** {verdict} the hypothesis (Δ={r['delta']:+}, "
                        f"n_true={r['n_true']}, n_false={r['n_false']}).\n")
            elif isinstance(r, dict) and "rho" in r and r["rho"] is not None:
                verdict = "SUPPORTS" if r["rho"] > 0 else "does NOT support"
                f.write(f"- **Direction:** {verdict} the hypothesis (ρ={r['rho']:+}, p={r['p']}, n={r['n']}).\n")
            f.write("\n")
    print("Wrote feature_perception_tests.{json,md}")

    # ---- OCR findings md ----
    with open(REPORTS / "strategic_findings_from_ocr.md", "w") as f:
        cov = int(100 * (df["ocr_char_len"] > 0).mean())
        f.write("# Phase 2 · OCR-backed findings (addendum)\n\n")
        f.write(f"**{len(df)} images**, OCR text on {(df['ocr_char_len']>0).sum()} ({cov}% coverage), "
                f"median chars/image = {int(df['ocr_char_len'].median())}.\n\n")
        f.write("## Narrative-framing sentiment (VADER on OCR — framing, not consumer perception)\n\n")
        mix = df["nf_label"].value_counts().to_dict()
        f.write("| Label | Count |\n|---|---:|\n")
        for k, v in mix.items():
            f.write(f"| {k} | {v} |\n")
        f.write("\n## LDA topics on OCR corpus\n\n")
        for k, top in topics:
            f.write(f"- **Topic {k}:** {', '.join(top)}\n")
    print("Wrote strategic_findings_from_ocr.md")

    # ---- BLIP captions md ----
    with open(REPORTS / "blip_captions.md", "w") as f:
        f.write("# BLIP visual captions\n\n| Image ID | Setting | Caption |\n|---|---|---|\n")
        for _, r in df.iterrows():
            f.write(f"| {r['image_id'][:8]} | {r['hl_setting']} | {r['blip_caption']} |\n")
    print("Wrote blip_captions.md")

    # ---- feature dictionary ----
    write_feature_dictionary(REPORTS / "feature_dictionary.md")

    # ---- summary stats ----
    def q(c):
        return dict(min=float(df[c].min()), median=float(df[c].median()),
                    mean=float(df[c].mean()), max=float(df[c].max()), std=float(df[c].std()))
    lowlevel = ["brightness", "contrast", "saturation", "sharpness", "warm_cool_bias",
                "colourfulness", "edge_density", "symmetry_h", "symmetry_v",
                "rule_of_thirds", "visual_balance", "figure_ground_sep", "aspect_ratio"]
    summary = {
        "n_images": len(df),
        "low_level": {c: q(c) for c in lowlevel},
        "palette_family": df["palette_family"].value_counts().to_dict(),
        "ar_bucket": df["ar_bucket"].value_counts().to_dict(),
        "hl_setting": df["hl_setting"].value_counts().to_dict(),
        "high_level_flag_rates": {c: round(float(df[c].mean()), 3) for c in
                                  ["hl_bus_visible", "hl_passenger_driver_visible",
                                   "hl_charger_depot_flag", "hl_accessibility_flag",
                                   "hl_bus_in_motion_flag", "hl_fleet_scale_deploy",
                                   "hl_govt_handover_flag", "hl_operational_proof_flag"]},
        "objects_total": {"bus": int(df["obj_bus_count"].sum()),
                          "person": int(df["obj_person_count"].sum()),
                          "truck": int(df["obj_truck_count"].sum())},
        "perception_proxy_mean": {d: round(float(df[f'pxy_{d}'].mean()), 1) for d in L.PERCEPTION_DIMS},
        "theme_flag_rates": {c: round(float(df[c + '_flag'].mean()), 3) for c in
                             ["theme_technology", "theme_comfort", "theme_trust", "theme_sustainability"]},
    }
    with open(REPORTS / "summary_stats.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("Wrote summary_stats.json")

    make_charts(df)
    print("\n=== DONE ===")
    print(f"n={len(df)}  cols={df.shape[1]}")
    print("high-level flag rates:", summary["high_level_flag_rates"])
    print("perception proxy means:", summary["perception_proxy_mean"])


def write_feature_dictionary(path):
    rows = [
        ("brightness", "low", "Mean grayscale luminance (0-255)"),
        ("contrast", "low", "Std-dev of grayscale luminance"),
        ("saturation", "low", "Mean HSV saturation (0-255)"),
        ("sharpness", "low", "Variance of Laplacian (focus/detail)"),
        ("warm_cool_bias", "low", "+ warm / − cool colour bias (−1..1)"),
        ("colourfulness", "low", "Hasler-Süsstrunk perceived colourfulness"),
        ("edge_density", "low", "Fraction of Canny-edge pixels (visual busyness)"),
        ("symmetry_h / _v", "low", "Left-right / top-bottom mirror symmetry (0-1)"),
        ("rule_of_thirds", "low", "Share of gradient energy near the 4 thirds points"),
        ("visual_balance", "low", "Left/right + top/bottom energy balance (0-1)"),
        ("figure_ground_sep", "low", "Centre-vs-border detail ratio (subject isolation)"),
        ("dominant_colors / palette_family", "low", "KMeans top-3 colours + bucket"),
        ("blip_caption", "high", "BLIP scene caption"),
        ("obj_bus/person/truck_count", "high", "DETR (COCO) object counts @0.7"),
        ("hl_bus_visible", "high", "Bus present (DETR or CLIP fleet)"),
        ("hl_passenger_driver_visible", "high", "Person present (DETR)"),
        ("hl_charger_depot_flag", "high", "CLIP: charger/depot visible"),
        ("hl_accessibility_flag", "high", "CLIP: wheelchair ramp / low-floor visible"),
        ("hl_bus_in_motion_flag", "high", "CLIP: bus in motion vs parked"),
        ("hl_fleet_scale_deploy", "high", "Fleet-scale deployment (DETR≥3 or CLIP)"),
        ("hl_govt_handover_flag", "high", "CLIP: govt handover/launch ceremony"),
        ("hl_operational_proof_flag", "high", "CLIP: real operation vs product showcase"),
        ("hl_setting", "high", "CLIP argmax: urban / natural / indoor_studio / infographic_text"),
        ("theme_* (_flag)", "high", "CLIP: technology / comfort / trust / sustainability"),
        ("ocr_text, nf_*", "text", "Tesseract OCR + VADER narrative-framing sentiment"),
        ("pxy_* (0-100)", "perception", "CLIP zero-shot PROXY for 7 perception dims"),
        ("coder_* ", "perception", "Blank — human/independent coder 1-7 ratings"),
    ]
    with open(path, "w") as f:
        f.write("# Phase 2 · Feature dictionary\n\n| Column | Layer | Meaning |\n|---|---|---|\n")
        for c, layer, desc in rows:
            f.write(f"| `{c}` | {layer} | {desc} |\n")
        f.write("\n> `pxy_*` are automated CLIP proxies, **not** human perception. "
                "Fill `perception_coding_template.csv` with real coders to replace them.\n")


def make_charts(df):
    # 1. low-level feature distributions (all 12)
    feats = ["brightness", "contrast", "saturation", "sharpness", "colourfulness",
             "edge_density", "symmetry_h", "rule_of_thirds", "visual_balance",
             "figure_ground_sep", "warm_cool_bias", "aspect_ratio"]
    fig, axs = plt.subplots(3, 4, figsize=(15, 9))
    for ax, c in zip(axs.ravel(), feats):
        ax.hist(df[c].dropna(), bins=10, color="#2980b9", edgecolor="white")
        ax.axvline(df[c].median(), color="k", ls="--", lw=1)
        ax.set_title(f"{c}\n(median={df[c].median():.2f})", fontsize=9)
    fig.suptitle("Low-level visual features (all 12)", fontsize=13)
    plt.tight_layout(); plt.savefig(CHARTS / "fig_feature_distributions.png", dpi=140); plt.close()

    # 2. palette strip
    top = [tuple(eval(r) if isinstance(r, str) else r) for r in df["top_color_rgb"]]
    fig, ax = plt.subplots(figsize=(12, 1.4))
    for i, (r, g, b) in enumerate(top):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=(r/255, g/255, b/255)))
    ax.set_xlim(0, len(top)); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Dominant colour per image (palette strip)")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_palette_strip.png", dpi=140); plt.close()

    # 3. high-level flag rates
    flags = {"bus visible": "hl_bus_visible", "person visible": "hl_passenger_driver_visible",
             "charger/depot": "hl_charger_depot_flag", "accessibility": "hl_accessibility_flag",
             "in motion": "hl_bus_in_motion_flag", "fleet-scale": "hl_fleet_scale_deploy",
             "govt handover": "hl_govt_handover_flag", "operational proof": "hl_operational_proof_flag"}
    rates = {k: 100 * df[v].mean() for k, v in flags.items()}
    plt.figure(figsize=(7, 4))
    pd.Series(rates).sort_values().plot(kind="barh", color="#8e44ad")
    plt.xlabel("% of corpus"); plt.title("High-level feature presence (%)")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_high_level_flags.png", dpi=140); plt.close()

    # 4. setting mix
    plt.figure(figsize=(6, 3))
    df["hl_setting"].value_counts().plot(kind="barh", color="#27ae60")
    plt.title("Scene setting (CLIP)"); plt.xlabel("Image count")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_setting_mix.png", dpi=140); plt.close()

    # 5. perception proxy radar-ish bar
    means = [df[f"pxy_{d}"].mean() for d in L.PERCEPTION_DIMS]
    plt.figure(figsize=(7, 4))
    plt.barh(L.PERCEPTION_DIMS, means, color="#e67e22")
    plt.axvline(50, color="k", ls="--", lw=0.8)
    plt.xlabel("proxy score (0-100)"); plt.title("Perception proxy — corpus mean (CLIP)")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_perception_proxy.png", dpi=140); plt.close()

    # 6. feature x perception correlation heatmap
    lowfeats = ["brightness", "contrast", "saturation", "sharpness", "colourfulness",
                "edge_density", "warm_cool_bias", "rule_of_thirds", "visual_balance", "figure_ground_sep"]
    pxy = [f"pxy_{d}" for d in L.PERCEPTION_DIMS]
    corr = df[lowfeats + pxy].corr(method="spearman").loc[lowfeats, pxy]
    plt.figure(figsize=(9, 6))
    sns.heatmap(corr, annot=True, fmt="+.2f", cmap="RdBu_r", center=0, cbar_kws={"label": "Spearman ρ"})
    plt.title(f"Low-level feature × perception proxy (Spearman, n={len(df)})")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_feature_perception_corr.png", dpi=140); plt.close()

    # 7. narrative sentiment mix
    plt.figure(figsize=(5, 2.8))
    order = ["positive", "neutral", "negative", "no_text"]
    counts = [df["nf_label"].value_counts().get(l, 0) for l in order]
    plt.bar(order, counts, color=["#27ae60", "#95a5a6", "#c0392b", "#bdc3c7"])
    plt.title("Narrative-framing sentiment (VADER/OCR)"); plt.ylabel("Images")
    plt.tight_layout(); plt.savefig(CHARTS / "fig_narrative_sentiment_mix.png", dpi=140); plt.close()

    print("Wrote 7 charts to", CHARTS)


if __name__ == "__main__":
    main()
