# File inventory

Scope: `00_original files`. Audit date: 2026-07-16. No original files were modified. ZIP members were extracted to temporary storage and compared with the expanded directory. Word and PDF files were text-extracted and rendered for readability checks.

## Physical files

| File name | File type | Size | Purpose inferred from contents | Content class | Readable and usable? |
|---|---:|---:|---|---|---|
| `01_data_extraction.ipynb` | Jupyter notebook | 40.7 KB | Runs a custom multi-platform extraction orchestrator; saved run collected Instagram material for seven OEM/operator labels. | Code + real extraction output | Readable; not runnable from this repository alone because custom modules/config/credentials are absent. |
| `02_outputs_explained.docx` | Word document | 53.6 KB | Explains the synthetic sentiment/topic notebook outputs, then appends unlabeled-looking example claims that conflict with the synthetic caveat. | Documentation + synthetic analysis interpretation | Yes; text extraction and page rendering succeeded with no blocking layout corruption. |
| `02_outputs_explained.md` | Markdown | 5.5 KB | Markdown counterpart/earlier explanation of the sentiment/topic notebook and sample results. | Documentation + synthetic analysis interpretation | Yes; parses successfully. |
| `02_sentiment_topic_analysis.ipynb` | Jupyter notebook | 608.9 KB | Custom pipeline for cleaning, lifecycle classification, VADER sentiment, OEM-group comparisons, LDA topic modeling and processed CSV export. | Code + synthetic/sample analysis outputs | Readable; runnable only with missing custom project modules/data; saved outputs are synthetic. |
| `EV_Bus_Tender_Competitor_User_Analysis.docx` | Word document | 43.5 KB | Nine-page strategic analysis of tender dynamics, competitors and user/operator requirements. | Research/analysis output | Yes; text extraction and page rendering succeeded with no blocking layout corruption. |
| `Group Project Assignment_TIVA AI_2026.pdf` | PDF | 208.5 KB | Four-page course assignment specifying multimodal analysis tasks, deliverables, grading and milestones. | Documentation / assignment brief | Yes; text extraction and page rendering succeeded with no blocking layout corruption. |
| `files.zip` | ZIP archive | 656.2 KB | Archive copy of the 14 substantive files in files/ plus macOS metadata entries. | Archive / exact duplicate container | Yes; parses successfully. |
| `files/AcadGroup8_EV_Bus_Project_Proposal.docx` | Word document | 23.5 KB | Three-page group proposal defining the EV-bus disruption problem, hypotheses, datasets and references. | Documentation / research proposal | Yes; text extraction and page rendering succeeded with no blocking layout corruption. |
| `files/EV_Bus_Text_Analysis-2.ipynb` | Jupyter notebook | 1.49 MB | Executed Colab-style real-corpus NLP notebook: cleaning, VADER, LDA, pyLDAvis and camp sentiment comparison. | Code + analysis outputs on mixed-provenance corpus | Readable and outputs present; rerun requires packages/NLTK downloads and correct working directory. |
| `files/EV_Bus_Text_Analysis.ipynb` | Jupyter notebook | 7.7 KB | Unexecuted template/earlier version of the real-corpus NLP notebook, without the final camp-comparison cell. | Code | Readable; unexecuted and requires internet/package/NLTK setup plus working-directory placement. |
| `files/India_s_Electric_Bus_Market__A_Strategic_Analysis.md` | Markdown | 16.6 KB | Manus-generated market synthesis with market, policy, tender, OEM and barrier claims. | Research material / AI-generated analysis | Yes; parses successfully. |
| `files/Manus_Prompt_EV_Bus_Market_Research.md` | Markdown | 7.2 KB | Prompt and schema instructions used to request market-research outputs from Manus. | Documentation / prompt | Yes; parses successfully. |
| `files/PROJECT_HANDOFF.md` | Markdown | 19.7 KB | Detailed project handoff describing provenance, corrections, results, caveats and remaining work. | Documentation + analysis summary | Yes; parses successfully. |
| `files/adoption_barriers.csv` | CSV | 2.4 KB | Research-compiled barrier metrics and claims with source fields. | Research data compilation | Yes; parses successfully. |
| `files/dataset_instagram-post-scraper_2026-07-08_06-00-31-568.csv` | CSV | 240.4 KB | Raw Apify Instagram post export with captions, media metadata and nested recent comments. | Real platform export; mostly brand content | Yes; parses successfully. |
| `files/dataset_youtube-comments-scraper_2026-07-08_05-29-21-490.csv` | CSV | 178.0 KB | Raw Apify YouTube comments/replies export across four videos. | Real platform export | Yes; parses successfully. |
| `files/ebus_opinions.csv` | CSV | 39.2 KB | Manus-compiled and pre-tagged public-opinion excerpts with URLs/dates. | AI/research-compiled text data; not independently authenticated | Yes; parses successfully. |
| `files/ev_bus_tenders_CORRECTED.csv` | CSV | 3.2 KB | Corrected tender table separating total OEM awards from city allocations. | Research data compilation / corrected output | Yes; parses successfully. |
| `files/ev_bus_tenders_ORIGINAL_manus.csv` | CSV | 2.8 KB | Original Manus tender table with unsupported city-to-OEM mappings and estimated rates. | Research data compilation with known fabricated/unsupported fields | Readable, but not usable as evidence because known mappings are unsupported. |
| `files/ev_bus_text_corpus.csv` | CSV | 108.8 KB | Merged 548-row English-filtered text corpus used by the executed NLP notebook. | Derived data; mixed real platform + AI-compiled opinions | Yes; parses successfully. |
| `files/market_policy_facts.csv` | CSV | 2.8 KB | Research-compiled market and policy facts with source fields. | Research data compilation | Yes; parses successfully. |
| `files/merge_corpus.py` | Python script | 3.6 KB | Generic configurable merger for CSV/JSON text sources; cleans and deduplicates text. | Code / documentation; not the exact batch recipe used | Readable; default CONFIG points to absent `raw/` files, so it will not recreate the supplied corpus as-is. |
| `files/oem_benchmark.csv` | CSV | 2.4 KB | Seven-OEM benchmark of orders, share, capacity, products, partners and customers. | Research data compilation | Yes; parses successfully. |

