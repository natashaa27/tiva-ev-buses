# Final Text Analysis Report

## 1. Executive summary

**Finding →** The frozen lifecycle layer combines 120 human-reviewed labels with conservatively handled automated labels. Consumer sentiment and topics are exploratory signals, not population estimates.  
**Evidence/metric →** N=438; Positive 51.4%, Neutral 29.2%, Negative 19.4%; mean compound 0.179; topic model K=8, coherence=0.356.  
**Interpretation →** The corpus surfaces recurring attitudes and themes, but mixed provenance and imbalance limit generalisation.  
**Business implication →** Use results to prioritise questions for primary research and operational review, not as causal proof.

## 2. Business question

How do consumer attitudes, lifecycle context, and recurring discussion themes differ across EV-bus entities, OEM groupings, operators, platforms, and provenance categories?

## 3. Dataset and analytical scopes

- Master corpus: 548 rows, all retained.
- Consumer sentiment scope: 438 audience-user rows with approved sentiment eligibility.
- Primary consumer-topic scope after usable-text and duplicate/role controls: 411 rows.
- NueGo is an operator; Anthony Travels and NueGo are excluded from OEM comparisons.

## 4. Data-quality and provenance limitations

The corpus mixes direct YouTube/Instagram-derived material with AI-compiled secondary excerpts. It is heavily imbalanced by platform and entity, lacks complete URL/date metadata, and is not a random sample. Findings are exploratory associations. Media/research and creator/brand rows are excluded from consumer scopes.

## 5. Lifecycle-classification method and validation

**Finding →** Human review substantially corrected difficult low-confidence cases.  
**Evidence/metric →** Risk-enriched round-1 agreement was 55.8% overall, 92.0% high, 94.1% medium, and 19.7% low; the main failure was `general_unspecified` under-classification.  
**Interpretation →** High/medium automated labels were retained, while 41 unreviewed low-confidence rows were conservatively set to `general_unspecified`.  
**Business implication →** Always use `lifecycle_label_source` to distinguish human-reviewed from automated evidence. Round 2 was generated but not manually completed due to the submission timeline.

## 6. Final lifecycle findings

| lifecycle_stage_final | row_count | percent | total_n |
|---|---|---|---|
| pre_adoption | 53 | 9.671532846715328 | 548 |
| procurement | 20 | 3.6496350364963503 | 548 |
| post_use | 74 | 13.503649635036496 | 548 |
| general_unspecified | 401 | 73.17518248175182 | 548 |

Small lifecycle groups must not be strongly interpreted. Lifecycle labels describe comment context, not market-funnel conversion.

## 7. Sentiment methodology

VADER used `sentiment_text` only for consumer-sentiment-eligible rows. Positive is compound ≥0.05, Negative ≤-0.05, Neutral otherwise. VADER is exploratory and may misread Indian English, Hinglish, sarcasm, code-switching, implicit sentiment, and domain-specific meanings.

## 8. Overall sentiment findings

**Finding →** The eligible corpus has the descriptive sentiment mix shown below.  
**Evidence/metric →** N=438; Positive 51.4%, Neutral 29.2%, Negative 19.4%; mean compound 0.179.  
**Interpretation →** This is a lexicon-based distribution over eligible comments, not validated customer satisfaction.  
**Business implication →** Use the manual sentiment-check sample before quoting fine-grained sentiment claims.

## 9. Lifecycle sentiment findings

| lifecycle_stage_final | eligible_n | positive_count | positive_pct | neutral_count | neutral_pct | negative_count | negative_pct | mean_compound | median_compound | small_sample_flag |
|---|---|---|---|---|---|---|---|---|---|---|
| pre_adoption | 48 | 24 | 50.0 | 13 | 27.083333333333332 | 11 | 22.916666666666668 | 0.193275 | 0.1072 | False |
| procurement | 19 | 13 | 68.42105263157895 | 2 | 10.526315789473685 | 4 | 21.05263157894737 | 0.2875263157894737 | 0.3182 | False |
| post_use | 49 | 24 | 48.97959183673469 | 8 | 16.3265306122449 | 17 | 34.69387755102041 | 0.08478367346938775 | 0.0 | False |
| general_unspecified | 322 | 164 | 50.93167701863354 | 105 | 32.608695652173914 | 53 | 16.459627329192546 | 0.18439006211180123 | 0.0772 | False |

Stages with N<15 are flagged and should not be interpreted without an explicit small-sample caveat.

## 10. Legacy versus new-age findings

