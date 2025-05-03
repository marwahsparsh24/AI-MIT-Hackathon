# My CRM 

---
## Features

- Upload business card images, Excel/PDF files, or Word docs
- Manual entry for individual contact details
- Store structured data in ChromaDB
- View extracted records live
---
## Project Structure

```bash
my-crm/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── extract_utils.py
│   ├── chroma_utils.py
│   └── requirements.txt
├── src/
│   ├── components/
│   │   ├── EventForm.jsx
│   │   └── RecordList.jsx
│   ├── App.jsx
│   ├── App.css
│   ├── index.js
│   └── package.json

---

## Setup Instructions

### Backend (FastAPI + ChromaDB)

1. Navigate to the backend folder:
   ```bash
   cd backend
   pip install -r requirements.txt

2. Install Tesseract OCR
Windows: https://github.com/tesseract-ocr/tesseract/wiki
macOS: brew install tesseract
Linux: sudo apt install tesseract-ocr

3. In extract_utils.py, configure the Tesseract path:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesse

### Frontend (React)

4. Run the backend server:
uvicorn main:app --reload

5. Frontend (React)
Navigate to the frontend:
cd my-crm
npm install
npm run dev  # or npm start
App will run on http://localhost:3000