## ZIP contents

The ZIP contains 14 substantive members, each byte-for-byte identical to the corresponding expanded file under `files/`, plus 15 macOS `__MACOSX`/AppleDouble metadata entries. The archive therefore adds no unique project content.

| Archive member | Size | Expanded-file comparison |
|---|---:|---|
| `__MACOSX/._files` | 176 B | macOS metadata; no analytical content |
| `files/ev_bus_tenders_CORRECTED.csv` | 3.2 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._ev_bus_tenders_CORRECTED.csv` | 176 B | macOS metadata; no analytical content |
| `files/market_policy_facts.csv` | 2.8 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._market_policy_facts.csv` | 176 B | macOS metadata; no analytical content |
| `files/AcadGroup8_EV_Bus_Project_Proposal.docx` | 23.5 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._AcadGroup8_EV_Bus_Project_Proposal.docx` | 176 B | macOS metadata; no analytical content |
| `files/adoption_barriers.csv` | 2.4 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._adoption_barriers.csv` | 176 B | macOS metadata; no analytical content |
| `files/EV_Bus_Text_Analysis-2.ipynb` | 1.49 MB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._EV_Bus_Text_Analysis-2.ipynb` | 176 B | macOS metadata; no analytical content |
| `files/dataset_instagram-post-scraper_2026-07-08_06-00-31-568.csv` | 240.4 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._dataset_instagram-post-scraper_2026-07-08_06-00-31-568.csv` | 176 B | macOS metadata; no analytical content |
| `files/merge_corpus.py` | 3.6 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._merge_corpus.py` | 176 B | macOS metadata; no analytical content |
| `files/ev_bus_text_corpus.csv` | 108.8 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._ev_bus_text_corpus.csv` | 176 B | macOS metadata; no analytical content |
| `files/ebus_opinions.csv` | 39.2 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._ebus_opinions.csv` | 176 B | macOS metadata; no analytical content |
| `files/EV_Bus_Text_Analysis.ipynb` | 7.7 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._EV_Bus_Text_Analysis.ipynb` | 176 B | macOS metadata; no analytical content |
| `files/oem_benchmark.csv` | 2.4 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._oem_benchmark.csv` | 176 B | macOS metadata; no analytical content |
| `files/dataset_youtube-comments-scraper_2026-07-08_05-29-21-490.csv` | 178.0 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._dataset_youtube-comments-scraper_2026-07-08_05-29-21-490.csv` | 176 B | macOS metadata; no analytical content |
| `files/PROJECT_HANDOFF.md` | 19.7 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._PROJECT_HANDOFF.md` | 176 B | macOS metadata; no analytical content |
| `files/Manus_Prompt_EV_Bus_Market_Research.md` | 7.2 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._Manus_Prompt_EV_Bus_Market_Research.md` | 176 B | macOS metadata; no analytical content |
| `files/ev_bus_tenders_ORIGINAL_manus.csv` | 2.8 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._ev_bus_tenders_ORIGINAL_manus.csv` | 176 B | macOS metadata; no analytical content |
| `files/India_s_Electric_Bus_Market__A_Strategic_Analysis.md` | 16.6 KB | byte-for-byte identical to expanded copy |
| `__MACOSX/files/._India_s_Electric_Bus_Market__A_Strategic_Analysis.md` | 176 B | macOS metadata; no analytical content |
