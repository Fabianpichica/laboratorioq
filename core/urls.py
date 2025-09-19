from django.urls import path
from . import views
from core.views import buscar_quimico_local

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_aprendiz, name='dashboard_aprendiz'),
    path('cuaderno/', views.cuaderno_aprendiz, name='cuaderno_aprendiz'),
    path('cuaderno/informe/<int:informe_id>/', views.informe_detalle, name='informe_detalle'),
    path('cuaderno/informe/<int:informe_id>/pdf/', views.descargar_informe_pdf, name='descargar_informe_pdf'),
    path('materiales/', views.materiales_equipos_view, name='materiales'),
    path('materiales/eliminar/<int:quimico_id>/', views.eliminar_quimico, name='eliminar_quimico'),
    path('materiales/editar/<int:quimico_id>/', views.editar_quimico, name='editar_quimico'),
    path('materiales/editar_material/<int:material_id>/', views.editar_material, name='editar_material'),
    path('materiales/eliminar_material/<int:material_id>/', views.eliminar_material, name='eliminar_material'),
    path('materiales/editar_equipo/<int:equipo_id>/', views.editar_equipo, name='editar_equipo'),
    path('materiales/eliminar_equipo/<int:equipo_id>/', views.eliminar_equipo, name='eliminar_equipo'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('perfil/', views.perfil_aprendiz, name='perfil_aprendiz'),
    path('logout/', views.logout_view, name='logout'),
    path('evaluaciones/', views.evaluaciones_aprendiz, name='evaluaciones_aprendiz'),
    path('buscar-quimico/', views.buscar_quimico_pubchem, name='buscar_quimico_pubchem'),
    path('buscar-quimico-local/', buscar_quimico_local, name='buscar_quimico_local'),
    path('detalle/quimico/<int:pk>/', views.detalle_quimico, name='detalle_quimico'),
    path('detalle/material/<int:pk>/', views.detalle_material, name='detalle_material'),
    path('detalle/equipo/<int:pk>/', views.detalle_equipo, name='detalle_equipo'),
]
