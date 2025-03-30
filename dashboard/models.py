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
    
class CustomForm(CompanyModel):
    """Definición de formulario personalizado para cada compañía"""
    name = models.CharField(max_length=100, verbose_name="Nombre del formulario")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    code_name = models.SlugField(max_length=100, verbose_name="Código identificador")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    departments = models.ManyToManyField(Department, related_name="custom_forms", verbose_name="Departamentos")
    
    # Manager específico para filtrar por compañía
    objects = CompanyManager()
    
    class Meta:
        verbose_name = "Formulario personalizado"
        verbose_name_plural = "Formularios personalizados"
        unique_together = ('company', 'code_name')
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"
    
class FormFieldGroup(models.Model):
    """Grupo para agrupar campos relacionados en un formulario"""
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name="field_groups")
    name = models.CharField(max_length=100, verbose_name="Nombre del grupo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_collapsed = models.BooleanField(default=True, verbose_name="Mostrar colapsado por defecto")
    
    class Meta:
        verbose_name = "Grupo de campos"
        verbose_name_plural = "Grupos de campos"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} ({self.form.name})"

class FormField(models.Model):
    """Campo de un formulario personalizado"""
    FIELD_TYPES = [
        ('text', 'Texto'),
        ('textarea', 'Área de texto'),
        ('number', 'Número'),
        ('decimal', 'Decimal'),
        ('date', 'Fecha'),
        ('select', 'Selección'),
        ('checkbox', 'Casilla de verificación'),
        ('radio', 'Opciones')
    ]
    
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name="fields")
    group = models.ForeignKey(FormFieldGroup, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name="fields", verbose_name="Grupo de campos")
    name = models.CharField(max_length=100, verbose_name="Nombre del campo")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, verbose_name="Tipo de campo")
    label = models.CharField(max_length=100, verbose_name="Etiqueta")
    placeholder = models.CharField(max_length=200, blank=True, null=True, verbose_name="Texto de ayuda")
    help_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Texto de ayuda")
    required = models.BooleanField(default=True, verbose_name="Obligatorio")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    default_value = models.CharField(max_length=255, blank=True, null=True, verbose_name="Valor predeterminado")
    options = models.JSONField(blank=True, null=True, verbose_name="Opciones (para select, radio)")
    
    class Meta:
        verbose_name = "Campo de formulario"
        verbose_name_plural = "Campos de formulario"
        ordering = ['group__order', 'group', 'order']
    
    def __str__(self):
        return f"{self.label} ({self.field_type})"

class FormData(CompanyModel):
    """Datos enviados a través de formularios personalizados"""
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name="submissions")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="form_submissions")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="+")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    data = models.JSONField(verbose_name="Datos del formulario")
    
    # Manager específico para filtrar por compañía
    objects = CompanyManager()
    
    class Meta:
        verbose_name = "Datos de formulario"
        verbose_name_plural = "Datos de formularios"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Datos de {self.form.name} - {self.date_created.strftime('%d/%m/%Y %H:%M')}"

# dashboard/models.py - Añadir al final del archivo

class CompanyTheme(models.Model):
    """Almacena estilos personalizados y configuraciones para cada compañía"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="theme")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Colores primarios
    primary_color = models.CharField(max_length=20, default="#56b3c7", verbose_name="Color primario")
    secondary_color = models.CharField(max_length=20, default="#8fc73e", verbose_name="Color secundario")
    accent_color = models.CharField(max_length=20, default="#FF9613", verbose_name="Color de acento")
    
    # Colores de texto
    text_color = models.CharField(max_length=20, default="#333333", verbose_name="Color de texto principal")
    light_text_color = models.CharField(max_length=20, default="#ffffff", verbose_name="Color de texto claro")
    
    # Fuentes
    font_family = models.CharField(max_length=100, default="'Montserrat', sans-serif", verbose_name="Familia de fuentes")
    
    # Logo
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Logo de la compañía")
    logo_small = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Logo pequeño/icono")
    
    # Fondo personalizado
    background_image = models.ImageField(upload_to='company_backgrounds/', null=True, blank=True, verbose_name="Imagen de fondo")
    
    # CSS personalizado
    custom_css = models.TextField(blank=True, null=True, verbose_name="CSS personalizado")
    
    # JavaScript personalizado
    custom_js = models.TextField(blank=True, null=True, verbose_name="JavaScript personalizado")
    
    # Habilitado/Deshabilitado
    enabled = models.BooleanField(default=True, verbose_name="Tema habilitado")
    
    class Meta:
        verbose_name = "Tema de compañía"
        verbose_name_plural = "Temas de compañías"
    
    def __str__(self):
        return f"Tema de {self.company.name}"
    
    def get_css_variables(self):
        """Devuelve las variables CSS para este tema"""
        return f"""
        :root {{
            --primary-color: {self.primary_color};
            --secondary-color: {self.secondary_color};
            --accent-color: {self.accent_color};
            --text-color: {self.text_color};
            --light-text-color: {self.light_text_color};
            --font-family: {self.font_family};
        }}
        """
    
    def get_compiled_css(self):
        """Combina las variables CSS con el CSS personalizado"""
        css = self.get_css_variables()
        
        # Añadir estilos base aplicando variables
        css += """
        body {
            font-family: var(--font-family);
            color: var(--text-color);
        }
        
        .navbar {
            background-color: var(--primary-color) !important;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        .btn-primary:hover {
            background-color: color-mix(in srgb, var(--primary-color) 80%, black);
            border-color: color-mix(in srgb, var(--primary-color) 80%, black);
        }
        
        .btn-secondary {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        
        .btn-secondary:hover {
            background-color: color-mix(in srgb, var(--secondary-color) 80%, black);
            border-color: color-mix(in srgb, var(--secondary-color) 80%, black);
        }
        
        .card-header {
            background-color: color-mix(in srgb, var(--primary-color) 30%, white) !important;
        }
        
        /* Estilos personalizados para formularios */
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.25rem rgba(var(--primary-color), 0.25);
        }
        """
        
        # Añadir CSS personalizado si existe
        if self.custom_css:
            css += "\n/* CSS personalizado */\n"
            css += self.custom_css
        
        return css
    
    @staticmethod
    def get_default_theme(company):
        """Obtiene el tema para una compañía, o crea uno por defecto si no existe"""
        theme, created = CompanyTheme.objects.get_or_create(company=company)
        return theme