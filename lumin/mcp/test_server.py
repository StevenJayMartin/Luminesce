import sys
import json
import time

def send(response):
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

def recv():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id", 1)

    if method == "mcp_echo":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"echo": params.get("text", "")}
        }

    if method == "mcp_add":
        a = int(params.get("a", 0))
        b = int(params.get("b", 0))
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"sum": a + b}
        }

    if method == "mcp_time":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"time": time.time()}
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": f"Unknown MCP method '{method}'"
    }

def main():
    # Advertise available tools
    send({
        "jsonrpc": "2.0",
        "id": 0,
        "result": {
            "tools": {
                "mcp_echo": {"description": "Echo text back"},
                "mcp_add": {"description": "Add two numbers"},
                "mcp_time": {"description": "Return server time"}
            }
        }
    })

    while True:
        req = recv()
        if req is None:
            break
        resp = handle_request(req)
        send(resp)

if __name__ == "__main__":
    main()

