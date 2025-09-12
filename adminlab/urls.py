from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('inventario/', views.inventario_admin, name='inventario_admin'),
    # CRUD Reactivos
    path('inventario/quimico/agregar/', views.agregar_quimico_admin, name='agregar_quimico_admin'),
    path('inventario/quimico/<int:quimico_id>/editar/', views.editar_quimico_admin, name='editar_quimico_admin'),
    path('inventario/quimico/<int:quimico_id>/eliminar/', views.eliminar_quimico_admin, name='eliminar_quimico_admin'),
    # CRUD Materiales
    path('inventario/material/agregar/', views.agregar_material_admin, name='agregar_material_admin'),
    path('inventario/material/<int:material_id>/editar/', views.editar_material_admin, name='editar_material_admin'),
    path('inventario/material/<int:material_id>/eliminar/', views.eliminar_material_admin, name='eliminar_material_admin'),
    # CRUD Equipos
    path('inventario/equipo/agregar/', views.agregar_equipo_admin, name='agregar_equipo_admin'),
    path('inventario/equipo/<int:equipo_id>/editar/', views.editar_equipo_admin, name='editar_equipo_admin'),
    path('inventario/equipo/<int:equipo_id>/eliminar/', views.eliminar_equipo_admin, name='eliminar_equipo_admin'),
]
