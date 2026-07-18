# Data Dictionary

## Purpose

This document defines the controlled terminology for the Indian electric-bus market project. These definitions apply to all future datasets, notebooks, analytical outputs, reports, and presentations.

## Entity types

| Controlled value | Definition |
|---|---|
| `OEM` | A company that manufactures or supplies electric buses under its own or an associated vehicle brand. |
| `Operator` | A company or consortium that operates bus services or participates in tenders primarily as a service operator rather than as a vehicle manufacturer. |
| `General/Industry` | Market-wide commentary, policy discussion, technology discussion, or material that cannot be attributed to one controlled OEM or operator. |

Anthony Travels and NueGo are operators. They must not be classified, counted, compared, or grouped as OEMs.

## Controlled entities

### Legacy OEMs

| Canonical name | Entity type | OEM group | Common variants to normalize |
|---|---|---|---|
| Tata Motors | OEM | Legacy | Tata; Tata Motors Buses & Vans |
| JBM Auto | OEM | Legacy | JBM; JBM Electric Vehicles |
| VECV / Eicher | OEM | Legacy | VECV; VE Commercial Vehicles; Eicher |

### New-age OEMs

| Canonical name | Entity type | OEM group | Common variants to normalize |
|---|---|---|---|
| Olectra Greentech | OEM | New-age | Olectra; Olectra-BYD |
| EKA Mobility | OEM | New-age | EKA; Eka Mobility |
| PMI Electro | OEM | New-age | PMI; PMI Electro Mobility |
| Switch Mobility | OEM | New-age | Switch; Switch Mobility India |

### Operators

| Canonical name | Entity type | OEM group | Common variants to normalize |
|---|---|---|---|
| NueGo | Operator | Not applicable | NueGo India; GreenCell Mobility/NueGo when the text concerns the operating brand |
| Anthony Travels | Operator | Not applicable | Anthony Travels consortium |

An operator must have a null or `Not applicable` OEM-group value. Operator rows must not be included in legacy-versus-new-age OEM calculations.

## Entity assignment rules

1. Preserve the original entity label in a separate source field before normalization.
2. Map recognized variants to the canonical names above.
3. Use `General/Industry` when content discusses the overall market or no controlled entity is identifiable.
4. Do not infer an entity from a video channel, account owner, or URL alone when the text discusses a different entity.
5. Where multiple entities are substantively discussed, retain a multi-entity flag or create a documented many-to-many mapping rather than forcing a single label.
6. Any new OEM or operator must be added to this dictionary before it enters group-level analysis.

## Lifecycle stages

| Controlled value | Definition | Typical evidence |
|---|---|---|
| `pre_adoption` | Awareness, consideration, evaluation, expected benefits, concerns, or intent before a purchase, award, deployment, or service experience. | Interest, comparisons, price or range questions, stated intent, expectations. |
| `procurement` | Formal acquisition and deployment process, including tenders, bidding, awards, contracting, financing, delivery planning, and institutional purchase decisions. | Tender documents, bid outcomes, GCC terms, orders, delivery commitments. |
| `post_use` | Direct or reported experience after a bus or service has been deployed or used. | Ride experience, reliability, charging operations, maintenance, breakdowns, refunds, service quality. |
| `general_unspecified` | General market, policy, technology, promotional, or opinion content without enough evidence for another lifecycle stage. | Industry news, generic praise/criticism, broad policy discussion, promotional captions. |

Lifecycle assignment must be based on the text itself and manually validated on a representative sample. Keyword rules may propose labels but must not be treated as ground truth without validation.

## Sentiment

Sentiment is based on the VADER compound score calculated from the raw text used for sentiment analysis.

| Controlled value | Rule |
|---|---|
| `Positive` | VADER compound score `>= 0.05` |
| `Negative` | VADER compound score `<= -0.05` |
| `Neutral` | Compound score is greater than `-0.05` and less than `0.05` |

Store both the continuous compound score and the categorical label. Do not substitute a topic-modeling cleaned-text field for the raw sentiment input without explicitly documenting and validating the change.

## Minimum provenance fields for derived text data

Future processed text records should retain, where available:

- source file
- platform/source
- original record ID
- parent record ID
- canonical entity
- original entity label
- entity type
- OEM group, if applicable
- original URL
- original or normalized publication date
- raw text
- cleaned LDA text
- provenance class
- lifecycle stage and validation status
- VADER compound score and sentiment category

