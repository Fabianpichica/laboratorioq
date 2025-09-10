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
    guias = Guia.objects.all().order_by('-fecha_creacion')
    return render(request, 'profesor/guias_profesor.html', {'guias': guias})

# Create your views here.
