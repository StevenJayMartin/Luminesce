import json
import uuid
import time
import math
import requests

class LuminSemanticMemory:
    def __init__(self, file_path: str, ollama_url: str, embedding_model: str):
        self.file_path = file_path
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.mem = self._load()

    def _load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.mem, f, indent=2)

    def _cosine(self, a, b):
        return sum(x * y for x, y in zip(a, b)) / (
            math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-8
        )

    def _embed(self, text: str):
        try:
            payload = {
                "model": self.embedding_model,
                "prompt": text,
                "stream": False,
            }
            r = requests.post(f"{self.ollama_url}/api/embeddings", json=payload)
            return r.json().get("embedding")
        except Exception:
            return None

    def init_session(self, sid: str):
        self.mem.setdefault(sid, [])

    def add(self, sid: str, *, type: str, key: str | None, value: str, text: str):
        emb = self._embed(value)
        if emb is None:
            return
        item = {
            "id": str(uuid.uuid4()),
            "type": type,
            "key": key,
            "value": value,
            "text": text,
            "embedding": emb,
            "ts": int(time.time()),
        }
        self.mem[sid].append(item)
        self._save()

    def recall(self, sid: str, query: str, *, type: str | None = None,
               key: str | None = None, top_k: int = 5):
        emb_q = self._embed(query)
        if emb_q is None:
            return []
        scored = []
        for item in self.mem.get(sid, []):
            if type and item["type"] != type:
                continue
            if key and item["key"] != key:
                continue
            score = self._cosine(emb_q, item["embedding"])
            scored.append((score, item))
        scored.sort(reverse=True)
        return [it for _, it in scored[:top_k]]

    def build_context(self, sid: str) -> str:
        items = self.recall(sid, "user info", top_k=10)
        if not items:
            return ""
        lines = ["Memory:"]
        for item in items:
            t = item["type"]
            k = item["key"]
            v = item["value"]
            if t == "user_profile" and k:
                lines.append(f"- {k}: {v}")
            elif t == "preference" and k:
                lines.append(f"- prefers {k}: {v}")
            else:
                lines.append(f"- {item['text']}")
        return "\n".join(lines) + "\n\n"

