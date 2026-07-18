# Notebook audit

Scope: all four `.ipynb` files in `00_original files`. Execution state and outputs were read directly from notebook JSON; notebooks were not rerun.

## `01_data_extraction.ipynb`

- **Objective:** Configure and run a custom `extraction.orchestrator` across Reddit, YouTube and Instagram; the saved run enables Instagram only for seven configured entities.
- **Expected inputs:** repository-level `.env`; `config.py`; `extraction/` package and orchestrator/source modules; OEM definitions; network/API access. None are present in the audited tree.
- **Generated outputs:** The notebook variable `combined_df`; the orchestrator likely persists raw data (the companion analysis expects `data/raw/combined_raw.csv`), but no explicit output path is visible in this notebook and no generated file is present here.
- **Libraries:** `logging`, `sys`, `pathlib`, `python-dotenv`, custom `extraction.orchestrator` (saved logs also show Apify client/actor use).
- **Execution:** 5/5 code cells have execution counts; 4 contain outputs. The run produced 234 Instagram rows across Anthony Travels (1), EKA (13), JBM (13), Olectra (61), PMI (12), Tata (90), and VECV (44).
- **Data basis:** Saved outputs appear to be real Instagram extraction results, including posts/comments and URLs; logs show free-tier limits, blocked/restricted posts and a background log-thread exception.
- **Missing items:** `.env`, custom `config.py`, entire `extraction` package, Apify credentials (likely `APIFY_TOKEN` although the notebook itself loads rather than names it), and any requirements/environment lockfile.
- **Hard-coded paths:** `PROJECT_ROOT = Path.cwd().parent`; assumes the notebook is one directory below project root. `.env` is forced at `PROJECT_ROOT/.env`.
- **Risks:** external APIs and mutable platform results; free-tier first-page cap; blocked Instagram posts; unclear persistence; no frozen actor version; no captured config modules; custom `tiva` Python 3.12 environment absent.
- **Overlap:** Feeds the same broad text-analysis workflow as `merge_corpus.py`, but uses a separate schema (`platform/oem/source_type/...`) and custom project architecture not used by `EV_Bus_Text_Analysis*.ipynb`.

## `02_sentiment_topic_analysis.ipynb`

- **Objective:** Clean extracted text, classify lifecycle stage, score VADER sentiment, compare OEM/OEM-group sentiment, sweep LDA topic counts, display pyLDAvis, and export processed data.
- **Expected inputs:** `data/sample/sample_ev_bus_comments.csv` when `USE_SAMPLE_DATA=True` (current state), otherwise `data/raw/combined_raw.csv`; custom `config.py`; custom `analysis.preprocessing`, `analysis.lifecycle`, `analysis.sentiment`, and `analysis.topics` modules.
- **Generated outputs:** `data/processed/sample_processed.csv` in current mode or `data/processed/combined_processed.csv` in real-data mode; plots/word cloud/pyLDAvis in notebook output. Neither processed CSV is in the audited tree.
- **Libraries:** `pandas`, `matplotlib`, `wordcloud`, `pyLDAvis`, Gensim through custom topic utilities, plus custom analysis modules.
- **Execution:** 13/13 code cells executed; 12 have outputs; no saved cell error object.
- **Data basis:** Explicitly synthetic. Output says 35 rows loaded from `sample_ev_bus_comments.csv`, and displayed URLs use `synthetic://...`.
- **Missing items:** both possible input CSVs; `config.py`; all custom `analysis/` modules; sample/raw/processed directories; dependency/environment specification.
- **Hard-coded paths/settings:** `PROJECT_ROOT = Path.cwd().parent`; `USE_SAMPLE_DATA = True`; topic range 2–7; relative output names controlled by missing config.
- **Risks:** saved percentages are tiny-cell synthetic illustrations, not findings; lifecycle rules and OEM grouping definitions are hidden in missing modules; no dependency versions; pyLDAvis compatibility risk; output documentation appends claims that look empirical despite the synthetic caveat.
- **Overlap:** Substantial functional overlap with both `EV_Bus_Text_Analysis` notebooks (cleaning, VADER, LDA, visualization). Unique elements are lifecycle-stage classification and custom OEM-group tables.

## `files/EV_Bus_Text_Analysis.ipynb`

