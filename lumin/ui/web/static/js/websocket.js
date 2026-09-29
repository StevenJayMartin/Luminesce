import { showTyping, hideTyping, updateConnectionStatus, addMessage } from "./ui.js";

export let ws = null;
let wsConnecting = false;
export let session = null;

export function connectWS() {
    if (wsConnecting) return;
    wsConnecting = true;

    updateConnectionStatus("connecting");

    ws = new WebSocket(`ws://${location.host}/ws/chat`);

    ws.onopen = () => {
        wsConnecting = false;
        updateConnectionStatus("connected");
    };

    ws.onclose = () => {
        wsConnecting = false;
        updateConnectionStatus("connecting");
        setTimeout(connectWS, 1000);
    };

    ws.onerror = () => {
        updateConnectionStatus("offline");
    };

    let currentAssistantDiv = null;

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        session = data.session;

        if (data.reasoning) {
            const panel = document.getElementById("reasoning-panel");
            const text = document.getElementById("reasoning-text");
            panel.style.display = "block";
            text.innerText = JSON.stringify(data.reasoning, null, 2);
        }

        const isStream = !!data.stream;
        const chunk = data.reply || "";

        // ---------------------------
        // NON‑STREAM (final message)
        // ---------------------------
        if (!isStream) {
            hideTyping();
            if (chunk) {
                addMessage("assistant", chunk);   // ALWAYS new bubble
            }
            currentAssistantDiv = null;           // reset for next assistant message
            return;
        }

        // ---------------------------
        // STREAMING
        // ---------------------------
        showTyping();

        // Create bubble ONCE at start of stream
        if (!currentAssistantDiv) {
            currentAssistantDiv = addMessage("assistant", "");
        }

        // ⭐ Append ONLY to msg-body
        const body = currentAssistantDiv.querySelector(".msg-body");
        body.innerHTML += chunk;
    };
}

export function sendWSMessage(text) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn("WS not connected");
        return;
    }
    ws.send(JSON.stringify({ session, text }));
}
