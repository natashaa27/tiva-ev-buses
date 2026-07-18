"""Phase 3 · Task 3.2 — Executive query testing on the multimodal RAG.

Retrieval: CLIP-ViT-B/32 text encoder → cosine similarity over pre-built index.
Synthesis: gpt-4o-mini (OpenAI) grounded strictly in retrieved evidence.
System-prompt discipline forbids fabrication and mandates the project's
Finding → Metric → Interpretation → Implication → Action structure (rule #15).

Outputs:
  04_outputs/rag/final/executive_queries.md     — human-readable brief
  04_outputs/rag/final/executive_queries.json   — raw retrievals + answers
"""
import json, re, os
from pathlib import Path
import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
PROC = ROOT / '01_data' / 'processed'
OUT  = ROOT / '04_outputs' / 'rag' / 'final'
OUT.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / '.env')
OAI_KEY = os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API_KEY')
if not OAI_KEY:
    raise SystemExit('OPENAI_KEY missing in .env')
oai = OpenAI(api_key=OAI_KEY)
LLM = 'gpt-4o-mini'

INDEX = np.load(PROC / 'rag_index.npz')['vectors'].astype('float32')
META = [json.loads(l) for l in open(PROC / 'rag_meta.jsonl')]
mod_counts = {}
for m in META: mod_counts[m['modality']] = mod_counts.get(m['modality'], 0) + 1
print(f'RAG index: {INDEX.shape[0]} docs × {INDEX.shape[1]}-d  modalities={mod_counts}')

device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
clip_model     = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').to(device).eval()
clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

def _t(o): return o.pooler_output if hasattr(o, 'pooler_output') else o

def encode(q):
    inp = clip_processor(text=[q], return_tensors='pt', padding=True, truncation=True, max_length=77).to(device)
    with torch.no_grad():
        v = _t(clip_model.get_text_features(**inp))
    v = v / v.norm(dim=-1, keepdim=True)
    return v.cpu().numpy()[0]

def retrieve(query, k=5):
    q = encode(query)
    sims = INDEX @ q
    idx = np.argsort(-sims)[:k]
    return [(float(sims[i]), META[i]) for i in idx]

def format_evidence(hits):
    """Turn the retrieved docs into a compact evidence bundle for the LLM."""
    blocks = []
    for score, m in hits:
        tfi = m.get('text_for_index','')
        cap_match = re.search(r'CAPTION:\s*(.*?)(?:\nOCR:|$)', tfi, re.S)
        ocr_match = re.search(r'OCR:\s*(.*)$', tfi, re.S)
        caption = (cap_match.group(1).strip() if cap_match else '')
        ocr     = re.sub(r'\s+', ' ', (ocr_match.group(1).strip() if ocr_match else '')).strip()
        meta = m.get('metadata') or {}
        b = [f'DOC_ID: {m["doc_id"]}',
             f'MODALITY: {m["modality"]}',
             f'COSINE_SIM: {score:.3f}',
             f'PALETTE: {meta.get("palette_family")}',
             f'BRIGHTNESS: {meta.get("brightness")}   CONTRAST: {meta.get("contrast")}   SHARPNESS: {meta.get("sharpness")}   WARM_COOL: {meta.get("warm_cool_bias")}',
             f'NARRATIVE_FRAMING_SENTIMENT: {meta.get("nf_label")} (compound={meta.get("nf_compound")})',
             f'OEM_SHOWN: {meta.get("oem_shown")}   LIFECYCLE: {meta.get("lifecycle_stage")}',
             f'CAPTION: {caption[:220]}',
             f'OCR: {ocr[:600]}']
        blocks.append('\n'.join(b))
    return '\n\n---\n\n'.join(blocks)

SYSTEM_PROMPT = """You are an executive analyst assembling evidence-grounded strategic briefs for an MBA project on the Indian EV-bus market disruption. You are working for an established (legacy) OEM whose strategic thesis is Trust-backed GCC Growth.

Discipline rules (do not violate):
1. Cite only from the provided evidence. Do not invent statistics, dates, OEM names, or quotations.
2. If the evidence does not support a claim, say "not evidenced in the retrieved corpus".
3. Every recommendation must follow: Finding → Metric → Interpretation → Business implication → Recommended action.
4. Never treat tender wins as proof of superior bus quality. Never mix operators (NueGo, Anthony Travels) with OEMs.
5. VADER sentiment on OCR text is NARRATIVE FRAMING SENTIMENT (marketing/PR framing), NOT consumer sentiment. Label it correctly.
6. The sample is small (~21 images). Flag every quantitative claim from a small sample as EXPLORATORY.
7. Correlation is not causation.
8. Be terse. No filler, no restating the question, no closing pleasantries. Deliver evidence and decisions."""

