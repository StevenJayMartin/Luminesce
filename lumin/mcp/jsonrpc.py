# lumin/mcp/jsonrpc.py

import json
import asyncio

class JsonRpcClient:
    """
    Minimal async JSON‑RPC transport layer.
    Handles sending/receiving framed JSON messages over an async stream.
    """

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self._id_counter = 0

    def next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    async def send_request(self, method: str, params: dict | None = None) -> dict:
        """
        Send a JSON‑RPC request and wait for the response.
        """
        req_id = self.next_id()

        message = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }

        encoded = json.dumps(message).encode("utf-8") + b"\n"
        self.writer.write(encoded)
        await self.writer.drain()

        return await self.receive_response(req_id)

    async def receive_response(self, req_id: int) -> dict:
        """
        Read a single JSON‑RPC response matching req_id.
        """
        while True:
            raw = await self.reader.readline()
            if not raw:
                raise RuntimeError("MCP server closed the connection")

            try:
                msg = json.loads(raw.decode("utf-8"))
            except Exception:
                continue  # skip malformed lines

            if msg.get("id") == req_id:
                return msg
