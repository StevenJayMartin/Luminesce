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


function loadMemory(sessionId) {
    fetch(`/api/memory/${sessionId}`)
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById("memory-summary");
            if (!el) return;

            const mem = data.memory;
            if (!mem) {
                el.textContent = "No stored memory.";
                return;
            }

            const lines = [];

            if (mem.name) {
                lines.push(`• Name: ${mem.name}`);
            }

            for (const fact of mem.facts || []) {
                lines.push(`• ${fact}`);
            }

            if (lines.length === 0) {
                el.textContent = "No stored memory.";
            } else {
                el.textContent = lines.join("\n");
            }
        })
        .catch(() => {
            const el = document.getElementById("memory-summary");
            if (el) el.textContent = "Memory unavailable.";
        });
}

document.addEventListener("DOMContentLoaded", () => {
    loadConfigAndModels();
    loadSystemInfo();
    loadMemory();
});

window.updateMemorySummary = function (memory) {
    const el = document.getElementById("memory-summary");
    if (!el) return;

    if (!memory || memory.length === 0) {
        el.textContent = "No stored memory.";
        return;
    }

    el.textContent = memory.map(item => `• ${item}`).join("\n");
};

async function refreshSemanticStatus() {
    try {
        const res = await fetch("/api/semantic-status");
        const data = await res.json();

        const panel = document.getElementById("semantic-panel");
        if (!panel) return;

        if (!data.active) {
            panel.textContent =
                "Semantic Memory: INACTIVE\n" +
                (data.reason ? `Reason: ${data.reason}\n` : "") +
                (data.model ? `Embedding Model: ${data.model}\n` : "");
        } else {
            panel.textContent =
                "Semantic Memory: ACTIVE\n" +
                `Embedding Model: ${data.model}\n` +
                `Stored Items: ${data.stored_items}\n`;
        }
    } catch (e) {
        const panel = document.getElementById("semantic-panel");
        if (panel) {
            panel.textContent =
                "Semantic Memory: UNKNOWN\nError contacting /api/semantic-status.";
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    refreshSemanticStatus();
});

async function refreshSystemInfo() {
    try {
        const res = await fetch("/api/model-info");
        const data = await res.json();

        const panel = document.getElementById("system-panel");
        if (!panel) return;

        panel.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        const panel = document.getElementById("system-panel");
        if (panel) {
            panel.textContent = "Error fetching system info.";
        }
    }
}

