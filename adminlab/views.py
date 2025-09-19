from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Equipo, Material
from core.models import Quimico
from profesor.models import Estudiante, Guia, Jornada, Salon

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    quimicos = Quimico.objects.all()
    estudiantes = Estudiante.objects.all()
    guias = Guia.objects.all()
    jornadas = Jornada.objects.all()
    salones = Salon.objects.all()
    return render(request, 'adminlab/dashboard_admin.html', {
        'quimicos': quimicos,
        'estudiantes': estudiantes,
        'guias': guias,
        'jornadas': jornadas,
        'salones': salones
    })

@login_required
def inventario_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    quimicos = Quimico.objects.all()
    materiales = Material.objects.all()
    equipos = Equipo.objects.all()
    return render(request, 'adminlab/inventario_admin.html', {
        'quimicos': quimicos,
        'materiales': materiales,
        'equipos': equipos
    })

@login_required
def agregar_quimico_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        Quimico.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            descripcion=descripcion,
            fecha_vencimiento=fecha_vencimiento if fecha_vencimiento else None
        )
        messages.success(request, 'Reactivo agregado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_quimico_admin.html', {})

@login_required
def editar_quimico_admin(request, quimico_id):
    if not request.user.is_superuser:
        return redirect('/')
    quimico = get_object_or_404(Quimico, id=quimico_id)
    if request.method == 'POST':
        quimico.nombre = request.POST.get('nombre')
        quimico.cantidad = request.POST.get('cantidad')
        quimico.descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        quimico.fecha_vencimiento = fecha_vencimiento if fecha_vencimiento else None
        quimico.save()
        messages.success(request, 'Reactivo editado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_quimico_admin.html', {'quimico': quimico})

@login_required
def eliminar_quimico_admin(request, quimico_id):
    if not request.user.is_superuser:
        return redirect('/')
    quimico = get_object_or_404(Quimico, id=quimico_id)
    quimico.delete()
    messages.success(request, 'Reactivo eliminado correctamente.')
    return redirect('inventario_admin')

@login_required
def agregar_material_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        Material.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            descripcion=descripcion
        )
        messages.success(request, 'Material agregado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_material_admin.html', {})

@login_required
def editar_material_admin(request, material_id):
    if not request.user.is_superuser:
        return redirect('/')
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.nombre = request.POST.get('nombre')
        material.cantidad = request.POST.get('cantidad')
        material.descripcion = request.POST.get('descripcion')
        material.save()
        messages.success(request, 'Material editado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_material_admin.html', {'material': material})

@login_required
def eliminar_material_admin(request, material_id):
    if not request.user.is_superuser:
        return redirect('/')
    material = get_object_or_404(Material, id=material_id)
    material.delete()
    messages.success(request, 'Material eliminado correctamente.')
    return redirect('inventario_admin')

@login_required
def agregar_equipo_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        Equipo.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            descripcion=descripcion
        )
        messages.success(request, 'Equipo agregado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_equipo_admin.html', {})

@login_required
def editar_equipo_admin(request, equipo_id):
    if not request.user.is_superuser:
        return redirect('/')
    equipo = get_object_or_404(Equipo, id=equipo_id)
    if request.method == 'POST':
        equipo.nombre = request.POST.get('nombre')
        equipo.cantidad = request.POST.get('cantidad')
        equipo.descripcion = request.POST.get('descripcion')
        equipo.save()
        messages.success(request, 'Equipo editado correctamente.')
        return redirect('inventario_admin')
    return render(request, 'adminlab/form_equipo_admin.html', {'equipo': equipo})

@login_required
def eliminar_equipo_admin(request, equipo_id):
    if not request.user.is_superuser:
        return redirect('/')
    equipo = get_object_or_404(Equipo, id=equipo_id)
    equipo.delete()
    messages.success(request, 'Equipo eliminado correctamente.')
    return redirect('inventario_admin')

