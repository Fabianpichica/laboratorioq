from django.db import models
from django.contrib.auth.models import User
from profesor.models import Guia

class Profile(models.Model):
    ROLE_CHOICES = [
        ('aprendiz', 'Aprendiz'),
        ('profesor', 'Profesor'),
        ('instructor', 'Instructor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Quimico(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class CuadernoEntry(models.Model):
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE)
    quimico = models.ForeignKey(Quimico, on_delete=models.CASCADE)
    guia = models.ForeignKey(Guia, on_delete=models.SET_NULL, null=True, blank=True, related_name='resultados')
    nota = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='cuadernos/', blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.aprendiz.username} - {self.guia.titulo if self.guia else 'Sin guía'} - {self.fecha.date()}"
