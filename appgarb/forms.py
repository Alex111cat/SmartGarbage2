from django import forms
from .models import Modules, Methods
import re
from django.core.exceptions import ValidationError


class ModuleForm(forms.Form):
    module = forms.CharField(max_length=4, label='',
                             widget=forms.TextInput(attrs={"class": "form-control"}))
    required_css_class = 'field'
    error_css_class ='error'

    def clean_module(self):
         module = self.cleaned_data['module']
         module = module.rjust(4, '0')
         if not ( re.match(r'\d{4}', module)):  # проверка на цифры
             raise ValidationError('код модуля должен состоять из цифр')
         try:
             obj = Modules.objects.get(m_module=module)
         except Modules.DoesNotExist:
             raise ValidationError('нет модуля с таким кодом')
         return module   # если проверка пройдена, возвращаем

class AnaliticsForm(forms.Form):
    module = forms.CharField(max_length=4, label='',
                             widget=forms.TextInput(attrs={"class": "form-control "}))
    methods = forms.ModelMultipleChoiceField(queryset=Methods.objects.all(), label = 'Выберите методы:',
                                             widget=forms.CheckboxSelectMultiple(attrs={"class": ""}),
                                             required=False)
    # is_method = forms.CheckboxInput()

    required_css_class = 'field'
    error_css_class ='error'

    def clean_module(self):
         module = self.cleaned_data['module']
         module = module.rjust(4, '0')
         if not ( re.match(r'\d{4}', module)):  # проверка на цифры
             raise ValidationError('код модуля должен состоять из цифр')
         try:
             obj = Modules.objects.get(m_module=module)
         except Modules.DoesNotExist:
             raise ValidationError('нет модуля с таким кодом')
         methods = self
         return module   # если проверка пройдена, возвращаем

    def clean_methods(self):
         methods = self.cleaned_data['methods']
         if not (methods):
             raise ValidationError('Выберите хотя бы один метод')
         return methods   # если проверка пройдена, возвращаем

