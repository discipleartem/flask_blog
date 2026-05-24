// Инициализация выпадающих меню в навигации
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(element => new bootstrap.Dropdown(element));
    
    const dropdownMenus = document.querySelectorAll('.dropdown-menu');
    dropdownMenus.forEach(menu => menu.addEventListener('click', e => e.stopPropagation()));
});
