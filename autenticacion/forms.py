# autenticacion/forms.py
from django import forms
from .models import Employee
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class EmployeeAdminForm(forms.ModelForm):
    # Campos para la creación del usuario
    username = forms.CharField(required=False, help_text="Dejarlo en blanco usará el email o generará uno automáticamente")
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, 
                               help_text="Opcional. Si se deja en blanco, se usará una contraseña predeterminada.")
    
    # Campo para seleccionar un usuario existente
    existing_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Usuario existente",
        help_text="Seleccione un usuario existente en lugar de crear uno nuevo"
    )
    
    class Meta:
        model = Employee
        fields = ['company', 'department', 'job_title', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.user:
            # Prellenar campos con datos del usuario existente
            self.fields['username'].initial = instance.user.username
            self.fields['email'].initial = instance.user.email
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['existing_user'].initial = instance.user
            # No mostramos la contraseña para usuarios existentes
            self.fields['password'].widget = forms.HiddenInput()
    
    def clean_username(self):
        """Validar que el nombre de usuario no exista ya"""
        username = self.cleaned_data.get('username')
        existing_user = self.cleaned_data.get('existing_user')
        
        # Si se seleccionó un usuario existente, no validamos username
        if existing_user:
            return username
        
        # Si se proporcionó un nombre de usuario, verificar que no exista
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    f"El usuario '{username}' ya existe. Por favor, elija otro nombre de usuario o seleccione un usuario existente."
                )
        
        return username