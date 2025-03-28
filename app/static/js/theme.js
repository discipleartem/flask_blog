document.addEventListener('DOMContentLoaded', function() {
    // Theme toggling function
    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    // Set initial theme
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme');

    // Only set theme if explicitly saved, otherwise keep light theme
    if (savedTheme) {
        html.setAttribute('data-theme', savedTheme);
    } else {
        html.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }

    // Add click handler
    document.getElementById('toggleTheme').addEventListener('click', toggleTheme);
});