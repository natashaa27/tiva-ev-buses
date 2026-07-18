# EV Bus Instagram Creative Teardown

**A data-driven analysis of 10 competitor Instagram posts — Tata Motors, Olectra, and Switch Mobility.**
Analysis date: 2026-07-18 · Interactive report: `campaign_report.html` · Dataset: `campaign_dataset.csv`

> **Read this as a compass, not a verdict.** With n = 10 posts, correlations point at *direction and effect size*, not statistical certainty — most p-values sit above 0.05 by design of the small sample. The signal is the consistent *pattern* across three independent method layers (pixel features, content codes, perception scores).

---

## 1. Method

| Layer | How it was produced |
|---|---|
| **Low-level visual features** | Computed from pixels in Python (OpenCV/PIL) on each creative after auto-cropping the Instagram chrome: brightness, saturation, contrast, colourfulness (Hasler–Süsstrunk), warm/cool ratio, blue-green proportion, edge density, sharpness (variance of Laplacian), left-right symmetry, dominant colour. |
| **High-level content** | Hand-coded 0/1 flags from visual inspection (25+): exterior/interior/cockpit, charging, real-road, fleet-scale, passengers, driver, women/elderly/children, ramp, depot, government, urban, green, performance metric, product-vs-human, studio-vs-real — plus one **communication theme** per post. |
| **Perception** | Scored 1–5 by a single systematic coder: trust, modernity, comfort, accessibility, sustainability, operational readiness, appeal. |
| **Statistics** | Spearman (numeric), Mann–Whitney U (binary), Kruskal–Wallis (themes), and a log-log OLS to separate follower base from creative effect. |

**Engagement Rate** = (Likes + Comments) ÷ Followers × 100.

**Follower counts** (web, Jul 2026): Tata 153K · Switch 41K · Hinduja 13K are verified. **Olectra ≈ 35K is an estimate** — the exact count was not retrievable, so Olectra's ER *level* carries that uncertainty (its internal rank order does not).

---

## 2. Engagement leaderboard

| # | Post | Brand | Followers | Likes | Comments | ER | Theme |
|---|------|-------|----------:|------:|---------:|----:|-------|
| 1 | Ultra Prime "productive workday" | Tata | 153K | 23,100 | 71 | **15.14%** 🏆 viral | Passenger comfort |
| 8 | Go Electric city EV | Olectra | ~35K* | 2,154 | 0 | 6.15% | Sustainability |
| 10 | Starbus EV | Tata | 153K | 8,444 | 53 | 5.55% | Sustainability |
| 6 | "Silence" fleet | Olectra | ~35K* | 1,589 | 1 | 4.54% | Product showcase |
| 3 | 2016 first-EV heritage | Olectra | ~35K* | 1,534 | 1 | 4.39% | Technology proof |
| 4 | Limca 13,000 ft record | Olectra | ~35K* | 1,446 | 4 | 4.14% | Operational proof |
| 9 | Ultra EV 200 kWh | Tata | 153K | 5,968 | 11 | 3.91% | Technology proof |
| 5 | Prawaas 5.0 fleet | Switch | 41K | 1,325 | 5 | 3.24% | Tender/fleet milestone |
| 2 | Switch double-decker | Switch/Hinduja | 13K | 85 | 4 | 0.68% | Sustainability |
| 7 | Starbus Prime diesel | Tata | 153K | 67 | 4 | **0.05%** 💤 flop | Service reliability |

\* Olectra followers estimated.

**Top:** Post 1 — aspirational office-goers stepping off a sleek bus at a corporate campus. Bright, high-contrast, human, real-use story; a clear viral outlier at 23.1K likes.
**Best EV-native:** Post 8 — sharp moving bus, driver visible, split green/urban backdrop; highest sustainability perception in the set (5/5).
**Worst:** Post 7 — a utilitarian diesel mini-bus in dull, low-contrast traffic. Same 153K follower base as Tata's winners, which proves the *creative*, not reach, sank it.

---

## 3. What worked / what didn't

