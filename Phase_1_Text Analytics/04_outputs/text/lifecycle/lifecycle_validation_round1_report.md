# Lifecycle Validation — Round 1

## Scope and caution

- Completed review file: `04_outputs/text/lifecycle/lifecycle_manual_validation_sample_completed.csv` (SHA-256 `4c7a0dfc04de294b9d39ee79548bc31fa2aca9e7322ec003d9b1b4252a3b63b3`).
- Reviewed rows: **120**; exact automated–human agreements: **67**; exact agreement: **55.8%**.
- The sample was deliberately enriched for low-confidence and difficult rows, including ambiguous, multistage, Hinglish-signal, underrepresented-OEM, and other manual-review cases.
- Therefore, sample accuracy must **not** be treated as unbiased corpus-wide accuracy. These results diagnose rule behaviour on a risk-enriched validation set.

## Agreement by automated confidence

- `high`: 23/25 (92.0%) agreement.
- `medium`: 32/34 (94.1%) agreement.
- `low`: 12/61 (19.7%) agreement.

## Agreement by automated class

- `pre_adoption`: 16/18 (88.9%) agreement.
- `procurement`: 10/10 (100.0%) agreement.
- `post_use`: 23/25 (92.0%) agreement.
- `general_unspecified`: 18/67 (26.9%) agreement.

## Class-level precision, recall, and F1

| Human stage | Precision | Recall | F1 | Reviewed support |
|---|---:|---:|---:|---:|
| `pre_adoption` | 0.889 | 0.314 | 0.464 | 51 |
| `procurement` | 1.000 | 0.625 | 0.769 | 16 |
| `post_use` | 0.920 | 0.676 | 0.780 | 34 |
| `general_unspecified` | 0.269 | 0.947 | 0.419 | 19 |
| Macro average | 0.769 | 0.641 | 0.608 | 120 |
| Weighted average | 0.814 | 0.558 | 0.587 | 120 |

## Main observed failure mode

- The most frequent disagreement was automated `general_unspecified` versus human `pre_adoption`: **35 rows**.
- Directionally, the classifier **under-classifies specific lifecycle stages in this enriched review sample (53 automated specific-stage labels versus 101 human labels)**.
- This direction statement applies only to the deliberately enriched round-1 sample and is not a corpus-wide error-rate estimate.

## Governance

- Lifecycle rules were not changed. Lifecycle-v1 and all protected upstream datasets remained read-only.
- No VADER sentiment analysis, LDA, topic modelling, synthetic-data generation, or internet access was used.
