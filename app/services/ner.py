import spacy
from spacy.training import Example
import random
import os
import re

# 1. THE EXPANDED TRAINING DATA
# We ensure the UNDERLYING span (start, end) includes the date.
TRAIN_DATA = [
    # --- Counterparty (CPTY) ---
    ("regarding BANK ABC to trade", {"entities": [(10, 18, "CPTY")]}),
    ("deal with DEUTSCHE BANK for", {"entities": [(10, 23, "CPTY")]}),
    ("Counterparty: GOLDMAN SACHS", {"entities": [(14, 27, "CPTY")]}),
    
    # --- Notional (NOTIONAL) ---
    ("for 200 mio", {"entities": [(4, 11, "NOTIONAL")]}),
    ("amount 150 million", {"entities": [(7, 18, "NOTIONAL")]}),
    ("notional 500 mio EUR", {"entities": [(9, 16, "NOTIONAL")]}),

    # --- ISIN & Underlying (Dates included in the span) ---
    ("FR001400QV82 AVMAFC FLOAT 06/30/28", {"entities": [(0, 12, "ISIN"), (13, 34, "UNDERLYING")]}),
    ("XS2293847561 GREENBOND 09/15/29", {"entities": [(0, 12, "ISIN"), (13, 31, "UNDERLYING")]}),
    ("US4592001014 APPLE INC 12/01/25", {"entities": [(0, 12, "ISIN"), (13, 31, "UNDERLYING")]}),

    # --- Maturity & Bid ---
    ("2Y EVG at estr+45bps", {"entities": [(0, 6, "MATURITY"), (10, 20, "BID")]}),
    ("5Y tenor @ +20bps", {"entities": [(0, 8, "MATURITY"), (11, 17, "BID")]}),

    # --- Negative Samples (To stop / Quarterly hallucination) ---
    ("Interest: / Quarterly", {"entities": []}),
    ("payment is Quarterly", {"entities": []}),
    ("semi-annual / Quarterly", {"entities": []})
]

MODEL_PATH = "./model_finance_trained"

def train_and_save_model():
    """Builds and trains the ML model."""
    print("Training ML model with date-aware Underlying spans...")
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")
    
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    optimizer = nlp.begin_training()
    for i in range(200):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
    
    nlp.to_disk(MODEL_PATH)
    print("Training complete.")

if not os.path.exists(MODEL_PATH):
    train_and_save_model()

nlp_trained = spacy.load(MODEL_PATH)

def extract_entities_ner(text):
    """Processes text and ensures Underlying includes the date."""
    # Pre-process: Clean tabs immediately
    text = text.replace('\t', ' ')
    
    doc = nlp_trained(text)
    entities = {
        "Counterparty": None, "Notional": None, "ISIN": None,
        "Underlying": None, "Maturity": None, "Bid": None,
        "Offer": None, "PaymentFrequency": "Quaterly"
    }

    label_map = {
        "CPTY": "Counterparty", "NOTIONAL": "Notional", 
        "ISIN": "ISIN", "UNDERLYING": "Underlying",
        "MATURITY": "Maturity", "BID": "Bid"
    }

    # Extract based on ML weights
    for ent in doc.ents:
        target_key = label_map.get(ent.label_)
        if target_key:
            # Notional digit validation
            if target_key == "Notional" and not any(char.isdigit() for char in ent.text):
                continue
            entities[target_key] = ent.text

    # REINFORCEMENT: Ensure the date stays with the Underlying
    # If the ML found an ISIN, we verify the rest of that line.
    if entities["ISIN"]:
        lines = text.split('\n')
        for line in lines:
            if entities["ISIN"] in line:
                # Remove ISIN and labels to get the full name + date
                desc = line.replace(entities["ISIN"], "").strip()
                desc = re.sub(r'(?i)Name:|ISIN:|Underlying:', '', desc).strip()
                if desc:
                    entities["Underlying"] = desc

    # Final whitespace cleanup
    for key in entities:
        if isinstance(entities[key], str):
            entities[key] = re.sub(r'\s+', ' ', entities[key]).strip()

    return entities