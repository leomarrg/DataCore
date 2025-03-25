# dashboard/forms.py
from django import forms
from .models import DashboardWidget

class DashboardConfigForm(forms.Form):
    widgets = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar widgets disponibles
        widgets = DashboardWidget.objects.all()
        self.fields['widgets'].choices = [(w.id, f"{w.name} ({w.get_widget_type_display()})") for w in widgets]

class WidgetConfigForm(forms.Form):
    is_visible = forms.BooleanField(required=False, initial=True, label="Visible")
    size = forms.ChoiceField(
        choices=[
            ('small', 'Pequeño'),
            ('medium', 'Mediano'),
            ('large', 'Grande')
        ],
        initial='medium',
        label="Tamaño"
    )
    
    def __init__(self, *args, **kwargs):
        # Obtener tipo de widget para personalizar campos
        widget_type = kwargs.pop('widget_type', None)
        super().__init__(*args, **kwargs)
        
        # Añadir campos específicos según tipo de widget
        if widget_type == 'chart':
            self.fields['period'] = forms.ChoiceField(
                choices=[
                    ('week', 'Última semana'),
                    ('month', 'Último mes'),
                    ('year', 'Último año')
                ],
                initial='month',
                label="Periodo"
            )
        elif widget_type == 'table':
            self.fields['limit'] = forms.IntegerField(
                min_value=1, 
                max_value=20,
                initial=5,
                label="Cantidad de filas"
            )