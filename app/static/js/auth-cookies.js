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
        this.initialized = false;
        this.init();
    }

    /**
     * Инициализация при загрузке страницы
     */
    init() {
        if (this.initialized) return;
        
        console.log('AuthCookieManager инициализирован');
        this.initialized = true;
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
                    // Используем более безопасный способ парсинга
                    const decodedValue = decodeURIComponent(value);
                    const data = this.safeJSONParse(decodedValue);
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
     * Безопасный парсинг JSON без использования eval
     * @param {string} jsonString - строка JSON
     * @returns {object} распарсенный объект
     */
    safeJSONParse(jsonString) {
        // Проверяем валидность JSON перед парсингом
        if (typeof jsonString !== 'string') {
            throw new Error('Invalid input: expected string');
        }
        
        // Базовая проверка на безопасность
        if (!jsonString.trim().startsWith('{') || !jsonString.trim().endsWith('}')) {
            throw new Error('Invalid JSON format');
        }
        
        return JSON.parse(jsonString);
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
    try {
        const authCookie = new AuthCookieManager();
        const form = document.querySelector('form[method="post"]');
        const usernameInput = document.getElementById('login_username') || document.getElementById('username');
        const fullUsernameHidden = document.getElementById('full_username');

        if (!form || !usernameInput) {
            console.warn('AuthCookieManager: Форма или поле логина не найдены');
            return;
        }

        form.addEventListener('submit', function(e) {
            try {
                const baseUsername = usernameInput.value.trim();
                
                if (!baseUsername) return;

                // Проверяем cookie
                const storedFullUsername = authCookie.getFullUsername(baseUsername);
                
                if (storedFullUsername && authCookie.validateUsernameMatch(baseUsername, storedFullUsername)) {
                    // Используем полный логин из cookie, только если скрытое поле пустое
                    if (fullUsernameHidden && !fullUsernameHidden.value.trim()) {
                        fullUsernameHidden.value = storedFullUsername;
                        console.log(`Используем полный логин из cookie: ${storedFullUsername}`);
                    } else if (fullUsernameHidden && fullUsernameHidden.value.trim()) {
                        console.log(`Скрытое поле уже заполнено: ${fullUsernameHidden.value}`);
                    }
                } else {
                    // Очищаем скрытое поле, будем использовать fallback логику на сервере
                    if (fullUsernameHidden) {
                        fullUsernameHidden.value = '';
                    }
                    console.log('Cookie не найден или не совпадает, используем fallback');
                }
            } catch (error) {
                console.error('Ошибка при обработке формы входа:', error);
            }
        });
    } catch (error) {
        console.error('Ошибка при инициализации AuthCookieManager:', error);
    }
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
