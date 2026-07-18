# Methodology

## Scope

This methodology governs the evidence and text-analytics work following the approved Phase 1 audit. It records provenance, exclusions, analytical distinctions, and validation requirements before analytical notebooks are developed.

## Evidence hierarchy

Evidence should be interpreted in the following order:

1. **Direct raw platform or administrative evidence** — original platform exports, tender documents, official government material, and other records captured without analytical transformation.
2. **Corrected source-linked research tables** — structured compilations that preserve citations and have passed internal conflict checks, including the corrected tender table.
3. **Derived datasets** — interim and processed tables produced reproducibly from higher-ranked evidence while retaining record-level lineage.
4. **AI-compiled or secondary research material** — Manus-generated tables, extracted opinions, market reports, and narrative syntheses that require verification against the cited source.
5. **Synthetic or demonstration material** — fixtures and sample outputs used to test code. These are excluded from empirical findings.

Lower-ranked evidence must not override contradictory higher-ranked evidence. Presence of a URL alone does not establish that an AI-compiled excerpt or claim was quoted accurately.

## Current 548-row corpus provenance

`01_data/interim/ev_bus_text_corpus.csv` is the approved current analysis input, but it is not a uniform direct social-media scrape. It combines:

- retained comments from a real YouTube export;
- a small amount of Instagram-derived material;
- AI/Manus-compiled public-opinion excerpts attributed to forums, review sites, social platforms, and news sources.

The corpus is therefore mixed provenance. It may support exploratory analysis if that limitation is disclosed, but AI-compiled rows must not be represented as independently authenticated direct observations. The existing file also has incomplete lineage: most general/YouTube rows lack URL and date values.

## Raw text for sentiment versus cleaned text for LDA

Two separate text representations are required:

- **Sentiment input:** the original raw text, with only minimal technical normalization needed for valid string handling. Punctuation, negation, emojis, capitalization, and sentiment-bearing function words should be preserved because VADER may use them.
- **LDA input:** a separately stored cleaned-text field. Topic-model preprocessing may lowercase text, remove noise, tokenize, remove selected stopwords, and lemmatize words. The exact transformation and stopword list must be reproducible.

The cleaned LDA field must not overwrite the raw text. Sentiment should not be calculated from aggressively cleaned or POS-filtered LDA text unless a separately validated experiment justifies it.

## Platform, entity, and sample imbalance

The 548-row corpus is imbalanced:

- 377 rows are attributed to YouTube;
- 382 rows are labelled `General`/mixed rather than a controlled OEM or operator;
- controlled comparison groups are much smaller: 41 legacy-OEM, 59 new-age-OEM, and 66 operator rows in the audited version;
- platform, entity, language, and time coverage are not balanced or randomly sampled.

Descriptive percentages must include sample sizes. Group comparisons must not be presented as population estimates. Source and entity composition should be reported alongside results, and sensitivity checks should be considered before making comparative claims.

## Synthetic outputs excluded

The executed outputs in `02_sentiment_topic_analysis.ipynb` were generated from a 35-row synthetic fixture with `synthetic://` URLs. Its lifecycle counts, sentiment counts, OEM-stage percentages, topic results, and appended interpretive claims are excluded from empirical evidence.

Synthetic processed outputs must not be copied into the working data structure or combined with the 548-row corpus. Synthetic fixtures may be retained in the immutable original archive solely for provenance and software testing.

## Tender-data authority

`01_data/interim/ev_bus_tenders_CORRECTED.csv` supersedes `ev_bus_tenders_ORIGINAL_manus.csv`.

The original Manus table contains unsupported city-to-OEM assignments and estimated rate fields. It must not be used as empirical evidence. The corrected table separates aggregate OEM awards from city allocations and explicitly marks city-level OEM attribution as undisclosed where appropriate.

The corrected table is authoritative within this repository, but its external claims should still be validated against cited or primary sources before final publication.

## VADER limitations

VADER is a lexicon- and rule-based English sentiment method. It has material limitations for this corpus:

- Indian English expressions may not carry the same lexicon weights as standard US English;
- Hinglish and transliterated Hindi terms may be unrecognized or incorrectly treated as neutral;
- sarcasm, indirect criticism, domain-specific terminology, and code-switching may be missed;
- spelling variation, informal grammar, repeated characters, and platform conventions can affect scores;
- promotional brand captions and customer comments represent different speech contexts and should not be interpreted identically.

VADER results are exploratory indicators rather than validated measures of customer satisfaction. Manual review of stratified samples and error cases is required before strong findings are reported.

## Lifecycle validation

Lifecycle classification may begin with transparent keyword or rule-based labeling using the controlled stages in `DATA_DICTIONARY.md`. Manual validation is mandatory because words such as “order,” “service,” “use,” or “delivery” can refer to different stages in different contexts.

The validation process should:

1. draw a stratified sample across platforms, entities, and proposed lifecycle stages;
2. have reviewers label the text using written stage definitions rather than keyword presence alone;
3. record disagreements and adjudicated labels;
4. calculate agreement and stage-level error rates where sample size allows;
5. revise rules before applying lifecycle labels to final analysis;
6. retain a validation-status field so machine-assigned and manually confirmed labels remain distinguishable.

## Reproducibility controls

- Original files remain immutable.
- Raw, interim, and processed data have separate directories.
- Every derived record should retain source lineage.
- Notebook execution order and random seeds should be explicit.
- Processed tables and figures should be saved outside notebooks.
- Package versions are pinned in `requirements.txt` for a Python 3.11 environment.
- Any change to entity, lifecycle, or sentiment definitions must be recorded in `DATA_DICTIONARY.md` and `PHASE1_DECISIONS.md` before rerunning analysis.

