import os
from pypdf import PdfReader
import chromadb
import requests

DB_PATH = "./chroma_db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="enterprise_docs")

def process_and_store_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = ""
    
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    chunk_size = 800
    overlap = 150
    
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids
    )
    return len(chunks)

def clear_vector_db():
    try:
        chroma_client.delete_collection(name="enterprise_docs")
    except Exception:
        pass
    
    global collection
    collection = chroma_client.get_or_create_collection(name="enterprise_docs")
    return True

def query_rag_engine(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=5
    )
    
    retrieved_chunks = results['documents'][0] if results['documents'] else []
    context = "\n".join(retrieved_chunks)
    
    prompt = f"""Sei un assistente di ricerca accademico di alto livello per una tesi di laurea magistrale. 
Il tuo compito è estrarre informazioni, definizioni e citazioni dai documenti forniti e restituire una trattazione chiara, rigorosa e **sempre in lingua italiana fluente e formale**, anche se il testo di partenza è in inglese.
- Non usare formule ripetitive o prefazioni standard (es. "According to the context..."). Vai dritto al punto con tono accademico.
- Usa virgolettati («...») per i passaggi chiave o le definizioni formali.
- Se l'informazione non è presente nel contesto, rispondi chiaramente: "Le informazioni fornite nel contesto non sono sufficienti per rispondere alla domanda."

Contesto estratto:
{context}

Domanda dello studente: {question}
Risposta accademica in italiano:"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return {
            "response": response.json().get("response"),
            "sources": retrieved_chunks
        }
    else:
        return {"error": "Errore di comunicazione con Ollama locale."}