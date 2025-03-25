# autenticacion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),  # Landing page como página principal
    path('login/', views.login_view, name='login'),  # Cambiar la ruta de login
    path('logout/', views.logout_view, name='logout'),
]