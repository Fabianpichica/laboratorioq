from django.contrib import admin
from .models import Jornada, Salon, Estudiante, Guia
from django import forms
from django.contrib.auth.models import User

class JornadaAdminForm(forms.ModelForm):
    class Meta:
        model = Jornada
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios con perfil de profesor
        self.fields['profesor'].queryset = User.objects.filter(profile__role='profesor')

class EstudianteAdminForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'documento', 'tipo_documento', 'salon', 'jornada']

class JornadaAdmin(admin.ModelAdmin):
    form = JornadaAdminForm
    filter_horizontal = ('salones',)

class EstudianteAdmin(admin.ModelAdmin):
    form = EstudianteAdminForm
    list_display = ('nombre', 'documento', 'tipo_documento', 'salon', 'jornada')
    search_fields = ('nombre', 'documento')

class GuiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion')
    search_fields = ('titulo',)

admin.site.register(Jornada, JornadaAdmin)
admin.site.register(Salon)
admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(Guia, GuiaAdmin)

# Register your models here.
