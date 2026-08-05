curl -X POST http://192.168.1.205:8001/rag \
     -H "Content-Type: application/json" \
     -d '{"query": "hello", "session": "test"}'
