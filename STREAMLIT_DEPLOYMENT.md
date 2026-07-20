# Deploy TIVA AI on Streamlit Community Cloud

## 1. Upload the app files to GitHub
Upload these items to the **root** of the repository:

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`

Keep the existing `Phase_3_RAG_and_Strategy/data/rag_meta.jsonl` file in place.

## 2. Create the Streamlit app

1. Open Streamlit Community Cloud and sign in with GitHub.
2. Select **Create app**.
3. Repository: `natashaa27/tiva-ev-buses`
4. Branch: `main`
5. Main file path: `app.py`
6. Choose an available URL, such as `tiva-ev-bus-ai`.

## 3. Add the API key privately

In **Advanced settings → Secrets**, add:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

Never commit the key to GitHub.

## 4. Deploy

Select **Deploy**. Streamlit will create a public URL similar to:

`https://tiva-ev-bus-ai.streamlit.app`

Use that URL or its QR code in the presentation.

## Notes

- The deployed interface retrieves from the preprocessed multimodal evidence documents (text, image captions/OCR, charts and market facts).
- It uses lightweight TF-IDF retrieval for reliable free-cloud deployment and OpenAI for evidence-grounded synthesis.
- The original CLIP index and notebook remain unchanged as the academic cross-modal RAG implementation.
