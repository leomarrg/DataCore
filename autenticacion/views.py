# autenticacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Special handling for superusers
                if user.is_superuser:
                    # Even if they don't have an employee account, allow login
                    if hasattr(user, 'employee'):
                        # If they do have an employee association, check company is active
                        if not user.employee.company.is_active:
                            logout(request)
                            messages.error(request, "Tu compañía está desactivada")
                            return redirect('login')
                    # Redirect superusers to admin or dashboard
                    return redirect('admin_dashboard')  # or any other suitable dashboard
                
                # For regular users, continue with existing checks
                elif hasattr(user, 'employee'):
                    # Verificar compañía activa
                    if not user.employee.company.is_active:
                        logout(request)
                        messages.error(request, "Tu compañía está desactivada")
                        return redirect('login')
                    
                    return redirect('company_dashboard')
                else:
                    messages.warning(request, "Tu usuario no está asociado a ninguna compañía")
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = LoginForm()
    
    return render(request, 'autenticacion/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

def landing_page(request):
    """Vista para el landing page"""
    return render(request, 'autenticacion/index.html')