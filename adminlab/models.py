from django.db import models

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='Disponible')

    def __str__(self):
        return self.nombre
