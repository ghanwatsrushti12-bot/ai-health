/**
 * Dark / light theme toggle.
 *
 * Bootstrap 5.3's `data-bs-theme` attribute on <html> drives every
 * component's color scheme. We just flip that attribute and remember the
 * choice in localStorage so it survives a reload; if the user is logged in,
 * `theme-sync.js`-style forms (see accounts/settings.html) also persist it
 * server-side so the preference follows them across devices.
 */
(function () {
    const STORAGE_KEY = "carepulse-theme";
    const root = document.documentElement;
    const toggleButton = document.getElementById("themeToggle");

    function applyTheme(theme) {
        root.setAttribute("data-bs-theme", theme);
        if (toggleButton) {
            const icon = toggleButton.querySelector("i");
            if (icon) {
                icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
            }
        }
    }

    const stored = localStorage.getItem(STORAGE_KEY);
    const serverPref = root.getAttribute("data-server-theme");
    const initial = stored || serverPref || "light";
    applyTheme(initial);

    toggleButton?.addEventListener("click", function () {
        const current = root.getAttribute("data-bs-theme");
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem(STORAGE_KEY, next);
    });
})();
