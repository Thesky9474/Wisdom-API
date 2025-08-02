
---

## 🔹 `Wisdom-of-Ashtavakra-API` — *API + Embedding/Vector Logic Repo*

```markdown
# 🤖 Wisdom of Ashtavakra — Gemini API + Embeddings

This repository powers the spiritual intelligence behind the Wisdom of Ashtavakra chatbot and verse embedding.

## 🌌 Capabilities

- ✨ Gemini Pro API integration (GCP-based)
- 📄 PDF parser to extract Sanskrit, translation, commentary
- 🧠 Vector embedding + MongoDB Atlas vector search
- 🏷️ Auto-tagging of verses based on theme
- 💬 RAG-based chatbot logic (retrieval + generation)

## 🔍 Stack

- Python or Node (depending on your base)
- `google.generativeai` for Gemini API
- `PyMuPDF` / `pdfplumber` for structured PDF extraction
- MongoDB Atlas Vector Search
- Sentence transformers / Gemini Embeddings

## 🔧 Files

- `extract_verses.py`: PDF to structured JSON
- `embed_verses.py`: Create and store vector embeddings
- `gemini_chat.py`: Retrieval-augmented response generation
- `tags.json`: Auto-generated list of spiritual themes

## 🧠 Sample Query Flow
User Prompt → Retrieve relevant verses by vector match → Send prompt + context to Gemini → Stream poetic response
