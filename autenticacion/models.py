# autenticacion/models.py
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"

class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    access_level = models.CharField(max_length=50, choices=[
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('user', 'Usuario Regular'),
    ])

    # Añade este campo nuevo
    parent_department = models.ForeignKey('self', null=True, blank=True, 
                                         on_delete=models.SET_NULL, 
                                         related_name='child_departments')
    
    # Añadir este método nuevo
    def get_all_child_departments(self):
        """Obtiene todos los departamentos descendientes incluyendo este"""
        departments = [self]
        for child in self.child_departments.all():
            departments.extend(child.get_all_child_departments())
        return departments
    
    class Meta:
        unique_together = ('company', 'name')
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="employees")
    job_title = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.company.name})"