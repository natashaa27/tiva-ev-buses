# Indian Electric-Bus Market Multimodal AI Analysis

## Project objective

This MBA group project examines disruption in the Indian electric-bus market using text, image, video, and retrieval-augmented analysis. The working repository separates immutable source material from reproducible data transformations, analytical notebooks, generated outputs, and final communication artifacts.

The immediate analytical focus is to establish trustworthy evidence and a reproducible text-analysis pipeline before extending the work to image, video, and RAG components.

## Repository structure

```text
00_original files/          Immutable source archive; never edit in place
01_data/
  raw/                      Future normalized copies of direct raw evidence
  interim/                  Approved inputs and intermediate transformations
  processed/                Reproducible notebook-ready analytical datasets
02_notebooks/               Analytical notebooks, created in later phases
03_outputs/
  text/                     Text-analysis tables and figures
  image/                    Image-analysis outputs
  video/                    Video-analysis outputs
  rag/                      Retrieval and RAG outputs
04_report/                  Report drafts and final report assets
05_presentation/            Presentation drafts and final deck assets
audit_outputs/              Approved Phase 1 repository audit
```

`00_original files` is the actual name of the original source directory in this repository. It corresponds to the protected `00_original_files` scope referenced in project instructions.

## Authoritative files

The following are the controlling files for the next stage of work:

- `00_original files/Group Project Assignment_TIVA AI_2026.pdf` — assignment requirements.
- `00_original files/files/AcadGroup8_EV_Bus_Project_Proposal.docx` — original project objective and hypotheses.
- `01_data/interim/ev_bus_text_corpus.csv` — approved current 548-row text input, with mixed-provenance disclosure.
- `01_data/interim/ev_bus_tenders_CORRECTED.csv` — controlling tender table within this repository.
- `DATA_DICTIONARY.md` — controlled entity, lifecycle, and sentiment definitions.
- `METHODOLOGY.md` — evidence hierarchy, exclusions, limitations, and validation rules.
- `PHASE1_DECISIONS.md` — approved Phase 1 governance decisions.
- `audit_outputs/` — detailed evidence supporting the Phase 1 decisions.

Direct raw YouTube and Instagram exports remain authoritative source records in the immutable original archive until a later phase creates normalized raw copies.

## Files that must not be used as empirical evidence

- `00_original files/files/ev_bus_tenders_ORIGINAL_manus.csv` — contains unsupported city-to-OEM attribution and estimated fields; superseded by the corrected tender table.
- Saved results from `00_original files/02_sentiment_topic_analysis.ipynb` — generated from a 35-row synthetic fixture.
- Synthetic processed CSVs or interpretations derived from that fixture.
- Appended claims in `02_outputs_explained.docx` that cannot be traced to a real-data notebook run.
- `files.zip` as a separate evidence source — it duplicates expanded files.
- AI/Manus-compiled market facts, benchmark values, and opinion excerpts unless their underlying citations have been verified.

The unexecuted and executed original notebooks are retained for provenance. They are not the controlled analytical notebooks for future phases.

## Environment setup

Use Python 3.11. From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the NLTK resources expected by the planned text pipeline:

```bash
python -m nltk.downloader punkt punkt_tab stopwords wordnet omw-1.4 averaged_perceptron_tagger averaged_perceptron_tagger_eng vader_lexicon
```

Start Jupyter from the repository root so all relative paths resolve consistently:

```bash
jupyter notebook
```

No analytical notebook has yet been created in `02_notebooks`.

## Planned execution order

1. Validate interim input schemas, hashes, provenance fields, and controlled entity mappings.
2. Build a reproducible corpus-preparation process and write versioned data to `01_data/processed`.
3. Create and run the controlled text-analytics notebook; save tables and figures under `03_outputs/text`.
4. Conduct image analysis and save outputs under `03_outputs/image`.
5. Conduct video analysis and save outputs under `03_outputs/video`.
6. Build and evaluate the retrieval/RAG component under `03_outputs/rag`.
7. Integrate verified findings and limitations into `04_report`.
8. Build the final presentation in `05_presentation`.

Each stage must consume approved inputs, preserve lineage, and exclude synthetic results from empirical findings.

