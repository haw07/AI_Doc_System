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

# 2. Counterparty (Expanded to look for 'deal with' or 'Counterparty:')
    cp_match = re.search(r"(?:regarding|deal with|Counterparty:)\s+([\w\s]+?)\s+(?:for|to|at|\n)", text, re.IGNORECASE)
    if cp_match:
        entities["Counterparty"] = cp_match.group(1).strip()

    # 3. Notional (Detects 'million' as well as 'mio')
    notional_match = re.search(r'(\d+\s*(?:mio|bn|m|b|million|billion))', text, re.IGNORECASE)
    if notional_match:
        entities["Notional"] = notional_match.group(1).replace("million", "mio") # Standardize

    # 4. Underlying (Improved to handle "Name: ..." label)
    lines = text.split('\n')
    for line in lines:
        if entities["ISIN"] and entities["ISIN"] in line:
            # Check the line AFTER the ISIN if the current line is just the ISIN
            idx = lines.index(line)
            if len(line.strip()) < 25 and idx + 1 < len(lines):
                potential_name = lines[idx+1]
            else:
                potential_name = line.replace(entities["ISIN"], "").replace("ISIN:", "")
            
            entities["Underlying"] = potential_name.replace("Name:", "").strip()

    # 5. Precise Maturity & Bid Logic
    # Looks for: [Label] [Maturity Content] [Spread/Price]
    # This regex specifically looks for 'bps' to define the end of the Bid.
    price_pattern = r'(?:offer|bid|indication|@)\s*:?\s*(.*?)\s+((?:estr|ms|euribor).*?bps)'
    price_match = re.search(price_pattern, text, re.IGNORECASE)
    
    if price_match:
        # group(1) captures "2Y EVG" or "3Y"
        entities["Maturity"] = price_match.group(1).strip()
        # group(2) captures "estr+45bps" or "ms + 35bps"
        entities["Bid"] = price_match.group(2).strip()
    else:
        # Fallback for simpler formats if the specific spread pattern isn't found
        fallback_match = re.search(r'(?:offer|bid|@)\s+(\d+[YM])\s+(.*bps)', text, re.IGNORECASE)
        if fallback_match:
            entities["Maturity"] = fallback_match.group(1).strip()
            entities["Bid"] = fallback_match.group(2).strip()

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