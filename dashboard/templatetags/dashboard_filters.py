# Ubicación: dashboard/templatetags/dashboard_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtener un elemento de un diccionario por su clave"""
    return dictionary.get(key)