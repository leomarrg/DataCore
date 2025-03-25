# dashboard/models.py
from django.db import models
from autenticacion.models import Company, Department, Employee
from DataCore.middleware import get_current_company

class CompanyModel(models.Model):
    """Modelo base para todos los modelos específicos de compañía"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class CompanyManager(models.Manager):
    """Manager que filtra automáticamente por la compañía actual"""
    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_current_company()
        
        if company:
            queryset = queryset.filter(company=company)
        
        return queryset

# Configuración de dashboard
class DashboardWidget(models.Model):
    """Define los tipos de widgets disponibles"""
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=50, choices=[
        ('chart', 'Gráfico'),
        ('table', 'Tabla'),
        ('kpi', 'Indicador KPI'),
        ('list', 'Lista')
    ])
    code_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class CompanyDashboard(models.Model):
    """Dashboard principal de una compañía"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dashboard de {self.company.name}"

class DashboardWidgetConfig(models.Model):
    """Configuración de un widget para un dashboard específico"""
    dashboard = models.ForeignKey(CompanyDashboard, on_delete=models.CASCADE, related_name="widgets")
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    position = models.IntegerField()
    size = models.CharField(max_length=20, choices=[
        ('small', 'Pequeño'),
        ('medium', 'Mediano'),
        ('large', 'Grande')
    ])
    is_visible = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.widget.name} - {self.dashboard.company.name}"

# Ejemplo de modelo específico con filtrado automático por compañía
class SalesData(CompanyModel):
    date = models.DateField()
    product = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    units = models.IntegerField()
    
    # Manager filtrado por compañía
    objects = CompanyManager()
    # Manager sin filtrar para uso administrativo
    all_objects = models.Manager()
    
    def __str__(self):
        return f"{self.product} - {self.date}"