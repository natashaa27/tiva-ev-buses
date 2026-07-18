# Phase 2 — Image Analytics for Brand Optimization

**Project:** Multimodal AI Strategy for EV-Bus Market Disruption in India
**Assignment coverage:**
- **Task 2.1** — extract low-level and high-level visual features + identify feature ↔ perception correlations
- **Strategic Output** — Ad-Campaign Optimization Playbook (visual-aesthetic recommendations)

## Folder contents

```
Phase_2_Image_Analytics/
├── README.md                        ← this file
├── notebooks/
│   └── 04_image_analysis.ipynb      ← THE consolidated end-to-end notebook (run this)
├── scripts/
│   ├── pipeline_lib.py              ← all feature/model/orchestration logic (imported by the notebook)
│   ├── run_full_pipeline.py         ← CLI mirror of the notebook (same outputs, headless)
│   └── run_image_pipeline.py / run_ocr_step.py / run_blip_step.py   ← legacy 3-step scripts (superseded)
├── data/
│   ├── ev_bus_image_analysis.csv    ← master table: 1 row/image × ~67 cols
│   ├── image_rag_documents.jsonl    ← RAG-ready docs (handoff to Phase 3)
│   └── perception_coding_template.csv ← BLANK sheet for human/independent coders (1–7 Likert)
├── outputs/
│   ├── charts/                      ← feature dists, high-level flags, setting mix, perception proxy, feature×perception heatmap, etc.
│   └── reports/
│       ├── strategic_output.md      ← main playbook (F1–F6, F6a, N1–N3)
│       ├── feature_perception_tests.{json,md}  ← the 5 hypothesis tests
│       ├── strategic_findings_from_ocr.md
│       ├── blip_captions.md
│       ├── feature_dictionary.md    ← what every column means
│       └── summary_stats.json
└── images/                          ← source images (JPG / jpeg / png)
```

## Pipeline coverage

- **Low-level (12):** brightness, saturation, contrast, sharpness, warm/cool hue, dominant colours, colourfulness (Hasler-Süsstrunk), edge density, symmetry (H/V), rule-of-thirds, visual balance, figure-ground separation.
- **High-level:** BLIP caption + **DETR** object detection (bus/person/truck counts) + **CLIP** zero-shot for charger/depot, wheelchair-ramp/low-floor access, bus-in-motion, fleet-scale deployment, government handover, urban/natural/indoor/infographic setting, product-showcase-vs-operational-proof, and technology/comfort/trust/sustainability themes.
- **Text:** Tesseract OCR + VADER narrative-framing sentiment + LDA topics.
- **Perception (7):** trust, modernity, comfort, accessibility, environmental-friendliness, operational-readiness, visual-appeal — as a CLIP zero-shot **proxy** (`pxy_*`, 0–100) **plus** a blank human-coder template.
- **Feature → perception:** the 5 spec hypotheses tested (`outputs/reports/feature_perception_tests.md`).

## How to reproduce

Python env with `torch, torchvision, transformers, timm, opencv-python-headless, pillow, scikit-learn, scipy, vaderSentiment, pytesseract, pandas, matplotlib, seaborn`. Tesseract binary installed at OS level (`sudo apt-get install -y tesseract-ocr`). On this machine the env is at `../.venv`.

```
# either run the notebook end-to-end:
jupyter notebook notebooks/04_image_analysis.ipynb
# or the headless CLI equivalent (identical outputs):
python scripts/run_full_pipeline.py
```

First run downloads BLIP + DETR + CLIP (~2 GB, cached afterwards). Both entrypoints call `scripts/pipeline_lib.py`, so results are identical.

### Perception scores — proxy vs human
`pxy_*` are automated CLIP proxies, **not** measured human perception. To use real ratings: have coders fill `data/perception_coding_template.csv` (1–7 per dimension), load + join on `image_id`, then re-run `pipeline_lib.hypothesis_tests(df, perception_prefix="coder_")`.

## Key findings (see `outputs/reports/strategic_output.md` for full playbook)

| Tag | Finding |
|---|---|
| **F1** | Legacy OEMs are publicly framed as *"priced out"* of largest EV bus tenders. |
| **F2** | Visual share-of-voice is being led by challengers (PMI Electro, Eka, Olectra). |
| **F3** | Bright + sharp + cool-leaning visuals correlate with positive framing (Spearman ρ ≈ +0.37 / +0.36 / −0.37; n=20). |
| **F4** | Corpus is 95% square + portrait — only 1 landscape asset → long-form / YouTube / CTV under-invested. |
| **F5** | 50% of assets fall below retina-grade sharpness. |
| **F6** | GCC/financing framing is a live public conversation legacy OEMs can own. |
| **F6a** | BLIP visual captioning fails on 60% of the corpus — corpus is infographic-first, not product-first. |
| **N1** | Only 38% of images actually contain a bus. |
| **N2** | Zero images depict passengers, drivers, mechanics, or depot service context. |
| **N3** | Corpus contains provenance impurities (truck comparison images, phone screenshots). |

## Limitations
- n = 21 → all correlations and share-of-voice numbers are **exploratory**.
- No engagement metrics attached to any image → "perception" is proxied by narrative-framing sentiment (VADER on OCR), not measured audience response.
- Manual OEM / operator / lifecycle tagging on each row still to be filled by the analyst.
- Corpus over-represents CV/truck comparison content; needs bus-specific expansion to ≥150 images.
