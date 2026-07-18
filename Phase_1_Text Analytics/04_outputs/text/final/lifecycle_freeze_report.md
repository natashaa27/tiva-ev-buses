# Final Lifecycle Freeze Report

- Lifecycle-v1 rows retained: **548**; unique IDs: **548**.
- Round-1 human labels applied: **120**.
- Round-1 sample was risk-enriched rather than random; its accuracy is not an unbiased corpus-wide estimate.
- Overall agreement: **55.8%**; high-confidence: **92.0%**; medium-confidence: **94.1%**; low-confidence: **19.7%**.
- Main failure: automated `general_unspecified` under-classified specific lifecycle stages, especially `pre_adoption`.
- All **41** remaining unreviewed low-confidence rows were conservatively retained as `general_unspecified`.
- The 87-row round-2 review was generated but not manually completed because of the submission timeline.
- High/medium unreviewed labels remain automated and must be distinguished from round-1 human-reviewed labels using `lifecycle_label_source`.
- No upstream dataset was overwritten and raw text was unchanged.