**Finding →** Descriptive sentiment differs between the two OEM groups.  
**Evidence/metric →** Legacy: N=21, mean compound 0.359; new-age: N=27, mean compound 0.264.  
**Interpretation →** Small, imbalanced samples and entity composition can drive differences; no significance or causal claim is made.  
**Business implication →** Treat this comparison as a hypothesis for balanced primary research, not a performance ranking.

## 11. Entity and operator findings

| entity_name_canonical | entity_type | eligible_n | positive_count | positive_pct | neutral_count | neutral_pct | negative_count | negative_pct | mean_compound | median_compound | small_sample_flag | comparison_role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EKA Mobility | OEM | 7 | 5 | 71.42857142857143 | 1 | 14.285714285714286 | 1 | 14.285714285714286 | 0.4955 | 0.7425 | True | OEM |
| JBM Auto | OEM | 11 | 7 | 63.63636363636363 | 2 | 18.181818181818183 | 2 | 18.181818181818183 | 0.2650636363636364 | 0.3008 | True | OEM |
| NueGo | Operator | 38 | 20 | 52.63157894736842 | 4 | 10.526315789473685 | 14 | 36.8421052631579 | 0.06847368421052631 | 0.1327 | False | Operator (not an OEM) |
| Olectra Greentech | OEM | 7 | 4 | 57.142857142857146 | 0 | 0.0 | 3 | 42.857142857142854 | 0.0972857142857143 | 0.4215 | True | OEM |
| PMI Electro | OEM | 6 | 4 | 66.66666666666667 | 2 | 33.333333333333336 | 0 | 0.0 | 0.24163333333333337 | 0.31565 | True | OEM |
| Switch Mobility | OEM | 7 | 3 | 42.857142857142854 | 4 | 57.142857142857146 | 0 | 0.0 | 0.2196428571428571 | 0.0 | True | OEM |
| Tata Motors | OEM | 10 | 7 | 70.0 | 3 | 30.0 | 0 | 0.0 | 0.46296 | 0.56465 | True | OEM |

NueGo is reported separately as an operator. Tender performance, operator service, and OEM product quality are distinct constructs and must not be conflated.

## 12. Topic-model methodology

Gensim LDA used existing `topic_model_text`, consumer-topic eligibility, audience-user roles, usable texts of ≥3 tokens, duplicate-representative controls, frequent bigrams, dictionary filtering, and seed 42. K=2–8 was evaluated using coherence, log perplexity, top-term overlap, interpretability, and parsimony. K=8 was selected with coherence 0.356; selection was not based on the numerical maximum alone. pyLDAvis status: `generated`.

## 13. Final topics and representative comments

- **Public Transport Economics & Government Operating Models** — 60 documents (14.6%); top terms: buses; like; india; time; battery; years; china; ev; cost; people; govt; much. Label approved through human interpretation of the top terms and representative comments.
- **Indian EV-Bus Adoption: R&D, Operations & User Experience** — 61 documents (14.8%); top terms: hai; bus; ki; buses; ke; ko; bhi; battery; delhi; tata; ev; batteries. Label approved through human interpretation of the top terms and representative comments.
- **Battery Technology, Swapping & Lifecycle Economics** — 43 documents (10.5%); top terms: battery; bus; batteries; much; sodium_ion; kwh; technology; years; would; battery_swap; future; hydrogen. Label approved through human interpretation of the top terms and representative comments.
- **Public Infrastructure, Funding & Alternative Transit** — 52 documents (12.7%); top terms: india; bus; buses; well; money; mobility; like; technology; say; corruption; infrastructure; pmi. Label approved through human interpretation of the top terms and representative comments.
- **Domestic Manufacturing, R&D & China Dependence** — 62 documents (15.1%); top terms: bus; buses; battery; indian; company; ev; electric; like; ac; chinese; companies; india. Label approved through human interpretation of the top terms and representative comments.
- **Tender Economics, Public Funding & Private Operators** — 47 documents (11.4%); top terms: china; bus; hai; jbm; tender; battery; se; please; ev; already; cities; better. Label approved through human interpretation of the top terms and representative comments.
- **New-Age OEM Execution, Reliability & Service Risk** — 42 documents (10.2%); top terms: olectra; india; bus; battery; indian; ac; buses; don; tata; electric; nothing; companies. Label approved through human interpretation of the top terms and representative comments.
- **Supply-Chain Risk, Charging Alternatives & Service Gaps** — 44 documents (10.7%); top terms: india; electric; china; model; government; long; good; use; ev; give; well; olectra. Label approved through human interpretation of the top terms and representative comments.

