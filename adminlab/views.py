from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Quimico, Profile, Material, Equipo
from profesor.models import Estudiante, Guia, Jornada, Salon
from .forms import ProfesorCustomForm
import json
import os
from googletrans import Translator
from datetime import datetime, timedelta

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    quimicos = Quimico.objects.all()
    estudiantes = Estudiante.objects.all()
    guias = Guia.objects.all()
    jornadas = Jornada.objects.all()
    salones = Salon.objects.all()
    profesores = User.objects.filter(is_staff=True)
    return render(request, 'adminlab/dashboard_admin.html', {
        'quimicos': quimicos,
        'estudiantes': estudiantes,
        'guias': guias,
        'jornadas': jornadas,
        'salones': salones,
        'profesores': profesores
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
        cas = request.POST.get('cas')
        codigo_inventario = request.POST.get('codigo_inventario')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        quimicos = Quimico.objects.all()  # Para mostrar en caso de error
        # Traducción de nombre si existe en quimicos_es.json, si no, traducir automáticamente
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'quimicos_es.json')
        nombre_es = None
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                traducciones = json.load(f)
            nombre_es = traducciones.get(nombre.strip().lower())
        except Exception:
            nombre_es = None
        # Si no hay traducción o es igual al original, forzar traducción automática
        if not nombre_es or nombre_es.strip().lower() == nombre.strip().lower():
            try:
                translator = Translator()
                nombre_es = translator.translate(nombre, src='en', dest='es').text
                # Si la traducción automática falla o no cambia, forzar español
                if not nombre_es or nombre_es.strip().lower() == nombre.strip().lower():
                    nombre_es = nombre
            except Exception:
                nombre_es = nombre
        # Si el nombre traducido sigue en inglés, forzar español manualmente
        if nombre_es and nombre_es.strip().lower() == nombre.strip().lower():
            # Si el nombre tiene palabras en inglés comunes, traducirlas manualmente
            traducciones_manual = {'water': 'agua', 'sodium': 'sodio', 'chloride': 'cloruro', 'acid': 'ácido', 'hydrogen': 'hidrógeno', 'oxygen': 'oxígeno'}
            for eng, esp in traducciones_manual.items():
                nombre_es = nombre_es.replace(eng, esp)
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        # Validación para código de inventario único
        if not codigo_inventario:
            messages.error(request, 'El campo Código inventario es obligatorio.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        if Quimico.objects.filter(codigo_inventario=codigo_inventario).exists():
            messages.error(request, 'Ya existe un reactivo con ese Código inventario. Debe ser único.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        Quimico.objects.create(
            nombre=nombre_es,
            cas=cas,
            codigo_inventario=codigo_inventario,
            cantidad=cantidad_int,
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
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/form_material_admin.html', {})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/form_material_admin.html', {})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/form_material_admin.html', {})
        Material.objects.create(
            nombre=nombre,
            cantidad=cantidad_int,
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
        cantidad = request.POST.get('cantidad')
        material.descripcion = request.POST.get('descripcion')
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/form_material_admin.html', {'material': material})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/form_material_admin.html', {'material': material})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/form_material_admin.html', {'material': material})
        material.cantidad = cantidad_int
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
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/form_equipo_admin.html', {})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/form_equipo_admin.html', {})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/form_equipo_admin.html', {})
        Equipo.objects.create(
            nombre=nombre,
            cantidad=cantidad_int,
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
        cantidad = request.POST.get('cantidad')
        equipo.descripcion = request.POST.get('descripcion')
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/form_equipo_admin.html', {'equipo': equipo})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/form_equipo_admin.html', {'equipo': equipo})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/form_equipo_admin.html', {'equipo': equipo})
        equipo.cantidad = cantidad_int
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

@login_required
def reactivos_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    from core.models import Quimico
    quimicos = Quimico.objects.all()
    # Calcular la fecha límite de vencimiento (hoy + 30 días)
    limite_vencimiento = datetime.now().date() + timedelta(days=30)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cas = request.POST.get('cas')
        codigo_inventario = request.POST.get('codigo_inventario')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        quimicos = Quimico.objects.all()  # Para mostrar en caso de error
        # Traducción de nombre si existe en quimicos_es.json, si no, traducir automáticamente
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'quimicos_es.json')
        nombre_es = None
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                traducciones = json.load(f)
            nombre_es = traducciones.get(nombre.strip().lower())
        except Exception:
            nombre_es = None
        # Si no hay traducción o es igual al original, forzar traducción automática
        if not nombre_es or nombre_es.strip().lower() == nombre.strip().lower():
            try:
                translator = Translator()
                nombre_es = translator.translate(nombre, src='en', dest='es').text
                if not nombre_es or nombre_es.strip().lower() == nombre.strip().lower():
                    nombre_es = nombre
            except Exception:
                nombre_es = nombre
        if nombre_es and nombre_es.strip().lower() == nombre.strip().lower():
            traducciones_manual = {'water': 'agua', 'sodium': 'sodio', 'chloride': 'cloruro', 'acid': 'ácido', 'hydrogen': 'hidrógeno', 'oxygen': 'oxígeno'}
            for eng, esp in traducciones_manual.items():
                nombre_es = nombre_es.replace(eng, esp)
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        # Validación para código de inventario único
        if not codigo_inventario:
            messages.error(request, 'El campo Código inventario es obligatorio.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        if Quimico.objects.filter(codigo_inventario=codigo_inventario).exists():
            messages.error(request, 'Ya existe un reactivo con ese Código inventario. Debe ser único.')
            return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos})
        Quimico.objects.create(
            nombre=nombre_es,
            cas=cas,
            codigo_inventario=codigo_inventario,
            cantidad=cantidad_int,
            descripcion=descripcion,
            fecha_vencimiento=fecha_vencimiento if fecha_vencimiento else None
        )
        messages.success(request, 'Reactivo agregado correctamente.')
        return redirect('reactivos_admin')
    return render(request, 'adminlab/reactivos.html', {'quimicos': quimicos, 'limite_vencimiento': limite_vencimiento})

