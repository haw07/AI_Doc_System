# app/routes/document.py
from fastapi import APIRouter, UploadFile
from app.services import parser, ner, llm

router = APIRouter()

@router.post("/document/process")
async def process_document(file: UploadFile):
    content = await file.read()
    filename = file.filename.lower()
    
    if filename.endswith(".docx"):
        text = parser.parse_docx(file.file)
        entities = parser.extract_entities_rule_based(text)
    elif filename.endswith(".txt"):
        text = content.decode()
        entities = ner.extract_entities_ner(text)
    elif filename.endswith(".pdf"):
        text = llm.parse_pdf(content)
        entities = llm.extract_entities_llm(text)
    else:
        return {"error": "Unsupported file type"}
    
    return {"text_preview": text[:200], "entities": entities}