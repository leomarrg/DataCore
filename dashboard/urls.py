# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_dashboard, name='company_dashboard'),
    path('admin/setup-dashboard/<int:company_id>/', views.setup_company_dashboard, name='setup_company_dashboard'),
    path('admin/configure-widget/<int:widget_config_id>/', views.configure_widget, name='configure_widget'),

    path('forms/', views.form_manager, name='form_manager'),
    path('forms/create/', views.create_edit_form, name='create_form'),
    path('forms/edit/<int:form_id>/', views.create_edit_form, name='edit_form'),
    path('forms/delete/<int:form_id>/', views.delete_form, name='delete_form'),
    path('forms/<slug:form_code>/', views.fill_form, name='fill_form'),
    path('forms/<slug:form_code>/data/', views.view_form_data, name='view_form_data'),
    path('forms/list/', views.list_available_forms, name='list_forms'),
]