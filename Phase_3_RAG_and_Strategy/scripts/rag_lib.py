"""Phase 3 · Multimodal RAG library (cross-modal CLIP index + retrieval + synthesis).

Shared cross-modal space: CLIP-ViT-B/32 (512-d) for both text and image/chart layouts.

Ingests four asset types into ONE index:
  1. image      — Phase 2 image_rag_documents.jsonl (39 docs): CLIP(text: caption+OCR) ⊕ CLIP(image), fused
  2. market_text— market_trends.jsonl (real IEA/BNEF/MoHI facts): CLIP text
  3. chart       — market_charts/*.png + statista/*.{png,jpg} (visual layouts): CLIP(image) ⊕ CLIP(caption), fused
  4. text        — drop-in Phase 1 text corpus CSV (auto-detected): CLIP text

Synthesis: gpt-4o-mini (OpenAI), grounded strictly in retrieved evidence.
Model/keys: HF for CLIP, OPENAI_KEY from the Phase 2 .env (or Phase 3 .env / env var).
"""
from __future__ import annotations
import json, re, os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent               # Phase_3_RAG_and_Strategy/
PHASE2 = ROOT.parent / "Phase_2_Image_Analytics"
DATA = ROOT / "data"
INDEX_NPZ = DATA / "rag_index.npz"
META_JSONL = DATA / "rag_meta.jsonl"

IMG_JSONL = PHASE2 / "data" / "image_rag_documents.jsonl"   # 39 Phase-2 image docs
MARKET_JSONL = DATA / "market_trends.jsonl"                  # IEA/BNEF/MoHI text
CHART_DIRS = [DATA / "market_charts", DATA / "statista", ROOT / "statista"]  # chart visual layouts
TEXT_DIRS = [DATA / "text", DATA, ROOT]                      # drop-in Phase-1 text corpus CSV

MODEL_ID = "openai/clip-vit-base-patch32"

# human-readable captions for the rendered charts (used as the text half of the fusion)
CHART_CAPTIONS = {
    "chart_india_ebus_stock_targets": "India electric bus stock and deployment targets: 3,000 in 2020 to 11,500 in 2024, 40,000 by 2027, Bharat Megabus 100,000",
    "chart_india_ebus_salesshare": "India electric bus sales share projection rising to 35% by 2030 and 60% by 2035 (IEA STEPS/APS)",
    "chart_china_ebus_share": "China share of global electric bus sales falling from 99% in 2017 to under 70% in 2024",
    "chart_battery_price_trend": "Lithium-ion battery pack price decline: $1183/kWh 2010 to $139 in 2023, $115 in 2024, $108 in 2025 (BloombergNEF)",
    "chart_china_vs_india_stock": "Electric bus fleet scale gap: China 680,000 vs India 11,500 in 2024",
    "chart_india_charging_2024": "India public EV charging stations reached 25,202 by December 2024 (PM E-DRIVE)",
}


# --------------------------------------------------------------------------- #
#  CLIP encoders
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _clip():
    import torch
    from transformers import CLIPModel, CLIPProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(MODEL_ID).to(dev).eval()
    proc = CLIPProcessor.from_pretrained(MODEL_ID)
    return model, proc, dev


def _embed(x):
    import torch
    return x.pooler_output if not torch.is_tensor(x) else x


def embed_texts(texts, batch=16):
    import torch
    model, proc, dev = _clip()
    outs = []
    for i in range(0, len(texts), batch):
        chunk = [t if (isinstance(t, str) and t.strip()) else " " for t in texts[i:i+batch]]
        inp = proc(text=chunk, return_tensors="pt", padding=True, truncation=True, max_length=77).to(dev)
        with torch.no_grad():
            v = _embed(model.get_text_features(**inp))
        v = v / v.norm(dim=-1, keepdim=True)
        outs.append(v.cpu().numpy())
    return np.vstack(outs)


