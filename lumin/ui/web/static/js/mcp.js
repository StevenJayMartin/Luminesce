// mcp.js
// Hooks for MCP / tools / external capabilities

window.showMcpInfo = function (info) {
    const panel = document.getElementById("semantic-panel");
    if (!panel) return;
    const existing = panel.textContent || "";
    panel.textContent = existing + "\n" + JSON.stringify(info, null, 2);
};