// ------------------------------------------------------------
// Streaming Module — migrated from your original code
// ------------------------------------------------------------

import { addMessage, showTyping, hideTyping } from "./ui.js";

let currentAssistantDiv = null;
let accumulated = "";

// Called by websocket.js when a streaming chunk arrives
export function handleStreamChunk(chunk) {
    showTyping();

    accumulated += chunk;

    if (!currentAssistantDiv) {
        currentAssistantDiv = addMessage("assistant", accumulated);
    } else {
        addMessage("assistant", accumulated, currentAssistantDiv);
    }
}

// Reset streaming state when a non-stream message arrives
export function resetStreaming() {
    hideTyping();
    currentAssistantDiv = null;
    accumulated = "";
}