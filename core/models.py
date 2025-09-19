from django.db import models
from django.contrib.auth.models import User
from profesor.models import Guia
import qrcode
from io import BytesIO
from django.core.files import File

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
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    ficha_seguridad = models.FileField(upload_to='fichas/', blank=True, null=True)
    protocolo_uso = models.FileField(upload_to='protocolos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        generating_qr = False
        if not self.pk:
            super().save(*args, **kwargs)  # Guardar primero para obtener el ID
            generating_qr = True
        if not self.qr_code or generating_qr:
            qr = qrcode.make(f"{self.get_absolute_url()}")
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f"quimico_{self.id}_qr.png"
            self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)  # Guardar normalmente

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detalle_quimico', args=[str(self.id)])

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_mantenimiento = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    ficha_seguridad = models.FileField(upload_to='fichas/', blank=True, null=True)
    protocolo_uso = models.FileField(upload_to='protocolos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Guardar primero para obtener el ID si es nuevo
        if not self.pk:
            super().save(*args, **kwargs)
        # Generar QR si no existe
        if not self.qr_code:
            from django.urls import reverse
            url = reverse('detalle_material', args=[str(self.id)])
            qr = qrcode.make(url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f"material_{self.id}_qr.png"
            self.qr_code.save(filename, File(buffer), save=False)
            # Guardar solo el campo qr_code
            super().save(update_fields=['qr_code'])
        else:
            # Guardar normalmente si no es nuevo
            if self.pk:
                super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detalle_material', args=[str(self.id)])

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_mantenimiento = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    ficha_seguridad = models.FileField(upload_to='fichas/', blank=True, null=True)
    protocolo_uso = models.FileField(upload_to='protocolos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Si el objeto es nuevo (no tiene pk), guardar primero para obtener el ID
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
        # Generar QR solo si no existe
        if not self.qr_code:
            from django.urls import reverse
            url = self.get_absolute_url()
            import qrcode
            from io import BytesIO
            from django.core.files import File
            qr = qrcode.make(url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f"equipo_{self.id}_qr.png"
            self.qr_code.save(filename, File(buffer), save=False)
            # Guardar solo el campo qr_code (no usar force_insert)
            super().save(update_fields=["qr_code"])
        elif not is_new:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detalle_equipo', args=[str(self.id)])

class CuadernoEntry(models.Model):
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE)
    quimico = models.ForeignKey(Quimico, on_delete=models.CASCADE)
    guia = models.ForeignKey(Guia, on_delete=models.SET_NULL, null=True, blank=True, related_name='resultados')
    nota = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='cuadernos/', blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    retroalimentacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.aprendiz.username} - {self.guia.titulo if self.guia else 'Sin guía'} - {self.fecha.date()}"
