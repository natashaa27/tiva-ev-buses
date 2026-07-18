"""Second-stage runner: OCR + VADER narrative-framing sentiment + LDA topics.
Reads the CSV produced by run_image_pipeline.py, adds ocr_text, nf_* fields,
LDA topic-word list, re-saves CSV, produces additional charts, and writes
strategic_findings_from_ocr.md.
"""
import re, json
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import pytesseract
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

sns.set_style('whitegrid')

ROOT = Path(__file__).resolve().parent.parent
CSV  = ROOT / 'data' / 'ev_bus_image_analysis.csv'
OUT  = ROOT / 'outputs' / 'charts'
REPORTS = ROOT / 'outputs' / 'reports'
df = pd.read_csv(CSV)
print(f'Loaded {len(df)} rows from {CSV}')

# ---- OCR ----
def ocr_of(rel_path):
    p = ROOT / rel_path
    with Image.open(p) as im:
        return pytesseract.image_to_string(im.convert('RGB')).strip()

ocrs = []
for i, r in df.iterrows():
    try:
        t = ocr_of(r['file_path'])
    except Exception as e:
        print(f'  OCR failed {r["image_id"][:8]}: {e}')
        t = ''
    ocrs.append(t)
    head = t[:70].replace('\n', ' ')
    print(f'  [{i+1:>2}/{len(df)}] {r["image_id"][:8]}  chars={len(t):4d}  head="{head}"')
df['ocr_text'] = ocrs
df['ocr_char_len'] = df['ocr_text'].str.len()

# ---- VADER narrative-framing sentiment ----
vader = SentimentIntensityAnalyzer()
def score(t):
    if not isinstance(t, str) or not t.strip():
        return dict(nf_neg=None, nf_neu=None, nf_pos=None, nf_compound=None, nf_label='no_text')
    s = vader.polarity_scores(t)
    lbl = 'positive' if s['compound'] >= 0.05 else ('negative' if s['compound'] <= -0.05 else 'neutral')
    return dict(nf_neg=s['neg'], nf_neu=s['neu'], nf_pos=s['pos'], nf_compound=s['compound'], nf_label=lbl)
nf = pd.DataFrame([score(t) for t in df['ocr_text']])
df = pd.concat([df.reset_index(drop=True), nf], axis=1)

# ---- LDA topics ----
STOP = {'the','and','for','with','from','you','are','this','that','they','their','has','have','been','not','but','all','any','was','were','its','can','will','more','than','into','who','how','what','why','when'}
def clean(t):
    if not isinstance(t, str): return ''
    t = re.sub(r'[^A-Za-z\s]', ' ', t.lower())
    t = re.sub(r'\s+', ' ', t).strip()
    return ' '.join(w for w in t.split() if len(w) > 2 and w not in STOP)
df['ocr_clean'] = df['ocr_text'].apply(clean)
corpus = df.loc[df['ocr_clean'].str.len() > 0, 'ocr_clean'].tolist()
print(f'\nOCR non-empty rows for LDA: {len(corpus)}')

topics = []
if len(corpus) >= 4:
    vec = CountVectorizer(max_df=0.9, min_df=1, stop_words='english')
    X = vec.fit_transform(corpus)
    n_topics = min(3, len(corpus))
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, learning_method='batch').fit(X)
    vocab = np.array(vec.get_feature_names_out())
    for k, comp in enumerate(lda.components_):
        top = list(vocab[np.argsort(comp)[::-1][:10]])
        topics.append((k, top))
        print(f'  Topic {k}: {" | ".join(top)}')

# ---- Correlations low-level features ↔ narrative sentiment ----
feats = ['brightness','contrast','saturation','sharpness','warm_cool_bias','aspect_ratio']
corr_df = df[feats + ['nf_compound']].dropna()
print(f'\nRows with OCR-scored sentiment for correlation: {len(corr_df)}')
corr = None
if len(corr_df) >= 5:
    corr = corr_df.corr(method='spearman')['nf_compound'].drop('nf_compound').sort_values()
    print('Spearman ρ vs nf_compound:'); print(corr)
    plt.figure(figsize=(6,3))
    corr.plot(kind='barh', color=['#c0392b' if v<0 else '#2e86de' for v in corr.values])
    plt.axvline(0, color='k', lw=0.5)
    plt.title(f'Feature ↔ narrative-framing sentiment (Spearman, n={len(corr_df)})')
    plt.tight_layout()
    plt.savefig(OUT / 'fig_feature_sentiment_correlation.png', dpi=150)
    plt.close()

