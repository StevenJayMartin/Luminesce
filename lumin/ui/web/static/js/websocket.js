// websocket.js
let ws = null;
let currentSession = null;

function connectWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws/chat`);

    ws.onopen = () => {
        console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);

            // Store session + load memory immediately
            if (msg.session) {
                currentSession = msg.session;
                loadMemory(currentSession);
            }

            // Streaming tokens
            if (msg.stream === true) {
                if (msg.reply) {
                    window.renderAssistantStream(msg.reply);
                }
                return;
            }

            // Final reply
            if (msg.reply) {
                window.renderAssistantMessage(msg.reply);

                // Only reload memory if session ID is valid
                if (currentSession && currentSession !== "undefined") {
                    loadMemory(currentSession);
                }
            }

            // Reasoning panel
            if (msg.reasoning) {
                window.updateReasoningPanel(msg.reasoning);
            }

            // Tool decisions
            if (msg.decision_result) {
                window.logToolDecision(msg.decision_result);
            }

        } catch (e) {
            console.error("WS message error:", e, event.data);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket closed, reconnecting in 2s...");
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

window.wsSend = function (text) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn("WebSocket not ready");
        return;
    }
    window.renderUserMessage(text);
    ws.send(JSON.stringify({ text }));
};

document.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
});
