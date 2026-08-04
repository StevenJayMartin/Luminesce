📘 RAG Server — README.md
Overview
This directory contains the RAG (Retrieval-Augmented Generation) microservice for Luminesce.
It runs independently from the main Web UI server and provides:

document ingestion

embeddings

FAISS vector search

retrieval

augmented prompt generation

Luminesce calls this service over HTTP:

Code
POST http://<rag-server-ip>:8001/rag
If the RAG server is offline, Luminesce automatically falls back to normal chat behavior.

Requirements
Install the following Python packages:

bash
pip install fastapi uvicorn faiss-cpu numpy requests ollama
Optional (recommended)
If you want to ingest PDFs or HTML:

bash
pip install beautifulsoup4 pypdf
Directory Structure
Code
lumin/rag_server/
  ├── __init__.py
  ├── server.py
  ├── embeddings.py
  ├── vector_store.py
  ├── ingest.py
  └── retrieval.py
Running the RAG Server
From the project root:

bash
uvicorn lumin.rag_server.server:app --host 0.0.0.0 --port 8001
This starts the RAG microservice on:

Code
http://<your-ip>:8001/rag
Luminesce will automatically call this endpoint if reachable.

Testing the RAG Endpoint
Send a test query:

bash
curl -X POST http://localhost:8001/rag \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "session": "abc"}'
Expected response:

json
{
  "augmented_prompt": "Use the following context to answer the question..."
}
Ingesting Documents
You can ingest documents manually using Python:

python
from lumin.rag_server.ingest import ingest_text

ingest_text("This is a test document about GPUs.")
Or create a script:

bash
python -c "from lumin.rag_server.ingest import ingest_text; ingest_text(open('notes.txt').read())"
Systemd Service (Optional)
Create a systemd unit file:

/etc/systemd/system/lumin-rag.service
Code
[Unit]
Description=Luminesce RAG Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/Luminesce
ExecStart=/usr/bin/python3 -m uvicorn lumin.rag_server.server:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
Replace:

YOUR_USERNAME

/path/to/Luminesce

Enable + Start the Service
bash
sudo systemctl daemon-reload
sudo systemctl enable lumin-rag.service
sudo systemctl start lumin-rag.service
Check status:

bash
sudo systemctl status lumin-rag.service
Stop:

bash
sudo systemctl stop lumin-rag.service
Restart:

bash
sudo systemctl restart lumin-rag.service
Verify RAG is Running
bash
curl http://localhost:8001/rag -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "hello", "session": "test"}'
If you see JSON output, the RAG server is healthy.

Integration With Luminesce
Your main WebSocket handler calls:

python
augmented_prompt = call_rag_server_safe(text, session_id)
If the RAG server is online:

Luminesce uses augmented prompts

Answers become grounded in your ingested documents

If the RAG server is offline:

Luminesce falls back to normal transcript-based chat

No errors, no downtime