@login_required
def materiales_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    materiales = Material.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/materiales.html', {'materiales': materiales})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/materiales.html', {'materiales': materiales})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/materiales.html', {'materiales': materiales})
        Material.objects.create(
            nombre=nombre,
            cantidad=cantidad_int,
            descripcion=descripcion
        )
        messages.success(request, 'Material agregado correctamente.')
        return redirect('materiales_admin')
    return render(request, 'adminlab/materiales.html', {'materiales': materiales})

@login_required
def equipos_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    equipos = Equipo.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        # Validación para cantidad
        if cantidad is None or cantidad == '':
            messages.error(request, 'El campo cantidad es obligatorio y debe ser un número.')
            return render(request, 'adminlab/equipos.html', {'equipos': equipos})
        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                messages.error(request, 'La cantidad debe ser un número positivo.')
                return render(request, 'adminlab/equipos.html', {'equipos': equipos})
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return render(request, 'adminlab/equipos.html', {'equipos': equipos})
        Equipo.objects.create(
            nombre=nombre,
            cantidad=cantidad_int,
            descripcion=descripcion
        )
        messages.success(request, 'Equipo agregado correctamente.')
        return redirect('equipos_admin')
    return render(request, 'adminlab/equipos.html', {'equipos': equipos})

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
        foto = request.FILES.get('foto')
        # Crear usuario Django para el estudiante
        user = User.objects.create_user(username=documento, password=password, first_name=nombre, email=correo)
        # Verificar si el perfil ya existe antes de crearlo
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user, role='aprendiz')
        estudiante = Estudiante.objects.create(
            nombre=nombre,
            documento=documento,
            tipo_documento=tipo_documento,
            salon_id=salon_id if salon_id else None,
            jornada_id=jornada_id if jornada_id else None,
            correo=correo,
            telefono=telefono,
            password=password,
            foto=foto
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
        foto = request.FILES.get('foto')
        if foto:
            estudiante.foto = foto
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
    if request.method == 'POST':
        guia.delete()
        messages.success(request, 'Guía eliminada correctamente.')
        return redirect('guias_admin')
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
            fecha=fecha
        )
        if profesor_id:
            jornada.profesores.add(profesor_id)
        salon_ids = request.POST.getlist('salones')
        if salon_ids:
            jornada.salones.set(salon_ids)
        messages.success(request, 'Jornada creada correctamente.')
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
        jornadas = Jornada.objects.filter(profesores=profesor)
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
def eliminar_profesor(request, profesor_id):
    if not request.user.is_superuser:
        return redirect('/')
    profesor = get_object_or_404(User, id=profesor_id)
    profesor.delete()
    messages.success(request, 'Profesor eliminado correctamente.')
    return redirect('profesores_admin')

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

