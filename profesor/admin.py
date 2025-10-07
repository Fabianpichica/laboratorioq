from django.contrib import admin
from .models import Jornada, Salon, Estudiante, Guia
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Profile

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
        fields = ['nombre', 'documento', 'tipo_documento', 'direccion', 'correo', 'telefono', 'password', 'contacto_emergencia', 'nombre_contacto_emergencia', 'eps', 'foto', 'jornada', 'salon']

class JornadaAdmin(admin.ModelAdmin):
    form = JornadaAdminForm
    filter_horizontal = ('salones',)

class EstudianteAdmin(admin.ModelAdmin):
    form = EstudianteAdminForm
    list_display = ('nombre', 'documento', 'tipo_documento', 'salon', 'jornada')
    search_fields = ('nombre', 'documento', 'correo', 'telefono')

    def save_model(self, request, obj, form, change):
        from django.contrib.auth.models import User
        from core.models import Profile
        # Crear usuario si no existe
        if not User.objects.filter(username=obj.documento).exists():
            user = User.objects.create_user(
                username=obj.documento,
                email=obj.correo or '',
                password=obj.password or User.objects.make_random_password()
            )
            Profile.objects.create(user=user, role='aprendiz')
        super().save_model(request, obj, form, change)

class GuiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion')
    search_fields = ('titulo',)

@receiver(post_save, sender=User)
def crear_profile_usuario(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        # Por defecto, asigna rol 'aprendiz' (puedes ajustar según lógica de tu sistema)
        from core.models import Profile
        Profile.objects.create(user=instance, role='aprendiz')
