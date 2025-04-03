# dashboard/admin.py
from django.contrib import admin
from .models import DashboardWidget, CompanyDashboard, DashboardWidgetConfig, SalesData
from .models import CustomForm, FormField, FormData, FormFieldGroup, CompanyTheme

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'code_name']
    search_fields = ['name', 'code_name']
    list_filter = ['widget_type']

class DashboardWidgetConfigInline(admin.TabularInline):
    model = DashboardWidgetConfig
    extra = 1
    fields = ['widget', 'position', 'size', 'is_visible']

@admin.register(CompanyDashboard)
class CompanyDashboardAdmin(admin.ModelAdmin):
    list_display = ['company', 'created_at']
    inlines = [DashboardWidgetConfigInline]
    
    def has_add_permission(self, request):
        # Dashboards solo se crean desde la vista personalizada
        return False

@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ['company', 'date', 'product', 'amount', 'units']
    list_filter = ['company', 'date']
    search_fields = ['product']
    
    def get_queryset(self, request):
        # Usar el manager sin filtrar para el admin
        return self.model.all_objects.all()
    
@admin.register(CustomForm)
class CustomFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'code_name', 'company', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'code_name']
    filter_horizontal = ['departments']

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

@admin.register(FormFieldGroup)
class FormFieldGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'form', 'order']
    list_filter = ['form__company']
    search_fields = ['name']
    inlines = [FormFieldInline]

@admin.register(FormData)
class FormDataAdmin(admin.ModelAdmin):
    list_display = ['form', 'department', 'created_by', 'date_created']
    list_filter = ['form', 'department', 'date_created']
    readonly_fields = ['date_created', 'date_modified', 'data']
    
    def get_queryset(self, request):
        # Usar el manager sin filtrar para el admin
        return self.model.all_objects.all()

# Registrar el modelo CompanyTheme para administración
@admin.register(CompanyTheme)
class CompanyThemeAdmin(admin.ModelAdmin):
    list_display = ['company', 'enabled', 'has_logo', 'has_background']
    list_filter = ['enabled']
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'enabled')
        }),
        ('Colores', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'text_color', 'light_text_color')
        }),
        ('Fuentes', {
            'fields': ('font_family',)
        }),
        ('Imágenes', {
            'fields': ('logo', 'logo_small', 'background_image')
        }),
        ('CSS y JavaScript Personalizado', {
            'fields': ('custom_css', 'custom_js', 'css_file'),
            'classes': ('collapse',)
        }),
    )
    
    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'Logo'
    
    def has_background(self, obj):
        return bool(obj.background_image)
    has_background.boolean = True
    has_background.short_description = 'Fondo'