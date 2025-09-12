from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Equipo, Material
from core.models import Quimico

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    return render(request, 'adminlab/dashboard_admin.html', {})

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
