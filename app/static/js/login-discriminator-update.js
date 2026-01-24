// Обновление поля логина на полный с дискриминатором по кнопке
document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('login_username');
    const passwordInput = document.getElementById('password');
    const fullUsernameHidden = document.getElementById('full_username');
    const updateButton = document.getElementById('update_username_button');

    if (!usernameInput || !passwordInput || !fullUsernameHidden || !updateButton) {
        return;
    }

    // Функция обновления логина
    function updateUsername(isUserAction = false) {
        const currentUsername = usernameInput.value.trim();
        const fullUsername = fullUsernameHidden.value.trim();
        
        // Обновляем только если это явное действие пользователя
        if (isUserAction && fullUsername) {
            usernameInput.value = fullUsername;
            
            const helpText = usernameInput.parentElement.parentElement.querySelector('.form-text');
            if (helpText) {
                helpText.textContent = 'Логин обновлён: ' + fullUsername;
                helpText.style.color = '#28a745';
            }
            
            return true;
        }
        
        return false;
    }

    // Показываем/скрываем кнопку в зависимости от наличия полного логина
    function toggleUpdateButton() {
        if (fullUsernameHidden.value.trim()) {
            updateButton.style.display = 'block';
        } else {
            updateButton.style.display = 'none';
        }
    }

    // Обработчик кнопки обновления
    updateButton.addEventListener('click', function() {
        // Добавляем анимацию вращения
        const icon = this.querySelector('i');
        icon.classList.add('fa-spin');
        
        const updated = updateUsername(true);
        
        if (updated) {
            // Фокус на поле логина, чтобы браузер распознал изменение
            usernameInput.focus();
            setTimeout(() => usernameInput.blur(), 100);
        }
        
        // Убираем анимацию через 500мс
        setTimeout(() => {
            icon.classList.remove('fa-spin');
        }, 500);
    });

    // Очищаем скрытое поле только если пользователь ввёл другой логин
    usernameInput.addEventListener('input', function() {
        const currentUsername = usernameInput.value.trim();
        const fullUsername = fullUsernameHidden.value.trim();
        
        // Очищаем только если поле не пустое и введённый логин отличается от сохранённого
        if (currentUsername && fullUsername && currentUsername !== fullUsername) {
            fullUsernameHidden.value = '';
            toggleUpdateButton();
        }
    });

    // Проверяем при загрузке
    setTimeout(toggleUpdateButton, 100);
});
