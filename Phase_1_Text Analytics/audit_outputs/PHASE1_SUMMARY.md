# Phase 1 summary

This is an audit status summary, not a strategic market recommendation.

## Complete

- Assignment brief and project proposal are present, readable and visually intact.
- A raw YouTube export (519 comments/replies) and raw Instagram post export (26 posts, 400 flattened fields) are present and machine-readable.
- The current merged text corpus (548 rows) and its executed NLP notebook are present; the notebook has complete saved outputs for cleaning, VADER sentiment, LDA and camp comparison.
- A corrected tender table exists and explicitly repairs the most serious city-to-OEM attribution error.
- Market/policy, barrier and OEM benchmark tables are present with source fields.
- Handoff and explanatory documents record many caveats and known issues.

## Partially complete

- Text analysis is technically executed, but provenance is mixed, source composition is imbalanced, entity/camp definitions vary, and no significance/stability tests or persistent result tables are supplied.
- Data extraction has saved real outputs, but its custom source code, configuration, credentials, environment and output files are missing.
- The custom lifecycle/OEM pipeline is executed only on 35 synthetic rows and cannot be rerun from this repository.
- Tender/market/OEM research is tabulated, but some sources are concentrated in a commercial aggregator, two rows cite prompt text, and the OEM share figures do not reconcile.
- Instagram data exists, but it is mainly brand post/caption material rather than a purpose-built customer-comment dataset.
- The strategic analysis DOCX is readable and developed, but it is an analysis output without complete executable lineage.

## Missing

- Image analysis and video analysis required by the assignment.
- The custom `config.py`, `analysis/`, and `extraction/` codebase; sample/raw/processed pipeline files; `.env`; dependency lockfile.
- A reproducible script/config that exactly generates `ev_bus_text_corpus.csv` from the raw files.
- Primary-source verification trail or archived evidence for key market/tender claims and all Manus-compiled opinions.
- Normalized dates for YouTube comments and a dedicated Instagram comment extraction.
- Saved machine-readable sentiment/topic/lifecycle outputs and figure exports.
- One controlled data dictionary defining OEM, operator, entity type, camp, lifecycle stage and sentiment.

## Authoritative sources within the current repository

- `Group Project Assignment_TIVA AI_2026.pdf` for requirements and grading scope.
- `files/AcadGroup8_EV_Bus_Project_Proposal.docx` for the original project intent and hypotheses.
- `files/dataset_youtube-comments-scraper_2026-07-08_05-29-21-490.csv` as the raw YouTube evidence.
- `files/dataset_instagram-post-scraper_2026-07-08_06-00-31-568.csv` as the raw Instagram-post evidence, with its post-not-comment limitation stated.
- `files/ev_bus_text_corpus.csv` as the current analysis input, explicitly labeled mixed provenance.
- `files/EV_Bus_Text_Analysis-2.ipynb` as the record of the current real-corpus text run.
- `files/ev_bus_tenders_CORRECTED.csv` as the repository's controlling tender table (pending external verification in a later phase).
- `files/PROJECT_HANDOFF.md` as the most complete provenance and issue log, not as primary evidence.

## Retain only as references/provenance

- `files.zip`: redundant archive copy.
- `files/EV_Bus_Text_Analysis.ipynb`: unexecuted predecessor/template.
- `02_sentiment_topic_analysis.ipynb` and `02_outputs_explained.*`: synthetic demonstration and explanation only.
- `01_data_extraction.ipynb`: execution record only until the custom code/config is recovered.
- `files/ev_bus_tenders_ORIGINAL_manus.csv`: error/provenance history only; never use for findings.
- `files/Manus_Prompt_EV_Bus_Market_Research.md`: prompt provenance.
- `files/India_s_Electric_Bus_Market__A_Strategic_Analysis.md` and `EV_Bus_Tender_Competitor_User_Analysis.docx`: research/analysis references, not raw evidence.
- `files/ebus_opinions.csv`, `market_policy_facts.csv`, `adoption_barriers.csv`, and `oem_benchmark.csv`: provisional research inputs pending verification/reconciliation.
- `files/merge_corpus.py`: generic logic reference; it does not reproduce the supplied corpus with its current CONFIG.

## Five most urgent actions required

1. Recover the missing custom project files and environment specification (`config.py`, `analysis/`, `extraction/`, data directories, lockfile and credential-variable documentation).
2. Freeze a reproducible corpus-building pipeline that maps the supplied raw exports and Manus rows into `ev_bus_text_corpus.csv`, preserving source file, platform, original ID, URL/date and provenance class.
3. Establish one controlled data dictionary and normalize entity names/types, OEM versus operator, legacy/new-age camp, lifecycle stages and sentiment definitions across all files.
4. Quarantine the synthetic notebook outputs and original Manus tender table from empirical reporting; add unmistakable provenance labels to every derived result.
5. Validate the current research tables and Manus-compiled opinions against their cited sources, remove prompt-text pseudo-sources, and reconcile OEM share/order measures before they are treated as evidence.
