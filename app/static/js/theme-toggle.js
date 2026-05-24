const getStoredTheme = () => localStorage.getItem('theme') || 'light';

const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-bs-theme', theme);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
};

applyTheme(getStoredTheme());

document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.querySelector('#themeSwitch');
    if (themeSwitch) {
        themeSwitch.checked = getStoredTheme() === 'dark';
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = themeSwitch.checked ? '☀️' : '🌙';

        themeSwitch.addEventListener('change', () => {
            const newTheme = themeSwitch.checked ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }
});