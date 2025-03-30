# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from autenticacion.models import Company, Department, Employee
from .models import DashboardWidget, CompanyDashboard, DashboardWidgetConfig, CustomForm, FormField, FormData, FormFieldGroup, CompanyTheme
from .widgets import get_widget_data
from .forms import DashboardConfigForm, WidgetConfigForm
import datetime
from django.db import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def setup_company_dashboard(request, company_id):
    """Vista para la configuración inicial del dashboard de una compañía"""
    company = get_object_or_404(Company, id=company_id)
    
    # Verificar si ya existe un dashboard
    dashboard, created = CompanyDashboard.objects.get_or_create(company=company)
    
    if request.method == 'POST':
        form = DashboardConfigForm(request.POST)
        if form.is_valid():
            # Limpiar widgets existentes
            DashboardWidgetConfig.objects.filter(dashboard=dashboard).delete()
            
            # Crear nuevos widgets
            widgets = form.cleaned_data['widgets']
            for i, widget_id in enumerate(widgets):
                widget = DashboardWidget.objects.get(id=widget_id)
                DashboardWidgetConfig.objects.create(
                    dashboard=dashboard,
                    widget=widget,
                    position=i,
                    size='medium',
                    is_visible=True
                )

            messages.success(request, f"Dashboard configurado para {company.name}")
            return redirect('admin:autenticacion_company_changelist')
    else:
        # Formulario con widgets disponibles
        form = DashboardConfigForm()
        
    return render(request, 'dashboard/admin/setup_dashboard.html', {
        'company': company,
        'dashboard': dashboard,
        'form': form,
        'existing_widgets': DashboardWidgetConfig.objects.filter(dashboard=dashboard).order_by('position')
    })

@user_passes_test(is_superuser)
def configure_widget(request, widget_config_id):
    """Vista para configurar un widget específico"""
    widget_config = get_object_or_404(DashboardWidgetConfig, id=widget_config_id)
    
    if request.method == 'POST':
        form = WidgetConfigForm(request.POST, widget_type=widget_config.widget.widget_type)
        if form.is_valid():
            # Actualizar configuración
            widget_config.configuration = form.cleaned_data
            widget_config.is_visible = form.cleaned_data.get('is_visible', True)
            widget_config.size = form.cleaned_data.get('size', 'medium')
            widget_config.save()
            
            messages.success(request, f"Widget configurado correctamente")
            return redirect('admin:dashboard_companydashboard_change', widget_config.dashboard.id)
    else:
        # Precargar con la configuración actual
        initial = widget_config.configuration.copy()
        initial['is_visible'] = widget_config.is_visible
        initial['size'] = widget_config.size
        form = WidgetConfigForm(initial=initial, widget_type=widget_config.widget.widget_type)
    
    return render(request, 'dashboard/admin/configure_widget.html', {
        'widget_config': widget_config,
        'form': form
    })

# Definir esta función antes de company_dashboard
def organize_departments_hierarchy(departments):
    """
    Organiza los departamentos en una estructura jerárquica
    para mostrarlos correctamente en el sidebar,
    ordenando por nivel de acceso (de mayor a menor)
    """
    # Definir el orden de los niveles de acceso (de mayor a menor)
    access_level_order = {
        'gerencial': 1,
        'admin': 2,
        'programatico': 3,
        'user': 4
    }
    
    # Primero identificamos departamentos raíz (sin padre)
    root_departments = [dept for dept in departments if not dept.parent_department]
    
    # Ordenar los departamentos raíz por nivel de acceso
    root_departments.sort(key=lambda dept: access_level_order.get(dept.access_level, 999))
    
    # Función para construir el árbol de departamentos
    def build_tree(parent):
        tree = {
            'department': parent,
            'children': []
        }
        
        # Encontrar todos los hijos directos
        children = [dept for dept in departments if dept.parent_department and dept.parent_department.id == parent.id]
        
        # Ordenar los hijos por nivel de acceso
        children.sort(key=lambda dept: access_level_order.get(dept.access_level, 999))
        
        # Para cada hijo, construir su subárbol
        for child in children:
            tree['children'].append(build_tree(child))
            
        return tree
    
    # Construir el árbol comenzando por cada departamento raíz
    hierarchy = []
    for root in root_departments:
        hierarchy.append(build_tree(root))
        
    return hierarchy