def embed_images(paths, batch=8):
    import torch
    from PIL import Image
    model, proc, dev = _clip()
    outs = []
    for i in range(0, len(paths), batch):
        imgs = [Image.open(p).convert("RGB") for p in paths[i:i+batch]]
        inp = proc(images=imgs, return_tensors="pt").to(dev)
        with torch.no_grad():
            v = _embed(model.get_image_features(**inp))
        v = v / v.norm(dim=-1, keepdim=True)
        outs.append(v.cpu().numpy())
    return np.vstack(outs)


def _l2(m):
    return m / np.linalg.norm(m, axis=1, keepdims=True)


# --------------------------------------------------------------------------- #
#  Ingestion
# --------------------------------------------------------------------------- #
def _load_image_docs():
    if not IMG_JSONL.exists():
        return []
    docs = [json.loads(l) for l in open(IMG_JSONL)]
    for d in docs:
        d["_abs_path"] = str((PHASE2 / d["file_path"]).resolve())
    return docs


def _load_market_docs():
    if not MARKET_JSONL.exists():
        return []
    return [json.loads(l) for l in open(MARKET_JSONL)]


def _chart_caption(stem: str) -> str:
    if stem in CHART_CAPTIONS:
        return CHART_CAPTIONS[stem]
    # Statista exports: "statistic_id1395761_electric-buses-sales-volume-in-india-2023--by-leading-oem"
    s = re.sub(r"^statistic_id\d+_", "", stem)
    s = re.sub(r"\s*\(\d+\)$", "", s)               # trailing "(1)" duplicate marker
    return "Statista chart: " + s.replace("--", ", ").replace("-", " ").replace("_", " ")


def _chart_ocr(path) -> str:
    """Tesseract OCR of the chart image so axis labels / datapoints / titles are
    retrievable and quotable by the synthesiser (not just the filename caption)."""
    try:
        import pytesseract
        from PIL import Image
        with Image.open(path) as im:
            txt = pytesseract.image_to_string(im.convert("RGB"))
        return re.sub(r"\s+", " ", txt).strip()
    except Exception:
        return ""


def _load_chart_docs():
    docs, seen = [], set()
    for d in CHART_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            key = re.sub(r"\s*\(\d+\)$", "", p.stem)  # dedupe "(1)" re-downloads
            if key in seen:
                continue
            seen.add(key)
            src = "statista" if d.name == "statista" else "rendered_from_IEA_BNEF_MoHI"
            cap = _chart_caption(p.stem)
            ocr = _chart_ocr(p)
            docs.append({
                "doc_id": f"chart_{key}", "modality": "chart",
                "file_path": str(p.relative_to(ROOT)), "_abs_path": str(p.resolve()),
                # CAPTION/OCR format matches image docs so format_evidence parses both
                "text_for_index": f"CAPTION: {cap}\nOCR: {ocr[:800]}" if ocr else cap,
                "metadata": {"source": src, "asset_type": "chart_visual_layout",
                             "ocr_chars": len(ocr)},
            })
    return docs


def _load_video_docs():
    """Task 2.2 drop-in: place video_rag_documents.jsonl in data/ (one doc per
    video; text_for_index = transcript + keyframe captions + OCR; optional
    keyframe_paths list of image files). Embedding = CLIP text, fused with the
    mean CLIP image embedding of any keyframes that exist on disk."""
    p = DATA / "video_rag_documents.jsonl"
    if not p.exists():
        return []
    docs = [json.loads(l) for l in open(p)]
    for d in docs:
        d.setdefault("modality", "video")
        frames = [ROOT / f for f in d.get("keyframe_paths", [])]
        d["_frame_paths"] = [str(f) for f in frames if f.exists()]
    return docs


def _find_text_csv():
    skip = {"rag_meta", "perception_coding_template"}
    for d in TEXT_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.csv")):
            if p.stem not in skip:
                return p
    return None


