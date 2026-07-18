"""Standalone runner that mirrors the low-level portion of 04_image_analysis.ipynb.
Skips BLIP + OCR (heavy downloads deferred to the user's Jupyter environment).
Produces:
  - 01_data/processed/ev_bus_image_analysis.csv
  - 04_outputs/images/final/*.png
  - 04_outputs/images/final/strategic_output.md
"""
import os, re, json, warnings, math
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import cv2
from sklearn.cluster import KMeans

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR   = PROJECT_ROOT / 'images'
PROCESSED    = PROJECT_ROOT / 'data'
CHARTS       = PROJECT_ROOT / 'outputs' / 'charts'
REPORTS      = PROJECT_ROOT / 'outputs' / 'reports'
OUTPUTS      = CHARTS  # charts default target
PROCESSED.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}
paths = sorted(p for p in IMAGES_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTS)
print(f'Found {len(paths)} images in {IMAGES_DIR}')

def dominant_colors(bgr, k=3, sample=15000):
    img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).reshape(-1, 3)
    if img.shape[0] > sample:
        img = img[np.random.choice(img.shape[0], sample, replace=False)]
    km = KMeans(n_clusters=k, n_init=4, random_state=42).fit(img)
    counts = Counter(km.labels_.tolist())
    total = sum(counts.values())
    centers = km.cluster_centers_.astype(int)
    return [(tuple(int(v) for v in centers[i]), round(c/total, 3)) for i, c in counts.most_common()]

def warm_cool_bias(rgb):
    r, g, b = rgb[..., 0].mean(), rgb[..., 1].mean(), rgb[..., 2].mean()
    warm = (r + 0.5*g) / 255.0
    cool = (b + 0.5*g) / 255.0
    if warm + cool == 0:
        return 0.0
    return round((warm - cool) / (warm + cool), 3)

def classify_palette(top_rgb):
    r, g, b = top_rgb
    if max(r, g, b) < 40:
        return 'dark/black'
    if min(r, g, b) > 220:
        return 'white'
    if r > g and r > b and r - b > 40:
        return 'warm (red/orange)'
    if b > r and b > g and b - r > 40:
        return 'cool (blue)'
    if g > r and g > b:
        return 'green'
    if abs(r-g) < 20 and abs(g-b) < 20:
        return 'neutral/gray'
    return 'mixed'

records = []
for p in paths:
    bgr = cv2.imread(str(p))
    if bgr is None:
        print(f'skip unreadable: {p.name}')
        continue
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv  = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    rgb  = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    brightness = float(gray.mean())
    contrast   = float(gray.std())
    saturation = float(hsv[..., 1].mean())
    sharpness  = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    warm_cool  = warm_cool_bias(rgb)
    dc         = dominant_colors(bgr, k=3)
    top_family = classify_palette(dc[0][0])
    records.append({
        'image_id'      : p.stem,
        'file_path'     : str(p.relative_to(PROJECT_ROOT)),
        'width'         : w,
        'height'        : h,
        'aspect_ratio'  : round(w/h, 3),
        'file_size_kb'  : round(p.stat().st_size/1024, 1),
        'brightness'    : round(brightness, 2),
        'contrast'      : round(contrast, 2),
        'saturation'    : round(saturation, 2),
        'sharpness'     : round(sharpness, 2),
        'warm_cool_bias': warm_cool,
        'top_color_rgb' : list(dc[0][0]),
        'top_color_share': dc[0][1],
        'palette_family': top_family,
        'dominant_colors': json.dumps(dc),
        # BLIP + OCR + manual metadata deferred to notebook run on user's env
        'blip_caption'  : '',
        'ocr_text'      : '',
        'oem_shown'     : 'unknown',
        'operator_shown': 'none',
        'image_type'    : 'unknown',
        'lifecycle_stage': 'general_unspecified',
        'is_ev_bus'     : None,
        'source_url'    : '',
        'source_date'   : '',
        'publisher'     : '',
    })
    print(f'  {p.stem[:8]}  b={brightness:5.1f}  c={contrast:5.1f}  s={saturation:5.1f}  sharp={sharpness:7.1f}  wc={warm_cool:+.2f}  top={top_family}')

df = pd.DataFrame(records)
csv_path = PROCESSED / 'ev_bus_image_analysis.csv'
df.to_csv(csv_path, index=False)
print(f'\nWrote {csv_path}')

