from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Quimico, CuadernoEntry
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            try:
                profile = Profile.objects.get(user=user)
                if profile.role == 'aprendiz':
                    return redirect('dashboard_aprendiz')
                elif profile.role == 'profesor':
                    return redirect('dashboard_profesor')
            except Profile.DoesNotExist:
                pass
            return redirect('/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
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
    if profile.role == 'aprendiz':
        if request.method == 'POST':
            nota = request.POST.get('nota')
            foto = request.FILES.get('foto')
            quimico_id = request.POST.get('quimico')
            quimico_usado = None
            if quimico_id:
                try:
                    quimico_usado = Quimico.objects.get(id=quimico_id)
                except Quimico.DoesNotExist:
                    quimico_usado = None
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
                'informes': informes
            })
        return render(request, 'cuaderno_aprendiz.html', {'quimicos': quimicos, 'informes': informes})
    else:
        return redirect('/')

@login_required
def informe_detalle(request, informe_id):
    informe = CuadernoEntry.objects.get(id=informe_id, aprendiz=request.user)
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
        if nombre and cantidad:
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
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'aprendiz':
        return redirect('/')
    quimico = Quimico.objects.get(id=quimico_id)
    if request.method == 'POST':
        quimico.nombre = request.POST.get('nombre')
        quimico.cantidad = request.POST.get('cantidad')
        quimico.descripcion = request.POST.get('descripcion')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        quimico.fecha_vencimiento = fecha_vencimiento if fecha_vencimiento else None
        quimico.save()
        return redirect('materiales')
    return render(request, 'editar_quimico.html', {'quimico': quimico})

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

def logout_view(request):
    logout(request)
    return redirect('login')