# --- CRUD ESTUDIANTE ---
@login_required
def estudiantes_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    estudiantes = Estudiante.objects.all()
    return render(request, 'adminlab/estudiantes_admin.html', {'estudiantes': estudiantes})

@login_required
def agregar_estudiante_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    salones = Salon.objects.all()
    jornadas = Jornada.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        documento = request.POST.get('documento')
        tipo_documento = request.POST.get('tipo_documento')
        salon_id = request.POST.get('salon')
        jornada_id = request.POST.get('jornada')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        estudiante = Estudiante.objects.create(
            nombre=nombre,
            documento=documento,
            tipo_documento=tipo_documento,
            salon_id=salon_id if salon_id else None,
            jornada_id=jornada_id if jornada_id else None,
            correo=correo,
            telefono=telefono,
            password=password
        )
        messages.success(request, 'Estudiante creado correctamente.')
        return redirect('estudiantes_admin')
    return render(request, 'adminlab/form_estudiante_admin.html', {'salones': salones, 'jornadas': jornadas})

@login_required
def editar_estudiante_admin(request, estudiante_id):
    if not request.user.is_superuser:
        return redirect('/')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    salones = Salon.objects.all()
    jornadas = Jornada.objects.all()
    if request.method == 'POST':
        estudiante.nombre = request.POST.get('nombre')
        estudiante.documento = request.POST.get('documento')
        estudiante.tipo_documento = request.POST.get('tipo_documento')
        estudiante.salon_id = request.POST.get('salon')
        estudiante.jornada_id = request.POST.get('jornada')
        estudiante.correo = request.POST.get('correo')
        estudiante.telefono = request.POST.get('telefono')
        estudiante.password = request.POST.get('password')
        estudiante.save()
        messages.success(request, 'Estudiante actualizado correctamente.')
        return redirect('estudiantes_admin')
    return render(request, 'adminlab/form_estudiante_admin.html', {'estudiante': estudiante, 'salones': salones, 'jornadas': jornadas})

@login_required
def eliminar_estudiante_admin(request, estudiante_id):
    if not request.user.is_superuser:
        return redirect('/')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estudiante.delete()
    messages.success(request, 'Estudiante eliminado correctamente.')
    return redirect('estudiantes_admin')

# --- CRUD GUIA ---
@login_required
def guias_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    guias = Guia.objects.all()
    return render(request, 'adminlab/guias_admin.html', {'guias': guias})

@login_required
def agregar_guia_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    salones = Salon.objects.all()
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        archivo = request.FILES.get('archivo')
        guia = Guia.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            archivo=archivo
        )
        salon_ids = request.POST.getlist('salones')
        if salon_ids:
            guia.salones.set(salon_ids)
        messages.success(request, 'Guía creada correctamente.')
        return redirect('guias_admin')
    return render(request, 'adminlab/form_guia_admin.html', {'salones': salones})

@login_required
def editar_guia_admin(request, guia_id):
    if not request.user.is_superuser:
        return redirect('/')
    guia = get_object_or_404(Guia, id=guia_id)
    salones = Salon.objects.all()
    if request.method == 'POST':
        guia.titulo = request.POST.get('titulo')
        guia.descripcion = request.POST.get('descripcion')
        if request.FILES.get('archivo'):
            guia.archivo = request.FILES.get('archivo')
        guia.save()
        salon_ids = request.POST.getlist('salones')
        if salon_ids:
            guia.salones.set(salon_ids)
        messages.success(request, 'Guía actualizada correctamente.')
        return redirect('guias_admin')
    return render(request, 'adminlab/form_guia_admin.html', {'guia': guia, 'salones': salones})

@login_required
def eliminar_guia_admin(request, guia_id):
    if not request.user.is_superuser:
        return redirect('/')
    guia = get_object_or_404(Guia, id=guia_id)
    guia.delete()
    messages.success(request, 'Guía eliminada correctamente.')
    return redirect('guias_admin')

