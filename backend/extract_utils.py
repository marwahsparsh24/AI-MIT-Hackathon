import os

# Import libraries as needed
import pytesseract
from PIL import Image
import pandas as pd
import fitz  # PyMuPDF
import docx

def extract_from_file(file_path, filename):
    extension = os.path.splitext(filename)[1].lower()

    if extension in ['.png', '.jpg', '.jpeg']:
        return extract_from_image(file_path, filename)

    elif extension == '.pdf':
        return extract_from_pdf(file_path, filename)

    elif extension in ['.xlsx', '.xls', '.csv']:
        return extract_from_excel(file_path, filename)

    elif extension == '.docx':
        return extract_from_docx(file_path, filename)

    return {}

def extract_from_image(path, filename):
    try:
        text = pytesseract.image_to_string(Image.open(path))
        return {"source_file": filename, "misc_info": text}
    except Exception as e:
        return {"source_file": filename, "misc_info": str(e)}

def extract_from_pdf(path, filename):
    try:
        doc = fitz.open(path)
        text = "\n".join([page.get_text() for page in doc])
        return {"source_file": filename, "misc_info": text}
    except Exception as e:
        return {"source_file": filename, "misc_info": str(e)}

def extract_from_excel(path, filename):
    try:
        df = pd.read_excel(path) if path.endswith('.xlsx') else pd.read_csv(path)
        text = df.astype(str).values.flatten().tolist()
        return {"source_file": filename, "misc_info": " | ".join(text)}
    except Exception as e:
        return {"source_file": filename, "misc_info": str(e)}

def extract_from_docx(path, filename):
    try:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return {"source_file": filename, "misc_info": text}
    except Exception as e:
        return {"source_file": filename, "misc_info": str(e)}