def _load_text_docs():
    csv = _find_text_csv()
    if csv is None:
        return [], None
    tdf = pd.read_csv(csv)
    text_col = next((c for c in ["raw_text", "clean_text", "processed_text", "comment_clean",
                                 "text_final", "content_clean", "sentiment_text",
                                 "topic_model_text", "comment_text", "text", "body"]
                     if c in tdf.columns), None)
    id_col = next((c for c in ["comment_id", "id", "post_id", "row_id"] if c in tdf.columns), None)
    if text_col is None:
        return [], csv
    if "analysis_eligible" in tdf.columns:
        tdf = tdf[tdf["analysis_eligible"].astype(bool)]
    keep_meta = [c for c in ["platform", "sentiment_label", "dominant_topic_id",
                             "provisional_topic_label", "lifecycle_stage_final", "lifecycle_stage",
                             "human_lifecycle_stage", "speaker_role", "entity_name_canonical",
                             "oem_group", "consumer_sentiment_eligible_final"] if c in tdf.columns]
    docs = []
    for i, r in tdf.iterrows():
        t = str(r[text_col])
        if not t or t == "nan":
            continue
        docs.append({
            "doc_id": str(r[id_col]) if id_col else f"text_{i}", "modality": "text",
            "file_path": "", "text_for_index": t[:1500],
            "metadata": {k: (None if (isinstance(r[k], float) and pd.isna(r[k])) else r[k]) for k in keep_meta},
        })
    return docs, csv


def build_index(verbose=True):
    """Embed every asset type into one L2-normalised CLIP matrix + metadata."""
    vecs, meta = [], []

    img = _load_image_docs()
    if img:
        tv = embed_texts([d.get("text_for_index") or " " for d in img])
        iv = embed_images([d["_abs_path"] for d in img])
        fused = _l2((tv + iv) / 2)
        for d, v in zip(img, fused):
            vecs.append(v); meta.append({k: d[k] for k in d if k != "_abs_path"})
        if verbose: print(f"  image docs:      {len(img)} (text⊕image fused)")

    charts = _load_chart_docs()
    if charts:
        tv = embed_texts([d["text_for_index"] for d in charts])
        iv = embed_images([d["_abs_path"] for d in charts])
        fused = _l2((tv + iv) / 2)
        for d, v in zip(charts, fused):
            vecs.append(v); meta.append({k: d[k] for k in d if k != "_abs_path"})
        if verbose: print(f"  chart layouts:   {len(charts)} (image⊕caption fused)")

    mkt = _load_market_docs()
    if mkt:
        tv = embed_texts([d["text_for_index"] for d in mkt])
        for d, v in zip(mkt, tv):
            vecs.append(v); meta.append(d)
        if verbose: print(f"  market text:     {len(mkt)} (IEA/BNEF/MoHI)")

    txt, csv = _load_text_docs()
    if txt:
        tv = embed_texts([d["text_for_index"] for d in txt])
        for d, v in zip(txt, tv):
            vecs.append(v); meta.append(d)
        if verbose: print(f"  text corpus:     {len(txt)} (from {csv.name})")
    elif verbose:
        print(f"  text corpus:     0 (drop a CSV into data/text/ and rebuild)")

    vids = _load_video_docs()
    if vids:
        tv = embed_texts([d.get("text_for_index") or " " for d in vids])
        for d, v in zip(vids, tv):
            if d["_frame_paths"]:  # fuse transcript text with mean keyframe embedding
                fv = embed_images(d["_frame_paths"]).mean(axis=0)
                v = (v + fv / np.linalg.norm(fv)) / 2
                v = v / np.linalg.norm(v)
            vecs.append(v); meta.append({k: d[k] for k in d if k != "_frame_paths"})
        if verbose: print(f"  video docs:      {len(vids)} (transcript⊕keyframes fused)")
    elif verbose:
        print(f"  video docs:      0 (drop video_rag_documents.jsonl into data/ and rebuild)")

    if not vecs:
        raise SystemExit("No documents to index.")
    mat = np.vstack(vecs).astype("float32")
    np.savez_compressed(INDEX_NPZ, vectors=mat)
    with open(META_JSONL, "w", encoding="utf-8") as f:
        for m in meta:
            f.write(json.dumps(m, ensure_ascii=False, default=str) + "\n")
    if verbose:
        from collections import Counter
        print(f"Index: {mat.shape[0]} vectors x {mat.shape[1]}-d  {dict(Counter(m['modality'] for m in meta))}")
    return mat, meta