### ✅ Worked
- **Real-world deployment with people** — buses operating on recognisable streets, passengers and drivers visible (Posts 1, 3, 8, 10).
- **High contrast & sharpness** — crisp, punchy images out-performed soft, flat ones on every cut.
- **An aspirational human story** — "productive workday", "trust it to get you there": outcomes, not spec sheets.
- **A single, confident subject** — one hero bus, clean figure-ground, minimal competing copy.
- **Green / sustainability framing** — nudged both engagement (median 5.9% vs 4.0%) and perceived sustainability (4.5 vs 3.0).

### ✖️ Didn't work
- **Utilitarian product shots with no story** — the diesel Starbus Prime in flat traffic collapsed to 0.05% ER.
- **Copy-dense event flyers** — the Prawaas 5.0 announcement (≈30% text overlay) under-performed the fleet's own average.
- **Beautiful-but-empty hero renders** — the Switch double-decker at the Gateway of India looked stunning but showed no operation and no people → 0.68%.
- **Studio VFX over proof** — lightning-bolt and light-trail renders (Posts 9, 10) scored high on *modernity* but lower on *trust* and operational readiness.

---

## 4. Feature-vs-engagement analysis

### Spearman correlations — low-level features vs ER (n = 10)

| Feature | ρ | p | Read |
|---|---:|---:|---|
| **Contrast** | **+0.72** | **0.02** | Only significant result. Every post above 68 contrast beat every post below 60. |
| Sharpness | +0.59 | 0.07 | Crisp beats soft. |
| Edge density | +0.58 | 0.08 | Detail/definition helps. |
| Brightness | +0.27 | 0.45 | Weak positive. |
| Bus-to-image area | +0.20 | 0.57 | Weak positive. |
| Colourfulness | +0.18 | 0.63 | Weak (but +0.62 once the viral outlier is removed). |
| Blue/green proportion | −0.15 | 0.68 | Negligible. |
| Background clutter | −0.11 | 0.76 | Negligible. |
| Negative space | −0.29 | 0.42 | Weak negative. |
| **Text-overlay %** | **−0.48** | 0.16 | The busier the copy, the colder the post. |

*Excluding the viral outlier (Post 1, n = 9): colourfulness ρ = +0.62 and contrast ρ = +0.61 lead — the craft signal strengthens, not weakens.*

### Mann–Whitney U — binary content features vs ER

| Feature present | Median ER on | Median ER off | p |
|---|---:|---:|---:|
| Human present | 5.55% | 3.91% | 0.22 |
| Green / environmental | 5.85% | 4.03% | 0.18 |
| Driver visible | 4.97% | 4.03% | 0.76 |
| Real deployment | 4.39% | 3.91% | 0.55 |
| Performance metric | 4.14% | 4.54% | 0.84 |
| Fleet-scale | 3.89% | 4.26% | 0.89 |

Medians favour human & green content; none clear significance at n = 10 — directional evidence, consistent with the pixel-level and perception results.

### Kruskal–Wallis — ER across the 7 themes
H = 5.65, p = 0.46 — too few posts per theme (mostly n = 1) to separate theme effects statistically. Reported for completeness.

### Regression sanity-check (log-log OLS)
`log10(engagement) = −1.22 + 0.93·log10(followers) + 0.05·human − 0.12·real_deploy` (R² ≈ 0.22, directional only).
Engagement scales **≈ proportionally with follower base** (β ≈ 0.93). Once normalised to a *rate*, follower size barely predicts ER (Spearman ER vs followers ρ = 0.10) — which is exactly why **engagement rate is the fair cross-brand comparator**.

---

## 5. Legacy vs new-age

Legacy = Tata Motors. New-age = Olectra + Switch (EV-native brands).

