# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_dashboard, name='company_dashboard'),
    path('admin/setup-dashboard/<int:company_id>/', views.setup_company_dashboard, name='setup_company_dashboard'),
    path('admin/configure-widget/<int:widget_config_id>/', views.configure_widget, name='configure_widget'),
]