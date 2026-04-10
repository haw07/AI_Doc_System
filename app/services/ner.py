import spacy
import re

# Load the NLP model once
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

def extract_entities_ner(text):
    entities = {
        "Counterparty": None, 
        "Notional": None, 
        "ISIN": None,
        "Underlying": None, 
        "Maturity": None, 
        "Bid": None,
        "PaymentFrequency": None 
    }

    # 1. ISIN (Strict 12-char identifier)
    isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}\d', text)
    if isin_match:
        entities["ISIN"] = isin_match.group()

    # 2. Counterparty (Logic: regarding [NAME] to/at)
    cp_match = re.search(r"regarding\s+([\w\s]+?)\s+(?:to|at)", text, re.IGNORECASE)
    if cp_match:
        entities["Counterparty"] = cp_match.group(1).strip()

    # 3. Notional (Number + mio/bn/m/b)
    notional_match = re.search(r'(\d+\s*(?:mio|bn|m|b))', text, re.IGNORECASE)
    if notional_match:
        entities["Notional"] = notional_match.group(1)

    # 4. Underlying (Logic: Grab the text content after the ISIN on the same line)
    lines = text.split('\n')
    for line in lines:
        if entities["ISIN"] and entities["ISIN"] in line:
            # Remove the ISIN from the line, keep the rest (Name + Date)
            name_part = line.replace(entities["ISIN"], "").strip()
            # Clean up tabs/extra spaces to keep it on one line
            entities["Underlying"] = re.sub(r'\s+', ' ', name_part).strip()

    # 5. Maturity & Bid Logic
    # Specifically looking for the pattern: offer [MATURITY] [PRICE]
    # e.g., "offer 2Y EVG estr+45bps"
    offer_line_match = re.search(r'offer\s+(.*?)\s+(estr[+-]\d+bps)', text, re.IGNORECASE)
    if offer_line_match:
        # Group 1 is "2Y EVG"
        entities["Maturity"] = offer_line_match.group(1).strip()
        # Group 2 is "estr+45bps", mapped to Bid per your request
        entities["Bid"] = offer_line_match.group(2).strip()

    # 6. Payment Frequency (Keyword Mapping)
    # Note: Mapping to your specific spelling "Quaterly"
    frequency_map = {
        "quarterly": "Quaterly", 
        "semi-annual": "Semi-Annual",
        "annual": "Annual"
    }

    text_lower = text.lower()
    for keyword, formal_name in frequency_map.items():
        if keyword in text_lower:
            entities["PaymentFrequency"] = formal_name
            break 

    return entities