| Dimension | Legacy (Tata) | New-age (Olectra/Switch) | Read |
|---|---:|---:|---|
| Median engagement rate | 4.73% | 4.26% | Near parity on rate… |
| **Median likes / post** | **7,206** | **1,490** | …but **4.8×** raw reach from base size |
| Human present | 75% | 33% | Tata leads with people |
| Performance metric shown | 75% | 33% | Tata badges specs (kWh, engine) |
| Colourfulness (0–100) | 46 | 70 | EV-natives are far more saturated |
| Perceived modernity (1–5) | 4.25 | 3.67 | Tata's VFX reads more modern |
| Perceived sustainability (1–5) | 2.75 | 3.67 | EV-natives own the green story |
| Perceived operational readiness | 3.25 | 3.83 | Olectra's record/street proof lands |

**Per-OEM** (avoids group distortion):

| Brand | n | Median ER | Median likes | Perceived trust | Perceived modernity |
|---|--:|--:|--:|--:|--:|
| Tata | 4 | 4.73% | 7,206 | 3.75 | 4.25 |
| Olectra | 4 | 4.46% | 1,562 | 3.75 | 3.50 |
| Switch | 2 | 1.96% | 705 | 3.00 | 4.00 |

- **Tata** — widest spread (15.1% viral commute → 0.05% diesel flop). Human-led + spec badges + studio polish; wins modernity, weakest on sustainability.
- **Olectra** — the most *consistent* performer (4.1–6.2%, tight band). Heritage & record proof, real streets, boldest colour; best operational-readiness perception.
- **Switch** — most striking art direction, weakest engagement. Hero renders and an event flyer — beauty without operation or people. Clear headroom.

---

## 6. Perception — engagement ≠ what the image said

Holding the 1–5 perception scores against the content codes gives clean, directionally strong links:

- **Real-operation → trust.** Deployment images averaged **4.0/5** trust vs **3.2** for studio/product shots.
- **Green context → sustainability.** **4.5 vs 3.0** — the clearest perception jump in the set.
- **Bright scenes → comfort.** The brighter half scored **3.0 vs 2.2**.
- **VFX spec renders → modernity, not trust.** Posts 9 & 10 top modernity (5/5) yet sit mid-pack on trust and low on operational readiness.

**Does perception track engagement?** Rank-correlation of perceived scores with actual ER: trust ρ = 0.43, appeal ρ = 0.36, modernity ρ = 0.28. Perceived **trust** is the dimension most aligned with real engagement — credibility, not gloss, is what the audience rewards.

> ⚠︎ Perception here is a **single systematic coder**. For a decision-grade read, have 2–3 independent coders (or a small respondent panel) rate each image and average — the scales above drop straight in.

---

## 7. Content coverage & gaps

Share of the 10 posts carrying each cue:

| Present in… | % | | Present in… | % |
|---|--:|---|---|--:|
| Urban setting | 70% | | Fleet-scale | 20% |
| Human present | 50% | | Government / STU livery | 20% |
| Real deployment | 50% | | Green / environmental | 20% |
| Performance metric | 50% | | **Charging infrastructure** | **0%** |
| Driver visible | 40% | | **Accessibility / ramp** | **0%** |
| Passengers visible | 30% | | **Depot / maintenance / uptime** | **0%** |

For a category sold largely to **government fleet operators and STUs**, the creatives are silent on the de-risking cues a procurement audience looks for — **no charging, no accessibility, no depot/maintenance** appears in any post. These are the exact visuals the target buyer uses to judge execution capability, and they are the campaign's biggest, cheapest opportunity.

---

## 8. Playbook — five moves, each earned by the data

Format: **Finding → Evidence → Interpretation → Implication → Action.**

**01 · Lead with real-operation proof, not studio hero shots**
- *Finding:* Real-deployment images earn higher trust and engagement than isolated product renders.
- *Evidence:* Deployment posts trust 4.0 vs 3.2; the two pure hero renders sit at 0.68% and 3.9% ER.
- *Interpretation:* "It's actually running" reads as credibility; a beauty render reads as a promise.
- *Implication:* Product photography alone is insufficient for a trust-led, procurement-facing category.
- *Action:* Shoot buses operating on recognisable routes with visible passengers; pair with a verifiable uptime or fleet-size number.

