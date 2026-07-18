# Lifecycle Validation — Round 2 Coverage

- Total lifecycle-v1 rows: **548**.
- Round-1 reviewed rows: **120**.
- Remaining unreviewed rows before round 2: **428**.
- Total low-confidence rows in lifecycle-v1: **102**.
- Low-confidence rows reviewed in round 1: **61**.
- Low-confidence rows remaining and included in round 2: **41 of 41**.
- Ambiguous rows remaining: **0**.
- Multistage rows remaining: **0**.
- Manual-review-required rows remaining: **87**.
- Round-2 sample size: **87**.

The sample exceeds the preferred approximate ceiling of 70 because every remaining low-confidence row and every other explicitly required high-risk row was retained. Routine high- or medium-confidence `general_unspecified` rows with zero lifecycle evidence were not added.

## Automated class distribution

- `pre_adoption`: 2
- `procurement`: 4
- `post_use`: 40
- `general_unspecified`: 41

## Confidence distribution

- `high`: 22
- `medium`: 24
- `low`: 41

## Entity-type distribution

- `General/Industry`: 48
- `Operator`: 21
- `OEM`: 18

## OEM-group distribution

- `not_applicable`: 69
- `legacy`: 12
- `new_age`: 6

## Platform distribution

- `YouTube`: 49
- `Review Platform`: 20
- `Forum`: 16
- `Reddit`: 1
- `News/Media`: 1

## High-risk inclusion check

- Qualifying high-risk rows excluded: **0**.
- No qualifying high-risk row was excluded. All remaining low-confidence, ambiguous, multistage, and relevant manual-review-required rows are present.
- Rows outside round 2 are unreviewed rows that did not meet the specified high-risk criteria; routine zero-evidence general rows were intentionally avoided.

## Governance

- Round 1 and round 2 have no overlapping `comment_id` values.
- Human-review fields in round 2 are blank.
- No lifecycle rules or protected datasets were modified. No VADER, LDA, topic modelling, synthetic data, or internet access was used.
