from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_profesor, name='dashboard_profesor'),
    path('salon/<int:salon_id>/jornada/<int:jornada_id>/', views.salon_estudiantes, name='salon_estudiantes'),
    path('guias/', views.guias_profesor, name='guias_profesor'),
    path('resultados-por-guia/', views.resultados_por_guia, name='resultados_por_guia'),
    path('materiales/', views.materiales_profesor, name='materiales_profesor'),
    path('perfil/', views.perfil_profesor, name='perfil_profesor'),
]