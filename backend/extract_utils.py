import os
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import docx
from transformers import pipeline

ner_pipeline = pipeline("ner", grouped_entities=True, model="dslim/bert-base-NER")

def extract_info_from_file(file_path, filename):
    ext = os.path.splitext(filename)[1].lower()

    if ext in ['.png', '.jpg', '.jpeg']:
        text = pytesseract.image_to_string(Image.open(file_path))
        return extract_named_entities(text)

    elif ext in ['.xlsx', '.xls', '.csv']:
        return extract_from_excel(file_path)

    elif ext == '.pdf':
        return extract_from_pdf(file_path)

    elif ext == '.docx':
        return extract_from_docx(file_path)

    return []

def extract_named_entities(text):
    entities = ner_pipeline(text)
    result = {"name": None, "company": None}

    for ent in entities:
        label = ent["entity_group"]
        if label == "PER" and not result["name"]:
            result["name"] = ent["word"]
        elif label == "ORG" and not result["company"]:
            result["company"] = ent["word"]

    return [result]

def extract_from_excel(path):
    df = pd.read_excel(path) if path.endswith('.xlsx') else pd.read_csv(path)
    df = df.dropna(how='all')
    df.columns = [col.lower().strip() for col in df.columns]
    result = []

    for _, row in df.iterrows():
        name = row.get('name') or row.get('full name')
        company = row.get('company') or row.get('organization')
        if name or company:
            result.append({
                "name": str(name).strip() if name else None,
                "company": str(company).strip() if company else None
            })
    return result

def extract_from_pdf(path):
    doc = fitz.open(path)
    text = "\n".join([page.get_text() for page in doc])
    return extract_named_entities(text)

def extract_from_docx(path):
    doc = docx.Document(path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return extract_named_entities(text)