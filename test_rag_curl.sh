
#curl -X POST http://192.168.1.205:8001/ingest_url \
#     -H "Content-Type: application/json" \
#     -d '{"url": "https://en.wikipedia.org/wiki/FAISS"}'
curl -X POST http://192.168.1.205:8001/rag \
     -H "Content-Type: application/json" \
     -d '{"query": "hello", "session": "test"}'

