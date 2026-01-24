// Обновление поля логина на полный с дискриминатором после автозаполнения пароля
document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('login_username');
    const passwordInput = document.getElementById('password');
    const fullUsernameHidden = document.getElementById('full_username');

    if (!usernameInput || !passwordInput || !fullUsernameHidden) {
        return;
    }

    // Функция обновления логина
    function updateUsername() {
        if (!fullUsernameHidden.value || usernameInput.value === fullUsernameHidden.value) {
            return;
        }
        
        usernameInput.value = fullUsernameHidden.value;
        
        const helpText = usernameInput.parentElement.querySelector('.form-text');
        if (helpText) {
            helpText.textContent = `Логин обновлён: ${fullUsernameHidden.value}`;
            helpText.style.color = '#28a745';
            helpText.style.cursor = 'pointer';
            helpText.title = 'Нажмите, чтобы исправить логин';
            
            // Делаем подсказку кликабельной
            helpText.addEventListener('click', function() {
                usernameInput.value = fullUsernameHidden.value;
                helpText.textContent = 'Логин исправлен для сохранения в браузере';
                helpText.style.color = '#007bff';
                
                // Фокус на поле логина, чтобы браузер распознал изменение
                usernameInput.focus();
                setTimeout(() => usernameInput.blur(), 100);
            });
        }
    }

    // Проверяем после загрузки и при изменении пароля
    setTimeout(updateUsername, 500);
    passwordInput.addEventListener('input', updateUsername);
});
