// ------------------------------------------------------------
// Additional UI Logic — migrated from bottom half
// ------------------------------------------------------------

import { connectWS, sendWSMessage } from "./websocket.js";
import { addMessage, showTyping, hideTyping } from "./ui.js";

export async function refreshModelInfo() {
    try {
        const info = await fetch("/api/model-info").then(r => r.json());
        const div = document.getElementById("model-info");

        let text = `Model: ${info.model}`;
        if (info.gpu) {
            text += ` | GPU: ${info.gpu.name} ${info.gpu.memory_used}/${info.gpu.memory_total} (${info.gpu.utilization}, ${info.gpu.temperature})`;
        }
        div.textContent = text;
    } catch (e) {
        console.error("refreshModelInfo error:", e);
    }
}

export async function loadConfig() {
    if (configLoaded) return;
    configLoaded = true;

    config = await fetch("/config").then(r => r.json());

    await loadModels();
    await loadPersonalities();
    await refreshModelInfo();
    setInterval(refreshModelInfo, 10000);

    connectWS();
}

// ------------------------------------------------------------
// Generate Mode (non-chat)
// ------------------------------------------------------------
export async function sendGenerate(text) {
    showTyping();
    const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    }).then(r => r.json());

    hideTyping();
    addMessage("assistant", resp.reply);
}

// ------------------------------------------------------------
// Export Chat
// ------------------------------------------------------------
export function exportChat() {
    if (!chatLog.length) return;
    const blob = new Blob([JSON.stringify(chatLog, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lumin-chat-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

// ------------------------------------------------------------
// Input Handlers
// ------------------------------------------------------------
export function initInputHandlers() {
    document.getElementById("export-chat").onclick = exportChat;

    document.getElementById("send").onclick = () => {
        if (!configLoaded) return;

        const text = document.getElementById("input").value.trim();
        if (!text) return;

        addMessage("user", text);
        document.getElementById("input").value = "";

        if (config.ollama.mode === "generate") {
            sendGenerate(text);
        } else {
            showTyping();
            sendWSMessage(text);
        }
    };

    document.getElementById("input").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            document.getElementById("send").click();
        }
    });

    document.getElementById("upload-btn").onclick = () => {
        document.getElementById("file-input").click();
    };

    document.getElementById("file-input").onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        addMessage("user", `📁 Uploaded: **${file.name}**`);

        const formData = new FormData();
        formData.append("file", file);

        const resp = await fetch("/api/upload", {
            method: "POST",
            body: formData
        }).then(r => r.json());

        addMessage("assistant", resp.reply);
    };
}