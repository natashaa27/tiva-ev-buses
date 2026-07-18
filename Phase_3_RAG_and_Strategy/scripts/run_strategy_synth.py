"""Phase 3 · Strategic Output — Comprehensive 3-Year Corporate EV Strategy.

Uses the RAG's 8 executive Q&A pairs (JSON) + the image-analytics strategic
output (MD) as evidence. gpt-4o-mini synthesizes a structured 3-year strategy
that MUST cite specific DOC_IDs / findings, cannot fabricate figures, and
follows the Finding → Metric → Interpretation → Implication → Action pattern.

Output:
  05_report/3_year_corporate_ev_strategy.md
"""
import json, os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
oai = OpenAI(api_key=os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API_KEY'))
LLM = 'gpt-4o-mini'

REPORT = ROOT / '05_report'
REPORT.mkdir(parents=True, exist_ok=True)
OUT_MD = REPORT / '3_year_corporate_ev_strategy.md'

rag_json = json.loads((ROOT / '04_outputs' / 'rag' / 'final' / 'executive_queries.json').read_text())
img_md   = (ROOT / '04_outputs' / 'images' / 'final' / 'strategic_output.md').read_text()

rag_blob = '\n\n'.join(f'### {qid} — {v["query"]}\n{v["llm_answer"]}' for qid, v in rag_json.items())

SYSTEM = """You are the head of corporate strategy for an established Indian automotive OEM entering the electric-bus market. You must produce a *Comprehensive 3-Year Corporate EV Strategy* for the board.

The company's working thesis is Trust-backed GCC Growth: compete on lifetime tender economics while differentiating through fleet uptime guarantees, repair-turnaround commitments, depot-level spares, transparent battery warranties, charging + financing partnerships, and better operator + passenger accountability.

Rules of production (do not violate):
1. Cite only evidence from the provided RAG Q&A pack and Image Analytics strategic output. Anywhere you make a numeric claim, reference the RAG Q ID (e.g., "per Q1") or a specific finding tag (F1, F2, F3, F4, F5, F6, F6a, N1, N2, N3). If a section needs evidence that is not in the pack, mark it "evidence gap — requires text/video/Statista/IEA index".
2. Do not fabricate figures, dates, partner names, or investment amounts. If specific numbers are unavailable, describe the KPI direction and target range (e.g., "target 40% of digital spend on YouTube long-form", not a rupee figure).
3. Do not treat tender wins as proof of superior bus quality.
4. Do not conflate operators (NueGo, Anthony Travels) with OEMs.
5. Flag every small-sample claim as EXPLORATORY. Correlation ≠ causation.
6. Every recommendation follows: Finding → Metric → Interpretation → Business implication → Recommended action.
7. Structure the strategy explicitly by the four board-mandated pillars: (a) Market Positioning, (b) Infrastructure Expansion Partnerships, (c) Battery Supply-Chain Risk Mitigations, (d) Digital Marketing Spend Optimization.
8. Phase everything as Year 1 / Year 2 / Year 3 with clear milestones.
9. Include a Limitations & Evidence-Gap section at the end. Be honest about what the current corpus does not answer.
10. Be terse. Board-quality writing: assertions first, evidence next, actions bulleted. No filler."""

USER = f"""Draft the Comprehensive 3-Year Corporate EV Strategy.

=== EVIDENCE PACK A — Multimodal RAG executive Q&A (8 queries answered against 21 CLIP-indexed image documents) ===

{rag_blob}

=== EVIDENCE PACK B — Image analytics strategic output (findings F1–F6, F6a, N1–N3) ===

{img_md}

=== DELIVERABLE ===

Produce a Markdown document with the following sections:

1. Executive Summary (≤200 words) — the thesis and the top 5 moves.
2. Situation Analysis — anchored on: public "priced out" narrative (Q1, F1), share-of-voice tilt (F2, N1), GCC/financing framing (Q3, F6), trust deficit signals (Q6), and the 62% bus-less corpus finding (N1, N2).
3. Strategic Direction — restate Trust-backed GCC Growth with a one-line brand promise.
4. Pillar 1: Market Positioning (Y1 / Y2 / Y3) — target segments, competitive stance vs new-age players (PMI Electro, Eka, Olectra), reference offer, pricing posture.
5. Pillar 2: Infrastructure Expansion Partnerships (Y1 / Y2 / Y3) — depot network, charging ecosystem, financing partners, State Transport Undertaking (STU) relationships. Mark evidence gaps.
6. Pillar 3: Battery Supply-Chain Risk Mitigations (Y1 / Y2 / Y3) — Chinese-component dependence risk, domestic sourcing roadmap, battery-warranty guarantees, second-life / swapping optionality. Mark evidence gaps clearly — most of this is not in the current corpus.
7. Pillar 4: Digital Marketing Spend Optimization (Y1 / Y2 / Y3) — content mix targets (F1, F2, N1, N2), channel mix (F4 — 16:9 masters, YouTube, CTV), creative quality standard (F5), brand palette rule (F3), BLIP-captionability KPI (F6a).
8. Governance & Cadence — KPIs, review cadence, ownership.
9. Risks & Sensitivities.
10. Limitations & Evidence Gaps — what the current corpus cannot substantiate; what is required in Phase 2 Task 2.2 + text pipeline text-corpus + Statista/IEA integration.

Length target: 2,000–3,000 words. Tables where useful."""

resp = oai.chat.completions.create(
    model=LLM,
    temperature=0.3,
    messages=[
        {'role':'system','content':SYSTEM},
        {'role':'user','content':USER},
    ],
)
strategy = resp.choices[0].message.content
OUT_MD.write_text(strategy)
print(f'Wrote {OUT_MD} ({len(strategy)} chars)')