# --------------------------------------------------------------------------- #
#  Retrieval
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _load_index():
    mat = np.load(INDEX_NPZ)["vectors"].astype("float32")
    meta = [json.loads(l) for l in open(META_JSONL)]
    return mat, meta


def retrieve(query, k=5, modalities=None):
    mat, meta = _load_index()
    q = embed_texts([query])[0]
    sims = mat @ q
    order = np.argsort(-sims)
    hits = []
    for i in order:
        if modalities and meta[i]["modality"] not in modalities:
            continue
        hits.append((float(sims[i]), meta[i]))
        if len(hits) >= k:
            break
    return hits


def format_evidence(hits):
    blocks = []
    for score, m in hits:
        tfi = m.get("text_for_index", "") or ""
        cap = re.search(r"CAPTION:\s*(.*?)(?:\nOCR:|$)", tfi, re.S)
        ocr = re.search(r"OCR:\s*(.*)$", tfi, re.S)
        caption = cap.group(1).strip() if cap else (tfi if m["modality"] != "image" else "")
        ocrtxt = re.sub(r"\s+", " ", ocr.group(1).strip()) if ocr else ""
        meta = m.get("metadata") or {}
        b = [f"DOC_ID: {m['doc_id']}", f"MODALITY: {m['modality']}", f"COSINE_SIM: {score:.3f}"]
        if meta.get("source"):
            b.append(f"SOURCE: {meta['source']}")
        if m["modality"] == "image":
            b.append(f"PALETTE: {meta.get('palette_family')}  SETTING: {meta.get('hl_setting')}  "
                     f"BUS_VISIBLE: {meta.get('hl_bus_visible')}  NARRATIVE_SENTIMENT: {meta.get('nf_label')}")
        elif m["modality"] == "text":
            b.append(f"PLATFORM: {meta.get('platform')}  SPEAKER: {meta.get('speaker_role')}  "
                     f"SENTIMENT: {meta.get('sentiment_label')}  TOPIC: {meta.get('provisional_topic_label')}  "
                     f"LIFECYCLE: {meta.get('lifecycle_stage_final')}  ENTITY: {meta.get('entity_name_canonical')}")
        b.append(f"TEXT: {caption[:280]}")
        if ocrtxt:
            b.append(f"OCR: {ocrtxt[:500]}")
        blocks.append("\n".join(b))
    return "\n\n---\n\n".join(blocks)


# --------------------------------------------------------------------------- #
#  LLM synthesis (gpt-4o-mini)
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _openai():
    from dotenv import load_dotenv
    from openai import OpenAI
    for envp in (PHASE2 / ".env", ROOT / ".env"):
        if envp.exists():
            load_dotenv(envp)
    key = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_KEY missing (checked Phase_2/.env, Phase_3/.env, env vars)")
    return OpenAI(api_key=key)


LLM = "gpt-4o-mini"

SYSTEM_QUERY = """You are an executive analyst assembling evidence-grounded strategic briefs on the Indian EV-bus market for an established (legacy) OEM whose thesis is Trust-backed GCC Growth.
Rules (do not violate):
1. Cite only the provided evidence (DOC_IDs, verbatim fragments, or the SOURCE for market_text/chart docs). Do not invent statistics, dates, or names.
2. If evidence is missing, write "not evidenced in the retrieved corpus".
3. Distinguish IEA/BNEF market data (market_text/chart docs) from image-corpus narrative-framing sentiment (VADER on OCR — marketing framing, NOT consumer sentiment).
4. The image sample is small (~39) — flag image-derived quantitative claims as EXPLORATORY. Correlation is not causation. Never treat tender wins as proof of bus quality; never conflate operators with OEMs.
5. Be terse: assertions first, evidence next, actions bulleted."""

