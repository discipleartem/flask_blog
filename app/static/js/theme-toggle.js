// Функция для получения текущей темы
const getStoredTheme = () => localStorage.getItem('theme') || 'light';

// Функция для применения темы к документу
const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-bs-theme', theme);
    // Обновляем иконку сразу, если DOM уже загружен
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
};

// Применяем тему немедленно (вызывается в head)
applyTheme(getStoredTheme());

document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.querySelector('#themeSwitch');

    if (themeSwitch) {
        themeSwitch.checked = getStoredTheme() === 'dark';

        // Устанавливаем корректную иконку при загрузке
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = themeSwitch.checked ? '☀️' : '🌙';

        themeSwitch.addEventListener('change', () => {
            const newTheme = themeSwitch.checked ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }
});