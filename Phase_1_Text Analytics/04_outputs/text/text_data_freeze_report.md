# Text Data Freeze Report

## Inputs and placement

- Source dataset: `01_data/processed/ev_bus_text_corpus_processed_v2.csv`
- Source SHA-256: `ae60e06cf143b5b82bc1a60bfd90d9dbfcdbae8a55e08b0193755bc6d6e247d9`
- Completed review file used: `04_outputs/text/manual_quality_review_completed.csv`
- Review SHA-256: `faa6fcca5ccef8dda3304fc4653942c84d244779012edc6c3d3a0efdf41247b6`
- Review file was found at: `manual_quality_review_completed.csv`
- Placement action: copied to the target location without deleting or altering the root copy.
- Source and target review copies had identical byte size and SHA-256 checksum.

## Freeze results

- Total rows retained: **548**
- Unique comment IDs: **548**
- Human-reviewed rows: **107**
- Non-reviewed rows: **441**
- Automated sentiment-eligible rows: **460**
- Final sentiment-eligible rows: **444**
- Automated topic-model-eligible rows: **456**
- Final topic-model-eligible rows: **441**
- Consumer sentiment-eligible rows: **438**
- Consumer topic-eligible rows: **435**
- Industry topic-eligible rows: **441**

## Speaker roles before review

| speaker_role | rows |
|---|---|
| audience_user | 531 |
| creator_or_brand | 2 |
| media_or_research | 14 |
| unknown | 1 |

## Speaker roles after review

| speaker_role_final | rows |
|---|---|
| audience_user | 522 |
| creator_or_brand | 3 |
| media_or_research | 23 |

## Human-review changes

- Speaker-role changes: **11**
- Sentiment-eligibility changes: **16**
- Topic-eligibility changes: **15**
- Rows with at least one changed classification: **18**

## Final eligible distribution by entity

| entity_name_canonical | entity_type | oem_group | total_rows | consumer_sentiment_eligible_final | consumer_topic_eligible_final | industry_topic_eligible_final |
|---|---|---|---|---|---|---|
| EKA Mobility | OEM | new_age | 9 | 7 | 7 | 8 |
| General/Industry | General/Industry | not_applicable | 382 | 352 | 349 | 349 |
| JBM Auto | OEM | legacy | 20 | 11 | 11 | 11 |
| NueGo | Operator | not_applicable | 66 | 38 | 38 | 38 |
| Olectra Greentech | OEM | new_age | 20 | 7 | 7 | 9 |
| PMI Electro | OEM | new_age | 20 | 6 | 6 | 8 |
| Switch Mobility | OEM | new_age | 10 | 7 | 7 | 8 |
| Tata Motors | OEM | legacy | 21 | 10 | 10 | 10 |

## Final eligible distribution by OEM group

| oem_group | total_rows | consumer_sentiment_eligible_final | consumer_topic_eligible_final | industry_topic_eligible_final |
|---|---|---|---|---|
| legacy | 41 | 21 | 21 | 21 |
| new_age | 59 | 27 | 27 | 33 |
| not_applicable | 448 | 390 | 387 | 387 |

## Final eligible distribution by platform

| platform_canonical | total_rows | consumer_sentiment_eligible_final | consumer_topic_eligible_final | industry_topic_eligible_final |
|---|---|---|---|---|
| Facebook | 9 | 6 | 6 | 6 |
| Forum | 67 | 37 | 37 | 37 |
| Instagram | 9 | 6 | 6 | 6 |
| LinkedIn | 8 | 0 | 0 | 2 |
| News/Media | 6 | 0 | 0 | 4 |
| Reddit | 28 | 23 | 23 | 23 |
| Review Platform | 42 | 21 | 21 | 21 |
| YouTube | 379 | 345 | 342 | 342 |

## Remaining limitations

- The corpus remains platform- and entity-imbalanced and contains mixed provenance.
- Many records lack original URL/date or platform author metadata.
- Human review covers 107 selected records, not every corpus row.
- Near-duplicate clusters inherit the v1 automated similarity heuristic.
- Final eligibility fields are analysis controls, not sentiment, lifecycle, or topic-model results.

## Integrity confirmation

- The frozen file preserves all 548 v2 rows, original `comment_id`, and `raw_text` values.
- All 107 completed review rows were applied by exact unique `comment_id`.
- Creator/brand rows, duplicate copies, and off-topic rows are excluded from final analysis controls.
- Media/research rows are excluded from consumer controls but may enter the industry topic control.
- No synthetic data was introduced; no internet access was used.
- No lifecycle labels, VADER sentiment scores, LDA models, or topic models were generated.
- No immutable original, interim, or v2 file was modified.
