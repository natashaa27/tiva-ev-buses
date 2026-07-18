# Phase 2 · Feature → Perception hypothesis tests

_Perception = CLIP zero-shot **proxy** (`pxy_*`, 0-100). Re-run on human `coder_*` ratings once `perception_coding_template.csv` is filled. n=39 — exploratory._

## H1. Does real-operation imagery increase trust?

- **Test:** trust for operational-proof images vs product-showcase images
- **Result:** `{'mean_true': 70.2, 'n_true': 21, 'mean_false': 66.9, 'n_false': 18, 'delta': 3.3}`
- **Reads as:** positive delta => operational imagery scores higher pxy_trust
- **Direction:** SUPPORTS the hypothesis (Δ=+3.3, n_true=21, n_false=18).

## H2. Do bright interiors improve comfort perception?

- **Test:** Spearman brightness vs comfort
- **Result:** `{'rho': 0.255, 'p': 0.1175, 'n': 39}`
- **Reads as:** positive rho => brighter images perceived as more comfortable
- **Direction:** SUPPORTS the hypothesis (ρ=+0.255, p=0.1175, n=39).

## H3. Does charging visibility improve technology perception?

- **Test:** modernity for charger/depot-visible vs not
- **Result:** `{'mean_true': 93.7, 'n_true': 6, 'mean_false': 75.0, 'n_false': 33, 'delta': 18.7}`
- **Reads as:** positive delta => charger visibility raises modernity/technology read
- **Direction:** SUPPORTS the hypothesis (Δ=+18.7, n_true=6, n_false=33).

## H4. Do passengers make images more relatable?

- **Test:** visual appeal for person-present vs person-absent
- **Result:** `{'mean_true': 84.2, 'n_true': 10, 'mean_false': 95.4, 'n_false': 29, 'delta': -11.3}`
- **Reads as:** positive delta => images with people score higher appeal/relatability
- **Direction:** does NOT support the hypothesis (Δ=-11.3, n_true=10, n_false=29).

## H5. Does accessibility visibility improve brand inclusiveness?

- **Test:** accessibility perception for ramp/low-floor-visible vs not
- **Result:** `{'mean_true': 71.5, 'n_true': 3, 'mean_false': 55.6, 'n_false': 36, 'delta': 15.9}`
- **Reads as:** positive delta => visible accessibility raises inclusiveness read
- **Direction:** SUPPORTS the hypothesis (Δ=+15.9, n_true=3, n_false=36).

