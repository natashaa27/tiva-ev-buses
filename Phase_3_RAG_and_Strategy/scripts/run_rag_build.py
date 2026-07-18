"""Phase 3 · Task 3.1 — Multimodal RAG index builder.

Uses CLIP-ViT-B/32 as the shared cross-modal embedding space, so text queries
and image-derived documents live in the same vector space. Ready to ingest:
  - Image documents (JSONL from run_ocr_step.py + run_blip_step.py)  <-- present
  - Text corpus rows from ev_bus_text_analysis_final.csv             <-- stub loader
  - Video transcripts + thumbnails                                    <-- stub loader

Outputs:
  01_data/processed/rag_index.npz       — matrix of L2-normalized doc vectors
  01_data/processed/rag_meta.jsonl      — one metadata row per index entry
"""
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

ROOT = Path(__file__).resolve().parent
PROC = ROOT / '01_data' / 'processed'
IMG_JSONL   = PROC / 'image_rag_documents.jsonl'
TEXT_CSV    = PROC / 'ev_bus_text_analysis_final.csv'   # ships from Drive
VIDEO_JSONL = PROC / 'video_rag_documents.jsonl'         # from Task 2.2

INDEX_NPZ = PROC / 'rag_index.npz'
META_JSONL = PROC / 'rag_meta.jsonl'

MODEL_ID = 'openai/clip-vit-base-patch32'
device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
print(f'device: {device}')

print(f'Loading CLIP: {MODEL_ID}')
model     = CLIPModel.from_pretrained(MODEL_ID).to(device).eval()
processor = CLIPProcessor.from_pretrained(MODEL_ID)

def _to_tensor(out):
    # transformers 5.x returns BaseModelOutputWithPooling; older returned a tensor.
    return out.pooler_output if hasattr(out, 'pooler_output') else out

def embed_texts(texts, batch=16):
    """CLIP text encoder → L2-normalized 512-d vectors."""
    outs = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i+batch]
        inp = processor(text=chunk, return_tensors='pt', padding=True, truncation=True, max_length=77).to(device)
        with torch.no_grad():
            v = _to_tensor(model.get_text_features(**inp))
        v = v / v.norm(dim=-1, keepdim=True)
        outs.append(v.cpu().numpy())
    return np.vstack(outs)

def embed_images(paths, batch=8):
    outs = []
    for i in range(0, len(paths), batch):
        pil_imgs = [Image.open(ROOT / p).convert('RGB') for p in paths[i:i+batch]]
        inp = processor(images=pil_imgs, return_tensors='pt').to(device)
        with torch.no_grad():
            v = _to_tensor(model.get_image_features(**inp))
        v = v / v.norm(dim=-1, keepdim=True)
        outs.append(v.cpu().numpy())
    return np.vstack(outs)

# ---- 1. Image documents ----------------------------------------------------
image_docs = []
if IMG_JSONL.exists():
    with open(IMG_JSONL) as f:
        for line in f:
            image_docs.append(json.loads(line))
    print(f'Loaded {len(image_docs)} image documents from {IMG_JSONL.name}')
else:
    print(f'WARN: {IMG_JSONL} missing — image documents will not be indexed.')

# ---- 2. Text corpus (Phase 1 output) ---------------------------------------
text_docs = []
if TEXT_CSV.exists():
    tdf = pd.read_csv(TEXT_CSV)
    print(f'Loaded {len(tdf)} text-corpus rows from {TEXT_CSV.name}')
    # Column names depend on the Phase 1 pipeline. Fall back gracefully.
    text_col = next((c for c in ['clean_text','processed_text','comment_clean','text_final','content_clean','text'] if c in tdf.columns), None)
    id_col   = next((c for c in ['comment_id','id','post_id','row_id'] if c in tdf.columns), None)
    if text_col:
        for i, r in tdf.iterrows():
            text_docs.append({
                'doc_id'   : str(r[id_col]) if id_col else f'text_{i}',
                'modality' : 'text',
                'file_path': '',
                'text_for_index': str(r[text_col])[:1500],
                'metadata' : {k: (None if (isinstance(r[k], float) and pd.isna(r[k])) else r[k]) for k in tdf.columns if k != text_col},
            })
    else:
        print(f'WARN: no text column found in {TEXT_CSV.name}. Skipping text indexing.')
else:
    print(f'INFO: {TEXT_CSV.name} not present locally — text pipeline output will be indexed on next run when Drive is synced.')

# ---- 3. Video documents ----------------------------------------------------
video_docs = []
if VIDEO_JSONL.exists():
    with open(VIDEO_JSONL) as f:
        for line in f:
            video_docs.append(json.loads(line))
    print(f'Loaded {len(video_docs)} video documents from {VIDEO_JSONL.name}')
else:
    print(f'INFO: {VIDEO_JSONL.name} not present — video pipeline (Task 2.2) not run yet. Skipping.')

# ---- 4. Compute embeddings -------------------------------------------------
all_vecs = []
all_meta = []

if image_docs:
    print(f'Embedding {len(image_docs)} image docs (text + image → averaged)...')
    txts = [d['text_for_index'] or ' ' for d in image_docs]
    txt_vecs = embed_texts(txts)
    img_vecs = embed_images([d['file_path'] for d in image_docs])
    # Fuse text + image by averaging then re-normalising — a common lightweight
    # multimodal fusion. Keeps the index single-vector-per-doc.
    fused = (txt_vecs + img_vecs) / 2
    fused = fused / np.linalg.norm(fused, axis=1, keepdims=True)
    for d, v in zip(image_docs, fused):
        all_vecs.append(v)
        all_meta.append(d)

if text_docs:
    print(f'Embedding {len(text_docs)} text docs...')
    tv = embed_texts([d['text_for_index'] for d in text_docs])
    for d, v in zip(text_docs, tv):
        all_vecs.append(v)
        all_meta.append(d)

if video_docs:
    print(f'Embedding {len(video_docs)} video docs...')
    vv = embed_texts([d['text_for_index'] for d in video_docs])
    for d, v in zip(video_docs, vv):
        all_vecs.append(v)
        all_meta.append(d)

if not all_vecs:
    raise SystemExit('No documents to index. Ensure image_rag_documents.jsonl exists.')

mat = np.vstack(all_vecs).astype('float32')
np.savez_compressed(INDEX_NPZ, vectors=mat)
with open(META_JSONL, 'w') as f:
    for m in all_meta:
        f.write(json.dumps(m, ensure_ascii=False, default=str) + '\n')

# ---- 5. Report -------------------------------------------------------------
counts = {}
for m in all_meta:
    counts[m['modality']] = counts.get(m['modality'], 0) + 1
print(f'\nRAG index built: {mat.shape[0]} vectors × {mat.shape[1]}-d')
for mod, c in counts.items():
    print(f'  {mod:8s}  {c}')
print(f'Wrote {INDEX_NPZ}')
print(f'Wrote {META_JSONL}')
