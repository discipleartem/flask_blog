/**
 * Модуль управления формой входа с поддержкой дискриминаторов
 * 
 * Функциональность:
 * - Обновление логина до полного формата с дискриминатором
 * - Управление видимостью кнопки обновления
 * - Очистка скрытого поля при изменении логина пользователем
 * - Анимация кнопки при взаимодействии
 */

class LoginFormManager {
    constructor() {
        // Константы
        this.SELECTORS = {
            USERNAME_INPUT: 'login_username',
            PASSWORD_INPUT: 'password',
            FULL_USERNAME_HIDDEN: 'full_username',
            UPDATE_BUTTON: 'update_username_button',
            HELP_TEXT: '.form-text'
        };
        
        this.CLASSES = {
            SPINNING: 'fa-spin',
            SUCCESS_COLOR: '#28a745'
        };
        
        this.TIMING = {
            INITIAL_CHECK: 100,
            FOCUS_DELAY: 100,
            ANIMATION_DURATION: 500
        };
        
        // Элементы DOM
        this.elements = {};
        
        this.init();
    }
    
    /**
     * Инициализация модуля
     */
    init() {
        this.cacheElements();
        
        if (!this.validateElements()) {
            console.warn('LoginFormManager: Не все необходимые элементы найдены');
            return;
        }
        
        this.bindEvents();
        this.initializeUI();
    }
    
    /**
     * Кэширование DOM элементов
     */
    cacheElements() {
        this.elements = {
            usernameInput: document.getElementById(this.SELECTORS.USERNAME_INPUT),
            passwordInput: document.getElementById(this.SELECTORS.PASSWORD_INPUT),
            fullUsernameHidden: document.getElementById(this.SELECTORS.FULL_USERNAME_HIDDEN),
            updateButton: document.getElementById(this.SELECTORS.UPDATE_BUTTON)
        };
    }
    
    /**
     * Проверка наличия всех необходимых элементов
     */
    validateElements() {
        return Object.values(this.elements).every(element => element !== null);
    }
    
    /**
     * Привязка обработчиков событий
     */
    bindEvents() {
        // Клик по кнопке обновления
        this.elements.updateButton.addEventListener('click', () => {
            this.handleUpdateButtonClick();
        });
        
        // Изменение поля логина
        this.elements.usernameInput.addEventListener('input', () => {
            this.handleUsernameInputChange();
        });
    }
    
    /**
     * Инициализация интерфейса при загрузке
     */
    initializeUI() {
        setTimeout(() => {
            this.toggleUpdateButton();
        }, this.TIMING.INITIAL_CHECK);
    }
    
    /**
     * Обновление поля логина до полного формата
     * @param {boolean} isUserAction - Инициировано ли действие пользователем
     * @returns {boolean} - Было ли обновление выполнено
     */
    updateUsername(isUserAction = false) {
        const currentUsername = this.getUsername();
        const fullUsername = this.getFullUsername();
        
        if (!isUserAction || !fullUsername) {
            return false;
        }
        
        this.elements.usernameInput.value = fullUsername;
        this.updateHelpText(fullUsername);
        
        return true;
    }
    
    /**
     * Получение текущего логина из поля ввода
     */
    getUsername() {
        return this.elements.usernameInput.value.trim();
    }
    
    /**
     * Получение полного логина из скрытого поля
     */
    getFullUsername() {
        return this.elements.fullUsernameHidden.value.trim();
    }
    
    /**
     * Обновление текста подсказки
     * @param {string} fullUsername - Полный логин для отображения
     */
    updateHelpText(fullUsername) {
        const helpText = this.findHelpText();
        if (helpText) {
            helpText.textContent = `Логин обновлён: ${fullUsername}`;
            helpText.style.color = this.CLASSES.SUCCESS_COLOR;
        }
    }
    
    /**
     * Поиск элемента текста подсказки
     */
    findHelpText() {
        return this.elements.usernameInput.parentElement.parentElement.querySelector(this.SELECTORS.HELP_TEXT);
    }
    
    /**
     * Переключение видимости кнопки обновления
     */
    toggleUpdateButton() {
        const isVisible = this.getFullUsername().length > 0;
        this.elements.updateButton.style.display = isVisible ? 'block' : 'none';
    }
    
    /**
     * Обработчик клика по кнопке обновления
     */
    handleUpdateButtonClick() {
        this.animateButton();
        
        const updated = this.updateUsername(true);
        
        if (updated) {
            this.focusAndBlurUsername();
        }
    }
    
    /**
     * Анимация кнопки (вращение)
     */
    animateButton() {
        const icon = this.elements.updateButton.querySelector('i');
        icon.classList.add(this.CLASSES.SPINNING);
        
        setTimeout(() => {
            icon.classList.remove(this.CLASSES.SPINNING);
        }, this.TIMING.ANIMATION_DURATION);
    }
    
    /**
     * Фокус на поле логина с последующим разфокусированием
     */
    focusAndBlurUsername() {
        this.elements.usernameInput.focus();
        setTimeout(() => {
            this.elements.usernameInput.blur();
        }, this.TIMING.FOCUS_DELAY);
    }
    
    /**
     * Обработчик изменения поля логина
     */
    handleUsernameInputChange() {
        const currentUsername = this.getUsername();
        const fullUsername = this.getFullUsername();
        
        // Очищаем скрытое поле если пользователь ввёл другой логин
        if (currentUsername && fullUsername && currentUsername !== fullUsername) {
            this.elements.fullUsernameHidden.value = '';
            this.toggleUpdateButton();
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    window.loginFormManager = new LoginFormManager();
});