USER_PROMPT_TEMPLATE = """EXECUTIVE QUERY: {query}

RETRIEVED EVIDENCE (top {k} multimodal RAG hits):
{evidence}

Produce a compact executive answer with this structure:
1. **Direct answer** (2–3 sentences, evidence-cited).
2. **Key evidence** (3–5 bullets, each citing DOC_ID and a specific verbatim OCR fragment or caption or metric).
3. **Interpretation** (2 sentences on what this means for the legacy OEM's Trust-backed GCC strategy).
4. **Recommended action** (1–3 numbered actions, following Finding → Metric → Interpretation → Implication → Action).
5. **Limitations of this answer** (1–2 bullets — e.g. small sample, no engagement metrics, no text-corpus evidence indexed yet if the question needed it)."""

QUERIES = [
    ('Q1', 'Why are new-age OEMs winning large Indian electric bus tenders and how are legacy OEMs positioned?'),
    ('Q2', 'What does public sentiment and framing say about Tata Motors and VECV in the EV bus market?'),
    ('Q3', 'How does the Gross Cost Contract (GCC) model and government financing shape the EV bus tender competition?'),
    ('Q4', 'What visual narratives, comparison graphics, and headlines dominate the EV bus category on social media?'),
    ('Q5', 'Which new-age operators and OEMs like Olectra, PMI Electro, Eka are gaining share of voice and why?'),
    ('Q6', 'What are the trust, reliability, uptime and post-use service gaps that need to be closed for EV buses?'),
    ('Q7', 'How should an established Indian automotive OEM respond to the EV-bus tender loss narrative over the next 3 years?'),
    ('Q8', 'What digital marketing spend, content mix and channel strategy will maximise engagement for a legacy EV bus OEM?'),
]

def answer(query, k=5):
    hits = retrieve(query, k=k)
    evidence = format_evidence(hits)
    resp = oai.chat.completions.create(
        model=LLM,
        temperature=0.2,
        messages=[
            {'role':'system','content':SYSTEM_PROMPT},
            {'role':'user','content':USER_PROMPT_TEMPLATE.format(query=query, k=k, evidence=evidence)},
        ],
    )
    return hits, resp.choices[0].message.content

md = [
    '# Phase 3 · Task 3.2 — Executive Query Testing (Multimodal RAG)\n',
    f'**Index:** {INDEX.shape[0]} documents × {INDEX.shape[1]}-d shared CLIP-ViT-B/32 space. '
    f'Modalities: {mod_counts}.\n',
    f'**Retriever:** cosine similarity over L2-normalised CLIP embeddings; top-K = 5.\n',
    f'**Synthesiser:** `{LLM}` (temperature 0.2), grounded strictly in retrieved evidence per the system prompt.\n',
    '**Discipline:** every answer flags limitations; nothing is fabricated beyond retrieved evidence.\n',
    '\n---\n',
]

results_json = {}
for qid, q in QUERIES:
    print(f'\n=== {qid} ===')
    hits, ans = answer(q, k=5)
    print(f'top1 sim={hits[0][0]:.3f} doc={hits[0][1]["doc_id"][:8]}')
    md.append(f'## {qid} — {q}\n')
    md.append(f'**Top-5 retrievals:** ' + ', '.join(f'`{m["doc_id"][:8]}`({s:.2f})' for s, m in hits) + '\n')
    md.append(ans + '\n\n---\n')
    results_json[qid] = {
        'query': q,
        'retrievals': [{'sim': s, 'doc_id': m['doc_id'], 'modality': m['modality']} for s, m in hits],
        'llm_answer': ans,
    }

(OUT / 'executive_queries.md').write_text('\n'.join(md))
(OUT / 'executive_queries.json').write_text(json.dumps(results_json, indent=2))
print(f'\nWrote {OUT/"executive_queries.md"}')
print(f'Wrote {OUT/"executive_queries.json"}')
