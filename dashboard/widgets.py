# dashboard/widgets.py
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay, TruncMonth
from autenticacion.models import Employee, Department
from .models import SalesData
import datetime

def get_widget_data(request, widget_code, config):
    """Obtiene datos específicos para un widget"""
    if not hasattr(request.user, 'employee'):
        return {'error': 'Usuario no asociado a empleado'}
    
    employee = request.user.employee
    company = employee.company
    
    # Obtener departamento seleccionado
    department_id = config.get('department_id')
    if department_id:
        try:
            department = Department.objects.get(id=department_id)
            # Verificar acceso al departamento
            user_dept = employee.department
            has_access = False
            
            if request.user.is_superuser or user_dept.access_level == 'admin':
                has_access = True
            elif user_dept.access_level == 'manager':
                child_depts = user_dept.get_all_child_departments()
                has_access = department in child_depts
            else:
                has_access = user_dept.id == department.id
                
            if not has_access:
                department = user_dept
                
        except Department.DoesNotExist:
            department = employee.department
    else:
        department = employee.department
    
    # Resto de tu código para resolvedores de widgets
    resolvers = {
        'sales_summary': get_sales_summary,
        'employee_count': get_employee_count,
        'department_distribution': get_department_distribution,
        'recent_sales': get_recent_sales,
        # Añade un nuevo resolvedor para el resumen de departamentos
        'departments_summary': get_departments_summary,
        # ... otros resolvedores
    }
    
    if widget_code in resolvers:
        return resolvers[widget_code](company, department, config)
    
    return {"error": f"Widget {widget_code} no implementado"}

def get_departments_summary(company, department, config):
    """Widget para mostrar resumen de todos los departamentos accesibles"""
    from django.db.models import Sum, Count
    from autenticacion.models import Employee
    try:
        # Determinar departamentos a incluir
        if department.access_level in ['admin', 'manager'] or request.user.is_superuser:
            if department.access_level == 'admin' or request.user.is_superuser:
                departments = Department.objects.filter(company=company)
            else:
                departments = department.get_all_child_departments()
            
            # Recopilar datos resumidos para cada departamento
            summary_data = []
            for dept in departments:
                # Contar empleados
                employee_count = Employee.objects.filter(department=dept).count()
                
                # Aquí puedes añadir cualquier otro dato específico del departamento
                # Por ejemplo, ventas del mes actual (si tienes un modelo SalesData)
                # sales = SalesData.objects.filter(...).aggregate(...)
                
                summary_data.append({
                    'id': dept.id,
                    'name': dept.name,
                    'level': dict(dept._meta.get_field('access_level').choices).get(dept.access_level),
                    'employees': employee_count,
                    # Otros datos que quieras incluir
                })
            
            return {
                'departments': summary_data
            }
        
        return {"error": "No tienes permisos para ver este resumen"}
    except Exception as e:
        return {"error": f"Error al generar resumen: {str(e)}"}

def get_sales_summary(company, employee, config):
    """Datos para gráfico de ventas"""
    # Obtener período desde configuración
    period = config.get('period', 'month')
    now = datetime.datetime.now()
    
    # Definir fechas según período
    if period == 'week':
        start_date = now - datetime.timedelta(days=7)
        trunc_func = TruncDay
        date_format = '%d/%m'
    elif period == 'month':
        start_date = now - datetime.timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d/%m'
    elif period == 'year':
        start_date = now - datetime.timedelta(days=365)
        trunc_func = TruncMonth
        date_format = '%m/%Y'
    else:
        start_date = now - datetime.timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d/%m'
    
    # Consulta de ventas agrupadas por fecha
    sales = SalesData.objects.filter(
        date__gte=start_date.date(),
        date__lte=now.date()
    )
    
    sales_by_date = sales.annotate(
        truncated_date=trunc_func('date')
    ).values('truncated_date').annotate(
        total=Sum('amount'),
        units=Sum('units')
    ).order_by('truncated_date')
    
    # Formato para chart.js
    return {
        'labels': [item['truncated_date'].strftime(date_format) for item in sales_by_date],
        'datasets': [
            {
                'label': 'Ventas',
                'data': [float(item['total']) for item in sales_by_date],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Unidades',
                'data': [item['units'] for item in sales_by_date],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }
        ]
    }

def get_employee_count(company, employee, config):
    """Datos para KPI de conteo de empleados"""
    count = Employee.objects.filter(company=company).count()
    return {
        'count': count,
        'title': 'Total Empleados',
        'icon': 'fa-users'
    }

def get_department_distribution(company, employee, config):
    """Datos para gráfico de distribución por departamento"""
    departments = Department.objects.filter(company=company)
    
    data = []
    for dept in departments:
        count = Employee.objects.filter(department=dept).count()
        data.append({
            'name': dept.name,
            'count': count
        })
    
    # Ordenar por cantidad
    data.sort(key=lambda x: x['count'], reverse=True)
    
    # Formato para gráfico
    return {
        'labels': [item['name'] for item in data],
        'datasets': [{
            'data': [item['count'] for item in data],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
            ]
        }]
    }

def get_recent_sales(company, employee, config):
    """Datos para tabla de ventas recientes"""
    limit = config.get('limit', 5)
    
    recent_sales = SalesData.objects.order_by('-date')[:limit]
    
    return {
        'columns': ['Fecha', 'Producto', 'Cantidad', 'Monto'],
        'data': [
            [
                sale.date.strftime('%d/%m/%Y'),
                sale.product,
                sale.units,
                f"${sale.amount}"
            ]
            for sale in recent_sales
        ]
    }