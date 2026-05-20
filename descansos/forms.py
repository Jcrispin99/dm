from django import forms


class UploadExcelForm(forms.Form):
    archivo = forms.FileField(
        label='Excel de descansos médicos',
        help_text='Archivo .xlsx con las columnas Código, Nombre del Trabajador, Gerencia, '
                  'Fecha de Inicio DM, Fecha de Término DM, Dias DM, Clasificación, Observaciones.',
    )

    def clean_archivo(self):
        f = self.cleaned_data['archivo']
        if not f.name.lower().endswith(('.xlsx', '.xlsm')):
            raise forms.ValidationError('El archivo debe ser .xlsx o .xlsm')
        return f
