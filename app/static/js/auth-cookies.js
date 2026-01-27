/**
 * Управление cookie для аутентификации с дискриминаторами
 * 
 * Логика:
 * 1. При регистрации сервер сохраняет полный логин в cookie
 * 2. При входе JavaScript проверяет cookie и подставляет полный логин
 * 3. Fallback для уникальных логинов если cookie пуст
 */

class AuthCookieManager {
    constructor() {
        this.cookieName = 'full_usernames';
        this.init();
    }

    /**
     * Инициализация при загрузке страницы
     */
    init() {
        console.log('AuthCookieManager инициализирован');
    }

    /**
     * Получение полного логина из cookie
     * @param {string} baseUsername - базовый логин (user)
     * @returns {string|null} полный логин или null
     */
    getFullUsername(baseUsername) {
        const cookies = document.cookie.split(';');
        
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === this.cookieName) {
                try {
                    const data = JSON.parse(decodeURIComponent(value));
                    return data[baseUsername.toLowerCase()] || null;
                } catch (e) {
                    console.error('Ошибка парсинга cookie:', e);
                    return null;
                }
            }
        }
        
        return null;
    }

    /**
     * Проверка совпадения базовых логинов
     * @param {string} baseUsername - базовый логин из формы
     * @param {string} fullUsername - полный логин из cookie
     * @returns {boolean} совпадают ли базовые логины
     */
    validateUsernameMatch(baseUsername, fullUsername) {
        if (!fullUsername || !fullUsername.includes('#')) {
            return false;
        }
        
        const storedBase = fullUsername.split('#')[0].toLowerCase();
        const inputBase = baseUsername.toLowerCase();
        
        return storedBase === inputBase;
    }
}

/**
 * Обработка формы входа с cookie
 */
function handleLoginWithCookies() {
    const authCookie = new AuthCookieManager();
    const form = document.querySelector('form[method="post"]');
    const usernameInput = document.getElementById('login_username') || document.getElementById('username');
    const fullUsernameHidden = document.getElementById('full_username');

    if (!form || !usernameInput) return;

    form.addEventListener('submit', function(e) {
        const baseUsername = usernameInput.value.trim();
        
        if (!baseUsername) return;

        // Проверяем cookie
        const storedFullUsername = authCookie.getFullUsername(baseUsername);
        
        if (storedFullUsername && authCookie.validateUsernameMatch(baseUsername, storedFullUsername)) {
            // Используем полный логин из cookie
            if (fullUsernameHidden) {
                fullUsernameHidden.value = storedFullUsername;
                console.log(`Используем полный логин из cookie: ${storedFullUsername}`);
            }
        } else {
            // Очищаем скрытое поле, будем использовать fallback логику на сервере
            if (fullUsernameHidden) {
                fullUsernameHidden.value = '';
            }
            console.log('Cookie не найден или не совпадает, используем fallback');
        }
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Для страницы входа
    if (window.location.pathname.includes('/login')) {
        handleLoginWithCookies();
    }
});

// Глобальный доступ для использования в других скриптах
window.AuthCookieManager = AuthCookieManager;
