# Phase 2 · Feature dictionary

| Column | Layer | Meaning |
|---|---|---|
| `brightness` | low | Mean grayscale luminance (0-255) |
| `contrast` | low | Std-dev of grayscale luminance |
| `saturation` | low | Mean HSV saturation (0-255) |
| `sharpness` | low | Variance of Laplacian (focus/detail) |
| `warm_cool_bias` | low | + warm / − cool colour bias (−1..1) |
| `colourfulness` | low | Hasler-Süsstrunk perceived colourfulness |
| `edge_density` | low | Fraction of Canny-edge pixels (visual busyness) |
| `symmetry_h / _v` | low | Left-right / top-bottom mirror symmetry (0-1) |
| `rule_of_thirds` | low | Share of gradient energy near the 4 thirds points |
| `visual_balance` | low | Left/right + top/bottom energy balance (0-1) |
| `figure_ground_sep` | low | Centre-vs-border detail ratio (subject isolation) |
| `dominant_colors / palette_family` | low | KMeans top-3 colours + bucket |
| `blip_caption` | high | BLIP scene caption |
| `obj_bus/person/truck_count` | high | DETR (COCO) object counts @0.7 |
| `hl_bus_visible` | high | Bus present (DETR or CLIP fleet) |
| `hl_passenger_driver_visible` | high | Person present (DETR) |
| `hl_charger_depot_flag` | high | CLIP: charger/depot visible |
| `hl_accessibility_flag` | high | CLIP: wheelchair ramp / low-floor visible |
| `hl_bus_in_motion_flag` | high | CLIP: bus in motion vs parked |
| `hl_fleet_scale_deploy` | high | Fleet-scale deployment (DETR≥3 or CLIP) |
| `hl_govt_handover_flag` | high | CLIP: govt handover/launch ceremony |
| `hl_operational_proof_flag` | high | CLIP: real operation vs product showcase |
| `hl_setting` | high | CLIP argmax: urban / natural / indoor_studio / infographic_text |
| `theme_* (_flag)` | high | CLIP: technology / comfort / trust / sustainability |
| `ocr_text, nf_*` | text | Tesseract OCR + VADER narrative-framing sentiment |
| `pxy_* (0-100)` | perception | CLIP zero-shot PROXY for 7 perception dims |
| `coder_* ` | perception | Blank — human/independent coder 1-7 ratings |

> `pxy_*` are automated CLIP proxies, **not** human perception. Fill `perception_coding_template.csv` with real coders to replace them.
