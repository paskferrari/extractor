from fastapi import FastAPI, File, UploadFile
import fitz  # PyMuPDF
import re
import json

app = FastAPI()

def extract_data(text, label):
    pattern = re.compile(fr"{label}\s*[:\-]?\s*\n\s*([^\n]+)")
    matches = pattern.search(text)
    if matches:
        clean_text = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]', '', matches.group(1).strip())
        return clean_text
    else:
        return f"{label} non trovato"




@app.post("/extract-pdf/")
async def extract_pdf(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        return {"error": "File non è un PDF"}
    
    try:
        contents = await file.read()
        
        with fitz.open(stream=contents, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        data = {
            'Data Inizio Attività': extract_data(text, "DATA INIZIO ATTIVITÀ"),
            'Sede Legale': extract_data(text, 'SEDE LEGALE'),
            'Email Certificata': extract_data(text, 'EMAIL CERTIFICATA'),
            'Sito Web': extract_data(text, 'SITO WEB')
        }

        json_data = json.dumps(data, ensure_ascii=False)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json_data
        }
    except Exception as e:
        return {"error": str(e)}