USER_QUERY_TMPL = """EXECUTIVE QUERY: {query}

RETRIEVED EVIDENCE (top {k} cross-modal RAG hits):
{evidence}

Answer with:
1. **Direct answer** (2-3 sentences, evidence-cited).
2. **Key evidence** (3-5 bullets, each citing a DOC_ID + a specific fragment/metric/source).
3. **Interpretation** (2 sentences for the legacy OEM's Trust-backed GCC strategy).
4. **Recommended action** (1-3 numbered: Finding -> Metric -> Interpretation -> Implication -> Action).
5. **Limitations** (1-2 bullets)."""


def retrieve_stratified(query, k=6, min_image=2, min_chart=1, min_market=1):
    """Cross-modal retrieval with per-modality floors: top-k overall, then
    guarantee the evidence bundle contains at least `min_image` image docs,
    `min_chart` chart-layout docs, and `min_market` market-text docs (the
    best-scoring of each), so multimodal evidence always reaches the
    synthesiser rather than being drowned out by the 548-doc text corpus."""
    hits = retrieve(query, k=k)
    have = lambda mod: sum(1 for _, m in hits if m["modality"] == mod)
    extras = []
    for mod, floor in (("image", min_image), ("chart", min_chart), ("market_text", min_market)):
        if have(mod) < floor:
            extras += retrieve(query, k=floor - have(mod), modalities=(mod,))
    seen = {m["doc_id"] for _, m in hits}
    hits += [(s, m) for s, m in extras if m["doc_id"] not in seen]
    return sorted(hits, key=lambda h: -h[0])


def answer_query(query, k=6, temperature=0.2):
    hits = retrieve_stratified(query, k=k)
    ev = format_evidence(hits)
    resp = _openai().chat.completions.create(
        model=LLM, temperature=temperature,
        messages=[{"role": "system", "content": SYSTEM_QUERY},
                  {"role": "user", "content": USER_QUERY_TMPL.format(query=query, k=k, evidence=ev)}])
    return hits, resp.choices[0].message.content


EXEC_QUERIES = [
    ("Q1", "Why are new-age OEMs winning large Indian electric bus tenders and how are legacy OEMs positioned?"),
    ("Q2", "How large is the India electric-bus market and what is its growth trajectory and government targets?"),
    ("Q3", "How does the Gross Cost Contract (GCC) model and government financing shape EV bus tender competition?"),
    ("Q4", "What are the battery supply-chain risks and how do falling battery prices and China dependence affect an Indian OEM?"),
    ("Q5", "What is the state of EV charging and depot infrastructure in India and who should an OEM partner with?"),
    ("Q6", "What trust, reliability, uptime and post-sale service gaps must be closed for EV buses?"),
    ("Q7", "How should a legacy Indian OEM respond to the EV-bus tender-loss narrative over the next 3 years?"),
    ("Q8", "What digital marketing spend, content mix and channel strategy will maximise engagement for a legacy EV bus OEM?"),
]


SYSTEM_STRATEGY = """You are head of corporate strategy for an established Indian automotive OEM entering the electric-bus market, writing a Comprehensive 3-Year Corporate EV Strategy for the board.
Thesis: Trust-backed GCC Growth — compete on lifetime tender economics while differentiating on fleet uptime guarantees, repair-turnaround, depot spares, transparent battery warranties, charging+financing partnerships.
Rules:
1. Cite evidence from the RAG Q&A pack (reference "per Q#"), the market data (IEA/BNEF/MoHI figures), and image-analytics finding tags (F1-F6, F6a, N1-N3). If a claim lacks evidence, mark "evidence gap".
2. Do not fabricate figures/dates/partners. Use the real market numbers where given; otherwise give KPI direction/target ranges.
3. Structure by the four board-mandated pillars: (a) Market Positioning, (b) Infrastructure Expansion Partnerships, (c) Battery Supply-Chain Risk Mitigations, (d) Digital Marketing Spend Optimization. Phase each Year 1 / Year 2 / Year 3.
4. Distinguish market data from small-sample image findings (flag EXPLORATORY). Never treat tender wins as bus-quality proof; never conflate operators with OEMs.
5. Board-quality: assertions first, evidence next, actions bulleted. End with Governance & Cadence, Risks, and Limitations & Evidence Gaps."""


