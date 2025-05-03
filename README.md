# My CRM – Event Networking Assistant 

A **personal CRM** built to help you manage contacts from networking events. Upload business cards, resumes, or attendee lists, extract names and affiliations, and send **personalized LinkedIn connection requests**. Later, query stored contact data using a chatbot interface.

---

## Features

- Upload images, PDFs, Excel, or Word files containing contact details
- Extract information like name, company, role
- Store structured data in **ChromaDB** (no-SQL vector DB)
- Manually add new contacts via form
- Auto-send **LinkedIn connection requests** with event-based personalization
- Query contacts using an **AI chatbot**

---

## Project Structure

```bash
AI-MIT-Hackathon/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── extract_utils.py
│   ├── chroma_utils.py
│   ├── linkedin_sender.py
│   ├── chatbot_utils.py
│   ├── chroma_db/
│   ├── temp_uploads/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── FileUpload.jsx, ChatBot.jsx, etc.
│   │   ├── App.jsx, App.css, index.js
│   └── package.json
└── README.md
```

# Setup Instructions

## Backend (FastAPI + ChromaDB)

1. Navigate to the backend directory:
```bash
cd backend
pip install -r requirements.txt
```

2. Install Tesseract OCR (used for image text extraction):
Windows: https://github.com/tesseract-ocr/tesseract/wiki
macOS: brew install tesseract
Linux: sudo apt install tesseract-ocr

3. Update path in extract_utils.py:
```bash
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

4. Update path in extract_utils.py:
```bash
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Frontend (React)

5. Open a new terminal, navigate to the frontend:
```bash
cd frontend
npm install
npm run dev
```
