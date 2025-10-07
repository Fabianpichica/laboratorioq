from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from profesor.models import Salon, Jornada
from core.models import Profile

class ProfesorProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'
    fields = ('role',)
    readonly_fields = ('role',)

class ProfesorForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre completo', max_length=150)
    tipo_documento = forms.ChoiceField(choices=[('CC', 'Cédula de ciudadanía'), ('EXT', 'Cédula extranjera')], label='Tipo de documento')
    numero_documento = forms.CharField(label='Número de documento', max_length=30)
    salones = forms.ModelMultipleChoiceField(queryset=Salon.objects.all(), required=False, widget=admin.widgets.FilteredSelectMultiple('Salones', False))
    jornadas = forms.ModelMultipleChoiceField(queryset=Jornada.objects.all(), required=False, widget=admin.widgets.FilteredSelectMultiple('Jornadas', False))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)
    fotografia = forms.ImageField(label='Fotografía', required=False)

    class Meta:
        model = User
        fields = ('username', 'nombre', 'tipo_documento', 'numero_documento', 'salones', 'jornadas', 'password', 'fotografia', 'email')

class ProfesorAdmin(admin.ModelAdmin):
    form = ProfesorForm
    inlines = [ProfesorProfileInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    def save_model(self, request, obj, form, change):
        obj.set_password(form.cleaned_data['password'])
        obj.first_name = form.cleaned_data['nombre']
        obj.save()
        # Crear o actualizar Profile
        Profile.objects.update_or_create(user=obj, defaults={'role': 'profesor'})
        # Guardar fotografía si se subió
        if form.cleaned_data.get('fotografia'):
            profile = Profile.objects.get(user=obj)
            profile.fotografia = form.cleaned_data['fotografia']
            profile.save()
        # Asignar salones y jornadas
        for jornada in form.cleaned_data['jornadas']:
            jornada.profesor = obj
            jornada.save()
        for salon in form.cleaned_data['salones']:
            salon.save()

# Registrar el admin personalizado solo para profesores
admin.site.unregister(User)
admin.site.register(User, ProfesorAdmin)
