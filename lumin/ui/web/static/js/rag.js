// rag.js
// Hooks for RAG-related UI updates

window.showRagInfo = function (info) {
    const panel = document.getElementById("rag-panel");
    if (!panel) return;
    panel.textContent = JSON.stringify(info, null, 2);
};
