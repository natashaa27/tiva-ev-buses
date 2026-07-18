# Phase 1 Decisions

## Status

The Phase 1 repository audit was reviewed and approved. The decisions below control subsequent data preparation and analysis.

## Repository governance

- Everything inside `00_original files` is immutable and must not be edited, renamed, moved, or deleted.
- Working data is separated into `raw`, `interim`, and `processed` directories.
- Analytical notebooks will live in `02_notebooks`; no notebook was created or modified during this restructuring step.
- Generated outputs are separated by text, image, video, and RAG modality.
- Report and presentation artifacts have dedicated directories.

## Approved interim inputs

- `01_data/interim/ev_bus_text_corpus.csv` is the approved current text-analysis input. It is a byte-for-byte copy of the 548-row original and must carry a mixed-provenance disclosure.
- `01_data/interim/ev_bus_tenders_CORRECTED.csv` is the controlling tender dataset within the repository. It is a byte-for-byte copy of the corrected original.
- Copies do not replace or alter the immutable original files.

## Excluded files and results

- `ev_bus_tenders_ORIGINAL_manus.csv` is excluded from working data and empirical findings because it contains unsupported city-to-OEM mappings and estimated values.
- Synthetic processed results are excluded from the working repository.
- Results saved in `02_sentiment_topic_analysis.ipynb` are synthetic demonstrations and must not be reported as market findings.
- AI/Manus-compiled research and opinions remain provisional until their citations or excerpts are verified.

## Controlled entity decisions

- Permitted entity types are `OEM`, `Operator`, and `General/Industry`.
- Legacy OEMs are Tata Motors, JBM Auto, and VECV / Eicher.
- New-age OEMs are Olectra Greentech, EKA Mobility, PMI Electro, and Switch Mobility.
- NueGo and Anthony Travels are operators.
- Anthony Travels and NueGo must never be grouped as OEMs or included in legacy-versus-new-age OEM comparisons.
- Entity variants must be normalized to the canonical names in `DATA_DICTIONARY.md` while preserving original labels.

## Controlled lifecycle decisions

The permitted lifecycle stages are:

- `pre_adoption`
- `procurement`
- `post_use`
- `general_unspecified`

Automated lifecycle labels require manual validation on a representative, stratified sample before they support findings.

## Controlled sentiment decisions

- Positive: VADER compound score `>= 0.05`.
- Negative: VADER compound score `<= -0.05`.
- Neutral: compound score between the two thresholds.
- Raw text is the default sentiment input.
- LDA must use a separate reproducibly cleaned-text field.
- Both the continuous compound score and categorical sentiment must be retained.

## Methodological decisions

- Evidence is ranked using the hierarchy in `METHODOLOGY.md`.
- The 548-row corpus is accepted for exploratory work only with explicit mixed-provenance, platform-imbalance, and sample-imbalance disclosures.
- VADER limitations for Indian English, Hinglish, sarcasm, and code-switching must be disclosed and manually assessed.
- The corrected tender table supersedes the original Manus tender table.
- Derived data and outputs must retain traceable source lineage and be saved outside notebook-only state.

## Deferred work

- No analytical notebook is created or modified in this phase.
- Corpus rebuilding, lifecycle validation, sentiment execution, LDA execution, image analysis, video analysis, RAG development, report integration, and presentation development remain future execution stages.

