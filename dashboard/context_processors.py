# Ubicación: dashboard/context_processors.py
from .models import CustomForm

def available_forms(request):
    """Añade los formularios disponibles al contexto de las plantillas."""
    if not request.user.is_authenticated or not hasattr(request.user, 'employee'):
        return {'available_forms': []}
    
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
    
    return {'available_forms': forms}