# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from autenticacion.models import Company, Department
from .models import DashboardWidget, CompanyDashboard, DashboardWidgetConfig
from .widgets import get_widget_data
from .forms import DashboardConfigForm, WidgetConfigForm

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
        return render(request, 'dashboard/dashboard_empty.html', {'company': company})
    
    # Determinar departamentos visibles según nivel de acceso
    visible_departments = []
    if request.user.is_superuser or department.access_level == 'admin':
        # Administradores ven todos los departamentos
        visible_departments = list(Department.objects.filter(company=company))
    elif department.access_level == 'manager':
        # Gerentes ven su departamento y todos los que están debajo
        visible_departments = department.get_all_child_departments()
    else:
        # Usuarios regulares solo ven su departamento
        visible_departments = [department]
    
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
    
    return render(request, 'dashboard/dashboard.html', {
        'company': company,
        'employee': employee,
        'widgets': widgets_data,
        'visible_departments': visible_departments,
        'selected_department': selected_dept
    })