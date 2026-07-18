# Multimodal AI Strategy for EV-Bus Market Disruption in India

MBA group project analyzing disruption in the Indian electric-bus market — how new-age OEMs (Olectra, Switch Mobility, Eka) are winning tenders and mindshare against legacy players (Tata Motors) — using text, image, video, and retrieval-augmented (RAG) analysis, culminating in a board-facing 3-year strategy and pitch deck.

Assignment brief: `Group Project Assignment_TIVA AI_2026.pdf`.

## Project structure

```
Phase_1_Text Analytics/       Text corpus, sentiment/lifecycle/topic analysis, tender/market data audit
Phase_2_Image_Analytics/      Visual feature extraction + feature↔perception analysis, ad-optimization playbook
Phase_2_Video_Analytics/      Frame-level visual/OCR/theme analysis of 4 brand videos (EKA, Olectra, Switch, Tata)
Phase_3_RAG_and_Strategy/     Multimodal CLIP RAG index (609 docs) + executive queries + 3-year corporate strategy
Ad Campaign/                  Instagram creative teardown (10 posts) + Tata vs. Olectra/Switch brand comparison
```

Each phase folder has its own `README.md` with reproduction steps; this file is the top-level map.

## Phases

### Phase 1 — Text Analytics
Establishes a reproducible, audited text-analysis pipeline before extending to other modalities.
- **Inputs:** 548-row merged text corpus (YouTube comments + Instagram posts, mixed provenance, explicitly disclosed), corrected tender table, market/policy/OEM benchmark tables.
- **Work:** data cleaning, VADER sentiment, LDA topic modeling, legacy-vs-new-age camp comparison, lifecycle classification.
- **Governance:** heavy audit trail (`PHASE1_DECISIONS.md`, `METHODOLOGY.md`, `DATA_DICTIONARY.md`, `audit_outputs/`) — tracks which files are authoritative evidence vs. synthetic/unverified and must not be used for findings.
- Notebooks: `02_notebooks/01_text_data_preparation.ipynb`, `02_lifecycle_classification.ipynb`, `03_final_text_analysis.ipynb`.

### Phase 2 — Image Analytics
Extracts low- and high-level visual features from ~21 competitor images and tests feature↔perception correlations.
- **Low-level (12 features):** brightness, saturation, contrast, sharpness, warm/cool hue, dominant colours, colourfulness, edge density, symmetry, rule-of-thirds, visual balance, figure-ground separation.
- **High-level:** BLIP captioning, DETR object detection, CLIP zero-shot tagging (charger/depot, accessibility, fleet-scale, government handover, themes), Tesseract OCR + VADER narrative sentiment, LDA topics.
- **Perception:** 7-dimension CLIP zero-shot proxy (trust, modernity, comfort, accessibility, sustainability, operational-readiness, appeal) plus a blank template for human coders.
- **Output:** `outputs/reports/strategic_output.md` — an ad-campaign optimization playbook (findings F1–F6, N1–N3).
- Notebook: `notebooks/04_image_analysis.ipynb` (consolidated, run via shared `pipeline_lib.py`); CLI equivalent `scripts/run_full_pipeline.py`.

### Phase 2 — Video Analytics
Frame-level analysis (1 fps, up to 120 frames/video, 480 frames total) of 4 brand videos: `eka.mp4`, `olectra.mp4`, `switch.mp4`, `tata.mp4`.
- Per-video metrics: shot cuts/min, brightness, contrast, saturation, sharpness, warm/cool bias, colourfulness, edge density, visual balance, figure-ground separation, OCR text-frame %, and text-theme tagging (battery tech, safety, comfort, technology, sustainability, reliability).
- Notebooks: `notebooks/05_video_analytics.ipynb` (local) and `05_video_analytics_colab.ipynb` (the run actually executed, per `outputs/pipeline_run_summary.json`, dated 2026-07-18).

