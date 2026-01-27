// Инициализация выпадающих меню в навигации
document.addEventListener('DOMContentLoaded', function() {
    console.log('Navbar JS loaded');
    
    // Инициализируем все dropdown элементы
    var dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    console.log('Found dropdown elements:', dropdownElements.length);
    
    dropdownElements.forEach(function(element) {
        console.log('Initializing dropdown for:', element);
        new bootstrap.Dropdown(element);
    });
    
    // Добавляем обработчик для предотвращения закрытия при клике внутри меню
    var dropdownMenus = document.querySelectorAll('.dropdown-menu');
    dropdownMenus.forEach(function(menu) {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});