@login_required
def company_dashboard(request):
    """Dashboard principal para usuarios de compañía"""
    # Verificar que el usuario pertenece a una compañía
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    department = employee.department
    
    # Verificar si la compañía está activa
    if not company.is_active:
        messages.error(request, "Tu compañía está desactivada")
        return redirect('logout')
    
    # Obtener el dashboard
    try:
        dashboard = CompanyDashboard.objects.get(company=company)
    except CompanyDashboard.DoesNotExist:
        messages.warning(request, "No hay dashboard configurado para tu compañía")
        return render(request, 'dashboard/dashboard_empty.html', {'company': company, 'employee': employee})
    
    # Determinar departamentos visibles según nivel de acceso
    visible_departments = []
    if request.user.is_superuser or department.access_level == 'gerencial':
        # Gerencial ve todos los departamentos
        visible_departments = list(Department.objects.filter(company=company))
    elif department.access_level in ['admin', 'programatico']:
        # Administrador y Programático ven su departamento y todos los que están debajo
        visible_departments = department.get_all_child_departments()
    else:
        # Usuarios regulares solo ven su departamento
        visible_departments = [department]
    
    # Organizar departamentos en jerarquía para el sidebar
    departments_hierarchy = organize_departments_hierarchy(visible_departments)

    # Definir el orden de los niveles de acceso (de mayor a menor)
    access_level_order = {
        'gerencial': 1,
        'admin': 2,
        'programatico': 3,
        'user': 4
    }

    # Ordenar los departamentos visibles por nivel de acceso
    visible_departments.sort(key=lambda dept: access_level_order.get(dept.access_level, 999))
    
    # ID de departamento seleccionado (si se proporciona en GET)
    selected_dept_id = request.GET.get('department')
    if selected_dept_id:
        try:
            selected_dept = Department.objects.get(id=selected_dept_id)
            # Verificar que el departamento seleccionado está entre los visibles
            if selected_dept not in visible_departments:
                selected_dept = department  # Volver al departamento del usuario
        except Department.DoesNotExist:
            selected_dept = department
    else:
        selected_dept = department
    
    # Obtener widgets configurados
    widget_configs = dashboard.widgets.filter(is_visible=True).order_by('position')
    
    # Preparar datos para cada widget
    widgets_data = []
    for config in widget_configs:
        # Añadir el departamento seleccionado a la configuración
        config_with_dept = config.configuration.copy() if config.configuration else {}
        config_with_dept['department_id'] = selected_dept.id
        
        # Obtener datos específicos para este widget
        data = get_widget_data(request, config.widget.code_name, config_with_dept)
        
        widgets_data.append({
            'widget': config.widget,
            'config': config,
            'data': data
        })
    
    # Obtener el tema de la compañía
    try:
        company_theme = CompanyTheme.objects.get(company=company)
    except CompanyTheme.DoesNotExist:
        company_theme = None
    
    return render(request, 'dashboard/dashboard.html', {
        'company': company,
        'employee': employee,
        'widgets': widgets_data,
        'visible_departments': visible_departments,
        'departments_hierarchy': departments_hierarchy,
        'selected_department': selected_dept,
        'company_theme': company_theme,
    })

#Función form_manager actualizada
@login_required
@user_passes_test(lambda u: u.is_superuser)
def form_manager(request):
    """Vista para administrar formularios personalizados"""
