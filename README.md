# CMI AI Document Reader 📄🤖

An end-to-end intelligent document processing system using FastAPI, Streamlit, and OpenAI (RAG).

##Features
- Deterministic Extraction: Regex-based parsing for structured DOCX term sheets.
- Cognitive Extraction (RAG: Retrieval Augmented Generation using ChromaDB for verbose PDFs.
- NER Engine: spaCy-powered entity recognition for financial chat logs.
- User Interface: Built with Streamlit for easy document uploads and visualization.

##Architecture (GAD)
The system uses a tri-layer strategy to triage documents based on complexity, ensuring high accuracy for both structured tables and unstructured legal text.

##How to Run
1. Clone the repo: `git clone https://github.com/haw07/AI_Doc_System.git`
2. Setup .env: Create a `.env` file and add `OPENAI_API_KEY=your_key_here`.
3. Install deps: `pip install -r requirements.txt`
4. Run Backend: `uvicorn app.main:app --reload`
5. Run UI: `streamlit run app/ui.py`