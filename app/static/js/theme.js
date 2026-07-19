(function () {
  const STORAGE_KEY = "flask-blog-theme";

  function preferredTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "light" || saved === "dark") {
      return saved;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-bs-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  applyTheme(preferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".theme-toggle").forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        const current = document.documentElement.getAttribute("data-bs-theme") || "light";
        applyTheme(current === "light" ? "dark" : "light");
      });
    });
  });
})();
