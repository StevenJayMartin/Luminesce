#!/usr/bin/env python3
import sys
import time
import os

# Diagnostics so you KNOW the server launched
print("SERVER STARTED IN:", os.getcwd(), file=sys.stderr, flush=True)
print("SERVER FILE:", __file__, file=sys.stderr, flush=True)

def send(obj):
    """Write a single-line JSON-ish response and flush."""
    sys.stdout.write(str(obj) + "\n")
    sys.stdout.flush()

def main():
    send({"status": "ready"})

    while True:
        line = sys.stdin.readline()
        if not line:
            break  # EOF → exit

        cmd = line.strip()

        if cmd == "mcp_time":
            send({"result": time.time()})
            continue

        if cmd.startswith("mcp_echo "):
            msg = cmd[len("mcp_echo "):]
            send({"result": msg})
            continue

        if cmd.startswith("mcp_add "):
            try:
                _, a, b = cmd.split()
                send({"result": float(a) + float(b)})
            except Exception as e:
                send({"error": f"bad arguments: {e}"})
            continue

        send({"error": f"unknown command '{cmd}'"})

if __name__ == "__main__":
    main()