# Special handling for superusers without employee records
    if request.user.is_superuser and not hasattr(request.user, 'employee'):
        # Get any company for superuser operations, or create one if needed
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(name="Admin Company", slug="admin-company", is_active=True)
            
        # Create dummy stats for the template
        department_stats = []
        available_departments = Department.objects.filter(company=company)
        forms = CustomForm.objects.filter(company=company)
        
        return render(request, 'dashboard/forms/form_manager.html', {
            'forms': forms,
            'company': company,
            'employee': None,  # No employee for superuser
            'available_departments': available_departments,
            'department_filter': None,
            'department_stats': department_stats
        })
    
    # Original code for users with employee records
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    
    # Obtener departamento para filtrar (desde GET)
    department_id = request.GET.get('department')
    department_filter = None
    
    # Obtener departamentos disponibles según el nivel de acceso
    if request.user.is_superuser or employee.department.access_level == 'gerencial':
        available_departments = Department.objects.filter(company=company)
    else:
        available_departments = employee.department.get_all_child_departments()
    
    # Aplicar filtro de departamento si se especifica
    base_forms = CustomForm.objects.filter(company=company)
    
    if department_id:
        try:
            department_filter = Department.objects.get(id=department_id, company=company)
            # Verificar que el departamento esté entre los disponibles para el usuario
            if department_filter in available_departments:
                forms = base_forms.filter(departments=department_filter)
            else:
                forms = base_forms
                department_filter = None
                messages.warning(request, "No tienes acceso a ese departamento")
        except Department.DoesNotExist:
            forms = base_forms
            messages.warning(request, "El departamento seleccionado no existe")
    else:
        forms = base_forms
    
    # Calcular estadísticas de formularios por departamento
    department_stats = []
    for dept in available_departments:
        form_count = base_forms.filter(departments=dept).count()
        department_stats.append({
            'department': dept,
            'form_count': form_count
        })
    
    # Ordenar por cantidad de formularios (mayor a menor)
    department_stats.sort(key=lambda x: x['form_count'], reverse=True)
    
    return render(request, 'dashboard/forms/form_manager.html', {
        'forms': forms,
        'company': company,
        'employee': employee,
        'available_departments': available_departments,
        'department_filter': department_filter,
        'department_stats': department_stats
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_edit_form(request, form_id=None):
    """Vista para crear o editar formularios personalizados"""
   # Special handling for superusers without employee records
    if request.user.is_superuser and not hasattr(request.user, 'employee'):
        # Get any company for superuser operations, or create one if needed
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(name="Admin Company", slug="admin-company", is_active=True)
            
        # Create dummy stats for the template
        department_stats = []
        available_departments = Department.objects.filter(company=company)
        forms = CustomForm.objects.filter(company=company)
        
        return render(request, 'dashboard/forms/form_manager.html', {
            'forms': forms,
            'company': company,
            'employee': None,  # No employee for superuser
            'available_departments': available_departments,
            'department_filter': None,
            'department_stats': department_stats
        })
    
    # Original code for users with employee records
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    
    # Determinar si estamos editando o creando
    if form_id:
        custom_form = get_object_or_404(CustomForm, id=form_id, company=company)
        is_new = False
    else:
        custom_form = CustomForm(company=company)
        is_new = True
    
    if request.method == 'POST':
        # Procesar datos del formulario
        form_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'code_name': request.POST.get('code_name'),
            'is_active': 'is_active' in request.POST
        }
        
        # Validar datos
        errors = {}
        if not form_data['name']:
            errors['name'] = "El nombre es obligatorio"
        
        if not form_data['code_name']:
            errors['code_name'] = "El código identificador es obligatorio"
        elif not is_new and CustomForm.objects.filter(company=company, code_name=form_data['code_name']).exclude(id=custom_form.id).exists():
            errors['code_name'] = "Este código ya está en uso"
        elif is_new and CustomForm.objects.filter(company=company, code_name=form_data['code_name']).exists():
            errors['code_name'] = "Este código ya está en uso"
        
        if not errors:
            # Guardar formulario
            custom_form.name = form_data['name']
            custom_form.description = form_data['description']
            custom_form.code_name = form_data['code_name']
            custom_form.is_active = form_data['is_active']
            if is_new:
                custom_form.company = company
            custom_form.save()
            
            # Guardar departamentos asignados
            selected_departments = request.POST.getlist('departments')
            custom_form.departments.set(selected_departments)
            
            # Procesar grupos de campos
            if 'group_names' in request.POST:
                group_names = request.POST.getlist('group_names')
                group_descriptions = request.POST.getlist('group_descriptions')
                group_orders = request.POST.getlist('group_orders')
                group_is_collapsed = request.POST.getlist('group_is_collapsed')
                group_ids = request.POST.getlist('group_ids')
                
                # Get existing group IDs (excluding temporary ones)
                existing_group_ids = [gid for gid in group_ids if gid and not gid.startswith('new_')]
                
                # Eliminar grupos que no están en el formulario actual
                FormFieldGroup.objects.filter(form=custom_form).exclude(id__in=existing_group_ids).delete()
                
                # Crear o actualizar grupos
                for i in range(len(group_names)):
                    group_id = group_ids[i] if i < len(group_ids) else None
                    
                    # Skip temporary IDs that start with "new_"
                    if group_id and not group_id.startswith('new_'):
                        # Actualizar grupo existente
                        try:
                            group = FormFieldGroup.objects.get(id=group_id)
                            group.name = group_names[i]
                            group.description = group_descriptions[i] if i < len(group_descriptions) else ''
                            group.order = int(group_orders[i]) if i < len(group_orders) and group_orders[i].isdigit() else i
                            group.is_collapsed = 'on' in group_is_collapsed[i] if i < len(group_is_collapsed) else True
                            group.save()
                        except FormFieldGroup.DoesNotExist:
                            # If the group ID doesn't exist, create a new one
                            FormFieldGroup.objects.create(
                                form=custom_form,
                                name=group_names[i],
                                description=group_descriptions[i] if i < len(group_descriptions) else '',
                                order=int(group_orders[i]) if i < len(group_orders) and group_orders[i].isdigit() else i,
                                is_collapsed='on' in group_is_collapsed[i] if i < len(group_is_collapsed) else True
                            )
                    else:
                        # Create new group (for new groups and when group_id is empty)
                        FormFieldGroup.objects.create(
                            form=custom_form,
                            name=group_names[i],
                            description=group_descriptions[i] if i < len(group_descriptions) else '',
                            order=int(group_orders[i]) if i < len(group_orders) and group_orders[i].isdigit() else i,
                            is_collapsed='on' in group_is_collapsed[i] if i < len(group_is_collapsed) else True
                        )
            
            # Procesar campos del formulario
            if 'field_names' in request.POST:
                field_names = request.POST.getlist('field_names')
                field_types = request.POST.getlist('field_types')
                field_labels = request.POST.getlist('field_labels')
                field_required = request.POST.getlist('field_required')
                field_placeholders = request.POST.getlist('field_placeholders')
                field_help_texts = request.POST.getlist('field_help_texts')
                field_orders = request.POST.getlist('field_orders')
                field_defaults = request.POST.getlist('field_defaults')
                field_options = request.POST.getlist('field_options')
                field_ids = request.POST.getlist('field_ids')
                field_groups = request.POST.getlist('field_groups')
                
                # Get existing field IDs (excluding temporary ones)
                existing_field_ids = [fid for fid in field_ids if fid and not fid.startswith('new_')]
                
                # Eliminar campos que no están en el formulario actual
                FormField.objects.filter(form=custom_form).exclude(id__in=existing_field_ids).delete()
                
                # Crear o actualizar campos
                for i in range(len(field_names)):
                    field_id = field_ids[i] if i < len(field_ids) else None
                    
                    # Obtener grupo si se especifica
                    group = None
                    if i < len(field_groups) and field_groups[i]:
                        # Solo procesar grupo si no es un ID temporal
                        if not field_groups[i].startswith('new_'):
                            try:
                                group = FormFieldGroup.objects.get(id=field_groups[i])
                            except FormFieldGroup.DoesNotExist:
                                pass
                    
                    # Convertir opciones de string a JSON si es necesario
                    options_json = None
                    if i < len(field_options) and field_options[i]:
                        try:
                            options_list = [opt.strip() for opt in field_options[i].split(',')]
                            options_json = {str(j): opt for j, opt in enumerate(options_list)}
                        except:
                            options_json = {}
                    
                    # Skip temporary IDs that start with "new_"
                    if field_id and not field_id.startswith('new_'):
                        # Actualizar campo existente
                        try:
                            field = FormField.objects.get(id=field_id)
                            field.name = field_names[i]
                            field.field_type = field_types[i]
                            field.label = field_labels[i]
                            field.required = 'on' in field_required[i] if i < len(field_required) else False
                            field.placeholder = field_placeholders[i] if i < len(field_placeholders) else ''
                            field.help_text = field_help_texts[i] if i < len(field_help_texts) else ''
                            field.order = int(field_orders[i]) if i < len(field_orders) and field_orders[i].isdigit() else i
                            field.default_value = field_defaults[i] if i < len(field_defaults) else ''
                            field.options = options_json
                            field.group = group
                            field.save()
                        except FormField.DoesNotExist:
                            # If the field doesn't exist, create a new one
                            FormField.objects.create(
                                form=custom_form,
                                name=field_names[i],
                                field_type=field_types[i],
                                label=field_labels[i],
                                required='on' in field_required[i] if i < len(field_required) else False,
                                placeholder=field_placeholders[i] if i < len(field_placeholders) else '',
                                help_text=field_help_texts[i] if i < len(field_help_texts) else '',
                                order=int(field_orders[i]) if i < len(field_orders) and field_orders[i].isdigit() else i,
                                default_value=field_defaults[i] if i < len(field_defaults) else '',
                                options=options_json,
                                group=group
                            )
                    else:
                        # Create new field
                        FormField.objects.create(
                            form=custom_form,
                            name=field_names[i],
                            field_type=field_types[i],
                            label=field_labels[i],
                            required='on' in field_required[i] if i < len(field_required) else False,
                            placeholder=field_placeholders[i] if i < len(field_placeholders) else '',
                            help_text=field_help_texts[i] if i < len(field_help_texts) else '',
                            order=int(field_orders[i]) if i < len(field_orders) and field_orders[i].isdigit() else i,
                            default_value=field_defaults[i] if i < len(field_defaults) else '',
                            options=options_json,
                            group=group
                        )
            
            messages.success(request, f"Formulario '{custom_form.name}' guardado correctamente")
            return redirect('form_manager')
        else:
            # Mostrar errores
            for field, error in errors.items():
                messages.error(request, error)
    
    # Obtener departamentos para asignar
    if request.user.is_superuser or employee.department.access_level == 'gerencial':
        available_departments = Department.objects.filter(company=company)
    else:
        available_departments = employee.department.get_all_child_departments()
    
    return render(request, 'dashboard/forms/create_edit_form.html', {
        'custom_form': custom_form,
        'is_new': is_new,
        'company': company,
        'employee': employee,
        'available_departments': available_departments,
        'selected_departments': custom_form.departments.all() if not is_new else [],
        'field_groups': custom_form.field_groups.all() if not is_new else []
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_form(request, form_id):
    """Vista para eliminar un formulario personalizado"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    
    custom_form = get_object_or_404(CustomForm, id=form_id, company=company)
    
    if request.method == 'POST':
        form_name = custom_form.name
        custom_form.delete()
        messages.success(request, f"Formulario '{form_name}' eliminado correctamente")
        return redirect('form_manager')
    
    return render(request, 'dashboard/forms/delete_form_confirm.html', {
        'custom_form': custom_form,
        'company': company,
        'employee': employee
    })

# dashboard/views.py - Actualizar la función fill_form

@login_required
def fill_form(request, form_code):
    """Vista para completar un formulario personalizado"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    department = employee.department
    
    # Verificar si la compañía está activa
    if not company.is_active:
        messages.error(request, "Tu compañía está desactivada")
        return redirect('logout')
    
    # Obtener el formulario personalizado
    try:
        custom_form = CustomForm.objects.get(company=company, code_name=form_code, is_active=True)
    except CustomForm.DoesNotExist:
        messages.error(request, "El formulario solicitado no existe o no está activo")
        return redirect('company_dashboard')
    
    # Verificar si el usuario tiene acceso a este formulario
    if not custom_form.departments.filter(id=department.id).exists():
        # Verificar si el usuario tiene acceso a través de su nivel de acceso
        has_access = False
        if request.user.is_superuser or department.access_level == 'gerencial':
            has_access = True
        elif department.access_level in ['admin', 'programatico']:
            # Comprobar si alguno de sus departamentos subordinados tiene acceso
            subordinate_depts = department.get_all_child_departments()
            if custom_form.departments.filter(id__in=[d.id for d in subordinate_depts]).exists():
                has_access = True
        
        if not has_access:
            messages.error(request, "No tienes acceso a este formulario")
            return redirect('company_dashboard')
    
    # Determinar departamentos visibles según nivel de acceso
    visible_departments = []
    if request.user.is_superuser or department.access_level == 'gerencial':
        # Gerencial ve todos los departamentos que tienen acceso al formulario
        visible_departments = list(custom_form.departments.all())
    elif department.access_level in ['admin', 'programatico']:
        # Admin y Programático ven sus departamentos subordinados que tienen acceso al formulario
        subordinate_depts = department.get_all_child_departments()
        visible_departments = [dept for dept in subordinate_depts if custom_form.departments.filter(id=dept.id).exists()]
    else:
        # Usuarios regulares solo ven su departamento si tiene acceso
        if custom_form.departments.filter(id=department.id).exists():
            visible_departments = [department]
    
    # Obtener departamento seleccionado de GET o usar el del usuario
    selected_dept_id = request.GET.get('department')
    if selected_dept_id:
        try:
            selected_dept = Department.objects.get(id=selected_dept_id)
            # Verificar que el departamento seleccionado está entre los visibles
            if selected_dept not in visible_departments:
                selected_dept = department  # Volver al departamento del usuario
        except Department.DoesNotExist:
            selected_dept = department
    else:
        selected_dept = department if department in visible_departments else (visible_departments[0] if visible_departments else None)
    
    # Si no hay departamentos visibles, mostrar error
    if not visible_departments:
        messages.error(request, "No hay departamentos con acceso a este formulario")
        return redirect('company_dashboard')
    
    # Procesar envío del formulario
    if request.method == 'POST':
        # Validar el formulario
        form_fields = custom_form.fields.all()
        form_data = {}
        errors = {}
        
        for field in form_fields:
            field_value = request.POST.get(f'field_{field.id}', '')
            
            # Validar campos requeridos
            if field.required and not field_value:
                errors[field.id] = f"El campo '{field.label}' es obligatorio"
            
            # Validar tipos de datos
            if field_value:
                if field.field_type == 'number':
                    try:
                        field_value = int(field_value)
                    except ValueError:
                        errors[field.id] = f"El campo '{field.label}' debe ser un número entero"
                
                elif field.field_type == 'decimal':
                    try:
                        field_value = float(field_value)
                    except ValueError:
                        errors[field.id] = f"El campo '{field.label}' debe ser un número decimal"
            
            # Añadir al diccionario de datos
            form_data[field.name] = field_value
        
        # Si no hay errores, guardar los datos
        if not errors:
            # Obtener el departamento seleccionado del formulario
            dept_id = request.POST.get('department')
            try:
                form_department = Department.objects.get(id=dept_id)
                # Verificar que el departamento está entre los visibles
                if form_department not in visible_departments:
                    messages.error(request, "Departamento no válido")
                    return redirect(request.path)
            except:
                form_department = selected_dept
            
            # Crear el registro de datos
            FormData.objects.create(
                form=custom_form,
                department=form_department,
                company=company,
                created_by=employee,
                data=form_data
            )
            
            messages.success(request, "Datos guardados correctamente")
            return redirect(request.path + f'?department={form_department.id}')
        else:
            # Mostrar errores
            for field_id, error in errors.items():
                messages.error(request, error)
    
    # Obtener registros recientes para este formulario y departamento
    recent_records = FormData.objects.filter(
        form=custom_form,
        department=selected_dept
    ).order_by('-date_created')[:10]
    
    # Obtener grupos de campos para este formulario
    field_groups = custom_form.field_groups.all().order_by('order')
    
    return render(request, 'dashboard/forms/fill_form.html', {
        'custom_form': custom_form,
        'form_fields': custom_form.fields.all().order_by('group__order', 'group', 'order'),
        'field_groups': field_groups,
        'company': company,
        'employee': employee,
        'visible_departments': visible_departments,
        'selected_department': selected_dept,
        'recent_records': recent_records
    })

@login_required
def view_form_data(request, form_code):
    """Vista para ver los datos enviados de un formulario"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    department = employee.department
    
    # Verificar si la compañía está activa
    if not company.is_active:
        messages.error(request, "Tu compañía está desactivada")
        return redirect('logout')
    
    # Obtener el formulario personalizado
    try:
        custom_form = CustomForm.objects.get(company=company, code_name=form_code, is_active=True)
    except CustomForm.DoesNotExist:
        messages.error(request, "El formulario solicitado no existe o no está activo")
        return redirect('company_dashboard')
    
    # Determinar departamentos visibles según nivel de acceso
    visible_departments = []
    if request.user.is_superuser or department.access_level == 'gerencial':
        # Gerencial ve todos los departamentos
        visible_departments = list(Department.objects.filter(company=company))
    elif department.access_level in ['admin', 'programatico']:
        # Admin y Programático ven sus departamentos subordinados
        visible_departments = department.get_all_child_departments()
    else:
        # Usuarios regulares solo ven su departamento
        visible_departments = [department]
    
    # Filtrar solo los departamentos que tienen datos para este formulario
    departments_with_data = Department.objects.filter(
        id__in=FormData.objects.filter(form=custom_form).values_list('department', flat=True)
    )
    visible_departments = [dept for dept in visible_departments if dept in departments_with_data]
    
    # Obtener departamento seleccionado de GET o usar el del usuario
    selected_dept_id = request.GET.get('department')
    if selected_dept_id:
        try:
            selected_dept = Department.objects.get(id=selected_dept_id)
            # Verificar que el departamento seleccionado está entre los visibles
            if selected_dept not in visible_departments:
                selected_dept = department  # Volver al departamento del usuario
        except Department.DoesNotExist:
            selected_dept = department
    else:
        selected_dept = department if department in visible_departments else (visible_departments[0] if visible_departments else None)
    
    # Si no hay departamentos visibles con datos, mostrar mensaje
    if not visible_departments:
        messages.warning(request, "No hay datos para este formulario")
        
    # Configurar filtros de fecha
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    date_filter = {}
    if start_date:
        try:
            date_filter['date_created__gte'] = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        except:
            pass
    
    if end_date:
        try:
            # Añadir un día para incluir todo el día final
            end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date_obj = end_date_obj + datetime.timedelta(days=1)
            date_filter['date_created__lt'] = end_date_obj
        except:
            pass
    
    # Obtener datos para el departamento seleccionado
    if selected_dept:
        records = FormData.objects.filter(
            form=custom_form,
            department=selected_dept,
            **date_filter
        ).order_by('-date_created')
    else:
        records = FormData.objects.none()
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(records, 25)  # 25 registros por página
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/forms/view_form_data.html', {
        'custom_form': custom_form,
        'form_fields': custom_form.fields.all().order_by('order'),
        'company': company,
        'employee': employee,
        'visible_departments': visible_departments,
        'selected_department': selected_dept,
        'records': page_obj,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def list_available_forms(request):
    """Lista todos los formularios disponibles para el usuario"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    department = employee.department
    
    # Determinar formularios visibles según nivel de acceso
    if request.user.is_superuser or department.access_level == 'gerencial':
        # Gerencial ve todos los formularios activos de la compañía
        forms = CustomForm.objects.filter(company=company, is_active=True)
    elif department.access_level in ['admin', 'programatico']:
        # Admin y Programático ven formularios de sus departamentos subordinados
        subordinate_depts = department.get_all_child_departments()
        forms = CustomForm.objects.filter(
            company=company, 
            is_active=True,
            departments__in=subordinate_depts
        ).distinct()
    else:
        # Usuarios regulares solo ven formularios de su departamento
        forms = CustomForm.objects.filter(
            company=company,
            is_active=True,
            departments=department
        )
    
    return render(request, 'dashboard/forms/list_forms.html', {
        'forms': forms,
        'company': company,
        'employee': employee
    })

# dashboard/views.py - Añadir al final

@login_required
@user_passes_test(lambda u: u.is_superuser)
def company_theme(request):
    """Vista para personalizar el tema de la compañía"""
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Tu usuario no está asociado a ninguna compañía")
        return redirect('logout')
    
    employee = request.user.employee
    company = employee.company
    
    # Obtener o crear el tema de la compañía
    theme, created = CompanyTheme.objects.get_or_create(company=company)
    
    if request.method == 'POST':
        # Actualizar configuración del tema
        theme.primary_color = request.POST.get('primary_color', theme.primary_color)
        theme.secondary_color = request.POST.get('secondary_color', theme.secondary_color)
        theme.accent_color = request.POST.get('accent_color', theme.accent_color)
        theme.text_color = request.POST.get('text_color', theme.text_color)
        theme.light_text_color = request.POST.get('light_text_color', theme.light_text_color)
        theme.font_family = request.POST.get('font_family', theme.font_family)
        theme.custom_css = request.POST.get('custom_css', theme.custom_css)
        theme.custom_js = request.POST.get('custom_js', theme.custom_js)
        theme.enabled = 'enabled' in request.POST
        
        # Procesar archivos subidos
        if 'logo' in request.FILES:
            theme.logo = request.FILES['logo']
        
        if 'logo_small' in request.FILES:
            theme.logo_small = request.FILES['logo_small']
        
        if 'background_image' in request.FILES:
            theme.background_image = request.FILES['background_image']
        
        # Manejar eliminación de archivos
        if 'remove_logo' in request.POST:
            theme.logo = None
        
        if 'remove_logo_small' in request.POST:
            theme.logo_small = None
        
        if 'remove_background' in request.POST:
            theme.background_image = None
        
        theme.save()
        messages.success(request, "Tema actualizado correctamente")
        return redirect('company_theme')
    
    # Obtener fuentes disponibles de Google Fonts (las más comunes)
    google_fonts = [
        ("'Montserrat', sans-serif", "Montserrat"),
        ("'Open Sans', sans-serif", "Open Sans"),
        ("'Roboto', sans-serif", "Roboto"),
        ("'Lato', sans-serif", "Lato"),
        ("'Poppins', sans-serif", "Poppins"),
        ("'Raleway', sans-serif", "Raleway"),
        ("'Ubuntu', sans-serif", "Ubuntu"),
        ("'Nunito', sans-serif", "Nunito"),
    ]
    
    return render(request, 'dashboard/settings/company_theme.html', {
        'company': company,
        'employee': employee,
        'theme': theme,
        'google_fonts': google_fonts
    })

def theme_context_processor(request):
    """Procesador de contexto para incluir el tema de la compañía en todas las plantillas"""
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'employee'):
        company = request.user.employee.company
        
        try:
            # Obtener el tema de la compañía si existe
            theme = CompanyTheme.objects.get(company=company)
            context['company_theme'] = theme
        except CompanyTheme.DoesNotExist:
            pass
    
    return context

# dashboard/views.py - Añadir vista para dashboard de administrador

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """Dashboard exclusivo para superusuarios con estadísticas y gestión global"""
    
    # Estadísticas generales
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()
    total_employees = Employee.objects.count()
    total_forms = CustomForm.objects.count()
    total_form_submissions = FormData.objects.count()
    
    # Compañías más recientes
    recent_companies = Company.objects.order_by('-created_at')[:5]
    
    # Formularios más utilizados (con más envíos)
    popular_forms = CustomForm.objects.annotate(
        submissions_count=models.Count('submissions')
    ).order_by('-submissions_count')[:5]
    
    # Compañías con más empleados
    companies_by_employees = Company.objects.annotate(
        employees_count=models.Count('employees')
    ).order_by('-employees_count')[:5]
    
    # Actividad reciente (últimos envíos de formularios)
    recent_activity = FormData.objects.select_related(
        'company', 'department', 'form', 'created_by'
    ).order_by('-date_created')[:10]
    
    return render(request, 'dashboard/admin/admin_dashboard.html', {
        'total_companies': total_companies,
        'active_companies': active_companies,
        'total_departments': total_departments,
        'total_employees': total_employees,
        'total_forms': total_forms,
        'total_form_submissions': total_form_submissions,
        'recent_companies': recent_companies,
        'popular_forms': popular_forms,
        'companies_by_employees': companies_by_employees,
        'recent_activity': recent_activity
    })