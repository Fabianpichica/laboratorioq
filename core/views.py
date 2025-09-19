from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Quimico, CuadernoEntry, Material, Equipo
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from profesor.models import Estudiante, Guia, Salon
import requests
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

def login_view(request):
    if request.method == 'POST':
        documento = request.POST['username']
        password = request.POST['password']
        from profesor.models import Estudiante
        from django.contrib.auth import authenticate, login as auth_login
        from core.models import Profile
        try:
            estudiante = Estudiante.objects.get(documento=documento)
            if estudiante.password == password:
                user = authenticate(request, username=estudiante.documento, password=password)
                if user:
                    auth_login(request, user)
                request.session['estudiante_id'] = estudiante.id
                return redirect('dashboard_aprendiz')
            else:
                messages.error(request, 'Documento o contraseña incorrectos.')
        except Estudiante.DoesNotExist:
            # Si no es aprendiz, intenta autenticar como User (profesor/instructor/superuser)
            user = authenticate(request, username=documento, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('dashboard_admin')
                try:
                    profile = Profile.objects.get(user=user)
                    if profile.role == 'profesor':
                        return redirect('dashboard_profesor')
                    elif profile.role == 'instructor':
                        return redirect('dashboard_instructor')
                except Profile.DoesNotExist:
                    pass
                return redirect('/')
            else:
                messages.error(request, 'Documento o contraseña incorrectos.')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST.get('role')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
        elif role not in ['aprendiz', 'profesor', 'instructor']:
            messages.error(request, 'Debes seleccionar un rol válido.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user, role=role)
            messages.success(request, 'Usuario creado correctamente. Puedes iniciar sesión.')
            return redirect('login')
    return render(request, 'register.html')

def landing_view(request):
    return render(request, 'landing.html')

@login_required
def dashboard_aprendiz(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'aprendiz':
        return render(request, 'dashboard_aprendiz.html', {
            'user': request.user,
            'profile': profile
        })
    else:
        return redirect('/')

@login_required
def cuaderno_aprendiz(request):
    profile = Profile.objects.get(user=request.user)
    quimicos = Quimico.objects.all()
    informes = CuadernoEntry.objects.filter(aprendiz=request.user).order_by('-fecha')
    # Obtener guías asignadas al aprendiz (según su salón)
    guias = []
    try:
        estudiante = Estudiante.objects.get(documento=request.user.username)
    except Estudiante.DoesNotExist:
        try:
            estudiante = Estudiante.objects.get(nombre=request.user.get_full_name())
        except Estudiante.DoesNotExist:
            estudiante = None
    salon = estudiante.salon if estudiante else None
    if salon:
        guias = Guia.objects.filter(salones=salon).distinct()
    if profile.role == 'aprendiz':
        if request.method == 'POST':
            nota = request.POST.get('nota')
            foto = request.FILES.get('foto')
            quimico_id = request.POST.get('quimico')
            guia_id = request.POST.get('guia')
            quimico_usado = None
            guia_usada = None
            if quimico_id:
                try:
                    quimico_usado = Quimico.objects.get(id=quimico_id)
                except Quimico.DoesNotExist:
                    quimico_usado = None
            if guia_id:
                try:
                    guia_usada = Guia.objects.get(id=guia_id)
                except Guia.DoesNotExist:
                    guia_usada = None
            imagen_url = None
            imagen_file = None
            if foto:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'cuadernos'))
                filename = fs.save(f"{request.user.username}_cuaderno_{foto.name}", foto)
                imagen_url = fs.url(filename)
                imagen_file = f"cuadernos/{filename.split('/')[-1]}"
            entry = CuadernoEntry.objects.create(
                aprendiz=request.user,
                quimico=quimico_usado,
                guia=guia_usada,
                nota=nota,
                imagen=imagen_file if imagen_file else None
            )
            informes = CuadernoEntry.objects.filter(aprendiz=request.user).order_by('-fecha')
            return render(request, 'cuaderno_aprendiz.html', {
                'nota': nota,
                'imagen_url': imagen_url,
                'quimicos': quimicos,
                'quimico_usado': quimico_usado,
                'quimico_usado_id': quimico_usado.id if quimico_usado else None,
                'guias': guias,
                'guia_usada_id': guia_usada.id if guia_usada else None,
                'informes': informes
            })
        return render(request, 'cuaderno_aprendiz.html', {'quimicos': quimicos, 'guias': guias, 'informes': informes})
    else:
        return redirect('/')

@login_required
def informe_detalle(request, informe_id):
    informe = get_object_or_404(CuadernoEntry, id=informe_id)
    # Solo permitir retroalimentar a profesores
    if request.method == 'POST' and hasattr(request.user, 'profile') and request.user.profile.role == 'profesor':
        retro = request.POST.get('retroalimentacion', '').strip()
        if retro:
            informe.retroalimentacion = retro
            informe.save()
    return render(request, 'informe_detalle.html', {'informe': informe})

@login_required
def descargar_informe_pdf(request, informe_id):
    informe = CuadernoEntry.objects.get(id=informe_id, aprendiz=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_{informe.id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height-50, "Informe de Laboratorio")
    p.setFont("Helvetica", 12)
    p.drawString(50, height-90, f"Fecha: {informe.fecha.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(50, height-110, f"Químico usado: {informe.quimico.nombre}")
    p.drawString(50, height-130, "Nota:")
    textobject = p.beginText(50, height-150)
    textobject.setFont("Helvetica", 12)
    for line in informe.nota.splitlines():
        textobject.textLine(line)
    p.drawText(textobject)
    if informe.imagen and informe.imagen.path:
        try:
            from reportlab.lib.utils import ImageReader
            p.drawImage(ImageReader(informe.imagen.path), 50, 100, width=200, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    p.showPage()
    p.save()
    return response

@login_required
def materiales_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'aprendiz':
        return redirect('/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        if nombre and cantidad and cantidad.isdigit():
            Quimico.objects.create(
                nombre=nombre,
                cantidad=cantidad,
                descripcion=descripcion,
                fecha_vencimiento=fecha_vencimiento if fecha_vencimiento else None
            )
    quimicos = Quimico.objects.all()
    return render(request, 'materiales.html', {'quimicos': quimicos})

@login_required
def eliminar_quimico(request, quimico_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'aprendiz':
        return redirect('/')
    Quimico.objects.filter(id=quimico_id).delete()
    return redirect('materiales')

@login_required
def editar_quimico(request, quimico_id):
    quimico = get_object_or_404(Quimico, id=quimico_id)
    if request.method == 'POST':
        quimico.nombre = request.POST.get('nombre')
        quimico.cantidad = request.POST.get('cantidad')
        quimico.descripcion = request.POST.get('descripcion')
        quimico.fecha_vencimiento = request.POST.get('fecha_vencimiento')
        if request.FILES.get('ficha_seguridad'):
            quimico.ficha_seguridad = request.FILES['ficha_seguridad']
        if request.FILES.get('protocolo_uso'):
            quimico.protocolo_uso = request.FILES['protocolo_uso']
        quimico.save()
        return redirect('materiales')
    return render(request, 'editar_quimico.html', {'quimico': quimico})

@login_required
def editar_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.nombre = request.POST.get('nombre')
        material.cantidad = request.POST.get('cantidad')
        material.descripcion = request.POST.get('descripcion')
        material.ubicacion = request.POST.get('ubicacion')
        material.fecha_mantenimiento = request.POST.get('fecha_mantenimiento')
        if request.FILES.get('ficha_seguridad'):
            material.ficha_seguridad = request.FILES['ficha_seguridad']
        if request.FILES.get('protocolo_uso'):
            material.protocolo_uso = request.FILES['protocolo_uso']
        material.save()
        return redirect('materiales')
    return render(request, 'editar_material.html', {'material': material})

@login_required
def eliminar_material(request, material_id):
    Material.objects.filter(id=material_id).delete()
    return redirect('materiales')

@login_required
def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    if request.method == 'POST':
        equipo.nombre = request.POST.get('nombre')
        equipo.cantidad = request.POST.get('cantidad')
        equipo.descripcion = request.POST.get('descripcion')
        equipo.ubicacion = request.POST.get('ubicacion')
        equipo.fecha_mantenimiento = request.POST.get('fecha_mantenimiento')
        if request.FILES.get('ficha_seguridad'):
            equipo.ficha_seguridad = request.FILES['ficha_seguridad']
        if request.FILES.get('protocolo_uso'):
            equipo.protocolo_uso = request.FILES['protocolo_uso']
        equipo.save()
        return redirect('materiales')
    return render(request, 'editar_equipo.html', {'equipo': equipo})

@login_required
def eliminar_equipo(request, equipo_id):
    Equipo.objects.filter(id=equipo_id).delete()
    return redirect('materiales')

@login_required
def reportes_view(request):
    User = get_user_model()
    aprendices = User.objects.filter(profile__role='aprendiz')
    aprendiz_id = request.GET.get('aprendiz')
    if aprendiz_id:
        aprendiz = User.objects.get(id=aprendiz_id)
    else:
        aprendiz = request.user if hasattr(request.user, 'profile') and request.user.profile.role == 'aprendiz' else aprendices.first()
    # Top 5 químicos más usados por el aprendiz
    quimicos_count = (CuadernoEntry.objects.filter(aprendiz=aprendiz)
                      .values('quimico__nombre')
                      .annotate(total=Count('quimico'))
                      .order_by('-total')[:5])
    labels = [q['quimico__nombre'] for q in quimicos_count]
    data = [q['total'] for q in quimicos_count]
    return render(request, 'reportes.html', {
        'labels': labels,
        'data': data,
        'aprendices': aprendices,
        'aprendiz_id': aprendiz.id if aprendiz else None
    })

@login_required
def perfil_aprendiz(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'aprendiz':
        return render(request, 'perfil_aprendiz.html', {
            'user': request.user,
            'profile': profile
        })
    else:
        return redirect('/')

@login_required
def evaluaciones_aprendiz(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'aprendiz':
        return redirect('/')
    # Buscar el estudiante por documento o por nombre de usuario
    estudiante = None
    try:
        estudiante = Estudiante.objects.get(documento=request.user.username)
    except Estudiante.DoesNotExist:
        # Buscar por nombre si el documento no coincide
        try:
            estudiante = Estudiante.objects.get(nombre=request.user.get_full_name())
        except Estudiante.DoesNotExist:
            return render(request, 'evaluaciones_aprendiz.html', {'guias': []})
    salon = estudiante.salon
    guias = Guia.objects.filter(salones=salon).distinct() if salon else []
    return render(request, 'evaluaciones_aprendiz.html', {'guias': guias})

@login_required
def buscar_quimico_pubchem(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/JSON'
    if query.replace('-', '').isdigit():
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/xref/RN/{query}/JSON'
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        results = []
        for c in data.get('PC_Compounds', []):
            props = c.get('props', [])
            nombre_iupac = None
            nombre_comun = None
            cas = None
            synonyms = c.get('synonyms', [])
            if synonyms:
                nombre_comun = synonyms[0]  # Primer sinónimo como nombre común
            for p in props:
                urn = p.get('urn', {})
                label = urn.get('label', '')
                name = urn.get('name', '')
                if label == 'IUPAC Name' and not nombre_iupac:
                    nombre_iupac = p.get('value', {}).get('sval', '')
                if label == 'Registry Number' and name == 'CAS':
                    cas = p.get('value', {}).get('sval', '')
            results.append({
                'nombre_comun': nombre_comun,
                'nombre_iupac': nombre_iupac,
                'cas': cas,
            })
        # Si no hay resultados, intentar buscar por synonym
        if not results and 'InformationList' in data:
            for info in data['InformationList'].get('Information', []):
                nombre_comun = info.get('Title', query)
                cas = info.get('RN', query)
                results.append({'nombre_comun': nombre_comun, 'nombre_iupac': None, 'cas': cas})
        return JsonResponse({'results': results})
    except Exception:
        return JsonResponse({'results': []})

@login_required
def buscar_quimico_local(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})
    quimicos = Quimico.objects.filter(nombre__istartswith=q)[:10]
    results = []
    for quimico in quimicos:
        results.append({
            'nombre_comun': quimico.nombre,
            'nombre_iupac': '',
            'cas': '',
        })
    return JsonResponse({'results': results})

@login_required
def materiales_equipos_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'aprendiz':
        return redirect('/')
    # CRUD para Químico
    if request.method == 'POST' and request.POST.get('tipo') == 'quimico':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        # Validar que todos los campos requeridos estén presentes y que cantidad sea un número
        if nombre and cantidad and cantidad.isdigit():
            # Validar que no exista un químico con el mismo nombre y fecha de vencimiento
            if not Quimico.objects.filter(nombre=nombre, fecha_vencimiento=fecha_vencimiento).exists():
                try:
                    Quimico.objects.create(
                        nombre=nombre,
                        cantidad=int(cantidad),
                        descripcion=descripcion,
                        fecha_vencimiento=fecha_vencimiento if fecha_vencimiento else None
                    )
                except Exception as e:
                    messages.error(request, f"Error al crear químico: {e}")
            else:
                messages.error(request, "Ya existe un químico con ese nombre y fecha de vencimiento.")
        else:
            messages.error(request, "Por favor, completa todos los campos requeridos y asegúrate de que la cantidad sea un número.")
    # CRUD para Material
    if request.method == 'POST' and request.POST.get('tipo') == 'material':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        ubicacion = request.POST.get('ubicacion')
        fecha_mantenimiento = request.POST.get('fecha_mantenimiento')
        if nombre and cantidad:
            if not Material.objects.filter(nombre=nombre, ubicacion=ubicacion).exists():
                Material.objects.create(
                    nombre=nombre,
                    cantidad=cantidad,
                    descripcion=descripcion,
                    ubicacion=ubicacion,
                    fecha_mantenimiento=fecha_mantenimiento if fecha_mantenimiento else None
                )
    # CRUD para Equipo
    if request.method == 'POST' and request.POST.get('tipo') == 'equipo':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        ubicacion = request.POST.get('ubicacion')
        fecha_mantenimiento = request.POST.get('fecha_mantenimiento')
        if nombre and cantidad:
            if not Equipo.objects.filter(nombre=nombre, ubicacion=ubicacion).exists():
                Equipo.objects.create(
                    nombre=nombre,
                    cantidad=cantidad,
                    descripcion=descripcion,
                    ubicacion=ubicacion,
                    fecha_mantenimiento=fecha_mantenimiento if fecha_mantenimiento else None
                )
    materiales = Material.objects.all()
    equipos = Equipo.objects.all()
    quimicos = Quimico.objects.all()

    # Alertas de stock bajo y vencimiento
    alerta_stock_bajo = []
    alerta_vencimiento = []
    for quimico in quimicos:
        if quimico.cantidad is not None and int(quimico.cantidad) <= 5:
            alerta_stock_bajo.append(quimico)
        if quimico.fecha_vencimiento and quimico.fecha_vencimiento <= timezone.now().date() + timedelta(days=30):
            alerta_vencimiento.append(quimico)
    return render(request, 'materiales.html', {
        'materiales': materiales,
        'equipos': equipos,
        'quimicos': quimicos,
        'alerta_stock_bajo': alerta_stock_bajo,
        'alerta_vencimiento': alerta_vencimiento
    })

def detalle_quimico(request, pk):
    quimico = get_object_or_404(Quimico, pk=pk)
    return render(request, 'detalle_quimico.html', {'quimico': quimico})

def detalle_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'detalle_material.html', {'material': material})

def detalle_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    return render(request, 'detalle_equipo.html', {'equipo': equipo})

def logout_view(request):
    logout(request)
    return redirect('login')