def registrar_profesor(request):
    if request.method == 'POST':
        form = ProfesorCustomForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['numero_documento']
            password = form.cleaned_data['password']
            nombre = form.cleaned_data['nombre']
            tipo_documento = form.cleaned_data['tipo_documento']
            numero_documento = form.cleaned_data['numero_documento']
            fotografia = form.cleaned_data['fotografia']
            salones = form.cleaned_data['salones']
            jornadas = form.cleaned_data['jornadas']
            # Validar que el username no exista
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ya existe un usuario con ese número de documento.')
                return render(request, 'adminlab/registrar_profesor.html', {'form': form})
            # Crear usuario y marcar como staff
            user = User.objects.create_user(username=username, password=password, first_name=nombre)
            user.is_staff = True
            user.save()
            # Crear perfil solo si no existe
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'profesor'})
            if not created:
                profile.role = 'profesor'
                profile.save()
            if fotografia:
                profile.fotografia = fotografia
                profile.save()
            # Asignar jornadas (ahora ManyToMany)
            for jornada in jornadas:
                jornada.profesores.add(user)
            # Asignar salones (sin cambios)
            for salon in salones:
                salon.save()
            messages.success(request, 'Profesor registrado correctamente.')
            return redirect('profesores_admin')
    else:
        form = ProfesorCustomForm()
    return render(request, 'adminlab/registrar_profesor.html', {'form': form})

@login_required
def editar_profesor(request, profesor_id):
    if not request.user.is_superuser:
        return redirect('/')
    profesor = get_object_or_404(User, id=profesor_id)
    profile, _ = Profile.objects.get_or_create(user=profesor, defaults={'role': 'profesor'})
    salones = Salon.objects.all()
    jornadas = Jornada.objects.all()
    jornadas_actuales = jornadas.filter(profesores=profesor)
    salones_actuales = set()
    for jornada in jornadas_actuales:
        salones_actuales.update(jornada.salones.all())
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        password = request.POST.get('password')
        fotografia = request.FILES.get('fotografia')
        jornadas_ids = request.POST.getlist('jornadas')
        salones_ids = request.POST.getlist('salones')
        profesor.first_name = nombre
        if password:
            profesor.set_password(password)
        profesor.save()
        if fotografia:
            profile.fotografia = fotografia
            profile.save()
        for jornada in jornadas:
            if str(jornada.id) in jornadas_ids:
                jornada.profesores.add(profesor)
            else:
                jornada.profesores.remove(profesor)
        for jornada in jornadas:
            if str(jornada.id) in jornadas_ids:
                for salon in salones:
                    if str(salon.id) in salones_ids:
                        jornada.salones.add(salon)
                jornada.save()
        messages.success(request, 'Profesor actualizado correctamente.')
        return redirect('profesores_admin')
    return render(request, 'adminlab/editar_profesor.html', {
        'profesor': profesor,
        'profile': profile,
        'salones': salones,
        'jornadas': jornadas,
        'jornadas_actuales': jornadas_actuales,
        'salones_actuales': salones_actuales
    })

@login_required
def perfil_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    return render(request, 'adminlab/perfil_admin.html', {'user': request.user})

@login_required
def eliminar_profesor(request, profesor_id):
    if not request.user.is_superuser:
        return redirect('/')
    profesor = get_object_or_404(User, id=profesor_id)
    profesor.delete()
    messages.success(request, 'Profesor eliminado correctamente.')
    return redirect('profesores_admin')
