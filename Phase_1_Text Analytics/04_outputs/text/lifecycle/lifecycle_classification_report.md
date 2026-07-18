# Lifecycle Classification Report

## Scope and provenance

- Input: `01_data/processed/ev_bus_text_corpus_frozen.csv`
- Input SHA-256: `cb367213ecfe96295dcb83beb615799d74882e65240cc6bc1e8901e26fa0be69`
- Rows classified: **548**; unique `comment_id`: **548**.
- All 548 frozen rows were classified. No row was deleted, and the frozen input was not modified.
- This output is automated classification only. It is **not** a validated lifecycle finding.

## Dictionary and scoring

- Dictionary version: `lifecycle_rules_v1.0`; rules: pre-adoption 10, procurement 8, post-use 9.
- Rules match protected phrases and contextual expressions in `sentiment_text` (falling back to `raw_text` only if needed). `topic_model_text` is not used.
- Weights are additive and non-negative. A stage normally requires score >= 2. Weak isolated terms do not force a stage.
- Explicit actual-use evidence outranks hypothetical language. Explicit tender/order/contract language remains procurement evidence. Speaker/source support can add one point only after text evidence exists.
- Unresolved top-score ties become `general_unspecified`; tied and multiple meaningful stages are retained for manual review.
- Confidence is high for explicit evidence with a clear margin, medium for sufficient less-decisive evidence or clear absence of lifecycle evidence, and low for weak/close/unresolved cases.

## Automated distribution (all 548 rows)

- `pre_adoption`: 20 (3.6%)
- `procurement`: 14 (2.6%)
- `post_use`: 65 (11.9%)
- `general_unspecified`: 449 (81.9%)

## Confidence and review flags

- `high`: 47 (8.6%)
- `medium`: 399 (72.8%)
- `low`: 102 (18.6%)
- Ambiguous/tied cases: 2.
- Multiple-stage secondary flags: 5.
- Automated manual-review-required flags: 207.

## Rule firing counts

- `PRE09`: 112 rows
- `POST09`: 35 rows
- `POST04`: 29 rows
- `POST06`: 19 rows
- `POST05`: 18 rows
- `POST07`: 14 rows
- `POST03`: 14 rows
- `PRO01`: 11 rows
- `PRE08`: 10 rows
- `PRO07`: 7 rows
- `POST02`: 6 rows
- `PRE02`: 5 rows
- `PRO02`: 5 rows
- `PRE10`: 4 rows
- `PRE06`: 4 rows
- `POST01`: 3 rows
- `PRE05`: 2 rows
- `PRE03`: 2 rows
- `PRO08`: 1 rows
- `PRE07`: 1 rows
- `PRO05`: 1 rows
- `PRO06`: 1 rows
- `POST08`: 1 rows

## Manual-validation sample

- Sample size: **120**, deterministic seed **42**, unique IDs: **120**.
- Class composition: `{"general_unspecified": 67, "post_use": 25, "pre_adoption": 18, "procurement": 10}`.
- Confidence composition: `{"high": 25, "low": 61, "medium": 34}`.
- Sampling prioritises ambiguous, multistage, low-confidence, Hinglish-signal, EKA Mobility, Switch Mobility, and other manual-review cases, then fills coverage across classes, confidence, entity type, OEM group, platform, and analysis scopes.
- Human-review fields are blank by design.

## Illustrative automated examples

- `pre_adoption` / `c_dab4965e02bbafc383d4`: @groww_edge what if we make a solar panel body in the buses to recover the extra charge that's taken by the ac cooler and cooling battery — evidence: `pre_adoption:solar panel; pre_adoption:battery`.
- `pre_adoption` / `c_735f6b0eb726ae45cc08`: We should invest Battery swap technology for buses for Big cities, There will 5-8 major bus station should have Battery swap station which can swap fully charged battery in 15 min. — evidence: `pre_adoption:battery swap; pre_adoption:battery`.
- `procurement` / `c_81251844778188004f9c`: If every contract just see cost and not r&d or long-term contract feasibility then we should not expect R&D from our brands. Thiese Chinese partner startups shows example that long — evidence: `pre_adoption:feasibility; pre_adoption:cost; procurement:bidding; procurement:contract`.
- `procurement` / `c_529bc0280cec5b65e64b`: Isn't easy green mobility going big on ev buses via securing tender from MP govt ? — evidence: `procurement:tender`.
- `post_use` / `c_56fd4f5a6dfbf0b563c2`: Loved the whole analysis. Brilliant strategies and financial models but there will be only 1 mega winner and 2 beneficiaries..... Environment will be the winner with pollution redu — evidence: `pre_adoption:environment; post_use:maintenance`.
- `post_use` / `c_2b15bd013d9666b18c99`: Fist driver sleeping room s provided please — evidence: `post_use:driver`.
- `general_unspecified` / `c_59483a2f6391e2efe7ea`: Hi all, your anchor here. Do share all the feedback and love! What you liked. What you did not like. Everything! What topics would you want me to cover in the coming times? Those t — evidence: `none`.
- `general_unspecified` / `c_3f225e0d09eb94f0a341`: Battery resources material are easily available in china, we dont have natural resources. Just petrol diesel and natural gas. Make video with real figures. Dont bluff. — evidence: `pre_adoption:battery`.

## Limitations and required human validation

- Keyword and regex rules cannot reliably resolve sarcasm, implicit meaning, negation scope, quoted material, or comments that discuss several lifecycle stages.
- Indian English and Hinglish vary in spelling and grammar. Only tokens observed in this frozen corpus are documented; code-switching itself never determines a label.
- Generic words such as cost, battery, service, route, order, and experience are context-sensitive. The conservative threshold reduces false specificity but increases `general_unspecified` assignments.
- Platform, entity, OEM-group, and provenance imbalance can distort apparent distributions. Every subgroup table identifies sample sizes and flags groups below 15 rows.
- Speaker role and source type are imperfect metadata and are supporting context only.
- The manual-validation sample must be reviewed before any lifecycle result is used in the MBA report. Automated outputs must not be reported as validated findings.
- No sentiment, VADER, LDA, topic modelling, or synthetic-data analysis was performed.
