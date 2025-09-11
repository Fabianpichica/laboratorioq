from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Jornada, Salon, Estudiante, Guia
from django.contrib.auth.models import User

@login_required
def dashboard_profesor(request):
    jornadas = Jornada.objects.filter(profesor=request.user)
    return render(request, 'profesor/dashboard_profesor.html', {'jornadas': jornadas})

@login_required
def salon_estudiantes(request, salon_id, jornada_id=None):
    salon = get_object_or_404(Salon, id=salon_id)
    if jornada_id:
        estudiantes = salon.estudiantes.filter(jornada_id=jornada_id)
        jornada = get_object_or_404(Jornada, id=jornada_id)
    else:
        estudiantes = salon.estudiantes.all()
        jornada = None
    return render(request, 'profesor/salon_estudiantes.html', {'salon': salon, 'estudiantes': estudiantes, 'jornada': jornada})

@login_required
def guias_profesor(request):
    jornadas = Jornada.objects.filter(profesor=request.user)
    salones = Salon.objects.filter(jornadas__profesor=request.user).distinct()
    mensaje = None
    if request.method == 'POST' and 'asignar_guia' in request.POST:
        salon_id = request.POST.get('salon_id')
        archivo = request.FILES.get('archivo_guia')
        titulo = request.POST.get('titulo', 'Guía sin título')
        descripcion = request.POST.get('descripcion', '')
        if salon_id and archivo:
            salon = Salon.objects.get(id=salon_id)
            guia = Guia.objects.create(titulo=titulo, descripcion=descripcion, archivo=archivo)
            guia.salones.add(salon)
            mensaje = f'Guía "{guia.titulo}" subida y asignada correctamente al salón {salon.nombre}.'
        else:
            mensaje = 'Debes subir el archivo final de la guía y seleccionar un salón.'
    return render(request, 'profesor/guia_form.html', {
        'jornadas': jornadas,
        'salones': salones,
        'mensaje': mensaje
    })

# Create your views here.
