# Dependency gaps

This lists run requirements absent from the audited tree. It does not assert that they are absent from the author's original machine or cloud environment.

## Missing files and project modules

- `config.py` providing `OEMS`, `PROCESSED_DIR`, `RAW_DIR`, `SAMPLE_DIR`, lifecycle keywords and extraction configuration.
- Entire `extraction/` package, especially `extraction.orchestrator` and its platform source implementations.
- Entire `analysis/` package: `preprocessing.py`, `lifecycle.py`, `sentiment.py`, `topics.py` and package initializers.
- `.env` expected at project root.
- `data/sample/sample_ev_bus_comments.csv`.
- `data/raw/combined_raw.csv`.
- Output directory `data/processed/` and the expected outputs `sample_processed.csv` / `combined_processed.csv`.
- A requirements file, lockfile, environment YAML, or equivalent reproducible dependency specification.
- The `raw/` directory and seven CSVs named in `merge_corpus.py`: `yt_tata_comments.csv`, `yt_jbm_comments.csv`, `yt_ebus_market_explainer.csv`, `yt_bharat_mobility.csv`, `ig_nuego_comments.csv`, `ig_tata_comments.csv`, and `manus_text_corpus.csv`. The script's default configuration therefore cannot recreate the supplied corpus.

## Python packages/runtime resources

- Direct notebook requirements: `pandas`, `matplotlib`, `python-dotenv`, `wordcloud`, `nltk`, `gensim`, `pyLDAvis`.
- Likely extraction requirements evidenced by saved output: `apify-client` and whatever HTTP/platform packages the missing extraction modules use.
- Likely sentiment/topic transitive requirements (cannot be confirmed without custom modules): VADER/NLTK or equivalent sentiment package, NumPy/SciPy and Gensim stack.
- NLTK datasets downloaded at runtime by the Colab notebooks: `punkt`, `punkt_tab`, `stopwords`, `wordnet`, `omw-1.4`, `averaged_perceptron_tagger`, `averaged_perceptron_tagger_eng`, `vader_lexicon`.
- Notebook kernel/environment named `tiva` using Python 3.12.13 for the custom pipeline; no environment definition is supplied.
- Jupyter/IPython display support; pyLDAvis saved HTML also references CDN assets when viewed interactively.

## Credentials and APIs

- An Apify API token/credential is required by the extraction workflow (the exact environment-variable name is hidden in missing modules; commonly `APIFY_TOKEN`, but that name cannot be proven from the notebook).
- Network access to Apify actors and Instagram/other configured platforms.
- If Reddit and YouTube are enabled, their exact API/actor credentials and endpoints are unknown because the source modules are missing.
- General internet/package-index access is assumed by `!pip install` and `nltk.download(...)` in both `EV_Bus_Text_Analysis` notebooks.

## Reproducibility gaps rather than installable dependencies

- No pinned package or actor versions.
- No saved exact batch configuration that produced `ev_bus_text_corpus.csv`; `PROJECT_HANDOFF.md` says merging was run interactively and the included script documents only generic logic.
- No normalized absolute publication dates for YouTube comments (`publishedTimeText` is relative).
- No saved processed result CSVs or static figure exports from either analysis pipeline.
