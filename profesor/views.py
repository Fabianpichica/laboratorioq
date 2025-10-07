from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Jornada, Salon, Estudiante, Guia
from django.contrib.auth.models import User
from core.models import CuadernoEntry, Quimico, Material, Equipo

@login_required
def dashboard_profesor(request):
    jornadas = Jornada.objects.filter(profesores=request.user)
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
    # Guías asignadas a este salón
    guias = salon.guias_asignadas.all()
    # Para cada guía, obtener dict de aprendiz: informe (o None)
    guias_info = []
    for guia in guias:
        entregas = {}
        for estudiante in estudiantes:
            user = User.objects.filter(username=estudiante.documento).first()
            informe = None
            if user:
                informe = CuadernoEntry.objects.filter(aprendiz=user, guia=guia).first()
            entregas[estudiante] = informe
        guias_info.append({'guia': guia, 'entregas': entregas})
    return render(request, 'profesor/salon_estudiantes.html', {
        'salon': salon,
        'estudiantes': estudiantes,
        'jornada': jornada,
        'guias_info': guias_info
    })

@login_required
def guias_profesor(request):
    jornadas = Jornada.objects.filter(profesores=request.user)
    salones = Salon.objects.filter(jornadas__profesores=request.user).distinct()
    quimicos = Quimico.objects.all()
    # Agregar materiales y equipos del inventario
    materiales = Material.objects.all()
    equipos = Equipo.objects.all()
    instrumentos = list(materiales) + list(equipos)
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
        'quimicos': quimicos,
        'instrumentos': instrumentos,
        'mensaje': mensaje
    })

@login_required
def resultados_por_guia(request):
    # Solo profesores
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'profesor':
        return redirect('/')
    # Obtener jornadas y salones del profesor
    jornadas = Jornada.objects.filter(profesores=request.user)
    salones = Salon.objects.filter(jornadas__profesores=request.user).distinct()
    guias = Guia.objects.filter(salones__in=salones).distinct()
    resultados = {}
    for guia in guias:
        # Entradas de cuaderno asociadas a la guía
        informes = CuadernoEntry.objects.filter(guia=guia).select_related('aprendiz', 'quimico').order_by('-fecha')
        resultados[guia] = informes
    return render(request, 'profesor/resultados_por_guia.html', {
        'guias': guias,
        'resultados': resultados,
        'jornadas': jornadas
    })

# Create your views here.