Topic labels were approved through human interpretation of the top terms and representative comments. Because model coherence is moderate, the topics remain overlapping exploratory themes. Representative comments are examples, not proof of prevalence beyond this sample.

## 14. Topic × sentiment × lifecycle findings

| topic_id | final_topic_label | document_count | prevalence_pct | dominant_lifecycle_stage | positive_pct | neutral_pct | negative_pct | mean_sentiment_compound | dominant_entity_or_oem_group | representative_comment_1 | representative_comment_2 | analytical_interpretation | preliminary_business_implication | small_sample_warning |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Public Transport Economics & Government Operating Models | 60 | 14.598540145985401 | general_unspecified | 41.666666666666664 | 36.666666666666664 | 21.666666666666668 | 0.13048500000000002 | legacy | Countries like Singapore, Dubai, and many European countries still don't have electric bus like what India has. I was surprised why the government is making such foolish decision, but thanks to this video, which explains that risk is with the operator not with the government. I personally feel that Askok Layland CNG buses are probably best and most economical solution in today's date.  A developing country like India should focus on quantity then quality. We will be able to buy 3 CNG buses in price of 1 electric bus. instade of buying these 3 buses buy 2 and saved additional cost will go towards additional running cost. Due to this we will have 2 buses on road instade of 1. | Why do you raise suspecisions about what may happen to these companies after 7 years?  Meanwhile, people and taxpayers are benefitting with this model.  Indians always want to live in status quo, no matter if it require suffering.  China started 15 years ago, India is starting just now. So why are you cribbing about Indian governments are not buying buses directly and rather renting them.  It is so because we are smart and know how to stretch our  money for solving problems. Using words like Poker game randomly without any logic, facts or sense, YOU ARE TRYING CREATE sensationalism without having any  understaing of economics, finance, project management, and realism, just like other Indians who just demand it all or nothing.  If these companies go under water after 7 years it is their problem, not government's or tax payers. Someone else will rebid at that time and citizens will have enjoyed the ride for 7 years in the mean time. | This topic is most associated with general_unspecified (47/60) and has 21.7% negative versus 41.7% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 1 | Indian EV-Bus Adoption: R&D, Operations & User Experience | 61 | 14.841849148418492 | general_unspecified | 50.81967213114754 | 26.229508196721312 | 22.950819672131146 | 0.16193934426229506 | legacy | Ye sari companies (electra , jsw ) ko ban krna chahiye india me , jab hum R &D ko support hee nhi krenge to wo apne aap to nhi  bedhega ,  phir hum log hee social media pe aake bolenge ki india ko R&D pathetic hai. Tata ne battery khud develop kia hai harrier ke lie , kya wo kahi se v byd se v pichhe lag rha hai aapko ?! Nhi , aur wo to off roader bna ke ad kia hai us gadi ko unhone. We still have time , govt ko jsw pe rok lgana chahiye nhi to wo v din v jyda dur nhi jab hum apni automobile industry ke lie ro rahenge honge jaisa ki aaj mobile phone wale industry me rote hai. Japanese log apne country ke product ke lie hamesha incline hote hai lekin hmara aise kuchh nhi hai , 2kw ki battery kisi Chinese me extra mil gya to use turant hee le lenge. | Indian govt should have started manufacturing eBus  instead of all this drama.  Rental model is stupidity ... electric buses cost 1.5Cr BECAUSE battery is imported  By operating buses on rent it will never know the charging, range and passenger congestion data.  Govt should have bought 1 bus every month because the savings cost of even 1 eBus is MASSIVE.  The operating cost of 1 diesel bus fuel+service is almost 50L to 1cr in 1yr  By operating the bus on rent the govt have no major benefit but staff reduction happens which is not good. | This topic is most associated with general_unspecified (36/61) and has 23.0% negative versus 50.8% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 2 | Battery Technology, Swapping & Lifecycle Economics | 43 | 10.46228710462287 | general_unspecified | 44.18604651162791 | 39.53488372093023 | 16.27906976744186 | 0.14259534883720928 | legacy | We should invest   Battery swap technology for  buses for Big cities,  There will  5-8 major bus station should have Battery swap station which can swap fully charged battery in 15 min.  Maximum distance travelled by City bus one way is around 50 km. So Battery capacity max required is 75 km. No need to have Big battery capacity Once Bus reaches end point It should swap new fully charged battery for return trip.  Smaller batteries will reduce cost and increase range.  Since battery are swappable and as well as smaller, their can be charged slowly overnight with more reliable charger.    Buses need not to have their own charger control which wil reduce weight and cost.  Now Government can "Buy batterie's Ampere" hours and Own the Basic bus without the battery. There will be bus routes with One way trip of 25 km, then they can have even smaller batteries during battery swap. | Electric buses are a pathetic investment. In my view commercial EVs are b*******! More than 100 kWh battery pack in present technology conditions is not eco friendly. If you can go with hydrogen powered or CNG based or flex fuel based commercial vehicles then it will be good. Efficiency is the best policy. | This topic is most associated with general_unspecified (30/43) and has 16.3% negative versus 44.2% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 3 | Public Infrastructure, Funding & Alternative Transit | 52 | 12.652068126520682 | general_unspecified | 59.61538461538461 | 23.076923076923077 | 17.307692307692307 | 0.20209423076923078 | new_age | Excellent video.  The money saved on capex of buying the buses either through loans or upfront will be far greater than installing charging infrastructure at the bus depots. This is of course assuming that BEVs are the de facto technology for commercial buses.  BEST buses clock ablout 150-200 kms a day on average person bus. A weekly payment or bi monthly payment schedule should keep all parties happy.  5-7 years is a significant amount of time to expect drastic improvements in battery technology both in terms of cost pkwh as well as battery density pkwh. | India we still pay rs 5 for public transport and rs 10 for metro and we expect govt to invest in infrastructure and technology. We Indians still want to be cheapskates and want free toll and then expect govt to build state highways. we should be blamed in a capitalist world. | This topic is most associated with general_unspecified (40/52) and has 17.3% negative versus 59.6% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 4 | Domestic Manufacturing, R&D & China Dependence | 62 | 15.085158150851582 | general_unspecified | 56.45161290322581 | 22.580645161290324 | 20.967741935483872 | 0.24640161290322582 | new_age | Truth tata ashok leyland just assemble company not manufactures and mail is worst company for Hyderabad bus or truck dnt manufacturing in India and in this business driver life khaya hoga bolo heavy vehicle operater salary 22000 per month in olatra company Hyderabad or Delhi Mumbai living cost kha hae bolo this called development why electric you guys educated people dnt have ane scene on any industry Cummins the amarican mechanism engine manufacturer research on Indian road and driver the get Cummins isbi bs 6 engine low pollution high performance every Indian driver likes Cummins that's tata and Bharath benz sustained in Indian with company tata wast company and same in ashok leyland with hino and zf garebox aray houly education engineering and business we want aa good engine and gareboxs for our national and good drivers and driver life  not electric or hydrogen | Ind has always short cut and mindset of slavery thatswhy no work on R&D ind only 10 companies has R&D 90 % imported thatswhy ind eco never self dependent or near self dependent anytime US,china hurt ind eco when they want due nostrategic future  planning investment on R&D by successive govt because govt only making 5 year plan and maximum time money govt invest to make happy its voters or appease certain section thatswhynow era of fast competition so ind need make independent body like courts EC to ensure continue focus on indian defence and industrial R&D and future planning which no hurt after govt change etc other ind already late and if this continues many countries like ind loose its eco industrial freedom and become dependent on china or US and behave modern colonies | This topic is most associated with general_unspecified (33/62) and has 21.0% negative versus 56.5% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 5 | Tender Economics, Public Funding & Private Operators | 47 | 11.435523114355231 | general_unspecified | 61.702127659574465 | 23.404255319148938 | 14.893617021276595 | 0.2551276595744681 | legacy | NOBODY realises the operating costs of 1 Diesel bus is almost 50L-1Cr per yr ... We are all ok with that... the whole department... In EVERY STATE  has become BANKRUPT because of that... Buy we will NOT BUY... ONLY RENT and incur same expense.  So companies like JBM Auto and Olectra Greentech get DOUBLE profit... 1. Cost of bus & 2. Operation profit.  So what the state transport dept had to save goes in the pocket of private bus companies.  BUYING WAS ALWAYS PROFITABLE. | Instead of freebies, even if 50% of freebie funds are used for investing in such infra, capital problem can be solved. Free dene keliye dunia barke loan , paisa hota hai govts ke paas, par baat tab public transport, education, health par aati hai tab funds ka achanak shortage hota hai, sabi public transport corporation gaate meh hota hai... | This topic is most associated with general_unspecified (39/47) and has 14.9% negative versus 61.7% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 6 | New-Age OEM Execution, Reliability & Service Risk | 42 | 10.218978102189782 | general_unspecified | 52.38095238095238 | 28.571428571428573 | 19.047619047619047 | 0.13822142857142858 | new_age | Please double check the Non AC vs AC electric buses that will be running all over India in this model. My understanding is that the ratio will be 90:10 non AC to AC. Your point about depleted battery life issues because of internal AC + external heat goes out of the window in that case for 90% of the cases.   The biggest challenge that these new manufacturers face right now for the next few years is the basic ability to keep buses running. In Karnataka, the minister has already flagged in Jan 2026 the many issues with the electric buses. Companies may go bankrupt much before the 6/7 years time when they have to replace the batteries | worst service ever, had to stand for 45 minutes as the bus was smaller than what is was supposed to be, had to mail more than thrice for which they said that i am not eligible for refund as i have completed the trip, i had to sit in a non recliner(after standing for more than 45 minutes) while i paid extra for the recliner ones, mistakes happen sometimes i understand but the service provided by the customer care is even worse, would not recommend, please be aware, they are here just for the money, they don’t care about customer service or satisfaction, no refund or compensation provided as well @nuegoindia | This topic is most associated with general_unspecified (30/42) and has 19.0% negative versus 52.4% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |
| 7 | Supply-Chain Risk, Charging Alternatives & Service Gaps | 44 | 10.70559610705596 | general_unspecified | 54.54545454545455 | 18.181818181818183 | 27.272727272727273 | 0.15941590909090905 | new_age | Most of us think China has made us it's customer but it is exactly opposite of what they are doing they want our disel vechile to be fully replaced by its electric one. We create body parts infrastructure and scrap old of disel. Then they give us batteries at subsidized price so that we think it is compitative to an environment friendly. Then they will use this leverage for geopolitical gain if we resist it simply denies to provide heart of these bodies under sanction. We are almost becoming gulam just China has used other model than Pakistan otherwise we are no different for them just cheap consumer who can't live without them. | My experience with NueGo has been extremely disappointing. My suitcase is still missing despite multiple calls, emails, follow-ups, and sharing all the required details, including my PNR. I have been repeatedly assured that the issue would be resolved soon, but I have only received delays and false commitments. The luggage contains my essential belongings, and the continued delay has caused me significant inconvenience as well as financial hardship. Instead of resolving the issue, customer support keeps providing new excuses without any concrete action. I expected professionalism and accountability from NueGo, but unfortunately, my experience has been the opposite. If this matter is not resolved immediately, I will have no option but to pursue legal and consumer protection remedies. Based on my experience, I cannot recommend NueGo's services to anyone. | This topic is most associated with general_unspecified (40/44) and has 27.3% negative versus 54.5% positive comments. | Preserve the attributes associated with positive comments while validating them with larger, direct-source samples. |  |

