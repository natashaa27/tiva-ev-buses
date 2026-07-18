# Text Preprocessing Report

## Scope

This layer prepares the approved mixed-provenance 548-row text corpus. It does not calculate final sentiment, lifecycle findings, or topic models. No synthetic data was used.

## Row flow

- Input rows: **548**
- Processed output rows: **548**
- Analysis-eligible rows: **548**
- Automatically excluded rows: **0**

All input rows remain in the processed file for lineage. `analysis_eligible=False` identifies clearly unusable rows; only those rows are also written to the exclusion log.

## Duplicate and quality flags

| Flag | Rows |
|---|---:|
| `duplicate_text` | 0 |
| `near_duplicate_text` | 118 |
| `very_short_text` | 13 |
| `emoji_only_text` | 0 |
| `possible_promotional_text` | 5 |
| `possible_brand_authored_content` | 0 |
| `possible_off_topic_content` | 1 |
| `missing_source_information` | 379 |
| `hinglish_or_code_switched` | 36 |

Exact duplicates use case-folded, whitespace-normalised raw text. Near duplicates use deterministic standard-library sequence similarity with a 0.92 threshold and a minimum length ratio of 0.85. These flags are review signals and do not automatically remove rows.

## Exclusions by reason

| Reason | Rows |
|---|---:|
| `blank_text` | 0 |
| `url_only_text` | 0 |
| `emoji_only_text` | 0 |

Automatic exclusion is deliberately limited to blank, URL-only, and emoji-only text.

## Entity distribution

| entity_name_canonical | entity_type | oem_group | row_count | percent_of_rows |
|---|---|---|---|---|
| General/Industry | General/Industry | not_applicable | 382 | 69.71 |
| NueGo | Operator | not_applicable | 66 | 12.04 |
| Tata Motors | OEM | legacy | 21 | 3.83 |
| JBM Auto | OEM | legacy | 20 | 3.65 |
| Olectra Greentech | OEM | new_age | 20 | 3.65 |
| PMI Electro | OEM | new_age | 20 | 3.65 |
| Switch Mobility | OEM | new_age | 10 | 1.82 |
| EKA Mobility | OEM | new_age | 9 | 1.64 |

## OEM-group distribution

| oem_group | row_count | percent_of_rows |
|---|---|---|
| not_applicable | 448 | 81.75 |
| new_age | 59 | 10.77 |
| legacy | 41 | 7.48 |

Anthony Travels and NueGo are controlled as operators and have `oem_group=not_applicable`; they are never included as OEMs.

## Platform distribution

| platform | row_count | percent_of_rows |
|---|---|---|
| YouTube | 377 | 68.8 |
| Team-BHP | 52 | 9.49 |
| MouthShut | 36 | 6.57 |
| Reddit | 28 | 5.11 |
| Forum | 14 | 2.55 |
| Instagram | 9 | 1.64 |
| Facebook | 7 | 1.28 |
| LinkedIn | 6 | 1.09 |
| News Article | 4 | 0.73 |
| News | 2 | 0.36 |
| Quora/LinkedIn | 2 | 0.36 |
| YouTube Comments | 2 | 0.36 |
| News/Ratings | 2 | 0.36 |
| Glassdoor/Forum | 2 | 0.36 |
| Facebook Group | 2 | 0.36 |
| Quora | 1 | 0.18 |
| EV Care | 1 | 0.18 |
| AmbitionBox | 1 | 0.18 |

The input has no independent platform field, so `platform` is derived from the preserved `source` value.

## Provenance distribution

| provenance | row_count | percent_of_rows |
|---|---|---|
| direct_platform_export_unlinked | 372 | 67.88 |
| ai_compiled_secondary | 167 | 30.47 |
| mixed_or_uncertain | 9 | 1.64 |

The input has no row-level source-file or provenance field. Provenance is derived conservatively from the approved Phase 1 lineage. Instagram rows are `mixed_or_uncertain` because direct salvaged comments cannot be distinguished reliably from AI-compiled excerpts in the merged file.

## Missing-value summary

| Field | Missing rows |
|---|---:|
| `source` | 0 |
| `url` | 379 |
| `date` | 379 |
| `entity_name_original` | 0 |
| `raw_text` | 0 |

Missing URL/date values are retained and flagged; no values are fabricated.

## Text representations

- `raw_text` is an unchanged copy of input `Text`.
- `sentiment_text` removes URLs and unnecessary whitespace only. Negations, stopwords, meaningful punctuation, capitalization, and emojis are retained.
- `topic_model_text` lowercases, removes URLs/punctuation/numbers and English stopwords, protects EV-bus domain terms, and applies conservative deterministic lemma rules (`deterministic_domain_lemma_v1`).
- Detected Hinglish tokens are retained in topic text unless they are independently removed by an explicit future rule, and are also recorded in `hinglish_terms_detected` for audit.

## Corpus limitations

- The corpus mixes direct platform exports with AI/Manus-compiled secondary excerpts.
- Most rows lack record-level IDs; stable IDs here are deterministic derived identifiers, not platform IDs.
- URL and date coverage is incomplete, limiting verification and time-based analysis.
- YouTube and General/Industry content dominate the sample; OEM and operator samples are much smaller.
- Sampling was not random or balanced across platforms, entities, time, or customer lifecycle.
- Instagram provenance is ambiguous in the merged file, and promotional/brand-authored material may remain.
- Hinglish and code-switched detection is a transparent term-list flag, not a full language classifier.
- Promotional, brand-authored, off-topic, short, duplicate, and near-duplicate rules are heuristics and require manual review.
- Topic preprocessing uses a conservative corpus-independent lemma rule set to avoid hidden downloads; it is less linguistically complete than a fully versioned POS-aware WordNet pipeline.
- This preparation layer does not validate sentiment accuracy, lifecycle labels, topic stability, or representativeness.

## Reproducibility

- All notebook paths are relative to the project root.
- Random seed: `42`.
- The approved interim input is read-only.
- Every derived CSV and this report are saved outside notebook state.
- No synthetic data, network browsing, final sentiment calculation, lifecycle classification, or topic modelling is performed.