**02 · Fill the trust vacuum: charging, depot, accessibility, uptime**
- *Finding:* Zero of 10 posts show charging, a ramp, or a depot/maintenance scene.
- *Evidence:* 0% charging · 0% accessibility · 0% depot · 20% fleet-scale · 20% government livery.
- *Interpretation:* The category ignores exactly the cues its dominant buyer uses to de-risk a purchase.
- *Implication:* Whoever fills this space owns the "execution capability" narrative uncontested.
- *Action:* Build a "proof" content pillar — depot charging at scale, low-floor ramp boarding, maintenance crews, a live uptime/route-km counter.

**03 · Win on craft: high contrast, sharp, low text**
- *Finding:* Crisper, higher-contrast, lower-text images consistently out-engage soft, copy-heavy ones.
- *Evidence:* Contrast ρ = +0.72 (p = 0.02); sharpness ρ = +0.59; text-overlay ρ = −0.48. The 30%-text expo flyer under-performed its own fleet.
- *Interpretation:* On a fast feed, punchy figure-ground stops the thumb; dense copy signals "ad".
- *Implication:* Production craft is a measurable performance lever, not a nice-to-have.
- *Action:* Set a standard — one headline ≤ 7 words, text overlay under ~15% of frame, strong subject-background separation, deep blacks.

**04 · Put people in the frame — and sell the outcome**
- *Finding:* Human-led creatives out-engage product-only ones; the top post is a pure human-outcome story.
- *Evidence:* Human median ER 5.55% vs 3.91% (1.4×); the "productive workday" post hit 15.1% — the ceiling.
- *Interpretation:* People buy the outcome (an easy commute, a cleaner city) and relate to faces more than sheet metal.
- *Implication:* The bus should be the enabler of a human moment, not the subject of a portrait.
- *Action:* Cast real riders — commuters, women, elderly, families, wheelchair users boarding — and frame the benefit to them.

**05 · Match the visual to the audience you're de-risking**
- *Finding:* Different perception levers fire for different content — trust from operation, sustainability from green context, modernity from spec/VFX.
- *Evidence:* Green context → sustainability 4.5 vs 3.0; VFX → modernity 5/5; real ops → trust 4.0 vs 3.2.
- *Interpretation:* One creative can't carry every message; the visual must be chosen for the outcome that audience needs.
- *Implication:* Plan the grid by audience-outcome, not by product-launch calendar.
- *Action:* Use the audience matrix below to brief each creative to a single desired outcome and its proven visual.

### Audience → outcome → visual

| Audience | Desired outcome | Recommended visual | Backed by |
|---|---|---|---|
| Government / fleet operators | Trust & execution capability | Fleet at scale, depot charging, maintenance crews, uptime/route-km proof | Moves 01, 02 |
| Passengers | Comfort & accessibility | Bright interiors, real riders, low-floor boarding & ramps in use | Move 04; bright→comfort |
| EV / tech audience | Modernity | Charging, cockpit, telematics, battery ecosystem, clean spec badges | VFX→modernity 5/5 |
| General public | Sustainability | Bus operating in a recognisable city with human & green context | Green→sustain 4.5 |

---

## 9. Caveats — read before quoting a number

- **Sample size (n = 10).** Everything is directional; most results won't reach p < 0.05 at this size. The value is the consistent pattern across independent method layers.
- **Follower counts.** Tata 153K, Switch 41K, Hinduja 13K verified. **Olectra ≈ 35K is an estimate** — Olectra's ER level shifts if the true figure differs, though rank order within Olectra is unaffected.
- **Collab posts.** Two posts are collaborations (Hinduja×Switch, Switch×Prawaas); real reach spans both audiences, so their ER is conservative.
- **Viral outlier.** Post 1's 23.1K likes (15.1% ER) is far above the field; key correlations are reported with and without it.
- **Rendered creatives.** All 10 appear AI-composited/rendered rather than photographed — a finding in itself: the category has little genuine on-road documentary imagery.
- **Single perception coder.** Upgrade to 2–3 coders or a respondent panel before this drives spend.
- **No video in this set.** The 10 assets are static posts; the video-analysis framework (hook, scene changes, screen-time, CTA) applies when reels are added.
