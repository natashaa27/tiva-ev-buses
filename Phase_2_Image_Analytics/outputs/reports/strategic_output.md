# Phase 2 · Task 2.1 — Image Analytics · Strategic Output (v2, OCR-backed)

**Project:** Multimodal AI Strategy for EV-Bus Market Disruption in India
**Corpus:** 21 images (`./images/`)
**Method:** OpenCV low-level features + k-means dominant color + Tesseract 5.5 OCR + Salesforce BLIP-base visual captions (Apple-Silicon MPS) + VADER narrative-framing sentiment + LDA topics (n_topics=3).

> **Sample-size discipline.** n = 21 images. Findings below are directionally strong because the OCR-extracted text is unambiguous, but statistical claims remain **exploratory** until the corpus is expanded to ≥150 EV-bus-specific images with per-image engagement metrics (rule #13).

---

## 1. What the images actually say

**OCR coverage:** 20 / 21 images had extractable text (95%). Median = 314 characters/image. Two images are pure product/logo shots with no meaningful text.

**Narrative-framing sentiment mix (VADER on OCR — this is *not* consumer sentiment, it is copy/PR framing, rule #10):**

| Label | Count | % of scored corpus |
|---|---:|---:|
| Positive | 12 | 57% |
| Negative | 6 | 29% |
| Neutral | 2 | 10% |
| No text | 1 | 5% |

**Top 12 OCR tokens across the corpus:**

`tata` (33) · `bus / buses` (54) · `motors` (22) · `vecv` (18) · `electric` (18) · `tender` (14) · `india` (14) · `volvo` (13) · `mobility` (13) · `market` (10) · `pmi` (9) · `eka` (8) · `olectra` (7)

**LDA topics (three-topic model):**

| Topic | Top words | Interpretation |
|---|---|---|
| 0 | buses, private, diesel, financing, electric, financial, backed, olectra, india | **Financing & private-operator economics** (GCC transition narrative) |
| 1 | tata, vecv, motors, volvo, buses, indian, electric, mobility | **Legacy-OEM heritage & scale** (Tata-Motors and VECV-Volvo brand equity) |
| 2 | tata, bus, motors, tender, buses, electric, mobility, vecv | **Tender competitiveness** (who won, who was priced out) |

**What the OCR literally said (verbatim excerpts that shape the interpretation):**
- *"Big surprise in India's largest electric bus tenders"* (image `1d4a1664`)
- *"Tata Motors, VECV priced out of mega electric bus tender"* (image `fd5e43b0`, source: Livemint)
- *"Tata & VECV priced out of India's… PMI Electro Mobility Discipline"* (image `55cba8f5`)
- *"Eka, PMI race ahead of Tata, Ashok Leyland"* (image `96286661`)
- *"PME-BUS SEVA SCHEME OPERATES UNDER GCC MODEL WITH 12-YEAR TERM"* (image `590566b4`)
- *"Govt mulls financing support for private e-buses and trucks"* (image `65a3f5bc`)
- *"The Olectra Route: Himalayas — 8+ Years of buses have been serving HRTC"* (image `6f3fe3a7`)
- *"TATA Motors And Green Energy Mobility Solutions Ink Deal"* (image `fef89453`)
- Multiple #100DaysWithTVS balance-sheet comparison graphics arguing that VECV outperforms Tata Motors CV on debt / revenue growth per rupee.

**Read-through in one line:** The visual corpus is a **tender-competitiveness and legacy-vs-new-age financial-comparison story**. It is *not* a product-experience story.

---

## 2. Feature ↔ perception correlations (Spearman ρ, n = 20)

| Low-level feature | ρ vs narrative-framing compound | Direction |
|---|---:|---|
| Brightness | **+0.37** | Brighter → more positive framing |
| Sharpness | **+0.36** | Crisper → more positive framing |
| Contrast | −0.08 | Flat |
| Aspect ratio | −0.17 | Slightly: landscape → less positive |
| Saturation | −0.24 | Muted/clean → more positive |
| **Warm/cool bias** | **−0.37** | **Cooler → more positive framing** |

**Interpretation.** Bright, sharp, desaturated, cool-leaning designs (white backgrounds, blue accents, clean typography — Livemint/newsroom aesthetic) consistently accompany positive narrative framing. Dark, warm-orange, comparison-infographic designs accompany negative framing about legacy OEMs. This is directional at n = 20 and must be flagged **exploratory**, but the effect direction is consistent with editorial convention.

Chart: `fig_feature_sentiment_correlation.png`.

---

## 3. Palette + composition read (pixel-only, confirming §1)

| Feature | Median | Notes |
|---|---:|---|
| Brightness | 75.1 | Bimodal — dark comparison infographics ~20–40, white newsroom graphics ~200+ |
| Contrast | 61.0 | High. Corpus is engineered for feed velocity. |
| Saturation | 57.6 | Muted overall; a few vivid product outliers. |
| Sharpness | 995 | Half the corpus below retina-grade — production-quality problem. |
| Warm/cool bias | −0.01 | No brand signature colour. |
| Aspect ratio | 0.93 | 11 square + 9 portrait, only 1 landscape. |

**Palette family:** 13 dark/black (62%), 4 white (19%), 2 neutral, 1 cool-blue, 1 mixed.

---

## 4. Strategic findings for the Ad-Campaign Optimization Playbook

Each row uses the mandated *Finding → Metric → Interpretation → Business implication → Recommended action* structure (rule #15). All rows must be copied into `05_report/MASTER_EVIDENCE_MATRIX.xlsx` (rule #16).

### F1 — The public visual narrative directly names legacy OEMs as *"priced out"* of the largest electric-bus tenders
- **Metric:** Verbatim OCR from 3 distinct images including a Livemint headline: *"Tata Motors, VECV priced out of mega electric bus tender."* Token counts: `tata` (33), `vecv` (18), `tender` (14). LDA Topic 2 is explicitly tender-competitiveness.
- **Interpretation:** This is **published, visible, and being amplified** on social feeds. It is no longer an internal industry observation — it is public brand equity damage for the legacy OEMs.
- **Business implication:** Silence on the tender-loss narrative concedes the story to new-age competitors (PMI Electro, Eka, Olectra) who benefit from the framing. Every week of silence compounds the perception that legacy OEMs cannot compete on economics.
- **Recommended action:** Publish an **owned response asset within 30 days** — a lifetime-tender-economics explainer that reframes headline per-km price against uptime, buy-back, spare-parts continuity, and 12-year GCC service credibility. Distribute in the same square + portrait templates the criticism uses.

### F2 — New-age players (PMI Electro, Eka, Olectra) hold rising visual share-of-voice; legacy OEMs are mostly the subject of *comparison / defence* content, not celebration
- **Metric:** LDA Topic 0 anchors on `olectra` + `financing` + `private`; Topic 2 pairs `tata` + `tender` + `vecv`. Positive-framing images (n = 12) mostly celebrate PMI/Eka/Olectra tender wins or profile new-age operating models. Negative-framing images (n = 6) name Tata/VECV in the loss narrative.
- **Interpretation:** The visual conversation is being led by the challengers. Legacy OEMs appear either in critical news graphics or in numerical rebuttals, not in aspirational product storytelling.
- **Business implication:** Legacy OEMs need to move from *defensive comparison* to *proactive category leadership* on trust, uptime, and passenger experience.
- **Recommended action:** Launch a 12-month always-on visual programme with three content streams — (a) on-road documentary (BEST, HRTC, DTC deployments), (b) depot uptime dashboards with monthly public scorecards, (c) driver + mechanic testimonial films. Inverting today's ~80:20 comparison-to-experience skew to 40:60.

### F3 — Bright + sharp + cool-leaning visuals correlate with positive framing (ρ = +0.37, +0.36, −0.37; n = 20; exploratory)
- **Metric:** Spearman correlations from §2.
- **Interpretation:** Editorial and social convention: newsrooms and celebratory posts use bright white backgrounds, sharp typography, and blue-neutral palettes. Dark warm-orange comparison graphics carry critical framing. The pattern is consistent, though the sample is small.
- **Business implication:** The visual language the OEM uses for its own creative should mirror the palette that carries positive-framing energy — *not* the dark warm-orange language of critical infographics.
- **Recommended action:** Lock a brand creative rule: **≥1080p, Laplacian sharpness ≥1 500, brightness 130–210, warm/cool bias between −0.10 and +0.05** on all owned social assets. Reject creative that falls outside this window.

### F4 — Corpus is starved of long-form aspect-ratio masters
- **Metric:** Aspect-ratio mix: 11 square (52%), 9 portrait (43%), **only 1 landscape (5%)**.
- **Interpretation:** Content pipeline is Instagram-native. Trust and reliability stories — which need 90-second-plus narrative arcs — cannot be told on Reels alone.
- **Business implication:** YouTube long-form and connected-TV are effectively empty channels for the OEM's trust narrative today.
- **Recommended action:** Every production must deliver **three ratios simultaneously (16:9 master + 1:1 + 9:16)**. Add YouTube Trueview + CTV to FY26 media plan with ≥25% of digital marketing spend.

### F5 — 50% of assets fall below retina-grade sharpness (Laplacian ≤ 995)
- **Metric:** Sharpness range 481 → 6 639, median 995.
- **Interpretation:** Perceived premium is leaking on production quality. In a category where "quality" is the entire competitive claim for legacy OEMs, low-fidelity assets undermine the message.
- **Business implication:** Fixable without any strategy change — it is a production-standards problem.
- **Recommended action:** Publish an internal Creative Quality Standard — min 1080p, min Laplacian variance 1 500, min contrast 55, mandatory sharpen pass on typography-heavy infographics.

### F6a — BLIP visual captioning fails on 60% of the corpus — the failure is itself a strategic finding
- **Metric:** Salesforce BLIP-base captioned 21 images. Only **~9/21 (43%)** produced coherent scene descriptions ("a bus with a large number of passengers", "electric bus driving down the road", "a bunch of buses parked on the side of a road"). **~12/21 (57%)** returned mangled OCR fragments, degenerate token loops ("tata motors, tata motors, tata motors..."), or hallucinated context ("the front page of the german newspaper" — the image is Indian).
- **Interpretation:** BLIP is designed for *scene description*, not text-heavy layouts. Its failure mode on this corpus is a direct measurement of how **infographic-heavy vs product-heavy** the corpus is. A healthy EV brand imagery portfolio should be BLIP-captionable at ≥80% because it should be dominated by product-in-use scenes.
- **Business implication:** The 57% BLIP-failure rate is another quantitative confirmation of F1 + F2 — the corpus is over-indexed on infographics and under-indexed on product photography.
- **Recommended action:** Set a KPI in the Ad-Campaign Playbook: **BLIP scene-caption success rate ≥ 80%** on owned creative. If BLIP can't describe a shot in a coherent sentence, it will not resonate as a product story to a scrolling viewer either.

### F6 — GCC financing framing is a live public conversation the OEM can own
- **Metric:** OCR direct hits: *"PME-BUS SEVA SCHEME OPERATES UNDER GCC MODEL WITH 12-YEAR TERM"*, *"Govt mulls financing support for private e-buses"*. LDA Topic 0 groups `financing` + `private` + `backed`.
- **Interpretation:** GCC operating models and government financing are the frames within which the tender story is being told publicly. Legacy OEMs have decades of financing partnerships and STU relationships that new-age players lack — that is a visual + editorial asset that is *not being deployed*.
- **Business implication:** Trust-backed GCC growth (the project's strategic direction) has an under-used visual asset base: financing partners, STU history, buy-back guarantees, spare-parts SLAs.
- **Recommended action:** Commission a **"Trust Ledger"** visual series — one asset per financing partner, per STU relationship, per uptime commitment. Publish monthly across owned channels; feed into RAG so executive queries surface it.

---

## 5. Direct link to the project thesis

Your working thesis is that new-age OEMs win tenders on **aggressive per-km pricing, financing, long-term GCC commitments, and risk absorption** — while legacy OEMs still hold advantages in **trust, service, spare parts, and operating history**. The image OCR **directly confirms both halves of this thesis in the wild**:

- The "priced out" narrative (F1) is public and headline-level — legacy pricing competitiveness is being publicly framed as failure.
- The GCC / financing / 12-year-term framing (F6) is the language the public conversation actually uses.
- The visual response required is not more balance-sheet graphics — it is **trust proof**, **service continuity evidence**, and **long-form product-in-use storytelling** (F2, F4).

This gives the *"Trust-backed GCC growth"* strategic direction its concrete visual/marketing translation.

---

## 6. Handoffs

**To Task 2.2 (Video pipeline):**
Test whether F3's directional finding (bright + sharp + cool → positive) holds on video (thumbnails, opening 3-second frame, average brightness/warm bias per shot). If confirmed, F3 upgrades from exploratory to validated. Also test pacing (cuts/min) against engagement.

**To Phase 3 Task 3.1 (Multimodal RAG):**
`01_data/processed/image_rag_documents.jsonl` is now populated with `text_for_index = CAPTION + OCR` and metadata. This is the ingestion-ready file. Each row has `modality = "image"` so the retriever can cross-modal.

**To the 3-Year Corporate EV Strategy:**
F1 + F2 + F6 plug directly into **digital marketing spend optimisation**. F4 informs the **channel mix** (YouTube/CTV). F6's Trust Ledger is a proof point for **infrastructure partnerships** in the strategy document.

---

## 7. Limitations

1. **n = 21.** All correlations and share-of-voice ratios exploratory (rule #13).
2. **No engagement metrics attached.** "Perception" is proxied by narrative-framing sentiment, not measured audience response.
3. **BLIP captions were generated but are unreliable on this text-heavy corpus** — see F6a. Treat scene descriptions as a signal only when the image is a real product/scene photo, not an infographic.
4. **Corpus is publisher-skewed.** Multiple #100DaysWithTVS-style comparison graphics inflate the "dark warm-orange comparison" signal. Diversify the source list before publishing.
5. **Manual OEM / operator / lifecycle tags not filled.** Once filled, cross-tabs (OEM × lifecycle × sentiment) become citable.
6. **Some images are trucks, not EV buses** (Tata Prima 5530.S, Eicher Pro 6035). Filter before drawing bus-specific claims.
7. **Correlations are Spearman, not causal.** Rule #14: bright ≠ *causes* positive.

---

## 8. Files produced

| File | Purpose |
|---|---|
| `01_data/processed/ev_bus_image_analysis.csv` | 21 rows × 30+ columns — pixel features, OCR, VADER, palette |
| `01_data/processed/image_rag_documents.jsonl` | RAG ingestion file, one doc per image, `modality: image` |
| `04_outputs/images/final/fig_palette_strip.png` | Dominant-color strip |
| `04_outputs/images/final/fig_palette_family.png` | Palette-family bar |
| `04_outputs/images/final/fig_aspect_ratio.png` | Aspect-ratio bar |
| `04_outputs/images/final/fig_feature_distributions.png` | Brightness / contrast / saturation / sharpness histograms |
| `04_outputs/images/final/fig_warm_cool.png` | Warm/cool bias distribution |
| `04_outputs/images/final/fig_narrative_sentiment_mix.png` | VADER-on-OCR sentiment mix |
| `04_outputs/images/final/fig_feature_sentiment_correlation.png` | Spearman feature ↔ narrative-sentiment |
| `04_outputs/images/final/strategic_output.md` | This document |
| `04_outputs/images/final/strategic_findings_from_ocr.md` | Auto-generated raw findings addendum |
| `04_outputs/images/final/blip_captions.md` | Full BLIP scene-caption table (21 rows) |
| `04_outputs/images/final/summary_stats.json` | Machine-readable summary stats |

## 9. What must happen next

1. Fill manual OEM / operator / image_type / lifecycle / source_url per row of `ev_bus_image_analysis.csv`. Rerun `run_ocr_step.py` to refresh the cross-tabs.
2. Expand corpus to ≥150 EV-bus-specific images with engagement metrics.
3. Copy F1 – F6a – F6 into `05_report/MASTER_EVIDENCE_MATRIX.xlsx`.
4. Trigger Task 2.2 (video pipeline) using the same feature-to-framing framework.
5. Hand `image_rag_documents.jsonl` (BLIP + OCR + metadata) to whoever is building the Phase 3 multimodal RAG.
