# dashboard/admin.py
from django.contrib import admin
from .models import DashboardWidget, CompanyDashboard, DashboardWidgetConfig, SalesData

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