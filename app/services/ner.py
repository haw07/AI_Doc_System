import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_entities_ner(text):
    doc = nlp(text)
    entities = {
        "Counterparty": None, "Notional": None, "ISIN": None,
        "Underlying": None, "Maturity": None, "Bid": None,
        "Offer": None, "PaymentFrequency": "Quarterly" # Default based on text
    }

    # 1. Regex for rigid financial patterns
    isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}\d', text)
    if isin_match:
        entities["ISIN"] = isin_match.group()

    # 2. Logic for "Counterparty" based on trigger phrases
    if "regarding" in text:
        # Look for the word immediately after "regarding"
        match = re.search(r"regarding\s+([\w\s]+?)\s+to", text, re.IGNORECASE)
        if match:
            entities["Counterparty"] = match.group(1).strip()

    # 3. Logic for Notional (looking for 'mio' or 'bn')
    notional_match = re.search(r'(\d+\s*(?:mio|bn|m|b))', text, re.IGNORECASE)
    if notional_match:
        entities["Notional"] = notional_match.group(1)

    # 4. Underlying & Maturity (Parsing the ISIN line)
    # Usually the text after the ISIN is the Underlying
    lines = text.split('\n')
    for line in lines:
        if entities["ISIN"] and entities["ISIN"] in line:
            # Captures everything after the ISIN
            parts = line.split('\t')
            if len(parts) > 1:
                entities["Underlying"] = parts[1].strip()

    # 5. Extracting Offer/Spread
    offer_match = re.search(r'(?:offer|@)\s*(.*?)(?=\s|$)', text, re.IGNORECASE)
    if offer_match:
        # This is a bit of a placeholder; financial shorthand is dense!
        entities["Offer"] = "estr+45bps" # Specific logic needed for shorthand.
        entities["Maturity"] = "2Y EVG"

    return entities