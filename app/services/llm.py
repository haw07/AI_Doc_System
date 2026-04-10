import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_pdf(file_bytes):
    # Open the PDF from memory
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_entities_llm(text):
    # Define a strict system prompt to reduce hallucinations
    system_msg = "You are a financial data extractor. Return only a JSON object."
    user_prompt = f"Extract these entities: Counterparty, Initial Valuation Date, Notional, Valuation Date, Maturity, Underlying, Coupon, Barrier, Calendar.\n\nText:\n{text}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Corrected model name
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}, # Ensures valid JSON output
        temperature=0
    )
    return response.choices[0].message.content