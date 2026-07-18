# Brand Visual Comparison — Ad-Campaign Instagram Corpus

**Scope:** the same 10-post Instagram corpus behind `campaign_report.html` (Tata n=4, Olectra n=4, Switch n=2 — **no EKA**; EKA only exists in the separate video corpus, `Phase_2_Video_Analytics/`). This folder checks four specific comparisons requested on top of that report: dominant palette per image, palette family, the feature↔perception heatmap, and feature distributions — each split Tata vs. the new-age brands.

> **Read this as a compass, not a verdict — more than the main report.** n=10 total, split 4 / 4 / **2**. The Switch group in particular is two data points; any "Switch mean" below is really just the midpoint of two individual posts, not a brand tendency. Correlations run at n=4 and n=6 are included because they were asked for, not because they're statistically stable — a single image can flip their sign.

Reproduce: `../../.venv/bin/python3 build_comparison.py` (regenerates `charts/*.png` and `brand_visual_comparison.csv`). Palette extraction and family classification reuse Phase 2's exact `dominant_colours()` / `classify_palette()` functions, so labels are defined identically across the whole project.

---

## 1. Dominant palette per image — `charts/01_dominant_palette_per_image.png`

Each post's real k=3 k-means palette (stacked by pixel share), grouped by brand.

- **Tata (#1, #7, #9, #10):** the most *visually consistent* set in the corpus — every post has a near-black lower band (~35–45% share) topped by a light gray-blue. This is a studio/product-shot signature, not a coincidence: three of four Tata posts are dominated by `dark/black` as their top cluster (see §2).
- **Olectra (#3, #4, #6, #8):** the most *varied* set — a warm tan/beige (#4), a vivid saturated blue (#6), and two dark-anchored posts (#3, #8). No single palette signature.
- **Switch (#2, #5):** polar opposites of each other — #2 (Gateway of India double-decker) is warm brown/red; #5 (Prawaas fleet) is cool blue. At n=2, "Switch's palette" isn't a thing yet; these are two unrelated creative choices.

**Read:** Tata's four posts look like they came from one brand book. Olectra's and Switch's don't — consistent with the main report's finding that new-age creative is more varied/EV-native-saturated (colourfulness 70 vs. 46) but also less standardized.

---

## 2. Palette family — `charts/02_palette_family_by_brand.png`

| Brand | dark/black | neutral/gray | cool (blue) |
|---|---:|---:|---:|
| Tata (n=4) | **3** | 0 | 1 |
| Olectra (n=4) | 1 | **2** | 1 |
| Switch (n=2) | 1 | 0 | 1 |

No post in this corpus classified as `white`, `green`, `warm (red/orange)`, or `mixed` under Phase 2's rule — worth flagging as a **methodology limitation, not a content finding**: `classify_palette()` buckets by raw RGB-channel deltas, and dark saturated colours (e.g. post 2's warm brown `(47,33,22)`) can fall through to `neutral/gray` because the channel gaps shrink at low absolute brightness even though the hue clearly reads warm to the eye. Treat family counts as directional; trust the actual swatches in §1 over the label.

**Read:** Tata leans dark/black 3-of-4; Olectra is the only brand with any neutral/gray reads; nobody leans warm or green. Given n=4/4/2 and the labelling caveat above, this is suggestive, not a finding to build a creative rule on.

---

## 3. Feature ↔ perception correlation — `charts/03_feature_perception_heatmap_by_brand.png`

Spearman ρ, Tata (n=4) vs. Olectra+Switch (n=6) vs. full corpus (n=10), features (rows) against the seven 1–5 perception scores (columns).

**The two relationships that hold in *both* brand groups AND the full corpus** — these are the closest thing in this dataset to a brand-independent signal, for what a 10-post corpus can support:

| Relationship | Tata (n=4) | New-age (n=6) | Full (n=10) |
|---|---:|---:|---:|
| warm_cool_ratio → Appeal | **+0.77** | **+0.89** | **+0.83** |
| txt_overlay → Modernity | **−0.82** | −0.41 | **−0.61** |

Warmer-toned images read as more appealing, and text-dense images read as less modern, regardless of brand.

**Where the two groups disagree sharply** — these are the "difference" the request asked about, and each is n=4 vs. n=6, so read direction only, not magnitude:

- **Brightness → Comfort:** Tata **+0.95** (near-perfect) vs. new-age **+0.21** (weak). For Tata's four posts, brighter almost perfectly predicts "feels comfortable"; for Olectra/Switch it barely moves.
- **Brightness → Operational readiness:** Tata **+0.95** vs. new-age **−0.35** — opposite sign. Same caution: 4 and 6 points respectively.
- **Edge density → Trust:** new-age **+0.88** vs. Tata **+0.26**. Crisp, detailed imagery tracks trust much more strongly in the Olectra/Switch posts than in Tata's.
- **Access. column is entirely undefined ("–") for the new-age group.** All six Olectra+Switch posts were scored an identical 2/5 on perceived accessibility — zero variance, so no correlation is computable. This isn't a gap in the analysis; it's the finding: **nothing in six new-age posts differentiates on accessibility at all**, which lines up exactly with the main report's content-flag result (0% of all 10 posts show a ramp/accessibility cue).

---

## 4. Feature distribution by brand — `charts/04_feature_distribution_by_brand.png`

Dots = individual posts, bar = mean (box plots were deliberately not used — they'd imply quartile structure from 2–4 points that isn't there).

| Feature | Tata (n=4) | Olectra (n=4) | Switch (n=2) |
|---|---:|---:|---:|
| Brightness | 140.8 | 132.4 | 152.2 |
| Contrast | 67.7 | 64.6 | 56.2 |
| Saturation | 81.0 | **119.4** | 113.9 |
| Colourfulness | 46.0 | **74.7** | 60.6 |
| Sharpness | 575.5 | 586.2 | **208.5** |
| Edge density | 0.056 | 0.059 | 0.031 |
| Warm/cool ratio | 0.3 | 1.1 | 52.3* |
| Text overlay % | 12.5 | 16.0 | 22.5 |

\* **Switch's warm/cool mean is not representative of either post** — it's the average of two opposite extremes (#2 warm-dominant ≈104, #5 cool-dominant ≈0.02), not a brand tendency. Flagged rather than smoothed over.

- **Saturation and colourfulness reproduce the main report's headline number** (Tata 46 vs. new-age ~70 colourfulness) inside this more granular view — Olectra alone (74.7) drives more of that gap than Switch (60.6).
- **Sharpness is Switch's real outlier**, not warm/cool: both Switch posts (208, 300 approx.) sit well below every Tata and Olectra post (450–835). At n=2 this could be two soft source images rather than a brand pattern — worth checking against source-asset resolution before treating it as a creative-quality finding.
- **Text overlay rises monotonically Tata → Olectra → Switch** (12.5 → 16.0 → 22.5), with Switch's high end driven by the Prawaas fleet-milestone post — the same post the main report already flagged as under-performing its own fleet's average engagement.

---

## 5. Net read

Everything above is consistent with, and adds texture to, the main `campaign_analysis.md` finding — it does not overturn it. Tata's four posts are visually the most *disciplined* (consistent dark palette, brightness that reliably predicts comfort). Olectra and Switch are more *saturated and varied*, but that variety comes with weaker, less predictable feature→perception relationships and, for accessibility specifically, no differentiation at all. The two relationships that survive across every cut of this data — warm tone → appeal, less on-image text → more modern — are the only ones worth treating as a creative rule at this sample size; everything else is a lead to re-test once the corpus grows past double digits.
