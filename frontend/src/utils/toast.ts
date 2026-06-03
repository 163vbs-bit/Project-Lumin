export function toast(message: string) {
  const root = document.getElementById("toast-root");
  if (!root) return;
  const node = document.createElement("div");
  node.className = "glass rounded-lg px-4 py-3 text-sm text-white shadow-card";
  node.textContent = message;
  root.appendChild(node);
  window.setTimeout(() => node.remove(), 2800);
}
