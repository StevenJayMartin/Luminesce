// tools.js
// Hooks for tool-related UI updates

window.logToolResult = function (toolName, result) {
    const panel = document.getElementById("tool-panel");
    if (!panel) return;
    const existing = panel.textContent || "";
    const entry = `\n[${toolName}]\n${JSON.stringify(result, null, 2)}\n`;
    panel.textContent = existing + entry;
};
