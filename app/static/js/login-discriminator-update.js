/** Модуль управления формой входа с поддержкой дискриминаторов */

class LoginFormManager {
    constructor() {
        if (window.loginFormManagerInstance) {
            return window.loginFormManagerInstance;
        }
        
        this.elements = {};
        window.loginFormManagerInstance = this;
        this.init();
    }
    
    init() {
        this.cacheElements();
        if (!this.validateElements()) return;
        this.bindEvents();
        this.initializeUI();
    }
    
    cacheElements() {
        this.elements = {
            usernameInput: document.getElementById('login_username'),
            passwordInput: document.getElementById('password'),
            fullUsernameHidden: document.getElementById('full_username'),
            updateButton: document.getElementById('update_username_button')
        };
    }
    
    validateElements() {
        return Object.values(this.elements).every(element => element !== null);
    }
    
    bindEvents() {
        this.elements.updateButton.addEventListener('click', () => this.handleUpdateButtonClick());
        this.elements.usernameInput.addEventListener('input', () => this.handleUsernameInputChange());
    }
    
    initializeUI() {
        setTimeout(() => this.toggleUpdateButton(), 100);
    }
    
    updateUsername(isUserAction = false) {
        const currentUsername = this.getUsername();
        const fullUsername = this.getFullUsername();
        
        if (!isUserAction || !fullUsername) return false;
        
        this.elements.usernameInput.value = fullUsername;
        this.updateHelpText(fullUsername);
        return true;
    }
    
    getUsername() {
        return this.elements.usernameInput.value.trim();
    }
    
    getFullUsername() {
        return this.elements.fullUsernameHidden.value.trim();
    }
    
    updateHelpText(fullUsername) {
        const helpText = this.findHelpText();
        if (helpText) {
            helpText.textContent = `Логин обновлён: ${fullUsername}`;
            helpText.style.color = '#28a745';
        }
    }
    
    findHelpText() {
        return this.elements.usernameInput.parentElement.parentElement.querySelector('.form-text');
    }
    
    toggleUpdateButton() {
        const isVisible = this.getFullUsername().length > 0;
        this.elements.updateButton.style.display = isVisible ? 'block' : 'none';
    }
    
    handleUpdateButtonClick() {
        this.animateButton();
        const updated = this.updateUsername(true);
        if (updated) this.focusAndBlurUsername();
    }
    
    animateButton() {
        const icon = this.elements.updateButton.querySelector('i');
        icon.classList.add('fa-spin');
        setTimeout(() => icon.classList.remove('fa-spin'), 500);
    }
    
    focusAndBlurUsername() {
        this.elements.usernameInput.focus();
        setTimeout(() => this.elements.usernameInput.blur(), 100);
    }
    
    handleUsernameInputChange() {
        this.toggleUpdateButton();
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (!window.loginFormManagerInstance) {
        window.loginFormManager = new LoginFormManager();
    } else {
        window.loginFormManager = window.loginFormManagerInstance;
    }
});
