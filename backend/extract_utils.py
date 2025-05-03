import os
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import docx
import re
from transformers import pipeline

# Load the NER pipeline
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
    lines = text.split('\n')
    results = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try regex-based structured extraction
        match = re.match(r'^([\w\s&]+?)\s+([A-Z][\w\s&]+)\s+[–-]\s+(.+)$', line)
        if match:
            name = match.group(1).strip()
            company = match.group(2).strip()
            designation = match.group(3).strip()

            results.append({
                "name": name,
                "company": company,
                "designation": designation
            })
        else:
            # fallback to NER
            ner_result = ner_pipeline(line)
            temp = {"name": None, "company": None}
            for ent in ner_result:
                label = ent["entity_group"]
                if label == "PER" and not temp["name"]:
                    temp["name"] = ent["word"]
                elif label == "ORG" and not temp["company"]:
                    temp["company"] = ent["word"]
            if temp["name"] or temp["company"]:
                results.append(temp)

    return results

def extract_from_excel(path):
    df = pd.read_excel(path) if path.endswith('.xlsx') else pd.read_csv(path)
    df = df.dropna(how='all')
    df.columns = [col.lower().strip() for col in df.columns]
    result = []

    for _, row in df.iterrows():
        name = row.get('name') or row.get('full name')
        company = row.get('company') or row.get('organization')
        designation = row.get('designation') or row.get('title')
        if name or company or designation:
            result.append({
                "name": str(name).strip() if name else None,
                "company": str(company).strip() if company else None,
                "designation": str(designation).strip() if designation else None
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
