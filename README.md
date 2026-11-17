# Academic RAG Assistant

Prototipo sperimentale di assistente RAG (Retrieval-Augmented Generation) locale, sviluppato per supportare la ricerca di citazioni, definizioni e dati all'interno di paper e documenti PDF.
## 🚀 Stack Tecnologico
* **Backend**: FastAPI (`main.py`)
* **Motore RAG**: ChromaDB, `pypdf`, Ollama (`llama3` in locale su GPU)
* **Frontend**: Interfaccia web con Tailwind CSS (`static/index.html`)

## ⚙️ Funzionalità
* **Upload e reset automatico**: L'evento `onchange` gestisce l'upload del PDF e il reset pulito del database vettoriale in sequenza.
* **Ricerca e Citazioni**: Estrazione mirata di finestre di contesto ottimizzate con citazione delle fonti.
* **Rispetto del contesto**: Prompt accademico rigoroso per evitare allucinazioni e gestire i fuori tema.
