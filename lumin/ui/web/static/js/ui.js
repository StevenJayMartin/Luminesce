
// ------------------------------------------------------------
// missing functions
// ------------------------------------------------------------

export async function loadModels() {
    try {
        const resp = await fetch("/api/models").then(r => r.json());
        models = resp.models || [];

        const picker = document.getElementById("model-picker");
        picker.innerHTML = "";

        models.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m;
            opt.textContent = m;
            picker.appendChild(opt);
        });

        if (models.length > 0) {
            picker.value = models[0];
        }
    } catch (e) {
        console.error("loadModels error:", e);
    }
}

export async function loadPersonalities() {
    try {
        const resp = await fetch("/api/personalities").then(r => r.json());
        personalities = resp.personalities || [];

        const picker = document.getElementById("personality-picker");
        picker.innerHTML = "";

        personalities.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = p.name;
            picker.appendChild(opt);
        });

        if (personalities.length > 0) {
            currentPersonality = personalities[0].id;
            picker.value = currentPersonality;
        }
    } catch (e) {
        console.error("loadPersonalities error:", e);
    }
}

// ------------------------------------------------------------
// UI MODULE — Corrected with all required exports
// ------------------------------------------------------------

export let config = null;
export let configLoaded = false;
export let models = [];
export let personalities = [];
export let currentPersonality = null;
export let chatLog = [];

// ------------------------------------------------------------
// Avatar + Typing Text
// ------------------------------------------------------------
export function getAvatar(role) {
    if (role === "user") return "🧑";
    switch (currentPersonality) {
        case "developer": return "💻";
        case "teacher": return "📘";
        case "playful": return "🎉";
        case "concise": return "⚡";
        default: return "✨";
    }
}

export function getTypingText() {
    switch (currentPersonality) {
        case "developer": return "Compiling thoughts…";
        case "teacher": return "Preparing explanation…";
        case "playful": return "Lumin is vibing…";
        case "concise": return "Thinking…";
        default: return "Lumin is thinking…";
    }
}

// ------------------------------------------------------------
// Markdown Rendering
// ------------------------------------------------------------
export function renderMarkdown(text) {
    const html = marked.parse(text);
    const container = document.createElement("div");
    container.innerHTML = html;

    container.querySelectorAll("pre code").forEach(block => {
        hljs.highlightElement(block);
        const pre = block.parentElement;

        const btn = document.createElement("button");
        btn.textContent = "Copy";
        btn.className = "copy-btn";
        btn.onclick = () => navigator.clipboard.writeText(block.innerText);

        pre.appendChild(btn);
    });

    return container.innerHTML;
}

// ------------------------------------------------------------
// Timestamp
// ------------------------------------------------------------
export function formatTimestamp(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// ------------------------------------------------------------
// Add Message Bubble
// ------------------------------------------------------------
export function addMessage(role, text, reuseDiv = null, timestamp = null) {
    const ts = timestamp || new Date();

    chatLog.push({
        role,
        content: text,
        timestamp: ts.toISOString()
    });

    let div = reuseDiv || document.createElement("div");
    div.className = `msg ${role}`;

    const header = document.createElement("div");
    header.className = "msg-header";

    const avatarSpan = document.createElement("span");
    avatarSpan.className = "msg-avatar";
    avatarSpan.textContent = getAvatar(role);

    const roleSpan = document.createElement("span");
    roleSpan.textContent = role === "user" ? "You" : "Lumin";

    const tsSpan = document.createElement("span");
    tsSpan.className = "msg-timestamp";
    tsSpan.textContent = formatTimestamp(ts);

    header.appendChild(avatarSpan);
    header.appendChild(roleSpan);
    header.appendChild(tsSpan);

    const body = document.createElement("div");
    body.className = "msg-body";
    body.innerHTML = renderMarkdown(text);

    div.innerHTML = "";
    div.appendChild(header);
    div.appendChild(body);

    if (!reuseDiv) {
        document.getElementById("chat-container").appendChild(div);
    }

    div.scrollIntoView({ behavior: "smooth" });
    return div;
}

// ------------------------------------------------------------
// Typing Indicator
// ------------------------------------------------------------
export function showTyping() {
    if (!document.getElementById("typing")) {
        const t = document.createElement("div");
        t.id = "typing";
        t.className = "msg assistant";
        t.textContent = getTypingText();
        document.getElementById("chat-container").appendChild(t);
        t.scrollIntoView({ behavior: "smooth" });
    }
}

export function hideTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
}

// ------------------------------------------------------------
// Connection Status
// ------------------------------------------------------------
export function updateConnectionStatus(status) {
    const dot = document.getElementById("connection-dot");
    const label = document.getElementById("connection-label");
    if (!dot || !label) return;

    if (status === true || status === "connected") {
        dot.style.background = "#22c55e";
        label.textContent = "Connected";
    } else if (status === "connecting") {
        dot.style.background = "#eab308";
        label.textContent = "Connecting…";
    } else {
        dot.style.background = "#ef4444";
        label.textContent = "Offline";
    }
}

// ------------------------------------------------------------
// Model Info
// ------------------------------------------------------------
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

// ------------------------------------------------------------
// Load Config
// ------------------------------------------------------------
import { connectWS, sendWSMessage } from "./websocket.js";

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
// Generate Mode
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