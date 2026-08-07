# lumin/mcp/jsonrpc.py

class JsonRpcClient:
    """
    JSON-RPC transport layer.
    Handles sending/receiving messages, framing, and correlation.
    """

    def __init__(self, reader=None, writer=None):
        self.reader = reader
        self.writer = writer
        self._id_counter = 0

    def next_id(self):
        self._id_counter += 1
        return self._id_counter

    async def send(self, method, params=None):
        """
        Send a JSON-RPC request.
        """
        request_id = self.next_id()
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        # TODO: serialize + write to transport
        return request_id

    async def receive(self):
        """
        Receive a JSON-RPC message.
        """
        # TODO: read + parse JSON
        return None

