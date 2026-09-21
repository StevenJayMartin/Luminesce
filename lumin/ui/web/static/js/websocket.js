// ------------------------------------------------------------
// WebSocket Core Module — migrated from your original code
// ------------------------------------------------------------

import { showTyping, hideTyping, updateConnectionStatus, addMessage } from "./ui.js";
import { handleStreamChunk } from "./streaming.js";

export let ws = null;
let wsConnecting = false;
export let session = null;

// ------------------------------------------------------------
// Connect WebSocket
// ------------------------------------------------------------
export function connectWS() {
    if (wsConnecting) return;
    wsConnecting = true;

    updateConnectionStatus("connecting");

    ws = new WebSocket(`ws://${location.host}/ws/chat`);

    ws.onopen = () => {
        console.log("WS connected");
        wsConnecting = false;
        updateConnectionStatus("connected");
    };

    ws.onclose = () => {
        console.log("WS closed, retrying...");
        wsConnecting = false;
        updateConnectionStatus("connecting");
        setTimeout(connectWS, 1000);
    };

    ws.onerror = () => {
        console.log("WS error");
        updateConnectionStatus("offline");
    };

    let currentAssistantDiv = null;
    let accumulated = "";

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        session = data.session;

        // Reasoning panel
        if (data.reasoning) {
            const panel = document.getElementById("reasoning-panel");
            const text = document.getElementById("reasoning-text");
            panel.style.display = "block";
            text.innerText = JSON.stringify(data.reasoning, null, 2);
        }

        // Decision router debug
        if (data.decision_result) {
            console.log("Decision:", data.decision_result);
        }

        const isStream = data.stream;
        const chunk = data.reply || "";

        if (!isStream) {
            hideTyping();
            currentAssistantDiv = null;
            accumulated = "";
            return;
        }

        showTyping();
        accumulated += chunk;

        if (!currentAssistantDiv) {
            currentAssistantDiv = addMessage("assistant", accumulated);
        } else {
            addMessage("assistant", accumulated, currentAssistantDiv);
        }
    };
}

// ------------------------------------------------------------
// Send message through WebSocket
// ------------------------------------------------------------
export function sendWSMessage(text) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn("WS not connected");
        return;
    }
    ws.send(JSON.stringify({ session, text }));
}