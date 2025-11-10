const STORAGE_KEY = "clientescrm-theme";

/**
 * @param {"dark" | "light"} mode
 */
function setTheme(mode) {
    const root = document.documentElement;
    if (mode === "light") {
        root.classList.remove("dark");
    } else {
        root.classList.add("dark");
    }
    localStorage.setItem(STORAGE_KEY, mode);
    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
        toggle.textContent = mode === "light" ? "Modo escuro" : "Modo claro";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const initial = stored === "light" ? "light" : "dark";
    setTheme(initial);
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
    const currentStored = localStorage.getItem(STORAGE_KEY);
    const current = currentStored === "light" ? "light" : "dark";
    setTheme(current === "dark" ? "light" : "dark");
    });
});
