// ui.js

function $(id) {
    return document.getElementById(id);
}

// Chat rendering
window.renderUserMessage = function (text) {
    const chat = $("chat-window");
    if (!chat) return;

    const row = document.createElement("div");
    row.className = "flex justify-end mb-2";

    const bubble = document.createElement("div");
    bubble.className = "bubble-user";
    bubble.textContent = text;

    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
};

window.renderAssistantMessage = function (text) {
    const chat = $("chat-window");
    if (!chat) return;

    const row = document.createElement("div");
    row.className = "flex justify-start mb-2";

    const bubble = document.createElement("div");
    bubble.className = "bubble-assistant whitespace-pre-wrap";
    bubble.textContent = text;

    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
};

// Streaming: append to last assistant bubble
window.renderAssistantStream = function (token) {
    const chat = $("chat-window");
    if (!chat) return;

    let lastRow = chat.lastElementChild;
    if (!lastRow || !lastRow.className.includes("justify-start")) {
        // create new assistant row
        lastRow = document.createElement("div");
        lastRow.className = "flex justify-start mb-2";
        const bubble = document.createElement("div");
        bubble.className = "bubble-assistant whitespace-pre-wrap";
        bubble.textContent = token;
        lastRow.appendChild(bubble);
        chat.appendChild(lastRow);
    } else {
        const bubble = lastRow.firstElementChild;
        bubble.textContent += token;
    }

    chat.scrollTop = chat.scrollHeight;
};

// Reasoning panel
window.updateReasoningPanel = function (reasoning) {
    const panel = $("reasoning-panel");
    if (!panel) return;
    panel.textContent = JSON.stringify(reasoning, null, 2);
};

// Tool decision log
window.logToolDecision = function (decision) {
    const panel = $("tool-panel");
    if (!panel) return;
    const existing = panel.textContent || "";
    panel.textContent = existing + "\n" + JSON.stringify(decision, null, 2);
};

// RAG panel hook
window.updateRagPanel = function (info) {
    const panel = $("rag-panel");
    if (!panel) return;
    panel.textContent = JSON.stringify(info, null, 2);
};

// Semantic memory panel hook
window.updateSemanticPanel = function (info) {
    const panel = $("semantic-panel");
    if (!panel) return;
    panel.textContent = JSON.stringify(info, null, 2);
};

// System info panel
function loadSystemInfo() {
    fetch("/api/model-info")
        .then(r => r.json())
        .then(data => {
            const panel = $("system-panel");
            if (!panel) return;
            panel.textContent = JSON.stringify(data, null, 2);
        })
        .catch(err => console.error("System info error:", err));
}

// Models + personalities
function loadConfigAndModels() {
    fetch("/config")
        .then(r => r.json())
        .then(cfg => {
            const modelSelect = $("model-select");
            if (modelSelect && cfg.ollama && cfg.ollama.model) {
                // current model will be set after /api/models
            }
        });

    fetch("/api/models")
        .then(r => r.json())
        .then(data => {
            const modelSelect = $("model-select");
            if (!modelSelect) return;
            modelSelect.innerHTML = "";
            (data.models || []).forEach(m => {
                const opt = document.createElement("option");
                opt.value = m;
                opt.textContent = m;
                modelSelect.appendChild(opt);
            });
        });

    fetch("/api/personalities")
        .then(r => r.json())
        .then(data => {
            const sel = $("personality-select");
            if (!sel) return;
            sel.innerHTML = "";
            (data.personalities || []).forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = p.name;
                sel.appendChild(opt);
            });
            if (data.current_personality) {
                sel.value = data.current_personality;
            }
        });
}

document.addEventListener("DOMContentLoaded", () => {
    loadConfigAndModels();
    loadSystemInfo();
});