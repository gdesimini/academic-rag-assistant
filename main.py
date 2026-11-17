from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from rag_engine import process_and_store_pdf, query_rag_engine, clear_vector_db

app = FastAPI(title="Academic RAG Assistant", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF.")
    
    temp_file_path = f"./{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        chunks_count = process_and_store_pdf(temp_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nell'elaborazione del PDF: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return {
        "filename": file.filename,
        "status": "Indicizzato con successo!",
        "chunks_created": chunks_count
    }

@app.delete("/reset-db/")
async def reset_database():
    try:
        clear_vector_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nello svuotamento del DB: {str(e)}")
    
    return {"status": "Database vettoriale svuotato con successo!"}

@app.post("/ask/")
async def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")
        
    result = query_rag_engine(request.question)
    return result