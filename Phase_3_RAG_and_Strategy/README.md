# Phase 3 — Multimodal RAG Pipeline & Executive Strategy

**Project:** Multimodal AI Strategy for EV-Bus Market Disruption in India
**Assignment coverage:**
- **Task 3.1** — operational multimodal RAG system with cross-modal embeddings (text + image + chart layouts + market trends)
- **Task 3.2** — executive query testing (8 multi-layered strategic queries)
- **Strategic Output** — Comprehensive 3-Year Corporate EV Strategy (4 board pillars, Y1/Y2/Y3)

## Folder contents

```
Phase_3_RAG_and_Strategy/
├── README.md                        ← this file
├── ev_bus_text_analysis_final.csv   ← Phase 1 final text corpus (548 rows) — INGESTED
├── statista/                        ← real Statista PNG exports — INGESTED as visual layouts
├── notebooks/
│   └── 05_multimodal_rag.ipynb      ← THE consolidated end-to-end notebook (run this)
├── scripts/
│   ├── rag_lib.py                   ← index build + retrieval + LLM synthesis (imported by notebook)
│   ├── build_market_assets.py       ← generates IEA/BNEF/MoHI market docs + rendered charts
│   └── run_rag_build.py / run_rag_query.py / run_strategy_synth.py  ← legacy (superseded)
├── data/
│   ├── rag_index.npz                ← L2-normalised 512-d CLIP vectors (one per doc)
│   ├── rag_meta.jsonl               ← per-doc metadata
│   ├── market_trends.jsonl          ← sourced IEA/BNEF/MoHI market facts (10 docs)
│   ├── market_charts/               ← 6 chart layouts rendered from those facts
│   └── text/                        ← (alt. drop-in location for text corpus CSVs)
└── outputs/
    ├── executive_queries/executive_queries.{md,json}   ← Task 3.2 results
    └── strategy/3_year_corporate_ev_strategy.md        ← board-facing Strategic Output
```

## Architecture (Task 3.1)

**Shared cross-modal space.** CLIP-ViT-B/32, 512-d, L2-normalised. Text queries and every document type live in one space; retrieval is cosine top-K over a single matrix.

**Ingestion (one vector per doc):**

| Asset type | Docs | Embedding |
|---|---|---|
| Text corpus (Phase 1 final, `raw_text` col, `analysis_eligible` rows) | 548 | CLIP text |
| Image corpus (Phase 2 `image_rag_documents.jsonl`: caption + OCR + features) | 39 | CLIP(text) ⊕ CLIP(image), mean-fused, re-normalised |
| Statista charts (PNG exports, deduped) | 6 | CLIP(image) ⊕ CLIP(caption), fused — **visual layout indexed** |
| Rendered market charts (from IEA/BNEF/MoHI data) | 6 | same fusion |
| IEA market-trend text (sourced facts) | 10 | CLIP text |
| **Total** | **609** | |

**Market-data sources (real, cited in `data/market_trends.jsonl`):** IEA Global EV Outlook 2024/2025 (India e-bus stock 11,500 by 2024; 50k-by-2027 target; 35%/60% sales-share projections; China 680k fleet, falling share), BloombergNEF battery price survey ($139→$115→$108/kWh 2023–25), India MoHI/PM E-DRIVE (25,202 public charging stations, Dec 2024).

**Synthesiser.** `gpt-4o-mini` (temp 0.2 queries / 0.3 strategy), system-prompt discipline: cite-only-evidence, market data vs narrative-framing sentiment kept distinct, small-sample flags, no operator/OEM conflation.

## How to reproduce

Env: the shared `../.venv` (torch-cpu, transformers, openai, python-dotenv). `OPENAI_KEY` read from `../Phase_2_Image_Analytics/.env` (or `./.env`).

```
python scripts/build_market_assets.py        # refresh IEA/BNEF market docs + rendered charts
jupyter nbconvert --execute notebooks/05_multimodal_rag.ipynb   # full pipeline: index → queries → strategy
```

Drop-in rebuild cycle: add Statista PNGs to `statista/`, update the text CSV, re-run Phase 2 for new images → re-run the notebook.

## Executive queries tested (Task 3.2)

1. Why are new-age OEMs winning large Indian electric bus tenders; legacy positioning?
2. India e-bus market size, growth trajectory, government targets?
3. How does the GCC model and government financing shape tender competition?
4. Battery supply-chain risks: falling prices vs China dependence?
5. State of EV charging/depot infrastructure; who to partner with?
6. Trust, reliability, uptime, post-sale service gaps to close?
7. How should a legacy OEM respond to the tender-loss narrative over 3 years?
8. Digital marketing spend, content mix, channel strategy?

## Strategic Output structure

Executive Summary → Situation Analysis → Strategic Direction (Trust-backed GCC Growth) → **Pillar 1** Market Positioning → **Pillar 2** Infrastructure Expansion Partnerships → **Pillar 3** Battery Supply-Chain Risk Mitigations → **Pillar 4** Digital Marketing Spend Optimization (each Y1/Y2/Y3) → Governance & Cadence → Risks → Limitations & Evidence Gaps.

## Limitations

- **Video assets (Task 2.2) intentionally excluded** from this run.
- Statista charts are indexed via visual layout + filename-derived caption; individual datapoints inside the chart are not OCR'd.
- Image-corpus findings remain **exploratory** (n=39, no engagement metrics).
- IEA 2030/2035 sales-share figures are **projections** (STEPS/APS), labelled as such in the corpus.