Negative post-use N=17; negative pre-adoption N=11; positive post-use N=24. Subgroups below 10 are explicitly weak samples.

## 15. Strategic implications

- **Finding →** Topics with more negative than positive comments identify candidate friction areas. **Evidence/metric →** See `topic_sentiment_lifecycle_insights.csv`. **Interpretation →** These are associations within an imbalanced corpus. **Business implication →** Validate through targeted interviews, service logs, and balanced surveys before intervention.
- **Finding →** Positive post-use topics identify attributes users may value. **Evidence/metric →** See `positive_experience_topics.csv`. **Interpretation →** VADER remains exploratory, while topic labels are human-interpreted descriptions of the LDA outputs. **Business implication →** Test whether these attributes persist in verified direct-source feedback.
- **Finding →** OEM-group and NueGo topic mixes differ descriptively. **Evidence/metric →** See topic/OEM tables and subgroup counts. **Interpretation →** Entity, platform, and provenance composition confound comparison. **Business implication →** Keep operator service, OEM product quality, and tender outcomes separate in decisions.

## 16. Limitations

Mixed provenance, incomplete lineage, platform/entity imbalance, small subgroups, non-random sampling, automated lifecycle labels outside the reviewed set, VADER language limitations, provisional topic labels, and LDA instability restrict inference. Association is not causality. Exploratory evidence is not definitive evidence.

## 17. Files and charts generated

All CSV tables, six sentiment/lifecycle charts, five topic charts, pyLDAvis HTML, lifecycle freeze report, manual-check sample, lifecycle-frozen dataset, and the 548-row final analysis dataset are saved under `04_outputs/text/final`, `01_data/processed`, and `02_notebooks` within the project Drive folder.



> **Topic interpretation note:** Topic labels were assigned through human
> review of top terms and representative comments. The selected eight-topic
> model has moderate coherence, so topics should be treated as overlapping
> exploratory themes rather than mutually exclusive consumer segments.
