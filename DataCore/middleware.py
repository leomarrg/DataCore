# proyecto/middleware.py
from django.utils.deprecation import MiddlewareMixin
import threading

# Variable global por hilo para almacenar la compañía actual
_company_data = threading.local()

def get_current_company():
    """Obtener la compañía del contexto actual"""
    return getattr(_company_data, 'company', None)

class CompanyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Limpiar compañía actual
        _company_data.company = None
        
        # Establecer compañía si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                employee = request.user.employee
                _company_data.company = employee.company
            except:
                pass