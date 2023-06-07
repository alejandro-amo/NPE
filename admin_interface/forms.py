from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from admin_api.models import Establecimiento, Poblacion
from unidecode import unidecode
from django.core.validators import EmailValidator
from core import settings
import logging
logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class NouEstablimentForm(forms.ModelForm):
    class Meta:
        model = Establecimiento
        fields = ['tipo_establecimiento', 'nombre', 'direccion', 'codigo_postal', 'poblacion', 'email', 'telefonos',
                  'web']
        labels = {
            'tipo_establecimiento': 'Tipus',
            'nombre': 'Nom',
            'direccion': 'Adreça¹',
            'codigo_postal': 'Codi postal²',
            'poblacion': 'Municipi³',
            'email': 'Correu electrónic',
            'telefonos': 'Telèfons⁴',
            'web': 'web'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # Ajustes al campo email
        self.fields['email'].widget = forms.TextInput()

        # Ajustes al campo poblacion
        poblaciones = Poblacion.objects.all()
        # Generar las opciones para el campo select
        opciones_select = [(p.nombre, p.nombre) for p in poblaciones]
        opciones_select = sorted(opciones_select, key=lambda x: unidecode(x[0]))
        # Generar la opción "sin opción" para el campo población
        opciones_select.insert(0, ('', '(Tria municipi)'))
        # Carga los valores en el widget
        self.fields['poblacion'].widget = forms.Select(choices=opciones_select)


class EditaEstablimentForm(forms.ModelForm):
    class Meta:
        model = Establecimiento
        fields = ['tipo_establecimiento', 'nombre', 'direccion', 'codigo_postal', 'poblacion', 'email', 'telefonos',
                  'web', 'latitud', 'longitud', 'activo', 'observaciones']
        labels = {
            'tipo_establecimiento': 'Tipus',
            'nombre': 'Nom',
            'direccion': 'Adreça¹',
            'codigo_postal': 'Codi postal²',
            'poblacion': 'Municipi³',
            'email': 'Correu electrónic',
            'telefonos': 'Telèfons⁴',
            'web': 'Lloc web',
            'latitud': 'GPS - Latitud',
            'longitud': 'GPS - Longitud',
            'activo': '← Desmarca aquesta casella per indicar que l\'establiment està tancat.',
            'observaciones': 'Observacions'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # Ajustes al campo email
        self.fields['email'].widget = forms.TextInput()
        self.fields['email'].validators.append(EmailValidator())

        # Ajustes al campo poblacion
        poblaciones = Poblacion.objects.all()
        # Generar las opciones para el campo select
        opciones_select = [(p.nombre, p.nombre) for p in poblaciones]
        opciones_select = sorted(opciones_select, key=lambda x: unidecode(x[0]))
        # Generar la opción "sin opción" para el campo población
        opciones_select.insert(0, ('', '(Tria població)'))
        # Carga los valores en el widget
        self.fields['poblacion'].widget = forms.Select(choices=opciones_select)
        botones = ButtonHolder(
            Button('btn-back', 'Tornar', css_class="bg-neutral btn-sm btn-warning mr-4"),
            Reset('reset', 'Desfer', css_class='btn btn-secondary btn-sm mr-4'),
            Submit('submit', 'Desar', css_class='btn btn-primary btn-sm mr-4'),
            css_class="d-flex justify-content-center"
        )
        # Row 1 stuff
        row1_col1 = Div('nombre', 'direccion', 'poblacion', 'email', 'latitud', css_class="col-sm")
        row1_col2 = Div('tipo_establecimiento', 'codigo_postal', 'telefonos', 'web', 'longitud', css_class="col-sm")
        row1 = Div(row1_col1, row1_col2, css_class="row")
        # Row 2 stuff
        row2_col1 = Div('observaciones', css_class="col-sm-12")
        row2 = Div(row2_col1, css_class="row")
        # Row 3 stuff
        row3_col1 = Div('activo', css_class="col-sm-12 d-flex justify-content-center align-items-center")
        row3 = Div(row3_col1, css_class="row")
        # Row 4 stuff
        row4_col1 = Div(botones, css_class="col-sm-12")
        row4 = Div(row4_col1, css_class="row")

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            # and a minor style tuning in observations text box field
            if field_name == 'observaciones':
                field.widget.attrs.update({'style': 'border: 1px solid rgb(82, 95, 127); border-radius: 10px'})

        self.helper.layout = Layout(row1, row2, row3, row4)


'''            

               
              
         
'''