# ---- Save ----
df.to_csv(CSV, index=False)
print(f'\nRe-saved {CSV}')

# JSONL for RAG
jsonl = ROOT / 'data' / 'image_rag_documents.jsonl'
with open(jsonl, 'w', encoding='utf-8') as f:
    for _, r in df.iterrows():
        doc = {
            'doc_id'    : r['image_id'],
            'modality'  : 'image',
            'file_path' : r['file_path'],
            'text_for_index': f"CAPTION: {r.get('blip_caption','') or ''}\nOCR: {r.get('ocr_text','') or ''}",
            'metadata'  : {k: (None if (isinstance(r[k], float) and pd.isna(r[k])) else r[k])
                            for k in ['brightness','contrast','saturation','sharpness','warm_cool_bias',
                                      'palette_family','nf_label','nf_compound','oem_shown','image_type',
                                      'lifecycle_stage','is_ev_bus','source_url']}
        }
        f.write(json.dumps(doc, ensure_ascii=False, default=str) + '\n')
print('Wrote', jsonl)

# ---- Word frequencies for interpretation ----
tokens = ' '.join(df['ocr_clean']).split()
top_tokens = Counter(tokens).most_common(25)
print('\nTop OCR tokens across corpus:')
for w, c in top_tokens:
    print(f'  {w:20s} {c}')

# ---- Sentiment mix ----
mix = df['nf_label'].value_counts().to_dict()
print('\nNarrative-framing sentiment mix:', mix)

# ---- Bar chart of sentiment mix ----
plt.figure(figsize=(5, 2.6))
labels_order = ['positive','neutral','negative','no_text']
counts = [mix.get(l, 0) for l in labels_order]
colors = ['#27ae60','#95a5a6','#c0392b','#bdc3c7']
plt.bar(labels_order, counts, color=colors)
plt.title('Narrative-framing sentiment mix (VADER on OCR)')
plt.ylabel('Image count')
plt.tight_layout()
plt.savefig(OUT / 'fig_narrative_sentiment_mix.png', dpi=150)
plt.close()

# ---- Write findings MD ----
findings = REPORTS / 'strategic_findings_from_ocr.md'
with open(findings, 'w') as f:
    f.write('# Phase 2 · Task 2.1 — OCR-Backed Strategic Findings (Addendum)\n\n')
    f.write(f'**Run summary:** {len(df)} images, OCR text extracted on {(df["ocr_char_len"]>0).sum()} images '
            f'({int(100*(df["ocr_char_len"]>0).mean())}% coverage), median chars/image = {int(df["ocr_char_len"].median())}.\n\n')
    f.write('## Narrative-framing sentiment (VADER on OCR text — not consumer sentiment)\n\n')
    f.write('| Label | Count | % |\n|---|---:|---:|\n')
    total = sum(counts)
    for l, c in zip(labels_order, counts):
        pct = round(100*c/total, 1) if total else 0
        f.write(f'| {l} | {c} | {pct}% |\n')
    f.write('\n')

    f.write('## LDA topics on OCR corpus\n\n')
    for k, top in topics:
        f.write(f'- **Topic {k}:** {", ".join(top)}\n')
    f.write('\n')

    f.write('## Top OCR tokens across the corpus\n\n')
    f.write('| Token | Freq |\n|---|---:|\n')
    for w, c in top_tokens:
        f.write(f'| {w} | {c} |\n')
    f.write('\n')

    if corr is not None:
        f.write('## Feature ↔ narrative-framing sentiment (Spearman ρ)\n\n')
        f.write('| Feature | ρ |\n|---|---:|\n')
        for k, v in corr.items():
            f.write(f'| {k} | {v:+.3f} |\n')
        f.write(f'\n_n = {len(corr_df)}_. Exploratory only.\n')

print('Wrote', findings)