### Phase 3 — Multimodal RAG & Strategy
Builds a single 609-document cross-modal CLIP-ViT-B/32 (512-d) retrieval index spanning:
- Phase 1 text corpus (548 docs), Phase 2 image corpus (39 docs, caption+OCR+features fused), Statista chart exports (6, visual-layout indexed), rendered IEA/BNEF/MoHI market charts (6), and sourced market-trend text (10).
- **Task 3.2:** 8 executive strategic queries answered via retrieval + `gpt-4o-mini` synthesis, with cite-only-evidence discipline (`outputs/executive_queries/`).
- **Strategic Output:** `outputs/strategy/3_year_corporate_ev_strategy.md` — 4 board pillars (Market Positioning, Infrastructure Partnerships, Battery Supply-Chain Risk, Digital Marketing Spend) across Y1/Y2/Y3, plus governance, risks, and evidence-gap disclosure.
- Video assets (Task 2.2) are intentionally excluded from the RAG index.
- Notebook: `notebooks/05_multimodal_rag.ipynb`.

### Ad Campaign
Instagram creative teardown of 10 competitor posts (Tata n=4, Olectra n=4, Switch n=2 — no EKA in this corpus).
- Combines pixel-level features (contrast, sharpness, colourfulness, symmetry), hand-coded content flags (25+, e.g. real-deployment, accessibility, government livery), and single-coder 1–5 perception scores, tied to engagement rate (verified follower counts except Olectra, which is estimated).
- Key result: contrast is the only statistically significant ER predictor (Spearman ρ=+0.72, p=0.02); real-operation imagery drives trust; zero posts show charging/accessibility/depot content — flagged as the category's biggest content gap.
- `brand_visual_comparison/` drills the same corpus into Tata vs. Olectra/Switch palette, feature-distribution, and feature↔perception differences.
- Report: `campaign_analysis.md` / `campaign_report.html`; data: `campaign_dataset.csv`.

### Supplementary data
`Phase_2_Video_Analytics/reels/dataset_instagram-reel-scraper_olectra.csv` and `..._tatamotors.csv` — raw Apify Instagram Reel scrapes (captions, engagement, hashtags, media URLs) not yet folded into any phase pipeline.

## Environment

Single shared virtual environment at `.venv/` (Python 3.11), used by Phases 2 and 3 (`torch`-CPU, `transformers`, `timm`, `opencv-python-headless`, `vaderSentiment`, `pytesseract`, `openai`, `python-dotenv`, `scikit-learn`, `pandas`, `matplotlib`, `seaborn`). Phase 1 defines its own `requirements.txt`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r "Phase_1_Text Analytics/requirements.txt"
# plus Phase 2/3 image+RAG deps: torch torchvision transformers timm opencv-python-headless \
#   pillow scikit-learn scipy vaderSentiment pytesseract pandas matplotlib seaborn openai python-dotenv
sudo apt-get install -y tesseract-ocr   # OS-level OCR binary, required by Phase 2
```

Phase 3 reads `OPENAI_KEY` from `Phase_2_Image_Analytics/.env` (or a local `.env`) for `gpt-4o-mini` synthesis.

## Reproduction order

1. `Phase_1_Text Analytics/` notebooks (01 → 02 → 03) — produces the text corpus + sentiment/lifecycle outputs feeding Phase 3.
2. `Phase_2_Image_Analytics/notebooks/04_image_analysis.ipynb` — produces `image_rag_documents.jsonl` feeding Phase 3.
3. `Phase_2_Video_Analytics/notebooks/05_video_analytics_colab.ipynb` — standalone; not currently ingested by Phase 3's RAG index.
4. `Ad Campaign/` — standalone teardown of a separate 10-post Instagram corpus; `brand_visual_comparison/build_comparison.py` reuses Phase 2's palette functions.
5. `Phase_3_RAG_and_Strategy/notebooks/05_multimodal_rag.ipynb` — ingests Phases 1 & 2 outputs plus Statista/market data, runs executive queries, and generates the final strategy doc.


**Note:** Due to GitHub’s file size limitations, the video files could not be uploaded to this repository and are available in the shared Google Drive folder. All other project files are included in this repository.
