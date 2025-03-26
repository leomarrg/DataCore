// Ubicación: dashboard/static/dashboard/js/sidebar.js

document.addEventListener('DOMContentLoaded', function() {
    // Manejar el toggle del sidebar en dispositivos móviles
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const contentWrapper = document.querySelector('.content-wrapper');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            contentWrapper.classList.toggle('active');
        });
    }
    
    // Resaltar el departamento seleccionado en el sidebar
    const currentDeptId = new URLSearchParams(window.location.search).get('department');
    if (currentDeptId) {
        const deptItems = document.querySelectorAll('.departments-menu li');
        deptItems.forEach(item => {
            const link = item.querySelector('a');
            const deptId = new URLSearchParams(new URL(link.href).search).get('department');
            
            if (deptId === currentDeptId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
});

// Añadir a dashboard/static/dashboard/js/sidebar.js

// Manejar expansión/colapso de departamentos con hijos
const deptWithChildren = document.querySelectorAll('.departments-menu li:has(.submenu)');
deptWithChildren.forEach(dept => {
    const link = dept.querySelector('a');
    const submenu = dept.querySelector('.submenu');
    
    // Añadir un icono para expandir/colapsar
    const toggleIcon = document.createElement('span');
    toggleIcon.className = 'toggle-icon ms-2';
    toggleIcon.innerHTML = '<i class="fas fa-chevron-down"></i>';
    link.appendChild(toggleIcon);
    
    // Manejar el clic en el icono
    toggleIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        submenu.classList.toggle('collapsed');
        
        // Cambiar el icono
        const icon = toggleIcon.querySelector('i');
        if (submenu.classList.contains('collapsed')) {
            icon.className = 'fas fa-chevron-right';
        } else {
            icon.className = 'fas fa-chevron-down';
        }
    });
});