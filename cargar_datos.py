# cargar_datos.py
import os
import django
import random
from datetime import date, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')
django.setup()

from django.contrib.auth.models import User
from autenticacion.models import Company, Department, Employee
from dashboard.models import DashboardWidget, CompanyDashboard, DashboardWidgetConfig, SalesData

# Crear widgets predefinidos
widgets = [
    {'name': 'Resumen de Ventas', 'widget_type': 'chart', 'code_name': 'sales_summary'},
    {'name': 'Total de Empleados', 'widget_type': 'kpi', 'code_name': 'employee_count'},
    {'name': 'Distribución por Departamento', 'widget_type': 'chart', 'code_name': 'department_distribution'},
    {'name': 'Ventas Recientes', 'widget_type': 'table', 'code_name': 'recent_sales'},
]

for widget in widgets:
    DashboardWidget.objects.get_or_create(
        code_name=widget['code_name'],
        defaults={'name': widget['name'], 'widget_type': widget['widget_type']}
    )

# Crear datos ficticios para compañía de prueba
if not Company.objects.filter(slug='empresa-ejemplo').exists():
    # Crear compañía
    company = Company.objects.create(
        name='Empresa Ejemplo',
        slug='empresa-ejemplo',
        is_active=True
    )
    
    # Crear departamentos
    dept_admin = Department.objects.create(company=company, name='Administración', access_level='admin')
    dept_ventas = Department.objects.create(company=company, name='Ventas', access_level='user')
    dept_it = Department.objects.create(company=company, name='IT', access_level='manager')
    
    # Crear usuarios y empleados
    admin_user = User.objects.create_user('admin_empresa', 'admin@ejemplo.com', 'password123', 
                                         first_name='Admin', last_name='Ejemplo')
    Employee.objects.create(user=admin_user, company=company, department=dept_admin, job_title='Director Administrativo')
    
    ventas_user = User.objects.create_user('vendedor', 'ventas@ejemplo.com', 'password123',
                                          first_name='Vendedor', last_name='Ejemplo')
    Employee.objects.create(user=ventas_user, company=company, department=dept_ventas, job_title='Ejecutivo de Ventas')
    
    it_user = User.objects.create_user('soporte', 'soporte@ejemplo.com', 'password123',
                                      first_name='Soporte', last_name='Técnico')
    Employee.objects.create(user=it_user, company=company, department=dept_it, job_title='Técnico de Soporte')
    
    # Crear dashboard
    dashboard = CompanyDashboard.objects.create(company=company)
    
    # Asignar widgets al dashboard
    for i, widget in enumerate(DashboardWidget.objects.all()):
        DashboardWidgetConfig.objects.create(
            dashboard=dashboard,
            widget=widget,
            position=i,
            size='medium',
            is_visible=True,
            configuration={}
        )
    
    # Crear datos de ventas ficticios
    products = ['Producto A', 'Producto B', 'Producto C', 'Producto D']
    
    # Generar datos para los últimos 60 días
    today = date.today()
    for i in range(60):
        day = today - timedelta(days=i)
        # Entre 1 y 5 ventas por día
        for _ in range(random.randint(1, 5)):
            SalesData.objects.create(
                company=company,
                date=day,
                product=random.choice(products),
                amount=random.uniform(100, 1000),
                units=random.randint(1, 10)
            )
    
    print('Datos de ejemplo creados correctamente')
else:
    print('Los datos de ejemplo ya existen')