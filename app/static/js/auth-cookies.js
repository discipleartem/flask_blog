/** Управление cookie для аутентификации с дискриминаторами */

class AuthCookieManager {
    constructor() {
        this.cookieName = 'full_usernames';
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        this.initialized = true;
    }

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

    validateUsernameMatch(baseUsername, fullUsername) {
        if (!fullUsername || !fullUsername.includes('#')) {
            return false;
        }
        
        const storedBase = fullUsername.split('#')[0].toLowerCase();
        const inputBase = baseUsername.toLowerCase();
        
        return storedBase === inputBase;
    }
}

function handleLoginWithCookies() {
    try {
        const authCookie = new AuthCookieManager();
        const form = document.querySelector('form[method="post"]');
        const usernameInput = document.getElementById('login_username') || document.getElementById('username');
        const fullUsernameHidden = document.getElementById('full_username');

        if (!form || !usernameInput) return;

        form.addEventListener('submit', function(e) {
            try {
                const baseUsername = usernameInput.value.trim();
                
                if (!baseUsername) return;

                // Проверяем cookie
                const storedFullUsername = authCookie.getFullUsername(baseUsername);
                
                if (storedFullUsername && authCookie.validateUsernameMatch(baseUsername, storedFullUsername)) {
                    if (fullUsernameHidden && !fullUsernameHidden.value.trim()) {
                        fullUsernameHidden.value = storedFullUsername;
                    }
                } else {
                    if (fullUsernameHidden) {
                        fullUsernameHidden.value = '';
                    }
                }
            } catch (error) {
                // Ошибка игнорируется
            }
        });
    } catch (error) {
        // Ошибка игнорируется
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
