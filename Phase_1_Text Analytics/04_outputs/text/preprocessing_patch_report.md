# Preprocessing Patch Report

## Scope

Targeted final data-quality patch applied to the approved 548-row processed corpus. All v1 rows and columns are retained. No original or interim file was modified. No synthetic data, internet browsing, lifecycle classification, VADER scoring, or LDA/topic modelling was used.

## Results

- Retained rows: **548**
- Duplicate clusters: **59**
- Duplicate representatives: **59**
- Duplicate copies: **59**
- Sentiment-eligible rows: **460**
- Topic-model-eligible rows: **456**
- Creator/brand flags: **2**
- Off-topic flags: **1**
- Manual-review rows: **107**

## Near-duplicate handling

The existing `near_duplicate_partner` links were treated as undirected graph edges. Each connected component of two or more rows received a deterministic `near_duplicate_cluster_id` derived from its sorted comment IDs. Exactly one representative was selected per cluster, preferring non-wrapper text, usable/audience text, available URL/date lineage, and richer text; comment ID breaks ties. No row was deleted. Non-representative cluster copies are ineligible for sentiment and topic modelling.

## Eligibility rules

- Blank, URL-only, emoji-only, inherited possible-off-topic rows, and obvious creator/brand content are ineligible for both uses.
- Near-duplicate representatives remain potentially eligible; duplicate copies are ineligible for both uses.
- Generic channel/video praise without a substantive EV-bus opinion is ineligible for both uses.
- Very-short but otherwise meaningful rows remain potentially sentiment eligible and are topic-model ineligible.
- Hinglish/code-switched rows are not automatically excluded.
- `eligibility_reason` records the applied rule; `manual_review_required` marks uncertain or high-risk cases.

## Speaker role

Controlled roles are `audience_user`, `creator_or_brand`, `media_or_research`, and `unknown`. Classification is conservative. Obvious channel-host language and likely OEM Instagram captions are flagged as creator/brand; ambiguous Instagram material remains unknown or audience only where user voice is explicit.

## Platform normalisation

The existing `platform` field is unchanged and copied to `platform_original`. `platform_canonical` consolidates variants into YouTube, Instagram, Reddit, Facebook, LinkedIn, Forum, Review Platform, News/Media, or Mixed/Unknown.

## Topic text regeneration

`topic_model_text` was regenerated from `raw_text`: lowercased; URLs, punctuation, standalone numbers, and explicit English stopwords removed; EV-bus domain and Hinglish terms protected. Aggressive suffix rules are not used. Method for this run: **cleaned_full_words_no_stemming_v2**. If local WordNet data is unavailable, cleaned full words are retained without stemming.

## Manual review

The review file contains every creator/brand flag, possible off-topic flag, promotional flag, very-short row, duplicate-cluster representative, generic channel-praise flag, unknown-speaker row, plus a deterministic stratified sample across entity type, OEM group, and canonical platform. Human-decision fields are blank by design.

## Limitations

- Near-duplicate links inherit the v1 heuristic and may join paraphrases that require human confirmation.
- Speaker role is inferred without original author/channel-owner fields.
- `possible_off_topic_content` is an inherited heuristic flag and remains subject to review.
- Platform and provenance fields remain derived from an imbalanced mixed-provenance corpus.
- Eligibility is a preparation decision, not an analytical result or human-validated ground truth.
