# autenticacion/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from .forms import EmployeeAdminForm
from django.urls import reverse
from django.utils.html import format_html
from .models import Company, Department, Employee
from django.shortcuts import redirect
from django.contrib import messages

class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'department_count', 'employee_count', 'actions_buttons']
    search_fields = ['name', 'slug']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DepartmentInline]
    
    def department_count(self, obj):
        return obj.departments.count()
    department_count.short_description = "Departamentos"
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = "Empleados"
    
    def actions_buttons(self, obj):
        setup_url = reverse('setup_company_dashboard', args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Configurar Dashboard</a>',
            setup_url
        )
    actions_buttons.short_description = "Acciones"
    
    def response_add(self, request, obj, post_url_continue=None):
        if '_addanother' not in request.POST:
            url = reverse('setup_company_dashboard', args=[obj.id])
            return redirect(url)
        return super().response_add(request, obj, post_url_continue)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'access_level', 'employee_count', 'actions_buttons']
    list_filter = ['company', 'access_level']
    search_fields = ['name', 'company__name']
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = "Empleados"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar el campo de departamento padre para mostrar solo departamentos de la misma compañía
        if db_field.name == "parent_department":
            company_id = request.GET.get('company')
            if company_id:
                kwargs["queryset"] = Department.objects.filter(company_id=company_id)
            elif getattr(self, 'obj', None):
                kwargs["queryset"] = Department.objects.filter(company=self.obj.company)
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def actions_buttons(self, obj):
        add_url = reverse('admin:autenticacion_employee_add') + f'?department={obj.id}&company={obj.company.id}'
        return format_html(
            '<a class="button" href="{}">Agregar Empleado</a>',
            add_url
        )
    actions_buttons.short_description = "Acciones"

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ['user', 'get_full_name', 'company', 'department', 'job_title']
    list_filter = ['company', 'department']
    search_fields = ['user__username', 'user__email', 'job_title', 'user__first_name', 'user__last_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = "Nombre Completo"
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario según parámetros GET"""
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Si es una creación nueva
            # Pre-llenar compañía y departamento desde GET
            company_id = request.GET.get('company')
            department_id = request.GET.get('department')
            
            if company_id:
                form.base_fields['company'].initial = company_id
                # Filtrar departamentos por compañía
                if 'department' in form.base_fields and company_id:
                    form.base_fields['department'].queryset = Department.objects.filter(company_id=company_id)
            
            if department_id:
                form.base_fields['department'].initial = department_id
        
        return form
    
    def save_model(self, request, obj, form, change):
        try:
            if not change:  # Si es una creación nueva
                # Verificar si se seleccionó un usuario existente
                existing_user = form.cleaned_data.get('existing_user')
                
                if existing_user:
                    # Usar el usuario existente
                    obj.user = existing_user
                    messages.info(request, f"Se asoció el empleado al usuario existente '{existing_user.username}'")
                else:
                    # Obtener datos del formulario
                    username = form.cleaned_data.get('username')
                    email = form.cleaned_data.get('email')
                    password = form.cleaned_data.get('password')
                    first_name = form.cleaned_data.get('first_name')
                    last_name = form.cleaned_data.get('last_name')
                    
                    # Si no hay username, usar email o generar uno
                    if not username:
                        if email:
                            base_username = email.split('@')[0]
                            username = base_username
                            # Verificar si el username generado ya existe y crear uno único
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{base_username}_{counter}"
                                counter += 1
                        else:
                            import time
                            username = f"user_{int(time.time())}"
                    
                    # Verificar si el username ya existe
                    if User.objects.filter(username=username).exists():
                        # Generar un nombre único
                        base_username = username
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{base_username}_{counter}"
                            counter += 1
                        
                        messages.warning(request, f"El nombre de usuario ya existía. Se generó automáticamente '{username}'")
                    
                    # Contraseña por defecto si no se proporciona
                    if not password:
                        password = 'changeme123'
                        messages.info(request, "Se ha creado el usuario con una contraseña por defecto. Recomiende al usuario cambiarla.")
                    
                    # Crear el usuario
                    user = User.objects.create_user(
                        username=username,
                        email=email or '',
                        password=password,
                        first_name=first_name or '',
                        last_name=last_name or ''
                    )
                    obj.user = user
                    messages.success(request, f"Se ha creado el usuario '{username}' y asociado al empleado.")
            
            super().save_model(request, obj, form, change)
            
        except Exception as e:
            messages.error(request, f"Error al guardar el empleado: {str(e)}")
            # Re-lanzar la excepción si es necesario
            raise