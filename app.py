from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import numpy as np
import streamlit as st
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent
RAG_DIR = ROOT / "Phase_3_RAG_and_Strategy"
META_PATH = RAG_DIR / "data" / "rag_meta.jsonl"
MODEL = "gpt-4o-mini"

st.set_page_config(
    page_title="TIVA | EV-Bus Strategy Intelligence",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root { --ink:#132238; --muted:#607086; --panel:#f6f8fb; --accent:#1565c0; }
.block-container {padding-top: 1.5rem; max-width: 1250px;}
[data-testid="stSidebar"] {background: #f4f7fb;}
.hero {padding: 1.25rem 1.4rem; border: 1px solid #dfe6ef; border-radius: 18px;
       background: linear-gradient(135deg,#ffffff 0%,#eef5ff 100%); margin-bottom: 1rem;}
.hero h1 {font-size:2rem; margin:0; color:var(--ink);}
.hero p {color:var(--muted); margin:.35rem 0 0;}
.metric-card {background:white; border:1px solid #e2e8f0; border-radius:14px; padding:1rem;}
.badge {display:inline-block; padding:.18rem .55rem; border-radius:999px; font-size:.76rem;
        background:#e8f1ff; color:#174f92; margin-right:.3rem;}
.source-card {border-left:4px solid #6c8ebf; background:#f8fafc; padding:.8rem 1rem;
             border-radius:8px; margin:.55rem 0;}
.small {font-size:.82rem; color:#667085;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading the 609-document evidence base…")
def load_corpus() -> tuple[list[dict[str, Any]], TfidfVectorizer, Any]:
    docs = [json.loads(line) for line in META_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = []
    for d in docs:
        meta = d.get("metadata") or {}
        meta_text = " ".join(str(v) for v in meta.values() if v is not None)
        texts.append(f"{d.get('modality','')} {d.get('text_for_index','')} {meta_text}")
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), min_df=1, max_features=30000, sublinear_tf=True
    )
    matrix = vectorizer.fit_transform(texts)
    return docs, vectorizer, matrix


def retrieve(query: str, k: int = 8) -> list[tuple[float, dict[str, Any]]]:
    docs, vectorizer, matrix = load_corpus()
    q = vectorizer.transform([query])
    scores = (matrix @ q.T).toarray().ravel()
    order = np.argsort(-scores)

    # Keep top evidence but ensure multimodal representation where relevant.
    chosen: list[int] = []
    for idx in order:
        if scores[idx] <= 0:
            break
        chosen.append(int(idx))
        if len(chosen) >= k:
            break

    # Add best image/chart/market evidence when absent, without forcing weak zero-score hits.
    present = {docs[i].get("modality") for i in chosen}
    for modality in ("image", "chart", "market_text"):
        if modality not in present:
            candidates = [i for i in order if docs[int(i)].get("modality") == modality and scores[int(i)] > 0]
            if candidates:
                chosen.append(int(candidates[0]))

    return [(float(scores[i]), docs[i]) for i in chosen]


def clean_excerpt(text: str, limit: int = 430) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def evidence_prompt(hits: list[tuple[float, dict[str, Any]]]) -> str:
    blocks = []
    for score, d in hits:
        meta = d.get("metadata") or {}
        blocks.append(
            "\n".join(
                [
                    f"DOC_ID: {d.get('doc_id')}",
                    f"MODALITY: {d.get('modality')}",
                    f"RETRIEVAL_SCORE: {score:.3f}",
                    f"SOURCE: {meta.get('source') or meta.get('platform') or d.get('file_path') or 'project corpus'}",
                    f"METADATA: {json.dumps(meta, ensure_ascii=False, default=str)[:700]}",
                    f"EVIDENCE: {clean_excerpt(d.get('text_for_index',''), 900)}",
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def get_api_key() -> str | None:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")


def answer(question: str, hits: list[tuple[float, dict[str, Any]]]) -> str:
    key = get_api_key()
    if not key:
        return (
            "The evidence retrieval is working, but answer generation requires an OpenAI API key. "
            "Add `OPENAI_API_KEY` under Streamlit App settings → Secrets. The retrieved evidence is shown below."
        )

    system = """You are TIVA, a boardroom decision-support assistant for the Indian EV-bus market.
Answer strictly from the retrieved project evidence. Never invent numbers or sources.
Distinguish consumer sentiment from OCR/news narrative sentiment. Never treat a tender win as proof of bus quality.
Never conflate operators (for example NueGo or Anthony Travels) with OEMs.
Flag small samples and correlations as exploratory. If evidence is missing, state that clearly.
Use this structure: Direct answer; Evidence; Strategic implication; Recommended action; Confidence and limitation.
Cite evidence inline using [DOC_ID]. Keep the response concise, practical and board-ready."""

    user = f"QUESTION: {question}\n\nRETRIEVED PROJECT EVIDENCE:\n{evidence_prompt(hits)}"
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return response.choices[0].message.content


SUGGESTED = {
    "Executive summary": "Give me the executive summary of the EV-bus market disruption and the recommended response for a legacy OEM.",
    "Why did legacy OEMs lose?": "Why did legacy OEMs lose the PM E-DRIVE tender, and does that mean their buses are inferior?",
    "Customer pain points": "What are the biggest customer pain points before adoption and after actual use?",
    "Legacy vs new-age": "Compare legacy and new-age EV-bus OEMs across tender strength, trust, branding and operations.",
    "Marketing strategy": "What content and channel strategy should a legacy EV-bus OEM follow?",
    "Three-year roadmap": "Recommend a practical three-year EV-bus strategy for a legacy OEM.",
}

with st.sidebar:
    st.markdown("## TIVA AI")
    st.caption("EV-Bus Strategy Intelligence")
    st.markdown("### Business questions")
    selected = st.radio("Choose a prompt", list(SUGGESTED), label_visibility="collapsed")
    if st.button("Load selected question", use_container_width=True):
        st.session_state["question"] = SUGGESTED[selected]
    st.divider()
    st.markdown("**Evidence base**")
    st.caption("609 indexed documents across consumer text, image captions/OCR, charts and market evidence.")
    st.markdown("<span class='badge'>Evidence-grounded</span><span class='badge'>Exploratory flags</span>", unsafe_allow_html=True)
    st.divider()
    st.caption("Academic prototype · Group 8")

st.markdown(
    """
<div class="hero">
  <h1>🚌 TIVA — EV-Bus Strategy Intelligence</h1>
  <p>Ask board-level questions about adoption, tenders, customer trust, branding, infrastructure and marketing.</p>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
for col, value, label in [
    (c1, "548", "Consumer-text records"),
    (c2, "39", "Brand-image documents"),
    (c3, "609", "RAG evidence documents"),
    (c4, "3 years", "Strategy horizon"),
]:
    with col:
        st.markdown(f"<div class='metric-card'><b style='font-size:1.35rem'>{value}</b><br><span class='small'>{label}</span></div>", unsafe_allow_html=True)

st.write("")
question = st.text_area(
    "Ask a strategic question",
    key="question",
    placeholder="For example: Why are new-age OEMs winning tenders, and how should Tata respond?",
    height=95,
)

ask_col, clear_col, _ = st.columns([1.2, 1, 5])
with ask_col:
    ask_clicked = st.button("Ask TIVA", type="primary", use_container_width=True)
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.session_state["question"] = ""
        st.rerun()

if ask_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving evidence and preparing a board-ready answer…"):
            hits = retrieve(question, k=8)
            response = answer(question, hits)
        st.session_state["last_hits"] = hits
        st.session_state["last_answer"] = response
        st.session_state["last_question"] = question

if st.session_state.get("last_answer"):
    st.markdown("## Answer")
    st.markdown(st.session_state["last_answer"])

    hits = st.session_state.get("last_hits", [])
    modalities = sorted({d.get("modality", "unknown") for _, d in hits})
    st.caption("Retrieved modalities: " + ", ".join(modalities))

    with st.expander("View retrieved evidence", expanded=False):
        for score, d in hits:
            meta = d.get("metadata") or {}
            source = meta.get("source") or meta.get("platform") or d.get("file_path") or "Project corpus"
            st.markdown(
                f"<div class='source-card'><b>{d.get('modality','').upper()} · {d.get('doc_id')}</b> "
                f"<span class='small'>score {score:.3f}</span><br>"
                f"<span class='small'>Source: {source}</span><br>"
                f"{clean_excerpt(d.get('text_for_index',''))}</div>",
                unsafe_allow_html=True,
            )

st.divider()
st.caption(
    "Answers are generated from the project's evidence base. Small subgroup, image and campaign findings are exploratory; "
    "retrieval relevance does not imply causation."
)