def synthesize_strategy(rag_json, image_strategy_md, temperature=0.3, min_words=2000):
    rag_blob = "\n\n".join(f"### {qid} — {v['query']}\n{v['llm_answer']}" for qid, v in rag_json.items())
    user = f"""Draft the Comprehensive 3-Year Corporate EV Strategy.

HARD LENGTH REQUIREMENT: the document MUST be 2,000-3,000 words. Do NOT summarise or stop early.
Each of the four pillar sections must contain: a short thesis paragraph, a Y1/Y2/Y3 milestone table,
and 3+ bulleted actions per year following Finding -> Metric -> Interpretation -> Implication -> Action.

HARD CITATION REQUIREMENT: cite BOTH evidence packs explicitly. Use "per Q#" for the RAG Q&A pack AND
the image-analytics finding tags (F1, F2, F3, F4, F5, F6, F6a, N1, N2, N3) from Evidence Pack B wherever
a claim rests on the image corpus — Pillar 4 (creative/content/channel decisions) and the Situation
Analysis MUST reference the relevant F/N tags inline (e.g., "only 1 landscape asset (F4)").

=== EVIDENCE PACK A — Multimodal RAG executive Q&A (cross-modal index: image + market_text + chart + text) ===
{rag_blob}

=== EVIDENCE PACK B — Image-analytics strategic output (findings F1-F6, F6a, N1-N3) ===
{image_strategy_md[:6000]}

Sections: 1 Executive Summary (top 5 moves); 2 Situation Analysis; 3 Strategic Direction (brand promise);
4 Pillar 1 Market Positioning (Y1/Y2/Y3); 5 Pillar 2 Infrastructure Expansion Partnerships (Y1/Y2/Y3);
6 Pillar 3 Battery Supply-Chain Risk Mitigations (Y1/Y2/Y3); 7 Pillar 4 Digital Marketing Spend Optimization (Y1/Y2/Y3);
8 Governance & Cadence (KPIs, cadence, ownership); 9 Risks & Sensitivities; 10 Limitations & Evidence Gaps."""
    client = _openai()
    msgs = [{"role": "system", "content": SYSTEM_STRATEGY}, {"role": "user", "content": user}]
    import re as _re2

    def _issues(d):
        probs = []
        if len(d.split()) < min_words:
            probs.append(f"only {len(d.split())} words — below the 2,000-word floor")
        if len(_re2.findall(r"\bF[1-6]a?\b|\bN[1-3]\b", d)) < 4:
            probs.append("missing image-analytics finding-tag citations (F1-F6a, N1-N3) — the Situation "
                         "Analysis and Pillar 4 must cite them inline")
        return probs

    resp = client.chat.completions.create(model=LLM, temperature=temperature,
                                          max_completion_tokens=8000, messages=msgs)
    draft = resp.choices[0].message.content
    for _ in range(2):  # correction passes if length/citation requirements missed
        probs = _issues(draft)
        if not probs:
            break
        msgs += [{"role": "assistant", "content": draft},
                 {"role": "user", "content":
                  "This draft violates hard requirements: " + "; ".join(probs) + ". Rewrite the FULL "
                  "document at 2,000-3,000 words: keep every section, expand each pillar with the required "
                  "Y1/Y2/Y3 milestone table and 3+ actions per year, citing per Q# AND the F/N finding tags "
                  "inline where image-corpus evidence is used. Output the complete document, not a diff."}]
        resp = client.chat.completions.create(model=LLM, temperature=temperature,
                                              max_completion_tokens=8000, messages=msgs)
        draft = resp.choices[0].message.content
    return draft
