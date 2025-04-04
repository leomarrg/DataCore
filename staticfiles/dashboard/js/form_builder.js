// dashboard/static/dashboard/js/form_builder.js
document.addEventListener('DOMContentLoaded', function() {
    const fieldsContainer = document.getElementById('fieldsContainer');
    const groupsContainer = document.getElementById('groupsContainer');
    const addFieldBtn = document.getElementById('addFieldBtn');
    const addGroupBtn = document.getElementById('addGroupBtn');
    const fieldTemplate = document.getElementById('fieldTemplate');
    const groupTemplate = document.getElementById('groupTemplate');
    const noFieldsMessage = document.getElementById('noFieldsMessage');
    const noGroupsMessage = document.getElementById('noGroupsMessage');
    
    // Guardar referencia a todos los contenedores de campos (principal y dentro de grupos)
    let allFieldsContainers = [fieldsContainer];
    document.querySelectorAll('.fields-container').forEach(container => {
        allFieldsContainers.push(container);
    });
    
    // Inicializar Sortable para arrastrar y ordenar campos en el contenedor principal
    new Sortable(fieldsContainer, {
        animation: 150,
        handle: '.handle',
        group: 'fields', // Para permitir mover campos entre contenedores
        onEnd: function(evt) {
            // Al mover un campo, actualizar su grupo
            const fieldElement = evt.item;
            const targetContainer = evt.to;
            
            // Si se movió a un contenedor de grupo
            if (targetContainer.classList.contains('fields-container')) {
                const groupId = targetContainer.dataset.groupId;
                
                // Actualizar el atributo data-group-id del campo
                fieldElement.setAttribute('data-group-id', groupId);
                fieldElement.classList.add('grouped');
                
                // Actualizar el select de grupo en las opciones del campo
                const groupSelect = fieldElement.querySelector('.field-group-select');
                if (groupSelect) {
                    // Si el grupo es nuevo (aún no guardado en BD), usar el ID temporal
                    if (groupId === 'new') {
                        // Buscar el primer select de grupo disponible en los grupos existentes
                        const newGroupRow = targetContainer.closest('.group-row');
                        const groupNameInput = newGroupRow.querySelector('input[name="group_names"]');
                        const groupName = groupNameInput ? groupNameInput.value : 'Nuevo grupo';
                        
                        // Añadir opción temporal para el grupo nuevo
                        let tempOption = document.createElement('option');
                        tempOption.value = 'new_temp';
                        tempOption.textContent = groupName;
                        groupSelect.appendChild(tempOption);
                        tempOption.selected = true;
                    } else {
                        groupSelect.value = groupId;
                    }
                }
                
                // Mostrar la etiqueta de grupo en el título del campo
                const groupName = getGroupName(groupId);
                updateFieldGroupBadge(fieldElement, groupName);
                
                // Actualizar contador de campos en el grupo
                updateGroupFieldCount(targetContainer.closest('.group-row'));
            } else {
                // Se movió al contenedor principal, quitar referencia de grupo
                fieldElement.removeAttribute('data-group-id');
                fieldElement.classList.remove('grouped');
                
                // Actualizar el select de grupo
                const groupSelect = fieldElement.querySelector('.field-group-select');
                if (groupSelect) {
                    groupSelect.value = '';
                }
                
                // Quitar la etiqueta de grupo
                removeFieldGroupBadge(fieldElement);
                
                // Si venía de un grupo, actualizar contador del grupo anterior
                if (evt.from.classList.contains('fields-container')) {
                    updateGroupFieldCount(evt.from.closest('.group-row'));
                }
            }
            
            // Actualizar el estado "empty" de los contenedores
            updateContainerEmptyState(evt.from);
            updateContainerEmptyState(evt.to);
            
            // Actualizar el orden de los campos
            updateFieldsOrder();
        }
    });
    
    // Inicializar Sortable para arrastrar y ordenar grupos
    new Sortable(groupsContainer, {
        animation: 150,
        handle: '.handle',
        onEnd: function() {
            // Actualizar el orden de los grupos
            updateGroupsOrder();
        }
    });
    
    // Inicializar Sortable para cada contenedor de campos dentro de grupos
    document.querySelectorAll('.fields-container').forEach(container => {
        initializeFieldsContainer(container);
    });
    
    // Función para obtener el nombre de un grupo por su ID
    function getGroupName(groupId) {
        if (groupId === 'new' || groupId === 'new_temp') {
            return 'Nuevo grupo';
        }
        
        const groupRow = document.querySelector(`.group-row[data-group-id="${groupId}"]`);
        if (groupRow) {
            return groupRow.querySelector('.group-title').textContent;
        }
        
        return '';
    }
    
    // Función para actualizar la etiqueta de grupo en un campo
    function updateFieldGroupBadge(fieldElement, groupName) {
        let badgeElement = fieldElement.querySelector('.badge');
        
        if (!badgeElement) {
            // Crear la etiqueta si no existe
            const titleElement = fieldElement.querySelector('.field-title');
            badgeElement = document.createElement('span');
            badgeElement.className = 'badge bg-info ms-2';
            titleElement.parentNode.appendChild(badgeElement);
        }
        
        badgeElement.textContent = 'Grupo: ' + groupName;
    }
    
    // Función para quitar la etiqueta de grupo de un campo
    function removeFieldGroupBadge(fieldElement) {
        const badgeElement = fieldElement.querySelector('.badge');
        if (badgeElement) {
            badgeElement.remove();
        }
    }
    
    // Función para actualizar el contador de campos en un grupo
    function updateGroupFieldCount(groupRow) {
        if (!groupRow) return;
        
        const fieldsContainer = groupRow.querySelector('.fields-container');
        const fieldCount = fieldsContainer.querySelectorAll('.field-row').length;
        const countBadge = groupRow.querySelector('.badge');
        
        if (countBadge) {
            countBadge.textContent = fieldCount + ' campos';
        }
    }
    
    // Función para actualizar el estado "empty" de un contenedor
    function updateContainerEmptyState(container) {
        if (!container) return;
        
        const hasFields = container.querySelectorAll('.field-row').length > 0;
        container.classList.toggle('empty', !hasFields);
        
        // Mostrar/ocultar mensaje de no hay campos
        const emptyMessage = container.querySelector('.text-muted');
        if (emptyMessage) {
            emptyMessage.style.display = hasFields ? 'none' : 'block';
        }
    }
    
    // Función para inicializar un contenedor de campos para Sortable
    function initializeFieldsContainer(container) {
        new Sortable(container, {
            animation: 150,
            handle: '.handle',
            group: 'fields', // Para permitir mover campos entre contenedores
            onEnd: function(evt) {
                // Al mover un campo, actualizar su grupo
                const fieldElement = evt.item;
                const targetContainer = evt.to;
                
                // Si se movió a un contenedor de grupo
                if (targetContainer.classList.contains('fields-container')) {
                    const groupId = targetContainer.dataset.groupId;
                    
                    // Actualizar el atributo data-group-id del campo
                    fieldElement.setAttribute('data-group-id', groupId);
                    fieldElement.classList.add('grouped');
                    
                    // Actualizar el select de grupo
                    const groupSelect = fieldElement.querySelector('.field-group-select');
                    if (groupSelect) {
                        groupSelect.value = groupId;
                    }
                    
                    // Mostrar la etiqueta de grupo
                    const groupName = getGroupName(groupId);
                    updateFieldGroupBadge(fieldElement, groupName);
                    
                    // Actualizar contador de campos en el grupo
                    updateGroupFieldCount(targetContainer.closest('.group-row'));
                } else {
                    // Se movió al contenedor principal, quitar referencia de grupo
                    fieldElement.removeAttribute('data-group-id');
                    fieldElement.classList.remove('grouped');
                    
                    // Actualizar el select de grupo
                    const groupSelect = fieldElement.querySelector('.field-group-select');
                    if (groupSelect) {
                        groupSelect.value = '';
                    }
                    
                    // Quitar la etiqueta de grupo
                    removeFieldGroupBadge(fieldElement);
                    
                    // Si venía de un grupo, actualizar contador del grupo anterior
                    if (evt.from.classList.contains('fields-container')) {
                        updateGroupFieldCount(evt.from.closest('.group-row'));
                    }
                }
                
                // Actualizar el estado "empty" de los contenedores
                updateContainerEmptyState(evt.from);
                updateContainerEmptyState(evt.to);
                
                // Actualizar el orden de los campos
                updateFieldsOrder();
            }
        });
        
        // Actualizar el estado inicial
        updateContainerEmptyState(container);
    }
    
    // Función para agregar un nuevo campo
    addFieldBtn.addEventListener('click', function() {
        // Clonar la plantilla
        const newField = document.importNode(fieldTemplate.content, true);
        
        // Generar un ID único para el campo
        const fieldId = 'new_' + Date.now();
        newField.querySelector('.field-row').setAttribute('data-field-id', fieldId);
        
        // Agregar el nuevo campo al contenedor
        fieldsContainer.appendChild(newField);
        
        // Ocultar el mensaje de "no hay campos"
        if (noFieldsMessage) {
            noFieldsMessage.style.display = 'none';
        }
        
        // Mostrar opciones del nuevo campo
        const fieldRow = fieldsContainer.lastElementChild;
        fieldRow.classList.add('show-options');
        
        // Inicializar eventos para el nuevo campo
        initFieldEvents(fieldRow);
        
        // Actualizar opciones de grupos en el select
        updateGroupSelect(fieldRow.querySelector('.field-group-select'));
    });
    
    // Función para agregar un nuevo grupo
    addGroupBtn.addEventListener('click', function() {
        // Clonar la plantilla
        const newGroup = document.importNode(groupTemplate.content, true);
        
        // Generar un ID único para el grupo
        const groupId = 'new_' + Date.now();
        const groupRow = newGroup.querySelector('.group-row');
        groupRow.setAttribute('data-group-id', groupId);
        
        // Actualizar IDs para collapse/expand
        const collapseTarget = groupRow.querySelector('[data-bs-target="#groupFields_new"]');
        const collapseContent = groupRow.querySelector('#groupFields_new');
        const newCollapseId = 'groupFields_' + groupId;
        
        if (collapseTarget) collapseTarget.setAttribute('data-bs-target', '#' + newCollapseId);
        if (collapseContent) collapseContent.id = newCollapseId;
        
        // Actualizar contenedor de campos
        const fieldsContainer = groupRow.querySelector('.fields-container');
        if (fieldsContainer) {
            fieldsContainer.setAttribute('data-group-id', groupId);
        }
        
        // Agregar el nuevo grupo al contenedor
        groupsContainer.appendChild(newGroup);
        
        // Ocultar el mensaje de "no hay grupos"
        if (noGroupsMessage) {
            noGroupsMessage.style.display = 'none';
        }
        
        // Mostrar opciones del nuevo grupo
        const newGroupRow = groupsContainer.lastElementChild;
        newGroupRow.classList.add('show-options');
        
        // Inicializar eventos para el nuevo grupo
        initGroupEvents(newGroupRow);
        
        // Inicializar el contenedor de campos dentro del grupo
        initializeFieldsContainer(newGroupRow.querySelector('.fields-container'));
        
        // Actualizar selects de grupo en todos los campos
        updateAllGroupSelects();
    });
    
    // Inicializar eventos para campos existentes
    document.querySelectorAll('.field-row').forEach(function(fieldRow) {
        initFieldEvents(fieldRow);
    });
    
    // Inicializar eventos para grupos existentes
    document.querySelectorAll('.group-row').forEach(function(groupRow) {
        initGroupEvents(groupRow);
    });
    
    // Función para actualizar todas las opciones de grupo en todos los selects de campo
    function updateAllGroupSelects() {
        document.querySelectorAll('.field-group-select').forEach(select => {
            updateGroupSelect(select);
        });
    }
    
    // Función para actualizar las opciones de grupo en un select específico
    function updateGroupSelect(select) {
        if (!select) return;
        
        // Guardar valor actual
        const currentValue = select.value;
        
        // Limpiar opciones actuales excepto la opción "Sin grupo"
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Añadir grupos disponibles
        document.querySelectorAll('.group-row').forEach(groupRow => {
            const groupId = groupRow.dataset.groupId;
            const groupNameElement = groupRow.querySelector('.group-name');
            const groupName = groupNameElement ? groupNameElement.value : groupRow.querySelector('.group-title').textContent;
            
            const option = document.createElement('option');
            option.value = groupId;
            option.textContent = groupName;
            select.appendChild(option);
        });
        
        // Restaurar valor si existe
        if (currentValue && select.querySelector(`option[value="${currentValue}"]`)) {
            select.value = currentValue;
        }
    }
    
    // Función para inicializar eventos de un grupo
    function initGroupEvents(groupRow) {
        // Botón para mostrar/ocultar opciones
        const toggleBtn = groupRow.querySelector('.toggle-group-options-btn');
        toggleBtn.addEventListener('click', function() {
            groupRow.classList.toggle('show-options');
        });
        
        // Botón para eliminar grupo
        const removeBtn = groupRow.querySelector('.remove-group-btn');
        removeBtn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de eliminar este grupo? Los campos asociados volverán al formulario principal.')) {
                // Mover campos del grupo al contenedor principal
                const groupFields = groupRow.querySelectorAll('.field-row');
                groupFields.forEach(field => {
                    // Quitar referencia al grupo
                    field.removeAttribute('data-group-id');
                    field.classList.remove('grouped');
                    
                    // Actualizar el select de grupo
                    const groupSelect = field.querySelector('.field-group-select');
                    if (groupSelect) {
                        groupSelect.value = '';
                    }
                    
                    // Quitar la etiqueta de grupo
                    removeFieldGroupBadge(field);
                    
                    // Mover al contenedor principal
                    fieldsContainer.appendChild(field);
                });
                
                // Eliminar el grupo
                groupRow.remove();
                
                // Actualizar contenedor principal
                updateContainerEmptyState(fieldsContainer);
                
                // Mostrar mensaje si no hay grupos
                if (groupsContainer.children.length === 0 && noGroupsMessage) {
                    noGroupsMessage.style.display = 'block';
                }
                
                // Actualizar selects de grupo en todos los campos
                updateAllGroupSelects();
            }
        });
        
        // Actualizar título al cambiar el nombre
        const nameInput = groupRow.querySelector('input[name="group_names"]');
        const groupTitle = groupRow.querySelector('.group-title');
        
        if (nameInput && groupTitle) {
            nameInput.addEventListener('input', function() {
                groupTitle.textContent = this.value || 'Sin nombre';
                
                // Actualizar también la opción en los selects de grupo de los campos
                updateAllGroupSelects();
                
                // Actualizar etiquetas de grupo en campos asociados
                const groupId = groupRow.dataset.groupId;
                document.querySelectorAll(`.field-row[data-group-id="${groupId}"]`).forEach(field => {
                    updateFieldGroupBadge(field, this.value || 'Sin nombre');
                });
            });
        }
        
        // Manejar colapsar/expandir campos del grupo
        const groupHeader = groupRow.querySelector('.group-header');
        const collapseElement = groupRow.querySelector('.collapse');
        if (groupHeader && collapseElement) {
            groupHeader.addEventListener('click', function() {
                const isCollapsed = !collapseElement.classList.contains('show');
                groupRow.classList.toggle('collapsed', !isCollapsed);
            });
        }
    }
    
    // Función para actualizar el orden de los campos
    function updateFieldsOrder() {
        // Actualizar campos en el contenedor principal
        fieldsContainer.querySelectorAll('.field-row').forEach(function(field, index) {
            const orderInput = field.querySelector('input[name="field_orders"]');
            if (orderInput) {
                orderInput.value = index;
            }
        });
        
        // Actualizar campos en cada grupo
        document.querySelectorAll('.fields-container').forEach(function(container) {
            if (container !== fieldsContainer) {
                container.querySelectorAll('.field-row').forEach(function(field, index) {
                    const orderInput = field.querySelector('input[name="field_orders"]');
                    if (orderInput) {
                        orderInput.value = index;
                    }
                });
            }
        });
    }
    
    // Función para actualizar el orden de los grupos
    function updateGroupsOrder() {
        document.querySelectorAll('.group-row').forEach(function(group, index) {
            const orderInput = group.querySelector('input[name="group_orders"]');
            if (orderInput) {
                orderInput.value = index;
            }
        });
    }
    
    // Validar formulario antes de enviar
    document.getElementById('formBuilder').addEventListener('submit', function(e) {
        // Validar nombre del formulario
        const formName = document.getElementById('name').value.trim();
        if (!formName) {
            e.preventDefault();
            alert('El nombre del formulario es obligatorio');
            return;
        }
        
        // Validar código del formulario
        const codeName = document.getElementById('code_name').value.trim();
        if (!codeName) {
            e.preventDefault();
            alert('El código identificador es obligatorio');
            return;
        }
        
        // Validar que el código solo contenga letras, números y guiones
        const codeNameRegex = /^[a-z0-9\-]+$/;
        if (!codeNameRegex.test(codeName)) {
            e.preventDefault();
            alert('El código identificador solo puede contener letras minúsculas, números y guiones');
            return;
        }
        
        // Validar que haya al menos un departamento seleccionado
        const departments = document.querySelectorAll('input[name="departments"]:checked');
        if (departments.length === 0) {
            e.preventDefault();
            alert('Debes seleccionar al menos un departamento con acceso al formulario');
            return;
        }
        
        // Validar que los nombres de grupos no estén vacíos
        const groupNames = document.querySelectorAll('input[name="group_names"]');
        for (let i = 0; i < groupNames.length; i++) {
            if (!groupNames[i].value.trim()) {
                e.preventDefault();
                alert('Todos los grupos deben tener un nombre');
                groupNames[i].focus();
                return;
            }
        }
        
        // Validar que los campos tengan nombres y etiquetas
        const fieldNames = document.querySelectorAll('input[name="field_names"]');
        const fieldLabels = document.querySelectorAll('input[name="field_labels"]');
        for (let i = 0; i < fieldNames.length; i++) {
            if (!fieldNames[i].value.trim()) {
                e.preventDefault();
                alert('Todos los campos deben tener un nombre');
                fieldNames[i].focus();
                return;
            }
            if (!fieldLabels[i].value.trim()) {
                e.preventDefault();
                alert('Todos los campos deben tener una etiqueta');
                fieldLabels[i].focus();
                return;
            }
        }
        
        // Actualizar el orden de los campos y grupos antes de enviar
        updateFieldsOrder();
        updateGroupsOrder();
    });
    
    // Actualizar todos los selectores de grupo al inicio
    updateAllGroupSelects();
    
    // Función para inicializar eventos de un campo
    function initFieldEvents(fieldRow) {
        // Botón para mostrar/ocultar opciones
        const toggleBtn = fieldRow.querySelector('.toggle-options-btn');
        toggleBtn.addEventListener('click', function() {
            fieldRow.classList.toggle('show-options');
        });
        
        // Botón para eliminar campo
        const removeBtn = fieldRow.querySelector('.remove-field-btn');
        removeBtn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de eliminar este campo?')) {
                // Si el campo está en un grupo, actualizar contador del grupo
                const groupId = fieldRow.dataset.groupId;
                if (groupId) {
                    const groupRow = document.querySelector(`.group-row[data-group-id="${groupId}"]`);
                    if (groupRow) {
                        fieldRow.remove();
                        updateGroupFieldCount(groupRow);
                        updateContainerEmptyState(groupRow.querySelector('.fields-container'));
                    }
                } else {
                    fieldRow.remove();
                }
                
                // Mostrar mensaje si no hay campos
                if (fieldsContainer.children.length === 0 && noFieldsMessage) {
                    noFieldsMessage.style.display = 'block';
                }
                
                // Actualizar el contenedor donde estaba el campo
                const parentContainer = fieldRow.parentElement;
                if (parentContainer) {
                    updateContainerEmptyState(parentContainer);
                }
            }
        });
        
        // Actualizar título al cambiar la etiqueta
        const labelInput = fieldRow.querySelector('input[name="field_labels"]');
        const fieldTitle = fieldRow.querySelector('.field-title');
        
        if (labelInput && fieldTitle) {
            labelInput.addEventListener('input', function() {
                fieldTitle.textContent = this.value || 'Sin etiqueta';
            });
        }
        
        // Manejar cambios en la selección de grupo
        const groupSelect = fieldRow.querySelector('.field-group-select');
        if (groupSelect) {
            groupSelect.addEventListener('change', function() {
                const selectedGroupId = this.value;
                const oldGroupId = fieldRow.dataset.groupId;
                
                // Si el grupo cambió
                if (selectedGroupId !== oldGroupId) {
                    // Actualizar data-group-id
                    if (selectedGroupId) {
                        fieldRow.setAttribute('data-group-id', selectedGroupId);
                        fieldRow.classList.add('grouped');
                        
                        // Actualizar etiqueta de grupo
                        const groupName = getGroupName(selectedGroupId);
                        updateFieldGroupBadge(fieldRow, groupName);
                        
                        // Mover visualmente el campo al grupo seleccionado
                        const targetGroupContainer = document.querySelector(`.fields-container[data-group-id="${selectedGroupId}"]`);
                        if (targetGroupContainer) {
                            // Remover del contenedor actual
                            fieldRow.parentNode.removeChild(fieldRow);
                            
                            // Añadir al nuevo contenedor de grupo
                            targetGroupContainer.appendChild(fieldRow);
                            
                            // Actualizar estados de contenedores
                            updateContainerEmptyState(targetGroupContainer);
                            
                            // Actualizar contadores de campos
                            const targetGroupRow = targetGroupContainer.closest('.group-row');
                            if (targetGroupRow) {
                                updateGroupFieldCount(targetGroupRow);
                            }
                        }
                    } else {
                        // Quitar asociación con grupo
                        fieldRow.removeAttribute('data-group-id');
                        fieldRow.classList.remove('grouped');
                        removeFieldGroupBadge(fieldRow);
                        
                        // Mover al contenedor principal
                        fieldRow.parentNode.removeChild(fieldRow);
                        fieldsContainer.appendChild(fieldRow);
                    }
                    
                    // Si tenía un grupo anterior, actualizar su contador
                    if (oldGroupId) {
                        const oldGroupRow = document.querySelector(`.group-row[data-group-id="${oldGroupId}"]`);
                        if (oldGroupRow) {
                            const oldGroupContainer = oldGroupRow.querySelector('.fields-container');
                            updateContainerEmptyState(oldGroupContainer);
                            updateGroupFieldCount(oldGroupRow);
                        }
                    }
                    
                    // Actualizar contenedor principal si es necesario
                    updateContainerEmptyState(fieldsContainer);
                }
            });
        }
    }
});