# aspect ratio buckets
def ar_bucket(r):
    if r < 0.9:  return 'portrait (<0.9)'
    if r > 1.1:  return 'landscape (>1.1)'
    return 'square (~1:1)'
df['ar_bucket'] = df['aspect_ratio'].apply(ar_bucket)

# ---- Charts ----
# 1. palette strip
top_colors = [tuple(r) for r in df['top_color_rgb']]
fig, ax = plt.subplots(figsize=(10, 1.4))
for i, (r,g,b) in enumerate(top_colors):
    ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=(r/255, g/255, b/255)))
ax.set_xlim(0, len(top_colors)); ax.set_ylim(0, 1); ax.axis('off')
ax.set_title('Dominant color per image (corpus palette strip)')
plt.tight_layout()
plt.savefig(OUTPUTS / 'fig_palette_strip.png', dpi=150)
plt.close()

# 2. palette family bar
plt.figure(figsize=(6, 3))
df['palette_family'].value_counts().plot(kind='barh', color='#2e86de')
plt.title('Palette family (dominant-color bucket)')
plt.xlabel('Image count')
plt.tight_layout()
plt.savefig(OUTPUTS / 'fig_palette_family.png', dpi=150)
plt.close()

# 3. aspect ratio bar
plt.figure(figsize=(6, 3))
df['ar_bucket'].value_counts().plot(kind='barh', color='#27ae60')
plt.title('Aspect-ratio mix (platform fit)')
plt.xlabel('Image count')
plt.tight_layout()
plt.savefig(OUTPUTS / 'fig_aspect_ratio.png', dpi=150)
plt.close()

# 4. feature distributions
fig, axs = plt.subplots(2, 2, figsize=(9, 6))
for ax, col, color in zip(axs.ravel(),
                          ['brightness','contrast','saturation','sharpness'],
                          ['#2980b9','#8e44ad','#e67e22','#16a085']):
    ax.hist(df[col].dropna(), bins=10, color=color, edgecolor='white')
    ax.axvline(df[col].median(), color='k', ls='--', lw=1)
    ax.set_title(f'{col} (median={df[col].median():.1f})')
plt.tight_layout()
plt.savefig(OUTPUTS / 'fig_feature_distributions.png', dpi=150)
plt.close()

# 5. warm/cool bias distribution
plt.figure(figsize=(6, 3))
plt.hist(df['warm_cool_bias'], bins=12, color='#c0392b', edgecolor='white')
plt.axvline(0, color='k', ls='--')
plt.title(f'Warm/cool bias — median {df["warm_cool_bias"].median():+.2f} (positive = warm)')
plt.xlabel('warm ← 0 → cool')
plt.tight_layout()
plt.savefig(OUTPUTS / 'fig_warm_cool.png', dpi=150)
plt.close()

print('Wrote 5 charts to', OUTPUTS)

# ---- Summary stats for strategic writeup ----
def q(col): return dict(min=df[col].min(), median=df[col].median(), mean=df[col].mean(), max=df[col].max(), std=df[col].std())
summary = {
    'n_images'       : len(df),
    'brightness'     : q('brightness'),
    'contrast'       : q('contrast'),
    'saturation'     : q('saturation'),
    'sharpness'      : q('sharpness'),
    'warm_cool_bias' : q('warm_cool_bias'),
    'aspect_ratio'   : q('aspect_ratio'),
    'palette_family' : df['palette_family'].value_counts().to_dict(),
    'ar_bucket'      : df['ar_bucket'].value_counts().to_dict(),
    'top_5_darkest'  : df.nsmallest(5, 'brightness')[['image_id','brightness','palette_family']].to_dict('records'),
    'top_5_brightest': df.nlargest(5, 'brightness')[['image_id','brightness','palette_family']].to_dict('records'),
    'lowest_sharp'   : df.nsmallest(5, 'sharpness')[['image_id','sharpness']].to_dict('records'),
}
with open(REPORTS / 'summary_stats.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)
print('Wrote', REPORTS / 'summary_stats.json')

print('\n=== SUMMARY ===')
print(f'n = {summary["n_images"]}')
for k in ['brightness','contrast','saturation','sharpness','warm_cool_bias','aspect_ratio']:
    s = summary[k]
    print(f'  {k:15s} median={s["median"]:.2f}  mean={s["mean"]:.2f}  range=[{s["min"]:.2f}, {s["max"]:.2f}]')
print(f'  palette_family  {summary["palette_family"]}')
print(f'  ar_bucket       {summary["ar_bucket"]}')