# --- CRUD JORNADA ---
@login_required
def jornadas_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    jornadas = Jornada.objects.all()
    return render(request, 'adminlab/jornadas_admin.html', {'jornadas': jornadas})

@login_required
def agregar_jornada_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    salones = Salon.objects.all()
    profesores = User.objects.filter(is_staff=True)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha')
        profesor_id = request.POST.get('profesor')
        jornada = Jornada.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            fecha=fecha,
            profesor_id=profesor_id
        )
        salon_ids = request.POST.getlist('salones')
        if salon_ids:
            jornada.salones.set(salon_ids)
        messages.success(request, 'Jornada creada correctamente.')
        return redirect('jornadas_admin')
    return render(request, 'adminlab/form_jornada_admin.html', {'salones': salones, 'profesores': profesores})

@login_required
def editar_jornada_admin(request, jornada_id):
    if not request.user.is_superuser:
        return redirect('/')
    jornada = get_object_or_404(Jornada, id=jornada_id)
    salones = Salon.objects.all()
    profesores = User.objects.filter(is_staff=True)
    if request.method == 'POST':
        jornada.nombre = request.POST.get('nombre')
        jornada.descripcion = request.POST.get('descripcion')
        jornada.fecha = request.POST.get('fecha')
        jornada.profesor_id = request.POST.get('profesor')
        jornada.save()
        salon_ids = request.POST.getlist('salones')
        if salon_ids:
            jornada.salones.set(salon_ids)
        messages.success(request, 'Jornada actualizada correctamente.')
        return redirect('jornadas_admin')
    return render(request, 'adminlab/form_jornada_admin.html', {'jornada': jornada, 'salones': salones, 'profesores': profesores})

@login_required
def eliminar_jornada_admin(request, jornada_id):
    if not request.user.is_superuser:
        return redirect('/')
    jornada = get_object_or_404(Jornada, id=jornada_id)
    jornada.delete()
    messages.success(request, 'Jornada eliminada correctamente.')
    return redirect('jornadas_admin')

# --- CRUD SALON ---
@login_required
def salones_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    salones = Salon.objects.all()
    return render(request, 'adminlab/salones_admin.html', {'salones': salones})

@login_required
def profesores_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    profesores = User.objects.filter(is_staff=True)
    profesores_info = []
    for profesor in profesores:
        jornadas = Jornada.objects.filter(profesor=profesor)
        jornadas_info = []
        for jornada in jornadas:
            salones_jornada = jornada.salones.all()
            jornadas_info.append({
                'jornada': jornada,
                'salones': salones_jornada
            })
        profesores_info.append({
            'profesor': profesor,
            'jornadas': jornadas_info
        })
    return render(request, 'adminlab/profesores_admin.html', {
        'profesores_info': profesores_info
    })

@login_required
def agregar_salon_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ubicacion = request.POST.get('ubicacion')
        Salon.objects.create(nombre=nombre, ubicacion=ubicacion)
        messages.success(request, 'Salón creado correctamente.')
        return redirect('salones_admin')
    return render(request, 'adminlab/form_salon_admin.html')

@login_required
def editar_salon_admin(request, salon_id):
    if not request.user.is_superuser:
        return redirect('/')
    salon = get_object_or_404(Salon, id=salon_id)
    if request.method == 'POST':
        salon.nombre = request.POST.get('nombre')
        salon.ubicacion = request.POST.get('ubicacion')
        salon.save()
        messages.success(request, 'Salón actualizado correctamente.')
        return redirect('salones_admin')
    return render(request, 'adminlab/form_salon_admin.html', {'salon': salon})

@login_required
def eliminar_salon_admin(request, salon_id):
    if not request.user.is_superuser:
        return redirect('/')
    salon = get_object_or_404(Salon, id=salon_id)
    salon.delete()
    messages.success(request, 'Salón eliminado correctamente.')
    return redirect('salones_admin')
