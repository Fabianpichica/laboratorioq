from django.db import models
from django.contrib.auth.models import User

class Salon(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class Estudiante(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    jornada = models.ForeignKey('Jornada', on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    nombre = models.CharField(max_length=100, blank=True, null=True)
    documento = models.CharField(max_length=30, blank=True, null=True, unique=True)
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('EXT', 'Cédula extranjera'),
    ]
    tipo_documento = models.CharField(max_length=4, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    direccion = models.CharField(max_length=200, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=100, blank=True, null=True)
    nombre_contacto_emergencia = models.CharField(max_length=100, blank=True, null=True)
    eps = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='aprendices/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Jornada(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jornadas')
    salones = models.ManyToManyField(Salon, blank=True, related_name='jornadas')

    def __str__(self):
        return f"{self.nombre} ({self.fecha}) - {self.profesor.username}"

class Guia(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='guias/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    salones = models.ManyToManyField(Salon, blank=True, related_name='guias_asignadas')

    def __str__(self):
        return self.titulo
