"""BLIP captioning step. Uses the torch conda env.
Reads the CSV from run_ocr_step.py, generates blip_caption for each image,
writes back to CSV, updates the RAG JSONL, and appends a caption summary
to the strategic output.
"""
import json
from pathlib import Path
import pandas as pd
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

ROOT = Path(__file__).resolve().parent.parent
CSV  = ROOT / 'data' / 'ev_bus_image_analysis.csv'
JSONL = ROOT / 'data' / 'image_rag_documents.jsonl'
OUT  = ROOT / 'outputs' / 'reports'

df = pd.read_csv(CSV)
print(f'Loaded {len(df)} rows.')

print('Loading BLIP (first run downloads ~1 GB)...')
proc  = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
model.eval()
print(f'BLIP ready on device: {device}')

captions = []
for i, r in df.iterrows():
    p = ROOT / r['file_path']
    with Image.open(p) as im:
        im_rgb = im.convert('RGB')
        inputs = proc(im_rgb, return_tensors='pt').to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=40)
        cap = proc.decode(out[0], skip_special_tokens=True)
    captions.append(cap)
    print(f'  [{i+1:>2}/{len(df)}] {r["image_id"][:8]}  |  {cap}')

df['blip_caption'] = captions
df.to_csv(CSV, index=False)
print(f'\nWrote captions back to {CSV}')

# Refresh RAG JSONL with real captions this time
with open(JSONL, 'w', encoding='utf-8') as f:
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
print(f'Refreshed {JSONL}')

# Write a small addendum with the captions
addendum = OUT / 'blip_captions.md'
with open(addendum, 'w') as f:
    f.write('# BLIP visual captions (Salesforce/blip-image-captioning-base)\n\n')
    f.write('| Image ID | Caption |\n|---|---|\n')
    for _, r in df.iterrows():
        f.write(f'| {r["image_id"][:8]} | {r["blip_caption"]} |\n')
print(f'Wrote {addendum}')
