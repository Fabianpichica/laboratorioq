from django import forms
from django.contrib.auth.models import User
from profesor.models import Salon, Jornada
from core.models import Profile

class ProfesorCustomForm(forms.Form):
    nombre = forms.CharField(label='Nombre completo', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nombre completo', 'autocomplete': 'off'
    }))
    tipo_documento = forms.ChoiceField(
        choices=[('CC', 'Cédula de ciudadanía'), ('EXT', 'Cédula extranjera')],
        label='Tipo de documento',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_documento = forms.CharField(label='Número de documento', max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Número de documento', 'autocomplete': 'off'
    }))
    salones = forms.ModelMultipleChoiceField(
        queryset=Salon.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    jornadas = forms.ModelMultipleChoiceField(
        queryset=Jornada.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Contraseña', 'autocomplete': 'new-password'
    }))
    fotografia = forms.ImageField(label='Fotografía', required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'form-control-file', 'accept': 'image/*'
    }))
