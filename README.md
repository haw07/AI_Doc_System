# CMI AI Document Reader 📄🤖
An end-to-end intelligent financial document processing system built with FastAPI, Streamlit, and hybrid extraction pipelines (NER, Rules, and LLM-based reasoning).


## Features
- Deterministic Extraction  
  Regex + rule-based parsing for structured DOCX financial term sheets.

- LLM-Based Extraction (PDF Intelligence Layer)  
  Uses OpenAI models with structured prompting for unstructured PDF documents, ensuring consistent JSON output.

- NER Engine (spaCy-based)  
  Domain-trained Named Entity Recognition for extracting financial entities from chat and free-text inputs.

- User Interface  
  Built with Streamlit for document upload, processing, and structured result visualization.


## Architecture (GAD)
The system follows a tri-layer adaptive extraction strategy:
- DOCX → Rule-Based Extraction (with lightweight pattern intelligence)
- PDF → LLM-Based Structured Extraction
- Chat/Text → spaCy NER + Rule-based EntityRuler + Post-processing validation

A routing layer dynamically selects the appropriate pipeline based on document type, ensuring:
- High accuracy for structured data
- Robustness for unstructured financial text
- Consistent output schema across all inputs


## How It Works
1. A document is uploaded via API or UI  
2. The system detects its type (DOCX / PDF / Chat)  
3. The router selects the appropriate extraction pipeline  
4. Entities are extracted using:
   - Rules (DOCX)
   - LLM (PDF)
   - NER + rules (Chat/Text)
5. Output is normalized into a unified JSON schema  
6. Structured data is returned to the user

##How to Run
1. Clone the repo: `git clone https://github.com/haw07/AI_Doc_System.git`
2. Setup .env: Create a `.env` file and add `OPENAI_API_KEY=your_key_here`.
3. Install deps: `pip install -r requirements.txt`
4. Run Backend: `uvicorn app.main:app --reload`
5. Run UI: `streamlit run app/ui.py`