- **Objective:** Portable Colab-style NLP template for `ev_bus_text_corpus.csv`: POS-aware cleaning, word cloud, VADER sentiment, LDA coherence sweep (K=2–8), and pyLDAvis.
- **Expected inputs:** `ev_bus_text_corpus.csv` in the kernel's current working directory.
- **Generated outputs:** Notebook-only tables/plots/interactive visualization; it does not save processed data or figures.
- **Libraries:** `pandas`, `matplotlib`, `nltk`, `wordcloud`, `gensim`, `pyLDAvis`, `re`, `warnings`.
- **Execution:** 0/9 code cells executed; no outputs.
- **Data basis:** Intended for the supplied 548-row mixed-provenance corpus (real scraped YouTube/Instagram-derived material plus Manus-compiled opinions), not purely synthetic.
- **Missing items/dependencies:** Runtime packages may be installed by `!pip`; NLTK resources are downloaded at runtime. Internet/package-index and NLTK access are therefore required unless cached.
- **Hard-coded paths/settings:** `FILENAME='ev_bus_text_corpus.csv'`; assumes execution from `files/` or manual upload. K=2–8, `random_state=100`, 10 passes, VADER thresholds ±0.05.
- **Risks:** `!pip install` is unpinned and mutates the environment; broad `except: pass` can hide failed NLTK downloads; strips all non-ASCII letters and is not suitable for Hindi/Hinglish; POS filter discards other parts of speech; output is not persisted; no requirements lock.
- **Overlap:** Near-duplicate/precursor of `EV_Bus_Text_Analysis-2.ipynb`; overlaps core sentiment/topic functions in `02_sentiment_topic_analysis.ipynb`.

## `files/EV_Bus_Text_Analysis-2.ipynb`

- **Objective:** Executed extension of the prior notebook using the 548-row corpus, adding a legacy/new-age/operator comparison chart.
- **Expected inputs:** `ev_bus_text_corpus.csv` in current working directory.
- **Generated outputs:** Saved notebook tables, plots and embedded pyLDAvis; no external CSV or image files. Outputs include Positive 267, Neutral 193, Negative 88; best K=5 (coherence 0.3534); and camp comparison chart.
- **Libraries:** same as the template: `pandas`, `matplotlib`, `nltk`, `wordcloud`, `gensim`, `pyLDAvis`, `re`, `warnings`.
- **Execution:** 10/10 code cells executed and all have outputs; no saved cell error object. Execution counts include a Colab run, and outputs include deprecation warnings.
- **Data basis:** Mixed provenance. The 548-row corpus combines a real 519-row YouTube export (377 retained), a small amount of Instagram-derived material, and 170 Manus-compiled opinion rows; only 169 rows have dates/URLs in the merged file. It must not be described as a uniformly direct social scrape.
- **Missing items/dependencies:** No missing input within `files/`; runtime still needs pip packages, NLTK corpora, and usually network access for first run.
- **Hard-coded paths/settings:** `FILENAME='ev_bus_text_corpus.csv'`; K=2–8; VADER thresholds ±0.05; hard-coded camp order and labels omit Switch from the displayed new-age label although the data definition includes it.
- **Risks:** environment/package installs are unpinned; relative path depends on working directory; Hinglish tokens (`hai`, `toh`, `bhi`, etc.) survive cleaning; VADER is not tuned for Indian English/Hinglish; source imbalance (382/548 `General`, 377/548 YouTube) limits OEM inference; camp sample sizes are only 41 legacy, 59 new-age, 66 operator; topic labels in handoff are human interpretations; pyLDAvis output references CDN assets; no persisted result table; analysis does not test significance or control for source/entity mix.
- **Overlap:** Near-duplicate of `EV_Bus_Text_Analysis.ipynb` with execution outputs and one additional comparison cell; overlaps `02_sentiment_topic_analysis.ipynb` but uses different schema, preprocessing, grouping and no lifecycle stage.

## Cross-notebook reproducibility conclusion

There are two incompatible pipelines: a missing custom project (`01_...`/`02_...`) and a self-contained Colab-style corpus notebook (`EV_Bus_Text_Analysis*`). The former cannot run from this repository; the latter can run with the supplied corpus after installing dependencies, but its provenance and analytical limitations remain material.
